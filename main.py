# 전체 main.py 코드 (최신 반영본)

import streamlit as st

# ✅ set_page_config는 가장 위에서 실행해야 함
st.set_page_config(page_title="소비자물가 및 소비 패턴 변화 분석", layout="wide")

# -------------------------------
# 라이브러리 불러오기
# -------------------------------
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.font_manager as fm
import os
import altair as alt

# -------------------------------
# 한글 폰트 설정 함수
# -------------------------------
def set_korean_font():
    font_path = "NanumGothic.ttf"
    if os.path.exists(font_path):
        fm.fontManager.addfont(font_path)
        plt.rcParams['font.family'] = 'NanumGothic'
        plt.rcParams['axes.unicode_minus'] = False
        return True
    return False

# -------------------------------
# 앱 제목 및 폰트 경고
# -------------------------------
st.title("📊 소비자물가 상승률과 소비 패턴 변화 분석")

if not set_korean_font():
    st.warning("⚠️ NanumGothic.ttf 폰트 파일이 없으면 그래프에 한글이 깨질 수 있습니다.")

# -------------------------------
# 데이터 불러오기 및 전처리
# -------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv(
        "지출목적별_소비자물가지수_품목포함__2020100__20250611104117_분석(전년_대비_증감률).csv",
        encoding='cp949',
        skiprows=[1]  # 헤더가 두 줄인 경우
    )
    df.columns = df.columns.str.strip()
    
    id_vars = ['시도별', '지출목적별']
    value_vars = [col for col in df.columns if col not in id_vars]

    # 연도/지표 나누기
    years = []
    indicators = []
    for i, col in enumerate(value_vars):
        if i % 2 == 0:
            indicators.append("원데이터")
        else:
            indicators.append("전년_대비_증감률")
        years.append(col)

    # 멀티 인덱스로 재구성
    df.columns = id_vars + pd.MultiIndex.from_tuples(zip(years, indicators))

    # long 형태로 변환
    df = df.melt(id_vars=id_vars, var_name=["연도", "지표"], value_name="값")

    # 피벗으로 원데이터와 증감률 분리
    df = df.pivot_table(index=['시도별', '지출목적별', '연도'], columns='지표', values='값').reset_index()

    df["연도"] = df["연도"].astype(str)
    df["표시용연도"] = df["연도"].str.replace(".1", "").str.replace(".0", "")
    df["전년_대비_증감률"] = pd.to_numeric(df["전년_대비_증감률"], errors="coerce")
    df["원데이터"] = pd.to_numeric(df["원데이터"], errors="coerce")

    return df

df_all = load_data()

# -------------------------------
# 필터: 연도/지출목적
# -------------------------------
st.sidebar.header("🔎 필터 설정")
min_year = int(df_all["표시용연도"].min())
max_year = int(df_all["표시용연도"].max())

year_range = st.sidebar.slider("연도 범위 선택", min_value=min_year, max_value=max_year, value=(min_year, max_year))
category_options = sorted(df_all["지출목적별"].unique())
category_options = [cat for cat in category_options if cat != "지출목적별"]  # 제거
selected_category = st.sidebar.selectbox("지출 항목 선택", category_options)

# 필터 적용
df = df_all[
    (df_all["지출목적별"] == selected_category) &
    (df_all["표시용연도"].astype(int) >= year_range[0]) &
    (df_all["표시용연도"].astype(int) <= year_range[1])
]

# -------------------------------
# 가장 많이 오른/내린 시점
# -------------------------------
max_row = df.loc[df["전년_대비_증감률"].idxmax()]
min_row = df.loc[df["전년_대비_증감률"].idxmin()]

col1, col2 = st.columns(2)
with col1:
    st.metric(
        label=f"📈 가장 많이 오른 시점 ({selected_category})",
        value=f"{max_row['표시용연도']}년",
        delta=f"{max_row['전년_대비_증감률']:.2f}%",
        help=f"지수: {max_row['원데이터']}"
    )
with col2:
    st.metric(
        label=f"📉 가장 많이 내린 시점 ({selected_category})",
        value=f"{min_row['표시용연도']}년",
        delta=f"{min_row['전년_대비_증감률']:.2f}%",
        help=f"지수: {min_row['원데이터']}"
    )

# -------------------------------
# 시각화: 꺾은선 그래프
# -------------------------------
st.subheader("📈 소비자물가지수 & 전년 대비 증감률")

line_cpi = alt.Chart(df).mark_line(color="green", strokeWidth=3).encode(
    x=alt.X("연도:O", title="연도", labelAngle=0),
    y=alt.Y("원데이터:Q", title="지수"),
    tooltip=["표시용연도", alt.Tooltip("원데이터:Q", title="지수")]
)

point_cpi = alt.Chart(df).mark_point(color="green", size=40, filled=True).encode(
    x=alt.X("연도:O", labelAngle=0),
    y="원데이터:Q",
    tooltip=["표시용연도", alt.Tooltip("원데이터:Q", title="지수")]
)

line_rate = alt.Chart(df).mark_line(color="blue", strokeDash=[0], strokeWidth=2).encode(
    x=alt.X("연도:O", labelAngle=0),
    y=alt.Y("전년_대비_증감률:Q", title="전년 대비 증감률 (%)"),
    tooltip=["표시용연도", alt.Tooltip("전년_대비_증감률:Q", title="전년 대비")]
)

point_rate = alt.Chart(df).mark_point(color="blue", size=40, filled=True).encode(
    x=alt.X("연도:O", labelAngle=0),
    y="전년_대비_증감률:Q",
    tooltip=["표시용연도", alt.Tooltip("전년_대비_증감률:Q", title="전년 대비")]
)

chart = alt.layer(line_cpi + point_cpi, line_rate + point_rate).resolve_scale(y='independent')
st.altair_chart(chart, use_container_width=True)

