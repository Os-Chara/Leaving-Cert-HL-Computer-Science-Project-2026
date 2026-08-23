# Leaving-Cert-HL-Computer-Science-Project-2026
This is my LC Computer Science project from the 2025-2026 academic year, from which I received a H1. The project focused on embedded systems and computer modeling. My project was a tree-mounted wildfire monitoring system created with a Raspberry Pi Pico W, and a python based model graphed using matplotlib.

To view the project open through "index.html" and navigate from there.

"main.py", "oled_1inch3.py", and secrets should all be contained onboard the Pico's internal flash memory.

"main.py" is the python file which is run on the Raspberry Pi Pico when powered on.
"oled_1inch3.py" is the driver file for the OLED display.
"secrets.py" is used to hide your network details for privacy. (The network details must match the network your computer is connected to in order to receive the real time data)

"Disaster Risk Model.py" should be ran on a computer in a Python IDE (e.g. Thonny) and contained in the same file as the .csv files.
