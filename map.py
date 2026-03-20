import streamlit as st
import geopandas as gpd
import matplotlib.pyplot as plt
import os
import io
import cartopy.crs as ccrs
import numpy as np

# 1. 페이지 설정
st.set_page_config(page_title="Stable Sphere Viewer", layout="wide")
st.title("🌎 Professional Sphere Map (Anti-Error Version)")

# 2. 데이터 로드
@st.cache_data
def load_data():
    target_file = "ne_110m_land.shp"
    current_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(current_dir, target_file)
    if os.path.exists(path):
        return gpd.read_file(path)
    return None

world_land = load_data()

# 3. 사이드바 설정
with st.sidebar:
    st.header("🛠️ Settings")
    view_lat = st.slider("View Latitude", -90.0, 90.0, 38.0)
    view_lon = st.slider("View Longitude", -180.0, 180.0, 127.0)
    st.divider()
    grid_step = st.select_slider("Grid Interval", options=[5, 10, 15, 30], value=15)
    show_coast = st.checkbox("Show Coastline", value=True)
    c_alpha = st.slider("Opacity", 0.0, 1.0, 0.4) if show_coast else 1.0

# 4. 지도 생성 로직
if world_land is not None:
    fig = plt.figure(figsize=(10, 10))
    # 구형 투영 설정
    target_crs = ccrs.Orthographic(central_longitude=view_lon, central_latitude=view_lat)
    ax = fig.add_subplot(1, 1, 1, projection=target_crs)
    ax.set_global()
    ax.set_facecolor('white')

    # 🛠️ 해결책 1: 수동 격자선 그리기 (에러 발생 지점 우회)
    # 위도선 그리기
    for lat in np.arange(-90, 91, grid_step):
        ax.plot([-180, 180], [lat, lat], color='gray', linewidth=0.5, 
                alpha=0.3, transform=ccrs.PlateCarree(), zorder=1)
    # 경도선 그리기
    for lon in np.arange(-180, 181, grid_step):
        ax.plot([lon, lon], [-90, 90], color='gray', linewidth=0.5, 
                alpha=0.3, transform=ccrs.PlateCarree(), zorder=1)

    # 5. 육지 그리기
    world_land.plot(ax=ax, transform=ccrs.PlateCarree(), 
                    color='#E8E8E8', 
                    edgecolor='black' if show_coast else (0,0,0,0), 
                    linewidth=0.5, alpha=c_alpha, zorder=2)

    # 지구 테두리 원형 강조
    ax.spines['geo'].set_linewidth(1.5)

    # 🛠️ 해결책 2: 저장 로직 최적화 (빈 화면 방지)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=300, bbox_inches='tight', facecolor='white')
    img_data = buf.getvalue()

    # 화면 표시
    st.pyplot(fig)

    # 다운로드 버튼
    st.download_button(label="📥 Download 300 DPI Map", data=img_data, 
                       file_name="sphere_map.png", mime="image/png")
else:
    st.error("⚠️ 데이터 파일을 찾을 수 없습니다. (ne_110m_land.shp)")
