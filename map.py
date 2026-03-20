import streamlit as st
import geopandas as gpd
import matplotlib.pyplot as plt
import os
import io
import cartopy.crs as ccrs
import numpy as np

# 1. 페이지 설정
st.set_page_config(page_title="Smooth Sphere Map", layout="wide")
st.title("🌎 Professional Sphere Map (Smooth Grid)")

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
    
    grid_step = st.select_slider("Grid Interval", options=[5, 10, 15, 30], value=15)

    st.divider()
    
    show_coast = st.checkbox("Show Coastline (Edge)", value=True)
    c_alpha = st.slider("Coastline Opacity", 0.0, 1.0, 0.4) if show_coast else 1.0

# 4. 지도 생성 및 에러 우회 로직
if world_land is not None:
    # Sphere 설정
    my_globe = ccrs.Globe(ellipse='sphere')
    target_crs = ccrs.Orthographic(central_longitude=view_lon, central_latitude=view_lat, globe=my_globe)

    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(1, 1, 1, projection=target_crs)
    ax.set_global()
    ax.set_facecolor('#FFFFFF')

    # 육지 그리기 (E8E8E8 회색 육지)
    world_land.plot(ax=ax, transform=ccrs.PlateCarree(), 
                    color='#E8E8E8', 
                    edgecolor='#000000' if show_coast else (0,0,0,0), 
                    linewidth=0.5, alpha=c_alpha, zorder=2)

    # 🛠️ 해결책: 촘촘하게 계산하여 부드러운 '곡선' 수동 격자선 그리기
    # 격자선의 정밀도를 결정하는 샘플링 개수 (높을수록 부드럽습니다)
    n_sample = 361 # 1도 단위로 계산

    try:
        # 위도선 그리기
        for lat in np.arange(-90, 91, grid_step):
            # 위도 고정, 경도를 361개로 조밀하게 채움
            lon_line = np.linspace(-180, 180, n_sample)
            lat_line = np.full(n_sample, lat)
            ax.plot(lon_line, lat_line, color='gray', linewidth=0.5, 
                    alpha=0.3, transform=ccrs.PlateCarree(), zorder=1)

        # 경도선 그리기
        for lon in np.arange(-180, 181, grid_step):
            # 경도 고정, 위도를 361개로 조밀하게 채움
            lat_line = np.linspace(-90, 90, n_sample)
            lon_line = np.full(n_sample, lon)
            ax.plot(lon_line, lat_line, color='gray', linewidth=0.5, 
                    alpha=0.3, transform=ccrs.PlateCarree(), zorder=1)
    except Exception as e:
        # 혹시 수동 격자선 그리기에서 충돌이 나면 지도는 계속 생성
        st.warning(f"격자선 렌더링 중 경고가 발생했으나 지도는 계속 생성합니다: {e}")

    # 지구 테두리 원형 강조
    ax.spines['geo'].set_linewidth(1.5)

    # 🛠️ PNG 빈 화면 해결: st.pyplot 호출 전에 '먼저' 버퍼에 저장
    buf = io.BytesIO()
    fig.savefig(buf,
