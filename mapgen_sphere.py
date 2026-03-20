import streamlit as st
import geopandas as gpd
import matplotlib.pyplot as plt
import os
import io
import cartopy.crs as ccrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import matplotlib.ticker as mticker
import numpy as np

# 1. 페이지 설정
st.set_page_config(page_title="Pro Sphere Map Viewer", layout="wide")
st.title("Sphere Map Generator")

# 2. 데이터 로드 (경로 문제 해결 버전)
@st.cache_data
def load_data():
    # 파일명 리스트 (image_c42471.png 확인 결과 110m 버전 존재)
    target_file = "ne_110m_land.shp"
    
    # 🛠️ 해결책: 현재 스크립트 위치뿐만 아니라 작업 디렉토리 전체에서 탐색
    current_dir = os.path.dirname(os.path.abspath(__file__))
    working_dir = os.getcwd()
    
    paths_to_check = [
        os.path.join(current_dir, target_file),
        os.path.join(working_dir, target_file),
        target_file  # 상대 경로 직접 지정
    ]
    
    for path in paths_to_check:
        if os.path.exists(path):
            try:
                return gpd.read_file(path)
            except Exception as e:
                st.error(f"파일 로드 중 오류 발생: {e}")
    return None

world_land = load_data()

# 3. 사이드바 설정 (회전 및 테두리 제어)
with st.sidebar:
    st.header("🛠️ View Settings")
    view_lat = st.slider("View Latitude", -90.0, 90.0, 38.0, step=1.0)
    view_lon = st.slider("View Longitude", -180.0, 180.0, 127.0, step=1.0)
    
    st.divider()
    
    st.subheader("📏 Grid Intervals (5° Step)")
    show_grid = st.radio("Show Grid Lines", ("Y", "N"), index=0)
    lon_interval = st.select_slider("Longitude Interval", options=[5, 10, 15, 30], value=10)
    lat_interval = st.select_slider("Latitude Interval", options=[5, 10, 15, 30], value=10)

    st.divider()
    
    st.subheader("🎨 Appearance Settings")
    show_coastline = st.checkbox("Show Coastline (Edge)", value=True)
    coastline_alpha = st.slider("Coastline Opacity", 0.0, 1.0, 0.4, step=0.1) if show_coastline else 1.0
    coastline_width = st.slider("Coastline Width", 0.1, 1.0, 0.5, step=0.1) if show_coastline else 0.5

# ... (상단 1, 2, 3번 섹션은 기존과 동일) ...

# 4. 지도 생성 로직
if world_land is not None:
    my_globe = ccrs.Globe(ellipse='sphere')
    target_crs = ccrs.Orthographic(central_longitude=view_lon, central_latitude=view_lat, globe=my_globe)

    fig = plt.figure(figsize=(12, 8), dpi=100)
    ax = fig.add_subplot(1, 1, 1, projection=target_crs)
    ax.set_facecolor('#FFFFFF')

    # 육지 그리기
    world_land.plot(ax=ax, transform=ccrs.PlateCarree(), 
                    color='#E8E8E8', 
                    edgecolor='#000000' if show_coastline else (0,0,0,0), 
                    linewidth=coastline_width,
                    alpha=coastline_alpha)

    # 격자선 설정
    if show_grid == 'Y':
        # 🛠️ 에러 방지를 위해 gridlines 인자를 최소화했습니다.
        gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=False, 
                          linestyle='-', linewidth=0.6, color='#AAAAAA', alpha=0.5)
        gl.xlocator = mticker.MultipleLocator(lon_interval)
        gl.ylocator = mticker.MultipleLocator(lat_interval)

    # --- 🛠️ PNG 다운로드 핵심 수정 구간 시작 ---
    
    # 1. 먼저 메모리 버퍼에 300 DPI로 저장 (st.pyplot 보다 앞에 와야 함)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches='tight', dpi=300, facecolor='#FFFFFF')
    img_data = buf.getvalue()
    
    # 2. 그 다음에 화면에 표시
    st.pyplot(fig)
    
    # 3. 다운로드 버튼에 위에서 만든 img_data 연결
    st.download_button(
        label="📥 Download Map (300 DPI)", 
        data=img_data, 
        file_name="sphere_map_300dpi.png",
        mime="image/png"
    )
    
    # --- 🛠️ 핵심 수정 구간 끝 ---

else:
    st.error("⚠️ 데이터 파일을 찾을 수 없습니다.")
    st.write("현재 폴더 파일 목록:", os.listdir(os.getcwd()))
