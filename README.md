# ^^ MicroFly ^^

**MicroFly** is an endless arcade game for the ESP32 platform featuring a unique touchless control system. By using an ultrasonic sensor, your hand becomes a physical controller—move it up or down to maneuver through obstacles.

## 🕹️ Game Concept

You control a small cube flying toward incoming pillars. Your mission is to navigate through the gaps between them. The difficulty (scrolling speed) increases every 5 points, testing your reflexes and hand-positioning precision.

### How to Play

1. **Start:** Place your hand within the sensor's active zone (**5 — 25 cm** or ~2 — 10 inches).
2. **Controls:**
   - Move your hand **closer** to the sensor to make the character **descend**.
   - Move your hand **further away** to make the character **ascend**.
3. **Pause:** If you remove your hand from the active zone during gameplay, the game will automatically pause.
   - *To resume:* Simply return your hand to the active zone.
4. **Restart:** After a "Game Over," move your hand completely away from the sensor (>45cm) and then back into the active zone to try again.

## 🚀 Key Features

* **Absolute Positioning:** The character's vertical position is directly mapped to the physical distance between the sensor and your hand.
* **Smart Filtering:**
  - **EMA Algorithm:** Uses Exponential Moving Average for buttery-smooth movement.
  - **Outlier Rejection:** Intelligently ignores sensor glitches to prevent "ghost" collisions.
* **High Score System:** The game tracks your best performance and displays the difference (`DIFF`) after each attempt compared to your previous record.
* **Clean Exit:** Implemented via `try...finally`. When the script is stopped, it displays a 3-second goodbye screen with your stats before safely clearing the display.

## 🛠️ Compatibility & Hardware

The project is developed and tested using the following configuration:

* **Controller:** ESP32 (30-pin Dual Core)
* **Display:** 0.96" OLED (SSD1306 chip, 128x64 pixels, I2C connection)
* **Sensor:** HC-SR04 Ultrasonic Rangefinder
* **Expansion:** Expansion Board for easy peripheral connection
* **Language:** MicroPython

### Wiring (GPIO)

| Component | Pin (ESP32) | Function |
| :--- | :--- | :--- |
| **OLED** | Pin 22 | SCL |
| **OLED** | Pin 21 | SDA |
| **HC-SR04** | Pin 5 | Trig |
| **HC-SR04** | Pin 18 | Echo |

> **Note:** Both the sensor and display should be powered by the 5V/3.3V rails on the expansion board for stability.

---
*Made with love for code and electronics.*