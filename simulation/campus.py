"""Virtual industrial campus: 400 m x 240 m (800 x 480 px, 0.5 m per px)."""
import numpy as np

W, H, SCALE = 800, 480, 0.5          # canvas size (px) and metres per pixel
BUILDINGS = [                        # x, y, width, height, name
    (40, 40, 220, 140, "Warehouse A"), (320, 40, 200, 140, "Manufacturing"),
    (580, 40, 180, 140, "Assembly line"), (40, 300, 200, 140, "Logistics hub"),
    (320, 320, 160, 120, "Control room"), (560, 300, 200, 140, "Admin & guest"),
]
WIFI_APS = [(130, 240), (400, 240), (670, 240)]            # 3 Wi-Fi access points
SMALL_CELLS = [(110, 240), (300, 240), (500, 240), (700, 240)]  # 4 private-5G small cells


def building_at(x, y):
    """Index of the building containing (x, y), or -1 if outdoors."""
    for i, (bx, by, bw, bh, _) in enumerate(BUILDINGS):
        if bx <= x <= bx + bw and by <= y <= by + bh:
            return i
    return -1


def wall_crossings(x1, y1, x2, y2, samples=16):
    """Approximate number of building walls crossed by the straight line."""
    n, prev = 0, building_at(x1, y1)
    for i in range(1, samples + 1):
        q = building_at(x1 + (x2 - x1) * i / samples, y1 + (y2 - y1) * i / samples)
        if q != prev and q >= 0:
            n += 1
        prev = q
    return n


def random_devices(n=80, seed=7):
    """Random IoT devices: first 12 robots (URLLC), next 14 CCTV (eMBB), rest sensors (mMTC)."""
    rng = np.random.default_rng(seed)
    kinds = ["Robot (URLLC)"] * 12 + ["CCTV (eMBB)"] * 14 + ["Sensor (mMTC)"] * (n - 26)
    return [(rng.uniform(0, W), rng.uniform(0, H), k) for k in kinds]
