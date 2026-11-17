"""NEXWAVE 5G - Intelligent Private 5G Network Simulation Platform.  Run: streamlit run app.py"""
import numpy as np, pandas as pd, plotly.graph_objects as go, streamlit as st
from simulation import campus, coverage, mobility, qos, security

st.set_page_config(page_title="NEXWAVE 5G", page_icon="📡", layout="wide")
st.title("NEXWAVE 5G")
st.caption("Intelligent Private 5G network simulation platform. All values are SIMULATED from documented assumptions, not real measurements.")
page = st.sidebar.radio("Section", ["Campus overview", "Coverage analysis", "Mobility simulation", "QoS analysis", "Security", "Final comparison"])
st.sidebar.markdown("**QoS settings (used in QoS + comparison)**")
rb = st.sidebar.slider("Robots", 1, 30, 10); cc = st.sidebar.slider("CCTV cameras", 0, 40, 12)
gu = st.sidebar.slider("Guest users", 0, 200, 40); io = st.sidebar.slider("IoT sensors", 0, 2000, 300)
pq = st.sidebar.checkbox("Priority queues", True)


def campus_fig(heat=None):
    f = go.Figure()
    if heat:
        xs, ys, z, _ = heat
        f.add_trace(go.Heatmap(x=xs, y=ys, z=z, colorscale="RdYlGn", zmin=-100, zmax=-55, colorbar=dict(title="dBm"), opacity=.85))
    for x, y, w, h, n in campus.BUILDINGS:
        f.add_shape(type="rect", x0=x, y0=y, x1=x + w, y1=y + h, line=dict(color="gray"), fillcolor="rgba(30,40,60,.35)")
        f.add_annotation(x=x + 8, y=y + 14, text=n, showarrow=False, xanchor="left", font=dict(size=11))
    f.add_trace(go.Scatter(x=[p[0] for p in campus.WIFI_APS], y=[p[1] for p in campus.WIFI_APS], mode="markers+text", text=[f"AP{i+1}" for i in range(3)],
                           textposition="bottom center", marker=dict(symbol="diamond", size=14, color="orange", line=dict(width=1, color="white")), name="Wi-Fi AP"))
    f.add_trace(go.Scatter(x=[p[0] for p in campus.SMALL_CELLS], y=[p[1] for p in campus.SMALL_CELLS], mode="markers+text", text=[f"SC{i+1}" for i in range(4)],
                           textposition="top center", marker=dict(size=13, color="teal", line=dict(width=1, color="white")), name="5G small cell"))
    f.update_xaxes(range=[0, campus.W], visible=False); f.update_yaxes(range=[campus.H, 0], scaleanchor="x", visible=False)
    f.update_layout(height=520, margin=dict(l=0, r=0, t=10, b=0))
    return f


if page == "Campus overview":
    f = campus_fig()
    d = pd.DataFrame(campus.random_devices(), columns=["x", "y", "kind"])
    col = {"Robot (URLLC)": "red", "CCTV (eMBB)": "royalblue", "Sensor (mMTC)": "gold"}
    for k, g in d.groupby("kind"):
        f.add_trace(go.Scatter(x=g.x, y=g.y, mode="markers", name=k, marker=dict(size=7, color=col[k])))
    st.plotly_chart(f, width='stretch')
    st.write("Virtual 400 m x 240 m campus: 6 buildings, 3 Wi-Fi APs, 4 private-5G small cells, 80 devices.")

elif page == "Coverage analysis":
    c1, c2 = st.columns(2)
    for col_, net in ((c1, "wifi"), (c2, "5g")):
        h = coverage.heatmap(net)
        col_.subheader(coverage.NETWORKS[net]["label"]); col_.plotly_chart(campus_fig(h), width='stretch')
        col_.metric("Area above -82 dBm", f"{h[3]:.0f}%")

