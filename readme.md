# pw-matrix
*Professional PipeWire Audio Routing Matrix*

## 1. Overview
**pw-matrix** is a lightweight, professional-grade visual patchbay for Linux systems running PipeWire. Designed with a DAW-style (Ardour/Reaper) matrix grid, it allows you to instantly route audio between hardware devices and software applications.

It features automatic intelligent port aliasing (cleaning up messy ALSA strings), crosshair highlighting to prevent routing mistakes, and a unique **Diagonal Swipe** feature for rapid bulk connections.

---

## 2. Installation Instructions
This application is written in Python and uses **PyQt6** for its graphical interface. It utilizes your system's native `pw-link` commands under the hood.

### Prerequisites (Ubuntu / Debian)
Open your terminal and install the required Python bindings:
```bash
sudo apt update
sudo apt install python3-pyqt6
