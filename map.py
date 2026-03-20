import geopandas as gpd
import matplotlib.pyplot as plt
import os
from shapely.geometry import box
from matplotlib.ticker import MultipleLocator

# 현재 폴더 경로 설정
current_folder = os.path.dirname(os.path.abspath(__file__))
land_path = os.path.join(current_folder, "ne_10m_land.shp")

def generate_exam_final_map():
    if not os.path.exists(land_path):
        print(f"에러: '{land_path}' 파일을 찾을 수 없습니다.")
        return

    # 1. 사용자 입력
    print("--- 수능/교과서 스타일 지도 생성기 ---")
    try:
        lon_min = float(input("최소 경도 (예: 110): "))
        lon_max = float(input("최대 경도 (예: 150): "))
        lat_min = float(input("최소 위도 (예: 20): "))
        lat_max = float(input("최대 위도 (예: 55): "))
        
        show_grid = input("실선 격자선을 표시할까요? (Y/N): ").upper()
    except ValueError:
        print("에러: 숫자만 입력해주세요.")
        return

    # 2. 데이터 처리
    world_land = gpd.read_file(land_path)
    scope = box(lon_min, lat_min, lon_max, lat_max)
    target_land = world_land.clip(scope)

    # 3. 그래프 설정
    fig, ax = plt.subplots(figsize=(10, 8), dpi=300)
    ax.set_facecolor('#FFFFFF') # 바다: 흰색

    # 4. 육지 그리기 (연한 회색, 선 없음)
    if not target_land.empty:
        target_land.plot(ax=ax, color='#E0E0E0', edgecolor='none') # 육지: 회색

    # 5. 범위 및 격자 설정
    ax.set_xlim(lon_min, lon_max)
    ax.set_ylim(lat_min, lat_max)

    if show_grid == 'Y':
        # 격자선을 '실선(-)'으로 설정
        ax.grid(True, linestyle='-', linewidth=0.5, color='#AAAAAA', zorder=0)
        
        # 숫자는 숨기고 눈금만 남기거나 포맷만 변경
        ax.tick_params(axis='both', which='both', length=0) # 눈금 표시 제거
        
        # 동경/서경, 북위/남위 구분 라벨 설정
        def lon_formatter(x, pos):
            if x > 0: return f'{int(x)}°E'
            elif x < 0: return f'{int(abs(x))}°W'
            else: return '0°'

        def lat_formatter(x, pos):
            if x > 0: return f'{int(x)}°N'
            elif x < 0: return f'{int(abs(x))}°S'
            else: return 'EQ'

        ax.xaxis.set_major_formatter(plt.FuncFormatter(lon_formatter))
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lat_formatter))
        
        # 격자 간격 (자동으로 10도 단위 설정, 원하시면 수정 가능)
        ax.xaxis.set_major_locator(MultipleLocator(10))
        ax.yaxis.set_major_locator(MultipleLocator(10))
        
        # 숫자 크기를 아주 작게 하거나, 필요 없다면 아래 줄을 활성화해서 숫자를 아예 지우세요.
        # plt.setp(ax.get_xticklabels(), visible=False) 
        # plt.setp(ax.get_yticklabels(), visible=False)
    else:
        ax.set_axis_off()

    # 6. 저장
    output_name = 'final_exam_style_map.png'
    save_path = os.path.join(current_folder, output_name)
    
    plt.tight_layout()
    plt.savefig(save_path, bbox_inches='tight', pad_inches=0.2, facecolor='#FFFFFF')
    
    print("-" * 30)
    print(f"저장 완료! 방위가 표시된 지도가 생성되었습니다: {save_path}")
    plt.show()

if __name__ == "__main__":
    generate_exam_final_map()