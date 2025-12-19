tilt controller system code 
import requests
import pyautogui
import time

# ---------- CONFIG ----------
PICO_IP = ""  # Replace with your Pico W IP
URL = f"http://{PICO_IP}:8080/data"

FAST_POLL = 0.05   # 50ms when actively tilting
SLOW_POLL = 0.15   # 150ms when neutral
DEAD_ZONE = 0.5    # Ignore tiny tilts

# Tilt thresholds
PITCH_FORWARD_TAP = 10
PITCH_FORWARD_HOLD = 20

PITCH_BACKWARD_TAP = -10
PITCH_BACKWARD_HOLD = -20

ROLL_RIGHT_TAP = 10
ROLL_RIGHT_HOLD = 20

ROLL_LEFT_TAP = -10
ROLL_LEFT_HOLD = -20

# Key mapping
UP_KEY = 'up'
DOWN_KEY = 'down'
LEFT_KEY = 'left'
RIGHT_KEY = 'right'

print("Starting hybrid adaptive tilt controller...")

# State trackers
key_states = {UP_KEY: False, DOWN_KEY: False, LEFT_KEY: False, RIGHT_KEY: False}
tap_states = {UP_KEY: False, DOWN_KEY: False, LEFT_KEY: False, RIGHT_KEY: False}

def press_and_hold(key):
    if not key_states[key]:
        pyautogui.keyDown(key)
        key_states[key] = True

def release_key(key):
    if key_states[key]:
        pyautogui.keyUp(key)
        key_states[key] = False

def single_tap(key):
    """Do a quick tap only once per tilt entry."""
    if not tap_states[key]:
        pyautogui.keyDown(key)
        pyautogui.keyUp(key)
        tap_states[key] = True

def reset_tap(key):
    tap_states[key] = False

try:
    while True:
        try:
            # Fetch tilt data from Pico W
            response = requests.get(URL, timeout=5)
            data = response.json()

            pitch = data.get('pitch', 0)
            roll  = data.get('roll', 0)

            # Apply dead zone
            pitch = 0 if abs(pitch) < DEAD_ZONE else pitch
            roll  = 0 if abs(roll) < DEAD_ZONE else roll

            # Track if we are in "active movement"
            active = False

            # ----- Forward / Backward -----
            if pitch > PITCH_FORWARD_HOLD:
                press_and_hold(UP_KEY)
                active = True
            elif pitch > PITCH_FORWARD_TAP:
                single_tap(UP_KEY)
                release_key(UP_KEY)
                active = True
            else:
                release_key(UP_KEY)
                reset_tap(UP_KEY)

            if pitch < PITCH_BACKWARD_HOLD:
                press_and_hold(DOWN_KEY)
                active = True
            elif pitch < PITCH_BACKWARD_TAP:
                single_tap(DOWN_KEY)
                release_key(DOWN_KEY)
                active = True
            else:
                release_key(DOWN_KEY)
                reset_tap(DOWN_KEY)

            # ----- Left / Right -----
            if roll > ROLL_RIGHT_HOLD:
                press_and_hold(RIGHT_KEY)
                active = True
            elif roll > ROLL_RIGHT_TAP:
                single_tap(RIGHT_KEY)
                release_key(RIGHT_KEY)
                active = True
            else:
                release_key(RIGHT_KEY)
                reset_tap(RIGHT_KEY)

            if roll < ROLL_LEFT_HOLD:
                press_and_hold(LEFT_KEY)
                active = True
            elif roll < ROLL_LEFT_TAP:
                single_tap(LEFT_KEY)
                release_key(LEFT_KEY)
                active = True
            else:
                release_key(LEFT_KEY)
                reset_tap(LEFT_KEY)

            # Adaptive polling: fast if active, slow if idle
            if active:
                time.sleep(FAST_POLL)
            else:
                time.sleep(SLOW_POLL)

        except (requests.exceptions.RequestException, ValueError) as e:
            print("Connection error:", e)
            time.sleep(SLOW_POLL)
            continue

except KeyboardInterrupt:
    print("Exiting... Releasing all keys.")
    for key in key_states.keys():
        pyautogui.keyUp(key)
