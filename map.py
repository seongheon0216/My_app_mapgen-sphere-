import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="Global Sphere Viewer", layout="wide")
st.title("🌍 3D Global Sphere Viewer")

# 사이드바 설정
with st.sidebar:
    st.header("👁️ View Settings")
    # 위도와 경도 슬라이더
    view_lat = st.slider("View Latitude", -90.0, 90.0, 20.0)
    view_lon = st.slider("View Longitude", -180.0, 180.0, 130.0)
    
    st.divider()
    
    grid_step = st.select_slider("Grid Interval", options=[5, 10, 15, 30], value=10)

# 지구본 생성 (안정적인 설정 적용)
fig = go.Figure(go.Scattergeo())

fig.update_geos(
    projection_type="orthographic", # 구형 투영
    showland=True,
    landcolor="rgb(240, 240, 240)", # 연회색 육지
    showocean=True,
    oceancolor="rgb(10, 20, 40)",   # 진한 남색 바다
    showcountries=True,
    countrycolor="rgb(200, 200, 200)",
    
    # 격자선 설정
    lataxis=dict(showgrid=True, dtick=grid_step, gridcolor="rgb(100, 100, 100)"),
    lonaxis=dict(showgrid=True, dtick=grid_step, gridcolor="rgb(100, 100, 100)"),
    
    # 🛠️ 핵심: 바라보는 방향 회전 (이 값이 정확해야 지도가 보입니다)
    projection_rotation=dict(lon=view_lon, lat=view_lat, roll=0)
)

fig.update_layout(
    height=800,
    margin={"r":0,"t":50,"l":0,"b":0},
    paper_bgcolor="black", # 배경색 우주 느낌
    plot_bgcolor="black"
)

# 차트 표시
st.plotly_chart(fig, use_container_width=True)
