"""Signal-strength model: log-distance path loss + wall penetration loss."""
import numpy as np
from .campus import *

THRESHOLD_DBM = -82   # usable-signal threshold used for BOTH networks

NETWORKS = {
    # tx power+antenna gain (dBm), path loss at 1 m (dB), path-loss exponent, wall loss (dB/wall)
    "wifi": dict(pt=23, pl1=47.0, n=3.3, wall=8, nodes=WIFI_APS, label="Wi-Fi (5 GHz)"),
    "5g":   dict(pt=35, pl1=43.3, n=3.2, wall=5, nodes=SMALL_CELLS, label="Private 5G (3.5 GHz n78)"),
}


def rss(net, node, x, y):
    c = NETWORKS[net]
    d = max(1.0, np.hypot(node[0] - x, node[1] - y) * SCALE)
    return c["pt"] - (c["pl1"] + 10 * c["n"] * np.log10(d)) - c["wall"] * wall_crossings(node[0], node[1], x, y)


def best_rss(net, x, y):
    return max(rss(net, n, x, y) for n in NETWORKS[net]["nodes"])


def heatmap(net, step=10):
    """Return xs, ys, z (dBm grid) and the % of campus area above threshold."""
    xs, ys = np.arange(step / 2, W, step), np.arange(step / 2, H, step)
    z = np.array([[best_rss(net, x, y) for x in xs] for y in ys])
    return xs, ys, z, float((z >= THRESHOLD_DBM).mean() * 100)
