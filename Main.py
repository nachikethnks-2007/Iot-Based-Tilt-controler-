tilt controller code 
import network
import socket
import utime
import math
from MPU6050 import MPU6050
from machine import Pin, SoftI2C

# ---------- Wi-Fi ----------
SSID = "your personal network name "
PASSWORD = "personal network password"

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if not wlan.isconnected():
    print("Connecting to Wi-Fi...")
    wlan.connect(SSID, PASSWORD)
    while not wlan.isconnected():
        utime.sleep(1)
print("Connected, IP:", wlan.ifconfig()[0])
ip = wlan.ifconfig()[0]

# ---------- MPU6050 Initialization with Retry ----------
def init_mpu(retries=5, delay=1):
    for attempt in range(retries):
        try:
            sensor = MPU6050()
            print("MPU6050 initialized successfully!")
            return sensor
        except Exception as e:
            print("MPU6050 init failed, retrying... ({}/{})".format(attempt+1, retries))
            utime.sleep(delay)
    raise Exception("MPU6050 failed to initialize after {} retries.".format(retries))

sensor = init_mpu()

def get_orientation(ax, ay, az):
    pitch = math.degrees(math.atan2(ax, math.sqrt(ay**2 + az**2)))
    roll = math.degrees(math.atan2(ay, math.sqrt(ax**2 + az**2)))
    yaw = math.degrees(math.atan2(az, math.sqrt(ax**2 + ay**2)))
    return pitch, roll, yaw

# ---------- HTML with Gauges ----------
html_template = """<!DOCTYPE html>
<html>
<head>
<title>Pico W Tilt Monitor Gauges</title>
<style>
body { font-family: Arial; text-align:center; }
h1 { color: #333; }
canvas { margin: 20px; background: #f0f0f0; border-radius: 10px; }
</style>
<script>
let pitch = 0, roll = 0, yaw = 0, temp = 0;
function fetchTilt() {
    fetch('/data').then(resp => resp.json()).then(data => {
        pitch = data.pitch;
        roll = data.roll;
        yaw = data.yaw;
        temp = data.temp;
        drawGauges();
    });
}
setInterval(fetchTilt, 100);
function drawGauge(ctx, value, label) {
    ctx.clearRect(0,0,220,220);
    let cx=110, cy=110, radius=90;
    let start=0.75*Math.PI, end=0.25*Math.PI;
    ctx.beginPath();
    ctx.arc(cx, cy, radius, start, end, false);
    ctx.strokeStyle='#ccc';
    ctx.lineWidth=15;
    ctx.stroke();
    let percent=Math.min(Math.max(value/180,0),1);
    let angle=start+percent*1.5*Math.PI;
    ctx.beginPath();
    ctx.arc(cx, cy, radius, start, angle, false);
    ctx.strokeStyle='green';
    ctx.lineWidth=15;
    ctx.stroke();
    let needleAngle=start+percent*1.5*Math.PI;
    ctx.beginPath();
    ctx.moveTo(cx, cy);
    ctx.lineTo(cx+radius*0.8*Math.cos(needleAngle), cy+radius*0.8*Math.sin(needleAngle));
    ctx.strokeStyle='#000';
    ctx.lineWidth=4;
    ctx.stroke();
    ctx.beginPath();
    ctx.arc(cx, cy, 5, 0, 2*Math.PI);
    ctx.fillStyle='#000';
    ctx.fill();
    ctx.font="16px Arial";
    ctx.fillStyle="#000";
    ctx.fillText(label+": "+value.toFixed(2), cx-50, cy+radius+20);
}
function drawGauges() {
    drawGauge(document.getElementById('pitchGauge').getContext('2d'), pitch, "Pitch");
    drawGauge(document.getElementById('rollGauge').getContext('2d'), roll, "Roll");
    drawGauge(document.getElementById('yawGauge').getContext('2d'), yaw, "Yaw");
    drawGauge(document.getElementById('tempGauge').getContext('2d'), temp, "Temp");
}
</script>
</head>
<body>
<h1>Pico W Tilt Monitor Gauges</h1>
<canvas id="pitchGauge" width="220" height="220"></canvas>
<canvas id="rollGauge" width="220" height="220"></canvas>
<canvas id="yawGauge" width="220" height="220"></canvas>
<canvas id="tempGauge" width="220" height="220"></canvas>
</body>
</html>
"""

# ---------- Webserver ----------
addr = socket.getaddrinfo('0.0.0.0', 8080)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)
print("Webserver running at http://{}".format(ip))

while True:
    try:
        cl, addr = s.accept()
        req = cl.recv(1024).decode('utf-8')
        if 'GET /data' in req:
            try:
                accel = sensor.read_accel_data(g=True)
                pitch, roll, yaw = get_orientation(accel['x'], accel['y'], accel['z'])
                temp = sensor.read_temperature()
            except Exception as e:
                pitch = roll = yaw = temp = 0
            response = "HTTP/1.0 200 OK\r\nContent-Type: application/json\r\n\r\n"
            response += '{{"pitch": {}, "roll": {}, "yaw": {}, "temp": {}}}'.format(pitch, roll, yaw, temp)
            cl.send(response)
        else:
            cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
            cl.send(html_template)
        cl.close()
    except Exception as e:
        print("Error:", e)
