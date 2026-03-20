import streamlit as st
import geopandas as gpd
import matplotlib.pyplot as plt
import os
import io
import cartopy.crs as ccrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import matplotlib.ticker as mticker

# 1. 페이지 설정
st.set_page_config(page_title="Sphere Map Pro", layout="wide")
st.title("🌎 Professional Sphere Map Viewer")

# 2. 데이터 로드 (경로 에러 방지)
@st.cache_data
def load_data():
    target_file = "ne_110m_land.shp"
    current_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(current_dir, target_file)
    if os.path.exists(path):
        return gpd.read_file(path)
    # 파일이 없으면 직접 작업 디렉토리에서 재시도
    if os.path.exists(target_file):
        return gpd.read_file(target_file)
    return None

world_land = load_data()

# 3. 사이드바 설정
with st.sidebar:
    st.header("🛠️ Settings")
    view_lat = st.slider("View Latitude", -90.0, 90.0, 38.0, step=1.0)
    view_lon = st.slider("View Longitude", -180.0, 180.0, 127.0, step=1.0)
    
    st.divider()
    
    grid_step = st.select_slider("Grid Step", options=[5, 10, 15, 30], value=10)

    st.divider()
    
    show_coast = st.checkbox("Show Coastline (Edge)", value=True)
    c_alpha = st.slider("Coastline Opacity", 0.0, 1.0, 0.4) if show_coast else 1.0

# 4. 지도 생성 및 에러 방지 로직
if world_land is not None:
    # Sphere 설정
    my_globe = ccrs.Globe(ellipse='sphere')
    target_crs = ccrs.Orthographic(central_longitude=view_lon, central_latitude=view_lat, globe=my_globe)

    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(1, 1, 1, projection=target_crs)
    ax.set_global()
    ax.set_facecolor('#FFFFFF')

    # 육지 그리기
    world_land.plot(ax=ax, transform=ccrs.PlateCarree(), 
                    color='#E8E8E8', 
                    edgecolor='#000000' if show_coast else (0,0,0,0), 
                    linewidth=0.5, alpha=c_alpha, zorder=2)

    # 🛠️ 격자선 에러 해결 포인트: 인자를 최대한 단순하게 전달
    try:
        gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=False, 
                          color='#AAAAAA', alpha=0.5,
                          linestyle='--', linewidth=0.5,
                          n_steps=500, zorder=1)
        gl.xlocator = mticker.MultipleLocator(grid_step)
        gl.ylocator = mticker.MultipleLocator(grid_step)
    except Exception as e:
        st.warning(f"격자선 렌더링 중 경고가 발생했으나 지도는 계속 생성합니다: {e}")

    # 🛠️ PNG 빈 화면 해결: st.pyplot 호출 전에 '먼저' 버퍼에 저장
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=300, bbox_inches='tight', facecolor='white')
    img_data = buf.getvalue()

    # 화면 표시
    st.pyplot(fig)

    # 다운로드 버튼
    st.download_button(
        label="📥 Download Map (300 DPI)",
        data=img_data,
        file_name="sphere_map_300dpi.png",
        mime="image/png"
    )
else:
    st.error("⚠️ 데이터 파일을 찾을 수 없습니다. (ne_110m_land.shp 확인)")
