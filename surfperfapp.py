import streamlit as st, pandas as pd, requests, gpxpy

st.title("Surf Performance-Score Dashboard")

uploaded = st.file_uploader("Upload GPX file", type="gpx")
if uploaded:
    gpx = gpxpy.parse(uploaded)
    pts = [(p.time, p.latitude, p.longitude)
           for t in gpx.tracks for s in t.segments for p in s.points]
    df = pd.DataFrame(pts, columns=["time","lat","lon"])
    df["dt"]   = df.time.diff().dt.total_seconds().fillna(0)/3600
    df["dist"] = df.dt * 10  # placeholder constant speed
    avg_speed  = df.dist.sum()/df.dt.sum() if df.dt.sum()>0 else 0

    lat, lon = df.lat.iloc[0], df.lon.iloc[0]
    key = st.secrets["OPENWEATHER_KEY"]
    r = requests.get(
        "https://api.openweathermap.org/data/2.5/weather",
        params={"lat":lat,"lon":lon,"appid":key,"units":"metric"}
    )
    wind = r.json().get("wind",{}).get("speed", 0)

    score = round(min(avg_speed/10*0.6 + wind/20*0.4, 1)*100)
    st.write(f"Avg speed: {avg_speed:.1f} km/h • Wind: {wind:.1f} m/s")
    st.metric("Performance Score", f"{score}/100")

