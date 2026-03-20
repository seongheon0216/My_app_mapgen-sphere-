import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

st.set_page_config(page_title="3D Globe Viewer", layout="wide")
st.title("🌍 Interactive 3D Sphere Map")

# 사이드바에서 관측 지점(Center) 설정
with st.sidebar:
    st.header("👁️ View Projection")
    # 내가 바라보는 방향 설정
    view_lat = st.slider("View Latitude", -90.0, 90.0, 38.0)
    view_lon = st.slider("View Longitude", -180.0, 180.0, 127.0)
    
    st.divider()
    
    st.subheader("📏 Grid Intervals")
    grid_step = st.select_slider("Grid Step", options=[5, 10, 15, 30], value=10)

# Plotly를 이용한 구형 투영
fig = go.Figure()

# 1. 지구 표면 (Geo Outline) 및 격자 설정
fig.update_geos(
    projection_type="orthographic",  # 🛠️ 핵심: 구형 지구본 모드
    showland=True,
    landcolor="LightGreen",
    showocean=True,
    oceancolor="LightBlue",
    showcountries=True,
    lonaxis_showgrid=True,
    lataxis_showgrid=True,
    lonaxis_gridcolor="gray",
    lataxis_gridcolor="gray",
    lonaxis_dtick=grid_step,  # 사용자가 설정한 경도 간격
    lataxis_dtick=grid_step,  # 사용자가 설정한 위도 간격
    projection_rotation=dict(lon=view_lon, lat=view_lat, roll=0), # 바라보는 방향 회전
    bgcolor="black" # 우주 느낌
)

fig.update_layout(
    height=800,
    margin={"r":0,"t":0,"l":0,"b":0}
)

# 결과 출력
st.plotly_chart(fig, use_container_width=True)

st.info(f"💡 현재 북위 {view_lat}°, 동경 {view_lon}° 지점을 정면으로 바라보고 있습니다.")
