# NEXWAVE 5G: Intelligent Private 5G Network Simulation Platform

Compares Wi-Fi and Private 5G in a simulated industrial campus (400 m x 240 m, 6 buildings,
3 Wi-Fi APs, 4 private-5G small cells, 80 devices).

## Two ways to run it
1. **Instant demo (no install):** double-click `assets/nexwave5g_standalone.html` (any browser, works offline except the font).
2. **Python / Streamlit version:**
   ```
   pip install -r requirements.txt
   streamlit run app.py
   ```

## Structure
| File | What it does |
|---|---|
| `app.py` | Streamlit dashboard, 6 sections |
| `simulation/campus.py` | Buildings, AP and small-cell positions, devices, wall-crossing count |
| `simulation/coverage.py` | Log-distance path loss + wall loss, heatmaps, coverage % |
| `simulation/mobility.py` | Moving robot, cell selection with hysteresis, handover events and delays |
| `simulation/qos.py` | Queueing model: latency, packet loss, throughput; priority queues |
| `simulation/security.py` | Shared-password Wi-Fi vs challenge-response (SIM-style) authentication |
| `assets/nexwave5g_standalone.html` | Self-contained interactive version (same models in JavaScript) |

## Models and assumptions (all SIMULATED, not measured)
- **Path loss:** RSS = Pt - (PL1m + 10 n log10 d) - walls x wall_loss.
  Wi-Fi 5 GHz: Pt 23 dBm, PL1m 47 dB, n 3.3, 8 dB/wall. 5G n78 3.5 GHz: Pt 35 dBm, PL1m 43.3 dB, n 3.2, 5 dB/wall.
- **Usable signal:** -82 dBm for both networks. 5G has 4 nodes vs 3 for Wi-Fi.
- **Handover:** Wi-Fi sticky client 8 dB hysteresis, 90-300 ms interruption; 5G 3 dB hysteresis, 10-25 ms.
- **QoS:** capacity Wi-Fi 250 Mbps /(1+0.004 N), 5G 450 Mbps /(1+0.0003 N) where N = devices.
  Latency = base + k x 8 x rho/(1-rho). Priority queues let robot traffic see only part of the lower-priority load
  (leak factor 0.35 Wi-Fi, 0.04 5G). Traffic per device: robot 3, CCTV 8, guest 4, IoT 0.05 Mbps.
- **Security:** simulated hash challenge-response; not real 5G-AKA.
- Defaults overload Wi-Fi on purpose. Lower the sliders (e.g. 5 robots, 4 CCTV, 10 guests) to show a moderate-load case.

## 5G service triangle
eMBB = throughput and video, URLLC = robot latency/reliability/handover, mMTC = IoT device count.

## Likely faculty questions
- *Is this real 5G?* No. It is a simulation based on standard propagation and queueing models.
- *Why is 5G better here?* Higher transmit power, lower path-loss exponent, fast measurement-based handover, network slicing/priority scheduling.
- *Limitations?* 2D map, simple wall model, no interference, fading or real protocol stack. Future work: ns-3/5G-LENA.
