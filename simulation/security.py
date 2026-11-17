"""Simulated device authentication (NOT real 5G-AKA): shared password vs challenge-response."""
import secrets

def _h(s):
    x = 5381
    for c in s:
        x = ((x << 5) + x + ord(c)) & 0xFFFFFFFF
    return format(x, "x")

REGISTRY = {"AGV Robot-01": "K-7F3A", "CCTV Cam-12": "K-91C2", "IoT Sensor-A7": "K-44D0", "Staff tablet": "K-B60E"}
DEVICES = [(n, k, False) for n, k in REGISTRY.items()] + [("Rogue laptop", "K-0000", True)]


def authenticate(password_leaked=False):
    rows = []
    for name, key, rogue in DEVICES:
        rand = secrets.token_hex(3)                                   # network challenge
        expected = _h(REGISTRY[name] + rand) if name in REGISTRY else None
        g5 = expected is not None and _h(key + rand) == expected      # device response vs registry
        wifi = (not rogue) or password_leaked                         # shared password
        rows.append(dict(device=name, rogue=rogue, wifi="Allowed" if wifi else "Denied",
                         five_g="Allowed" if g5 else "Denied", challenge=rand, response=_h(key + rand)))
    return rows
