import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import folium_static
from geopy.geocoders import Nominatim
import task2
    
st.set_page_config(page_title="경험 기반 음식점 추천 서비스", page_icon="🍔", layout="wide")

# 세션 상태 초기화
if "page_number" not in st.session_state:
    st.session_state.page_number = 1
if "user_name" not in st.session_state:
    st.session_state.user_name = ""

user_favorite = []
user_ID = "0"

if st.session_state.page_number == 1:
    user_favorite = []

    welcome = st.empty()
    welcome.title("안녕하세요!")
    user_name_input = st.empty()
    #button = st.button("회원 가입", key="button")
    user_name = user_name_input.text_input("회원이시면, ID를 입력해 주세요", key="user_name")
    main_text_container = st.empty()
    main_text_container.caption("Visit [GitHub](https://github.com/The-Martin-Kim/2023-Machine-Learning-Term-Project)")

    if user_name != "":
        st.session_state.page_number += 1
        user_ID = user_name

        user_name_input.empty()
        welcome.empty()
        main_text_container.empty()


if st.session_state.page_number == 2:
    Hello_name = st.empty()
    Hello_name.title(f"반가워요, {user_ID} 님!")
    Hello_choice = st.empty()
    Hello_choice.subheader(f"{user_ID} 님께서 다녀오신 곳이에요")

    #select_restaurants = restaurants.sample(10, random_state=42)  # 더미

    container1= st.empty()
    with container1.expander(f"Went", expanded=True):
        selected_restaurant_name = st.selectbox("", select_restaurants)

        selected_restaurant = restaurants[restaurants['Name'] == selected_restaurant_name]
        st.write(f"{selected_restaurant['Name'].values[0]}")
        st.write(f"내 리뷰: {selected_restaurant['Review'].values[0]}")
        
        next_button_3 = st.button("다음", key="next_button_3")
        if next_button_3:
            st.session_state.page_number += 1

if st.session_state.page_number == 3:
    container1.expander(f"Choice")

    st.write("---")
    Answer_name = st.empty()
    Answer_name.subheader(f"이번엔 여기 어떠세요?")
    selected_restaurant = task2.recommended_2(user_name)

    container2= st.empty()
    with container2.expander(f"Recommend", expanded=True):
        for i in range(3):
            col1, col2 = st.columns(2, gap="small")
            with col1:
                st.write(f"식당: {selected_restaurant['Name'].values[0]}")
                st.write(f"주소: {selected_restaurant['address'].values[0]}")
                st.write(f"cuisines: {selected_restaurant['cuisines'].values[0]}")
                st.write(f"리뷰: {selected_restaurant['reviews_list'].values[0]}")
            with col2:
                geolocator = Nominatim(user_agent="my_geocoder")
                location = geolocator.geocode(selected_restaurant['address'].values[0])
                
                if location:
                    latitude, longitude = location.latitude, location.longitude
                else:
                    latitude, longitude = None, None

                selected_restaurant.loc[i, 'Latitude'] = latitude
                selected_restaurant.loc[i, 'Longitude'] = longitude
                
                m = folium.Map(location=selected_restaurant.iloc[i][['Latitude', 'Longitude']], zoom_start=15)
                folium.Marker(selected_restaurant.iloc[i][['Latitude', 'Longitude']], popup=f"추천 음식점\n{selected_restaurant['Address'].iloc[0]}").add_to(m)
                folium_static(m, width=350, height=150)
