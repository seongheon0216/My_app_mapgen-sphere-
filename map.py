import streamlit as st
import geopandas as gpd
import matplotlib.pyplot as plt
import os
import cartopy.crs as ccrs
import io

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="Interactive Globe Generator", layout="wide")
st.title("🌐 Interactive Sphere Globe (110m)")
st.markdown("---")

# 2. 데이터 로드 (지구본 깨짐 방지를 위해 110m 사용)
current_folder = os.path.dirname(os.path.abspath(__file__))
# 파일 이름이 ne_110m_land.shp 인지 확인해주세요.
land_110m = os.path.join(current_folder, "ne_110m_land.shp")

@st.cache_data
def load_data(path):
    if os.path.exists(path):
        gdf = gpd.read_file(path)
        # 구형 투영 시 대륙 깨짐 방지를 위한 버퍼 처리 ( buffer(0) )
        gdf['geometry'] = gdf.geometry.buffer(0)
        return gdf
    return None

world_land = load_data(land_110m)

# 3. 사이드바 설정 (정면 좌표 입력)
with st.sidebar:
    st.header("🛠️ Globe Settings")
    st.subheader("📍 Center Position (Front View)")
    # 사용자가 입력한 좌표를 정면으로 바라봅니다.
    lon_center = st.number_input("Center Longitude", value=127.0, min_value=-180.0, max_value=180.0)
    lat_center = st.number_input("Center Latitude", value=37.5, min_value=-90.0, max_value=90.0)
    
    st.divider()
    
    st.subheader("📏 Grid & Design")
    # 지구본이라 격자 간격은 넓게 가져갑니다.
    grid_interval = st.select_slider("Grid Interval (deg)", options=[10, 15, 20, 30], value=30)
    
    # 정면 위치에 점 표시 여부
    show_point = st.checkbox("Show Center Point", value=True)

# 4. 지도 생성 메인 로직
if world_land is not None:
    # --- 투영법 설정: Orthographic (지구본) ---
    # 사용자가 입력한 좌표(central_longitude, central_latitude)를 지구의 정면으로 설정합니다.
    target_crs = ccrs.Orthographic(central_longitude=lon_center, central_latitude=lat_center)

    # 도화지 생성 (지구본이니까 정사각형 비율)
    fig = plt.figure(figsize=(10, 10), dpi=100)
    ax = fig.add_subplot(1, 1, 1, projection=target_crs)

    # 지구본 전체(Global)를 보여줍니다.
    ax.set_global()
    
    # 배경 및 바다색 (옵션: 바다색을 연한 파란색으로 하려면 '#E0F7FA')
    ax.set_facecolor('#FFFFFF')

    # --- 그리기 ---
    # 육지 그리기 (저해상도라 빠름)
    world_land.plot(ax=ax, transform=ccrs.PlateCarree(), 
                    color='#E0E0E0', edgecolor='#AAAAAA', linewidth=0.3)
    
    # 격자선 (구형 좌표 기준)
    ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=False, 
                 linestyle='--', linewidth=0.5, color='#AAAAAA', alpha=0.7)

    # (옵션) 지구 외곽선(테두리) 그리기
    # ax.add_feature(cartopy.feature.OCEAN, facecolor='none', edgecolor='black', linewidth=1)

    # 정면 좌표에 점 표시 (입력한 위치 확인용)
    if show_point:
        ax.plot(lon_center, lat_center, marker='o', color='#FF6F00', markersize=8, 
                transform=ccrs.PlateCarree(), zorder=10, label='Center')
        # ax.legend(loc='lower right')

    # 5. 결과 표시 및 고해상도 다운로드
    st.pyplot(fig, clear_figure=True)

    # 다운로드 시에만 300 DPI 렌더링 (일러스트 작업용)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches='tight', dpi=300, facecolor='#FFFFFF', pad_inches=0.1)
    
    st.download_button(
        label=f"📥 Download High-Res Globe (300 DPI PNG)",
        data=buf.getvalue(),
        file_name=f"globe_{lon_center:.1f}_{lat_center:.1f}_300dpi.png",
        mime="image/png"
    )
else:
    st.error("⚠️ 110m 데이터 파일(ne_110m_land.shp)을 찾을 수 없습니다.")
    st.info("💡 ne_110m_land.shp, ne_110m_land.shx, ne_110m_land.dbf 파일이 같은 폴더에 있어야 합니다.")
