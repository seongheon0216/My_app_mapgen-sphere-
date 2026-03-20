import streamlit as st
import geopandas as gpd
import matplotlib.pyplot as plt
import os
import io
import cartopy.crs as ccrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import matplotlib.ticker as mticker
import numpy as np
from shapely.geometry import box

# 1. 페이지 설정
st.set_page_config(page_title="Pro Sphere Map Viewer", layout="wide")
st.title("🌎 Professional Sphere Map Viewer")

# 2. 데이터 로드 (클리핑 및 최적화 완료)
current_folder = os.path.dirname(os.path.abspath(__file__))
land_path = os.path.join(current_folder, "ne_110m_land.shp")

@st.cache_data
def load_data():
    if os.path.exists(land_path):
        return gpd.read_file(land_path)
    return None

world_land = load_data()

# 3. 사이드바 설정 (회전 및 테두리 제어)
with st.sidebar:
    st.header("🛠️ View Settings")
    # 바라보는 중심점 설정
    view_lat = st.slider("View Latitude", -90.0, 90.0, 38.0, step=1.0)
    view_lon = st.slider("View Longitude", -180.0, 180.0, 127.0, step=1.0)
    
    st.divider()
    
    st.subheader("📏 Grid Intervals (5° Step)")
    show_grid = st.radio("Show Grid Lines", ("Y", "N"), index=0)
    # 위경도 개별 설정 (5, 10, 15, 30 고정)
    lon_interval = st.select_slider("Longitude Interval", options=[5, 10, 15, 30], value=10)
    lat_interval = st.select_slider("Latitude Interval", options=[5, 10, 15, 30], value=10)

    st.divider()
    
    st.subheader("🎨 Coastline & Country Settings")
    # 🛠️ 사용자 요청: 국가 경계선 지우기 (st.checkbox로 On/Off 구현)
    show_countries = st.checkbox("Show Country Borders", value=False)
    
    # 🛠️ 사용자 요청: 해안선 따라 생긴 검은 선 옵션 (체크박스 & 투명도 슬라이더)
    show_coastline = st.checkbox("Show Coastline (검은 선)", value=True)
    coastline_alpha = st.slider("Coastline Opacity (투명도)", 0.0, 1.0, 0.4, step=0.1) if show_coastline else 1.0
    coastline_width = st.slider("Coastline Width (두께)", 0.1, 1.0, 0.5, step=0.1) if show_coastline else 0.5

# 4. 지도 생성 로직
if world_land is not None:
    # --- [Sphere 설정] 지구를 완벽한 구체로 정의하여 안정성 확보 ---
    my_globe = ccrs.Globe(ellipse='sphere')

    # --- [핵심] 투영법 설정 (지구본 정면 시점) ---
    target_crs = ccrs.Orthographic(central_longitude=view_lon, central_latitude=view_lat, globe=my_globe)

    # 도화지 생성 및 설정 (가로로 긴 비율로 시각적 안정감 부여)
    fig_width = 12
    fig_height = 8
    fig = plt.figure(figsize=(fig_width, fig_height), dpi=100)
    ax = fig.add_subplot(1, 1, 1, projection=target_crs)
    ax.set_facecolor('#FFFFFF') # 배경은 흰색 (깔끔하게 처리)

    # 육지 데이터 그리기 (회색 육지 + 사용자 설정 해안선)
    world_land.plot(ax=ax, transform=ccrs.PlateCarree(), 
                    color='#E8E8E8', # 회색 육지
                    # 🛠️ 요청사항: 해안선 색상, 투명도, 두께 조절 (끄면 투명해짐)
                    edgecolor='#000000' if show_coastline else (0,0,0,0), 
                    linewidth=coastline_width,
                    alpha=coastline_alpha)

    # 🛠️ 요청사항: 국가 경계선 표시 (사용자가 선택했을 때만 그리기)
    if show_countries:
        # 국가 경계선 데이터가 필요합니다 (기본적으로 ne_10m_admin_0_countries.shp 등)
        country_path = os.path.join(current_folder, "ne_10m_admin_0_countries.shp")
        if os.path.exists(country_path):
            countries = gpd.read_file(country_path)
            countries.plot(ax=ax, transform=ccrs.PlateCarree(), 
                           color=(0,0,0,0), # 채우기는 투명하게
                           edgecolor='#888888', linewidth=0.3, alpha=0.5)

    # 격자선 (전문 기상 지도 스타일)
    if show_grid == 'Y':
        gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, 
                          linestyle='-', linewidth=0.6, color='#AAAAAA', alpha=0.5)
        gl.top_labels = gl.right_labels = False
        gl.xformatter, gl.yformatter = LONGITUDE_FORMATTER, LATITUDE_FORMATTER
        # 선택한 간격 적용
        gl.xlocator = mticker.MultipleLocator(lon_interval)
        gl.ylocator = mticker.MultipleLocator(lat_interval)

    # 5. 결과 표시 및 다운로드
    st.pyplot(fig, clear_figure=True)

    # 🛠️ 요청사항: 300 DPI 이미지 다운로드
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches='tight', dpi=300, facecolor='#FFFFFF')
    st.download_button(label="📥 Download Map (300 DPI)", data=buf.getvalue(), file_name="professional_map.png")

else:
    st.error("⚠️ 데이터 파일(ne_10m_land.shp)이 같은 폴더에 없습니다.")
