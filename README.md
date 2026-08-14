# LagForge ⚡
> **Obsidian Glassmorphic Global Latency Control for Windows**

LagForge is a high-performance Windows desktop application built with **Python**, **PySide6**, and **WinDivert** (`pydivert`) that injects artificial, controlled latency into system-wide network traffic for network resilience testing, game simulation, and QA engineering.

---

## 📸 Preview & Design
Designed with an **Obsidian Dark Glassmorphism** aesthetic:
- **Base Background:** Deep Obsidian / Pitch Slate (`#090A0F`)
- **Card Panels:** Frosted translucent slate (`#13151E`) with subtle `1px` borders (`#212638`) and `12px` rounded corners
- **Accents:** Electric Cyan (`#00F0FF`) slider & highlights with Neon Emerald (`#10B981`) active indicators
- **Live Telemetry:** Smooth rolling sparkline graph showing real-time network throughput and packet delay metrics

---

## 🚀 Key Features
- 🎛️ **Precision Delay Slider**: Dynamically adjust latency from `0ms` to `1000ms` in real-time without restarting the network filter.
- ⚡ **One-Click Presets**: Fast switching between common testing profiles (`+50ms`, `+100ms`, `+200ms`, `+500ms`).
- 🔄 **Bidirectional Half-RTT Ping Engine**: Automatically splits target ping in half (`target_ping / 2.0`) to model real-world inbound and outbound RTT symmetry.
- 📊 **Real-time Telemetry & Sparkline**: Live packet counter, packets-per-second throughput graph, and split Inbound/Outbound millisecond readouts.
- 🛡️ **Zero-Drop Clean Teardown**: Automatically drains and safely re-injects pending packets on shutdown so your network stack never stalls or hangs.
- 🔑 **Automatic UAC Elevation**: Verifies Windows Administrator privileges at startup and requests elevation seamlessly via `runas`.

---

## 🛠️ Project Structure
```
lagforge/
├── main.py                # App entry point, UAC admin elevation wrapper
├── engine.py              # WinDivert packet capture, PriorityQueue scheduler, and telemetry
├── ui/
│   ├── __init__.py        # UI package initialization
│   ├── main_window.py     # Master Obsidian Glassmorphic layout & signal bindings
│   ├── custom_controls.py # Custom Slider with ticks, geometric logo, status dots
│   ├── pill_switch.py     # Animated Active/Inactive toggle switch
│   ├── sparkline.py       # Live rolling QPainter sparkline graph
│   └── styles.py          # Curated Obsidian Glassmorphic QSS stylesheet & color tokens
├── requirements.txt       # Dependencies (PySide6, pydivert)
├── .gitignore             # Python / Windows build ignores
└── README.md              # Project documentation
```

---

## 📦 Installation & Requirements

### Prerequisites
- **Operating System:** Windows 10 / Windows 11 (64-bit)
- **Python:** Python 3.10+ (Python 3.11 recommended)
- **Administrator Rights:** Required by the WinDivert kernel driver to capture and re-inject network packets.

### Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/valliente/lagforge.git
   cd lagforge
   ```

2. **Create a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run LagForge:**
   ```bash
   python main.py
   ```
   *(A Windows UAC prompt will appear to grant administrator privileges for WinDivert).*

   To run in preview/dry-run mode without UAC elevation:
   ```bash
   python main.py --no-elevation
   ```

---

## 📐 Architecture & Ping Delay Math
```
                      +-----------------------------+
                      |   LagForge PySide6 GUI      |
                      |  (Obsidian Glassmorphism)   |
                      +--------------+--------------+
                                     |
                       User adjusts latency (e.g. 325ms)
                                     v
                 +---------------------------------------+
                 |       PacketDelayEngine (engine.py)   |
                 +---------------------------------------+
                     /                               \
                    v                                 v
   +---------------------------------+   +---------------------------------+
   | Capture Worker Thread (QThread) |   | Sender Worker Thread (QThread)  |
   | Reads: WinDivert("!loopback")   |   | Monitors PriorityQueue          |
   | Delay = Target Ping / 2.0       |   | Pops when release_time <= now   |
   | Enqueues (release_time, pkt)    |   | Calls w.send(pkt) to re-inject  |
   +---------------------------------+   +---------------------------------+
```

---

## 📜 License
MIT License. Created for network simulation, developer testing, and game resilience profiling.
