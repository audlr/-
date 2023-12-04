import streamlit as st
import pandas as pd
import numpy as np
import folium

# 음식점 데이터 생성 (랜덤 데이터 예시)
np.random.seed(42)
categories = ["Korean", "Italian", "Mexican", "Japanese", "Indian"]
restaurants = pd.DataFrame({
    'Name': [f'Restaurant_{i}' for i in range(1, 101)],
    'Category': np.random.choice(categories, size=100),
    'Latitude': np.random.uniform(37.5, 37.8, size=100),  # 가짜 위도 데이터
    'Longitude': np.random.uniform(126.9, 127.2, size=100),  # 가짜 경도 데이터
})

# 넷플릭스 스타일의 UI
st.set_page_config(page_title="음식점 추천 서비스", page_icon="🍔", layout="wide")

st.title("음식점 추천 서비스")

# 사용자 선택 화면
selected_category = st.selectbox("카테고리 선택", categories)

# 랜덤하게 선택된 음식점 표시 및 선호 음식점 선택
for i in range(3):
    st.subheader(f"Round {i + 1}: 선택지 {i + 1}")

    # 원하는 카테고리에 속하는 랜덤 음식점 선택
    selected_restaurants = restaurants[restaurants['Category'] == selected_category].sample(5, random_state=42)
    selected_restaurants_names = selected_restaurants['Name'].tolist()

    # 사용자가 가장 선호하는 음식점 선택
    user_favorite = st.radio(f"가장 선호하는 음식점을 선택하세요 ({i + 1}/3)", selected_restaurants_names)

# 선택한 음식점과 비슷한 카테고리의 음식점 지도에 표시
st.subheader("선택한 음식점과 비슷한 카테고리의 음식점 지도")
selected_restaurant_location = restaurants[restaurants['Name'] == user_favorite][['Latitude', 'Longitude']].values[0]
m = folium.Map(location=selected_restaurant_location, zoom_start=15)
folium.Marker(selected_restaurant_location, popup=user_favorite).add_to(m)
folium.Marker([37.6, 127.0], popup="추천 음식점 1").add_to(m)
folium.Marker([37.7, 127.1], popup="추천 음식점 2").add_to(m)
folium.Marker([37.8, 127.2], popup="추천 음식점 3").add_to(m)

st.map(m)
