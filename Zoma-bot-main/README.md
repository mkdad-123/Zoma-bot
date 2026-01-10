#  Zuma Vision Bot (Computer Vision Project)

##  Project Overview

This project is an **academic computer vision project** that applies **classical image processing techniques** (no machine learning) to analyze and interact with the game **Zuma**.

The goal is to:

* Detect the game window automatically
* Detect colored balls on the path
* Detect the frog’s **current ball** and **next ball**
* Visualize detections in real time using OpenCV

⚠️ **Note:**
This project is **still under development**. Shooting logic and decision-making are not implemented yet.

---

##  Core Concepts Used

* HSV color space
* Color thresholding
* Hough Circle Transform
* Region of Interest (ROI) sampling
* Rule-based color classification
* Real-time screen capture
* Geometry-based detection

---

## 🗂️ Project Structure

```text
CV_PROJECT/
│
├── main.py          # Main loop and screen capture
├── config.py        # Constants and configuration
├── vision.py        # All vision-related algorithms
├── utils.py         # Helper utilities (FPS, resizing, windows)
├── frog_calibration.png  # Saved frame for manual calibration
└── README.md
```

---

## ⚙️ File Descriptions

### `config.py`

Contains:

* HSV thresholds
* Display settings
* Color maps
* Manually calibrated frog parameters:

  * `FROG_CENTER`
  * `FROG_RADIUS`

---

### `vision.py`

Contains all computer vision logic:

* `detect_game_window()`
  Detects the Zuma game window using green background segmentation.

* `detect_balls()`
  Detects path balls using **HoughCircles + HSV color validation**.

* `detect_frog_balls()`
  Detects:

  * **Next ball** (ball on frog’s back)
  * **Current ball** (ball in frog’s mouth)
    using geometric search and HSV ROI sampling.

* `classify_ball_color()`
  Rule-based color classification (Red, Green, Blue, Yellow, Purple).

---

### `utils.py`

Utility functions:

* FPS calculation
* Window management
* Frame resizing for preview

---

### `main.py`

* Locks the game window
* Captures frames using `mss`
* Runs detection pipelines
* Draws visual debugging information
* Displays FPS and detection results

---

## 🎯 Current Features

✅ Game window detection
✅ Ball detection on the path
✅ Frog back ball detection (next ball)
✅ Frog mouth ball detection (current ball)
✅ Real-time visualization
✅ Modular & readable code structure

---

## 🚧 Known Limitations

* Frog center and radius are **manually calibrated**
* Current ball detection depends on geometric assumptions
* No shooting logic implemented yet
* No trajectory prediction
* No collision simulation

---

## 🛠️ Planned Next Steps

* Implement state-based shooting logic
* Compute shooting angle
* Predict ball collision
* Improve robustness against lighting changes
* Optional: automatic frog calibration

---

## 📚 Academic Context

This project was developed as part of a **computer vision course**, with the constraint of:

> ❌ No machine learning
> ❌ No deep learning
> ✅ Classical image processing only

---

## 👥 Team & Collaboration

This repository is shared for **educational purposes**.
Feel free to explore, suggest improvements, or extend the logic.

---

## ⚠️ Disclaimer

This project is **not intended for cheating or competitive use**.
It is strictly an academic experiment to practice computer vision techniques.

---
