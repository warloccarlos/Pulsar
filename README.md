# 🛰️ Pulsar

Pulsar is a high-performance, keyboard-centric audio engine built for the terminal. Unlike traditional terminal players that feel like static lists, Pulsar features a fluid, synchronized visualizer and a responsive layout designed for modern terminal emulators.

## ✨ Why Pulsar?

Not Your Average CLI: Featuring a multi-line, 8-row high frequency visualizer with built-in "gravity" for smooth, non-flickering motion.

Smart Directory Scanning: On launch, Pulsar automatically scans your Home, Downloads, and Music directories to build your library instantly.

Modern Interaction: Full support for Drag-and-Drop. Just drop an .mp3 from your file explorer directly into the terminal window.

Intelligent Autoplay: Seamlessly transitions between tracks with support for Shuffle and Repeat modes.

### ⌨️ Pro Controls

<img width="1004" height="537" alt="image" src="https://github.com/user-attachments/assets/a2c06e6b-a483-4370-9cda-d80de0c5eabb" />


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
