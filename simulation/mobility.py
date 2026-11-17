"""Robot (AGV) mobility and hysteresis-based handover simulation."""
import numpy as np
from .coverage import NETWORKS, rss, THRESHOLD_DBM

PATH = [(20, 210), (300, 210), (300, 270), (620, 270), (620, 210), (780, 210)]
SEGS = [np.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(PATH, PATH[1:])]
PATH_LEN = sum(SEGS)
# handover hysteresis (dB) and interruption time range (ms) per network
HO = {"wifi": dict(hys=8, delay=(90, 300)),   # sticky-client Wi-Fi roaming
      "5g":   dict(hys=3, delay=(10, 25))}    # 5G measurement-based handover


def pos_at(s):
    """Robot position after travelling s px (robot drives the path back and forth)."""
    s %= 2 * PATH_LEN
    if s > PATH_LEN:
        s = 2 * PATH_LEN - s
    for (a, b), L in zip(zip(PATH, PATH[1:]), SEGS):
        if s <= L:
            f = s / L
            return a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f
        s -= L
    return PATH[-1]


def run(net, speed_px_s=40.0, laps=1, dt=0.05, seed=1):
    """Simulate `laps` back-and-forth laps. Returns dict with trace, events and statistics."""
    rng = np.random.default_rng(seed)
    nodes, hys = NETWORKS[net]["nodes"], HO[net]["hys"]
    srv, t, s, events, trace, out = -1, 0.0, 0.0, [], [], 0.0
    total_time = 2 * PATH_LEN * laps / speed_px_s
    while t < total_time:
        x, y = pos_at(s)
        r = [rss(net, n, x, y) for n in nodes]
        b = int(np.argmax(r))
        if srv < 0:
            srv = b
        elif b != srv and r[b] > r[srv] + hys:
            events.append(dict(time_s=round(t, 2), **{"from": srv + 1, "to": b + 1},
                               interruption_ms=round(float(rng.uniform(*HO[net]["delay"])), 1)))
            srv = b
        if r[srv] < THRESHOLD_DBM:
            out += dt
        trace.append((t, x, y, srv + 1, r[srv]))
        t += dt; s += speed_px_s * dt
    return dict(trace=trace, events=events, handovers=len(events),
                avg_delay_ms=float(np.mean([e["interruption_ms"] for e in events])) if events else 0.0,
                outage_pct=out / total_time * 100)
