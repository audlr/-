import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import folium_static
from geopy.geocoders import Nominatim
import task1

st.set_page_config(page_title="음식점 추천 서비스", page_icon="🍔", layout="wide")

# 세션 상태 초기화
if "page_number" not in st.session_state:
    st.session_state.page_number = 1
if "user_name" not in st.session_state:
    st.session_state.user_name = ""

user_favorite = []
user_name = "user"

if st.session_state.page_number == 1:
    welcome = st.empty()
    welcome.title("안녕하세요!")
    user_name_input = st.empty()
    user_name = user_name_input.text_input("성함이 어떻게 되세요?", key="user_name")
    main_text_container = st.empty()
    main_text_container.caption("Visit [GitHub](https://github.com/The-Martin-Kim/2023-Machine-Learning-Term-Project)")

    if user_name != "":
        st.session_state.page_number += 1

        user_name_input.empty()
        welcome.empty()
        main_text_container.empty()

if st.session_state.page_number == 2:
    Hello_name = st.empty()
    Hello_name.title(f"반가워요, {user_name} 님!")
    Hello_choice = st.empty()
    Hello_choice.subheader(f"{user_name} 님과 맞는 식당을 찾기 위해, 마음에 드는 곳을 골라주세요.")

    select_restaurants = task1.df['name'].sample(10, random_state=42)  # 더미

    container1= st.empty()
    with container1.expander(f"Choice", expanded=True):
        selected_restaurant_name = st.selectbox("레스토랑을 선택하세요", select_restaurants)

        selected_restaurant = task1.df[task1.df['name'] == selected_restaurant_name]
        st.write(f"선택한 식당: {selected_restaurant['name'].values[0]}")
        st.write(f"리뷰: {selected_restaurant['reviews_list'].values[0]}")
        user_favorite = [selected_restaurant]

    next_button_1 = st.button("결과 확인", key="next_button_1")
    if next_button_1 and not selected_restaurant.empty:
        st.session_state.page_number += 1
        recommended_df = task1.recommended_1(selected_restaurant)

if st.session_state.page_number == 3:
    container1.expander(f"Choice")

    st.write("---")
    Answer_name = st.empty()
    Answer_name.subheader(f"{user_name} 님께서 선택하신 곳과 비슷한 식당이에요")

    if selected_restaurant is not None:
        container2= st.empty()
        with container2.expander(f"Recommend", expanded=True):
            for i in range(5):
                col1, col2 = st.columns(2, gap="small")
                with col1:
                    st.write(f"식당: {selected_restaurant['name'].values[i]}")
                    st.write(f"주소: {selected_restaurant['address'].values[i]}")
                    st.write(f"cuisines: {selected_restaurant['cuisines'].values[i]}")
                    review_text = selected_restaurant['reviews_list'].values[i]
                    st.write(f"리뷰: {review_text[:500]}")
                with col2:                
                    geolocator = Nominatim(user_agent="my_geocoder")
                    location = geolocator.geocode(selected_restaurant['address'].values[i])
                
                    if location:
                        latitude, longitude = location.latitude, location.longitude
                        selected_restaurant.loc[i, 'Latitude'] = latitude
                        selected_restaurant.loc[i, 'Longitude'] = longitude
                
                        m = folium.Map(location=[latitude, longitude], zoom_start=15)
                        folium.Marker([latitude, longitude], popup=f"{selected_restaurant['address'].iloc[i]}").add_to(m)
                        folium_static(m, width=500, height=400)
                    else:
                        st.warning(f"Location not found for {selected_restaurant['name'].values[i]}. Skipping map creation.")
    else:
        st.warning("User not found. Please provide a valid user ID.")

    next_button_2 = st.button("다시 선택", key="next_button_2")
    if next_button_2 and not selected_restaurant.empty:
        st.session_state.page_number -= 1
        Answer_name.empty()

