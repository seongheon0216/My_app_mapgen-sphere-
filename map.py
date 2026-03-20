import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="Grey Globe Viewer", layout="wide")
st.title("🌍 3D Grey Globe (5° Step Grid)")

# 사이드바 설정
with st.sidebar:
    st.header("👁️ View Projection")
    # 바라보는 중심점 설정
    view_lat = st.slider("View Latitude", -90.0, 90.0, 38.0)
    view_lon = st.slider("View Longitude", -180.0, 180.0, 127.0)
    
    st.divider()
    
    st.subheader("📏 Grid Intervals")
    # 🛠️ 요청사항: 5도 단위로 조절 가능한 슬라이더 (5부터 30까지)
    grid_step = st.slider("Grid Step (degrees)", min_value=5, max_value=30, value=10, step=5)

# 구형 지구본 생성
fig = go.Figure(go.Scattergeo())

fig.update_geos(
    projection_type="orthographic", # 구형 모드
    
    # --- [색상 설정] ---
    showland=True,
    landcolor="rgb(120, 120, 120)",  # 🛠️ 요청사항: 회색 육지
    showocean=True,
    oceancolor="rgb(255, 255, 255)", # 바다는 흰색 유지
    showcountries=True,
    countrycolor="rgb(80, 80, 80)",  # 국가 경계선 (진회색)
    countrywidth=0.5,
    
    # --- [격자 설정] ---
    lataxis=dict(
        showgrid=True, 
        dtick=grid_step,            # 🛠️ 5도 단위 적용
        gridcolor="rgb(200, 200, 200)", 
        gridwidth=0.5
    ),
    lonaxis=dict(
        showgrid=True, 
        dtick=grid_step,            # 🛠️ 5도 단위 적용
        gridcolor="rgb(200, 200, 200)", 
        gridwidth=0.5
    ),
    
    # 바라보는 방향 회전
    projection_rotation=dict(lon=view_lon, lat=view_lat, roll=0)
)

fig.update_layout(
    height=850,
    margin={"r":0,"t":50,"l":0,"b":0},
    paper_bgcolor="white", # 배경을 흰색으로 해서 깔끔하게 처리
    plot_bgcolor="white"
)

# 차트 표시
st.plotly_chart(fig, use_container_width=True)
