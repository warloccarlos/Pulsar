# 🛰️ Pulsar

Pulsar is a high-performance, keyboard-centric audio engine built for the terminal. Unlike traditional terminal players that feel like static lists, Pulsar features a fluid, synchronized visualizer and a responsive layout designed for modern terminal emulators.

## ✨ Why Pulsar?

Not Your Average CLI: Featuring a multi-line, 8-row high frequency visualizer with built-in "gravity" for smooth, non-flickering motion.

Smart Directory Scanning: On launch, Pulsar automatically scans your Home, Downloads, and Music directories to build your library instantly.

Modern Interaction: Full support for Drag-and-Drop. Just drop an .mp3 from your file explorer directly into the terminal window.

Intelligent Autoplay: Seamlessly transitions between tracks with support for Shuffle and Repeat modes.

### ⌨️ Pro Controls

<img width="591" height="290" align="right" alt="image" src="https://github.com/user-attachments/assets/5d3ca895-9404-4a74-9471-b4bfaba73fe0" />


Pulsar is designed to stay out of your way. Control everything with a few keystrokes:
##### Key	Action

##### Space	Play / Pause
##### ↑ / ↓	Volume Control (with visual HUD)
##### N / Z	Next / Previous Track
##### S	Shuffle Mode Toggle
##### R	Repeat Mode Toggle
##### X	Delete selected track from playlist
##### B	Sidebar Toggle (Hide for "Zen" mode)
##### Q	Quit

#### Installation

clone the repo
      
      cd Pulsar

      python -m venv .venv

      For Windows - .venv\Scripts\activate and For Linux - source .venv/bin/activate
      
      pip install textual pygame numpy
   
      python pulsar.py
