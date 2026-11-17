"""Simplified queueing model of QoS: latency, packet loss, throughput per traffic class."""
DEMAND = dict(robot=3.0, cctv=8.0, guest=4.0, iot=0.05)   # Mbps per device
CLASSES = ["Robot control (URLLC)", "CCTV video (eMBB)", "Guest internet"]


def evaluate(net, robots, cctv, guests, iot, priority=True):
    n = robots + cctv + guests + iot
    cap = 250 / (1 + .004 * n) if net == "wifi" else 450 / (1 + .0003 * n)   # contention reduces Wi-Fi capacity more
    dr, dc, dg, di = (robots * DEMAND["robot"], cctv * DEMAND["cctv"], guests * DEMAND["guest"], iot * DEMAND["iot"])
    total = dr + dc + dg + di
    rho = total / cap
    leak = .35 if net == "wifi" else .04      # how much lower-priority load still hurts high-priority traffic
    base, k, loss0 = (6, 1.4, .2) if net == "wifi" else (4, .6, .01)
    eff = [dr / cap + leak * (rho - dr / cap) if priority else rho,
           (dr + dc) / cap + leak * (rho - (dr + dc) / cap) if priority else rho, rho]
    rows = []
    for name, e, dem in zip(CLASSES, eff, (dr, dc, dg)):
        lat = base + k * 8 * e / (1 - min(e, .97))
        loss = min(100, loss0 + (3 * ((e - .8) / .2) ** 2 if e > .8 else 0) + (100 * (1 - 1 / e) if e > 1 else 0))
        rows.append(dict(traffic=name, latency_ms=round(lat, 1), loss_pct=round(loss, 2),
                         delivered_mbps=round(dem * min(1, 1 / max(e, 1)), 1)))
    return dict(capacity=cap, offered=total, utilisation=rho, rows=rows)


def max_iot(net, robots, cctv, guests, limit=20000):
    """mMTC: most IoT sensors the network carries below 80 % utilisation."""
    return max([i for i in range(0, limit + 1, 50) if evaluate(net, robots, cctv, guests, i)["utilisation"] < .8] or [0])
