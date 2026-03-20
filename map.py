import streamlit as st
import geopandas as gpd
import matplotlib.pyplot as plt
import os
import io
import cartopy.crs as ccrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import matplotlib.ticker as mticker

# 1. 페이지 설정
st.set_page_config(page_title="Stable Sphere Viewer", layout="wide")
st.title("🌍 Professional Sphere Map (Clean Grid)")

# 2. 데이터 로드 (경로 에러 방지 포함)
current_dir = os.path.dirname(os.path.abspath(__file__))
land_path = os.path.join(current_dir, "ne_110m_land.shp")

@st.cache_data
def load_data():
    if os.path.exists(land_path):
        return gpd.read_file(land_path)
    return None

world_land = load_data()

# 3. 사이드바 설정
with st.sidebar:
    st.header("🛠️ View Settings")
    view_lat = st.slider("View Latitude", -90.0, 90.0, 38.0, step=1.0)
    view_lon = st.slider("View Longitude", -180.0, 180.0, 127.0, step=1.0)
    
    st.divider()
    
    st.subheader("📏 Grid Intervals")
    lon_interval = st.select_slider("Lon Interval", options=[5, 10, 15, 30, 45], value=15)
    lat_interval = st.select_slider("Lat Interval", options=[5, 10, 15, 30, 45], value=15)

    st.divider()
    
    st.subheader("🎨 Appearance")
    show_coast = st.checkbox("Show Coastline (Edge)", value=True)
    c_alpha = st.slider("Opacity", 0.0, 1.0, 0.4) if show_coast else 1.0

if world_land is not None:
    my_globe = ccrs.Globe(ellipse='sphere')
    target_crs = ccrs.Orthographic(central_longitude=view_lon, central_latitude=view_lat, globe=my_globe)

    # 1. 도화지 생성
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(1, 1, 1, projection=target_crs)
    ax.set_global()
    ax.set_facecolor('#FFFFFF')

    # 2. 육지 및 격자 그리기
    world_land.plot(ax=ax, transform=ccrs.PlateCarree(), 
                    color='#E8E8E8', 
                    edgecolor='#000000' if show_coastline else (0,0,0,0), 
                    linewidth=coastline_width, alpha=coastline_alpha, zorder=2)

    if show_grid == 'Y':
        gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=False, 
                          linewidth=0.5, color='#AAAAAA', alpha=0.5,
                          linestyle='--', n_steps=500, zorder=1)
        gl.xlocator = mticker.MultipleLocator(lon_interval)
        gl.ylocator = mticker.MultipleLocator(lat_interval)

    # 🛠️ 해결책: st.pyplot()을 부르기 전에 '먼저' 이미지를 버퍼에 저장합니다.
    # 이렇게 해야 메모리에서 그림이 날아가기 전에 안전하게 캡처됩니다.
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=300, bbox_inches='tight', facecolor='white', transparent=False)
    img_data = buf.getvalue()

    # 3. 화면에 표시
    st.pyplot(fig, clear_figure=True)

    # 4. 다운로드 버튼 (이미 생성된 img_data 사용)
    st.download_button(
        label="📥 Download High-Res Map (300 DPI)",
        data=img_data,
        file_name="final_sphere_map.png",
        mime="image/png"
    )
