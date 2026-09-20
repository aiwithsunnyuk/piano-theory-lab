# 🎹 Piano Theory Lab

Piano Theory Lab is an interactive, full-stack web application designed for music theory visualization, chord progression generation, and practice tracking. Built with Streamlit, it bridges advanced Python music theory calculations (`music21`) with real-time browser audio (`Tone.js`) and persistent data storage (`SQLAlchemy`).

## ✨ Features

* **Interactive 88-Key Visualizer:** A dynamic SVG-based piano keyboard that maps out generated chords and scales in real-time.
* **AI Practice Instructor:** Generates musically accurate 4-chord progressions (e.g., Modern Worship, Jazz, Pop) dynamically based on selected root notes, chord qualities, and skill levels (Triads, 7ths, Extensions).
* **Browser Audio Engine:** Integrated `Tone.js` allows users to hear acoustic grand piano playback of generated chords with a single click.
* **Web MIDI Integration:** Connect a physical USB MIDI keyboard (like a Korg EK-50) to see physical key presses highlighted directly on the web interface.
* **Practice History & Persistence:** Save favorite progressions to a local SQLite database using SQLAlchemy. Users can load past progressions from the sidebar or delete them to keep their workspace clean.

## 🛠️ Tech Stack

* **Frontend / UI:** [Streamlit](https://streamlit.io/) (Python)
* **Music Theory Engine:** [music21](https://web.mit.edu/music21/)
* **Audio Synthesis:** [Tone.js](https://tonejs.github.io/) (JavaScript injected via Streamlit components)
* **Database / ORM:** SQLite & SQLAlchemy
* **Language:** Python 3

## 🚀 Local Development Setup

### 1. Prerequisites
Ensure you have Python 3.9+ installed on your machine. 

### 2. Clone and Initialize
Clone this repository and navigate into the project directory:
```bash
git clone [https://github.com/YOUR-USERNAME/piano-theory-lab.git](https://github.com/YOUR-USERNAME/piano-theory-lab.git)
cd piano-theory-lab