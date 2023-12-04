import streamlit as st
import pandas as pd
import numpy as np

# 음식점 데이터 생성 (랜덤 데이터 예시)
np.random.seed(42)
categories = ["Korean", "Italian", "Mexican", "Japanese", "Indian"]
restaurants = pd.DataFrame({
    'Name': [f'Restaurant_{i}' for i in range(1, 101)],
    'Category': np.random.choice(categories, size=100),
})

# 넷플릭스 스타일의 UI
st.set_page_config(page_title="음식점 추천 서비스", page_icon=":fork_and_knife:", layout="wide")

st.title("음식점 추천 서비스")

# 사용자 선택 화면
col1, col2 = st.columns(2)
selected_category = col1.selectbox("카테고리 선택", categories)
col2.image("https://media.giphy.com/media/3oEjI6SIIHBdRxXI40/giphy.gif", use_column_width=True)

# 랜덤하게 선택된 음식점 표시
selected_restaurants = restaurants[restaurants['Category'] == selected_category].sample(15, random_state=42)
selected_restaurants_names = selected_restaurants['Name'].tolist()

st.subheader("랜덤으로 선택된 15개의 음식점:")
st.write(selected_restaurants_names)

# 사용자가 선택한 음식점
st.subheader("가장 선호하는 음식점 3개를 선택하세요:")
user_selection = st.multiselect("선호하는 음식점 선택", selected_restaurants_names, default=[])
st.write("선택한 음식점:", user_selection)

# 선택한 음식점과 유사한 음식점 추천
if user_selection:
    similar_restaurants = restaurants[restaurants['Name'].isin(user_selection)]
    recommended_restaurants = restaurants[restaurants['Category'] == selected_category].sample(3, random_state=42)
    
    st.subheader("추천 음식점:")
    st.write(recommended_restaurants[['Name', 'Category']])