elif page == "Mobility simulation":
    speed = st.slider("Robot speed (px/s, 0.5 m per px)", 10, 100, 40)
    res = {n: mobility.run(n, speed) for n in ("wifi", "5g")}
    pos = st.slider("Robot position along route (%)", 0, 100, 0)
    x, y = mobility.pos_at(pos / 100 * mobility.PATH_LEN)
    f = campus_fig(); f.add_trace(go.Scatter(x=[x], y=[y], mode="markers", name="AGV-01", marker=dict(size=14, color="white", line=dict(width=3, color="red"))))
    st.plotly_chart(f, width='stretch')
    c1, c2 = st.columns(2)
    for col_, n in ((c1, "wifi"), (c2, "5g")):
        r = res[n]; col_.subheader(coverage.NETWORKS[n]["label"])
        col_.metric("Handovers per lap", r["handovers"]); col_.metric("Avg interruption", f"{r['avg_delay_ms']:.0f} ms"); col_.metric("Time in outage", f"{r['outage_pct']:.0f}%")
        col_.dataframe(pd.DataFrame(r["events"]), width='stretch')
    tr = go.Figure()
    for n, c in (("wifi", "orange"), ("5g", "teal")):
        t = np.array(res[n]["trace"]); tr.add_trace(go.Scatter(x=t[:, 0], y=t[:, 4], name=n, line=dict(color=c)))
    tr.add_hline(y=coverage.THRESHOLD_DBM, line_dash="dash", line_color="red"); tr.update_layout(xaxis_title="time (s)", yaxis_title="serving signal (dBm)")
    st.plotly_chart(tr, width='stretch')

elif page == "QoS analysis":
    for n in ("wifi", "5g"):
        r = qos.evaluate(n, rb, cc, gu, io, pq); st.subheader(coverage.NETWORKS[n]["label"])
        st.caption(f"Offered {r['offered']:.0f} Mbps / capacity {r['capacity']:.0f} Mbps ({r['utilisation']*100:.0f}% utilisation)")
        st.dataframe(pd.DataFrame(r["rows"]), width='stretch')
    xs = list(range(0, 201, 5)); f = go.Figure()
    for n, c in (("wifi", "orange"), ("5g", "teal")):
        f.add_trace(go.Scatter(x=xs, y=[qos.evaluate(n, rb, cc, g, io, pq)["rows"][0]["latency_ms"] for g in xs], name=n, line=dict(color=c)))
    f.add_hline(y=10, line_dash="dash", line_color="red"); f.update_yaxes(range=[0, 100], title="robot latency (ms)"); f.update_xaxes(title="guest users")
    st.plotly_chart(f, width='stretch')

elif page == "Security":
    leak = st.checkbox("Wi-Fi password leaked to rogue device")
    st.dataframe(pd.DataFrame(security.authenticate(leak)).rename(columns={"wifi": "Wi-Fi (shared password)", "five_g": "5G (challenge-response)"}), width='stretch')
    st.caption("Simulated challenge-response; not real SIM/5G-AKA authentication.")

else:
    a, b = qos.evaluate("wifi", rb, cc, gu, io, pq), qos.evaluate("5g", rb, cc, gu, io, pq)
    m = {n: mobility.run(n) for n in ("wifi", "5g")}
    cov = {n: coverage.heatmap(n)[3] for n in ("wifi", "5g")}
    st.dataframe(pd.DataFrame([
        ["eMBB", "Peak capacity (Mbps)", round(a["capacity"]), round(b["capacity"])],
        ["eMBB", "Campus coverage (%)", round(cov["wifi"]), round(cov["5g"])],
        ["URLLC", "Robot latency (ms)", a["rows"][0]["latency_ms"], b["rows"][0]["latency_ms"]],
        ["URLLC", "Robot packet loss (%)", a["rows"][0]["loss_pct"], b["rows"][0]["loss_pct"]],
        ["URLLC", "Avg handover interruption (ms)", round(m["wifi"]["avg_delay_ms"]), round(m["5g"]["avg_delay_ms"])],
        ["mMTC", "IoT sensors before 80% load", qos.max_iot("wifi", rb, cc, gu), qos.max_iot("5g", rb, cc, gu)],
    ], columns=["5G pillar", "Metric", "Wi-Fi", "Private 5G"]), width='stretch', hide_index=True)
