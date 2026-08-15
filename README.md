# LagForge ⚡
> **Obsidian Glassmorphic Global Latency & Network Condition Control for Windows (v1.101)**

LagForge is a high-performance Windows desktop application built with **Python**, **PySide6**, and **WinDivert** (`pydivert`) that injects artificial, controlled latency, Gaussian jitter, and packet loss into system-wide network traffic for network resilience testing, game simulation, and QA engineering.

---

## 📸 Preview & Design
Designed with an **Obsidian Dark Glassmorphism** aesthetic:
- **Base Background:** Deep Obsidian / Pitch Slate (`#090A0F`)
- **Card Panels:** Frosted translucent slate (`#13151E`) with subtle `1px` borders (`#212638`) and `12px` rounded corners
- **Accents:** Electric Cyan (`#00F0FF`) slider & highlights with Neon Emerald (`#10B981`) active indicators and Coral (`#F43F5E`) packet drop counters
- **Live Telemetry:** Smooth 60fps rolling sparkline graph showing real-time network throughput and packet delay metrics

---

## 🚀 Key Features (v1.101)
- 🎛️ **Precision Delay Slider**: Dynamically adjust latency from `0ms` to `1000ms` in real-time without restarting the network filter.
- 〰️ **Gaussian Packet Jitter**: Simulate erratic, fluctuating connections with customizable jitter (`0ms` to `±100ms`).
- 🛑 **Packet Drop Simulation**: Emulate real-world packet loss (`0%` to `25%`) with stochastic drop algorithms.
- ⚡ **One-Click Presets & Profiles**: Instant switching between presets (`+50ms`, `+100ms`, `+200ms`, `+500ms`) or save custom named profiles (`config.json`).
- ⌨️ **Global Hotkey Toggle**: Press `F8` or `Ctrl+Shift+L` anywhere in Windows to toggle lag on/off without alt-tabbing out of fullscreen games.
- 📥 **System Tray Quick-Switch**: Context menu to toggle active state or switch latency presets directly from the notification area.
- 🔄 **Bidirectional Half-RTT Ping Engine**: Automatically splits target ping in half (`target_ping / 2.0`) to model real-world inbound and outbound RTT symmetry.
- 📊 **Real-time Telemetry & Sparkline**: Live packet counter, dropped packet counter, throughput (KB/s in/out), and split Inbound/Outbound millisecond readouts.
- 🛡️ **Zero-Drop Clean Teardown**: Automatically drains and safely re-injects pending packets on shutdown so your network stack never stalls or hangs.
- 🔑 **Automatic UAC Elevation**: Verifies Windows Administrator privileges at startup and requests elevation seamlessly via `runas`.

---

## 🛠️ Project Structure
```
lagforge/
├── main.py                # App entry point, UAC admin elevation wrapper, hotkey wiring
├── engine.py              # WinDivert packet capture, PriorityQueue scheduler, jitter & loss
├── hotkey_manager.py      # Win32 global hotkey listener (F8 / Ctrl+Shift+L)
├── config_manager.py      # JSON persistent settings and custom profile storage
├── ui/
│   ├── __init__.py        # UI package initialization
│   ├── main_window.py     # Master Obsidian Glassmorphic layout & signal bindings
│   ├── custom_controls.py # Sliders (Latency, Jitter, Loss), geometric logo, status dots
│   ├── profile_dialog.py  # Profile presets management modal dialog
│   ├── pill_switch.py     # Animated Active/Inactive toggle switch with pulsing glow
│   ├── sparkline.py       # Live rolling 60fps QPainter sparkline graph
│   └── styles.py          # Curated Obsidian Glassmorphic QSS stylesheet & color tokens
├── tests/
│   └── test_lagforge.py   # Test suite for engine math, jitter, packet loss, and UI
├── requirements.txt       # Dependencies (PySide6, pydivert, pytest)
├── LagForge.spec          # PyInstaller standalone build specification
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

2. **Create a virtual environment (optional):**
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

---

## ⌨️ Hotkeys & Shortcuts
| Key | Action |
| :--- | :--- |
| `F8` | Global Active / Inactive Toggle |
| `Ctrl+Shift+L` | Global Active / Inactive Toggle |
| `Profiles ⚙` | Open Custom Presets Manager |

---

## 📜 License
MIT License. Created for network simulation, developer testing, and game resilience profiling.
