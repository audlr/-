import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import folium_static

# 더미 데이터
np.random.seed(42)
categories = ["Korean", "Italian", "Mexican", "Japanese", "Indian"]
restaurants = pd.DataFrame({
    'Name': [f'Restaurant_{i}' for i in range(1, 101)],
    'Category': np.random.choice(categories, size=100),
    'Latitude': np.random.uniform(37.5, 37.8, size=100),
    'Longitude': np.random.uniform(126.9, 127.2, size=100),
    'Address': [f'Address_{i}' for i in range(1, 101)],
    'Review': [f'Review_{i}' for i in range(1, 101)],
})

# 세션 상태 초기화
if "page_number" not in st.session_state:
    st.session_state.page_number = 1
    
st.set_page_config(page_title="음식점 추천 서비스", page_icon="🍔", layout="wide")
welcome = st.empty()
welcome.title("Welcome!")
category_choice = st.empty()
Resta_category = category_choice.selectbox("categories", categories)

selected_restaurants = restaurants[restaurants['Category'] == Resta_category].sample(15, random_state=42)
user_favorite = []
restaurants_choices = []

for i in range(3):
    container = st.empty()
    with container.expander(f"Round {i + 1}", expanded=True):

        start_index = i * 5
        end_index = (i + 1) * 5
        round_restaurants = selected_restaurants.iloc[start_index:end_index]

        user_favorite = st.radio(f"가장 선호하는 음식점을 선택하세요 ({i + 1}/3)", round_restaurants['Name'])

        st.session_state.selected_restaurant = {
            'Name': round_restaurants[round_restaurants['Name'] == user_favorite]['Name'].values[0],
            'Address': round_restaurants[round_restaurants['Name'] == user_favorite]['Address'].values[0],
            'Review': round_restaurants[round_restaurants['Name'] == user_favorite]['Review'].values[0],
        }

        st.write(f"선택한 음식점: {st.session_state.selected_restaurant['Name']}")
        st.write(f"주소: {st.session_state.selected_restaurant['Address']}")
        st.write(f"한 줄 평: {st.session_state.selected_restaurant['Review']}")


        restaurants_choices.append(container)

button_next = st.empty()
if button_next.button("Next"):
    st.session_state.page_number = 2

main_text_container = st.empty()
main_text_container.caption("Visit [GitHub](https://github.com/The-Martin-Kim/2023-Machine-Learning-Term-Project)")

if st.session_state.page_number == 2:
    welcome.empty()
    category_choice.empty()
    for container in restaurants_choices:
        container.empty()
    button_next.empty()
    main_text_container.empty()

    recommend = st.empty()
    recommend.title("Recommend restaurant!")
    
    recommended_restaurants = restaurants[restaurants['Category'] == Resta_category].sample(3, random_state=42)

    # 추천 음식점 표시
    for i in range(3):
        col1, col2 = st.columns(2, gap="small")
        with col1:
            st.write(f"선택한 음식점: {recommended_restaurants.iloc[i]['Name']}")
            st.write(f"주소: {recommended_restaurants.iloc[i]['Address']}")
            st.write(f"한 줄 평: {recommended_restaurants.iloc[i]['Review']}")
        with col2:
            m = folium.Map(location=recommended_restaurants.iloc[i][['Latitude', 'Longitude']], zoom_start=15)
            folium.Marker(recommended_restaurants.iloc[i][['Latitude', 'Longitude']], popup=f"추천 음식점\n{recommended_restaurants['Address'].iloc[0]}").add_to(m)
            folium_static(m, width=350, height=150)

    recommend_table_container = st.empty()
    with recommend_table_container.expander(f"Recommend table"):
        recommended_restaurants = restaurants[restaurants['Category'] == Resta_category].sample(3, random_state=42)
        st.write(recommended_restaurants)
