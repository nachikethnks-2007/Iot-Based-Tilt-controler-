# IoT-Based Tilt Controller 🎮

This project demonstrates a tilt-controlled IoT system built using
**Raspberry Pi Pico W** and **MicroPython** as a college IoT mini project.

## Overview
The system detects tilt using a sensor and performs actions such as
controlling the **navigation (arrow) keys of a laptop keyboard**
based on the direction of tilt.

Using this mechanism, the project can be used to control **racing or
gesture-based games** on a laptop. It showcases sensor interfacing,
wireless data transfer, and control logic using **MicroPython and Python**.

## Hardware Used
- Raspberry Pi Pico W
- Tilt Sensor / MPU6050
- Breadboard
- Jumper Wires
- Power Supply

## Software & Tools
- MicroPython
- Python
- Thonny IDE
- VS Code

## Working
- The tilt sensor detects changes in orientation.
- Raspberry Pi Pico W reads the sensor data using MicroPython.
- The tilt values are sent to a web interface hosted by the Pico W.
- A Python program running on the laptop reads the tilt data.
- Based on the received values, the laptop’s **arrow keys** are controlled,
  enabling gesture-based navigation or gaming control.

## Applications
- Gesture-controlled devices
- Gesture-based gaming controllers
- Robotics control
- Smart embedded systems

## Academic Context
Developed as part of a college IoT mini project in a previous semester.
