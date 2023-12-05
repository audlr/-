import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import folium_static
from geopy.geocoders import Nominatim

import sys
import csv

csv.field_size_limit(sys.maxsize)

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns

import warnings
warnings.filterwarnings('ignore')

df = pd.read_csv('zomato.csv',
                 engine='python', on_bad_lines='skip', encoding='utf-8')

# 전처리 과정
df = df.drop(['url', 'phone', 'dish_liked', 'menu_item', 'listed_in(city)'], axis=1)

df = df.rename(columns={'approx_cost(for two people)':'cost',
                        'listed_in(type)':'type'})

df.name = df.name.apply(lambda x:x.title())

df.online_order.replace(('Yes','No'),(True, False),inplace=True)
df.book_table.replace(('Yes','No'),(True, False),inplace=True)

df['cost'] = df['cost'].astype(str)
df['cost'] = df['cost'].apply(lambda x: x.replace(',','.'))
df['cost'] = df['cost'].astype(float)

df = df.loc[df.rate !='NEW']
df = df.loc[df.rate !='-'].reset_index(drop=True)

remove_slash = lambda x: x.replace('/5', '') if isinstance(x, str) else x
df.rate = df.rate.apply(remove_slash).str.strip().astype('float')

# 추천 시스템 1
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

tfidf_vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf_vectorizer.fit_transform(df['reviews_list'])

cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

def get_recommendations(df, title):
    idx = df.index[df['name'] == title].tolist()[0]

    sim_scores = list(enumerate(cosine_sim[idx]))

    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    sim_scores = [score for score in sim_scores if df['name'].iloc[score[0]] != title]

    recommended_restaurants = []
    seen_names = set()
    for score in sim_scores:
        if len(recommended_restaurants) == 5:
            break
        restaurant_name = df['name'].iloc[score[0]]
        if restaurant_name not in seen_names:
            recommended_restaurants.append(restaurant_name)
            seen_names.add(restaurant_name)

    return recommended_restaurants

df_copied = df.copy()

def recommended_1(resta_name):
    recommended_restaurants = get_recommendations(df_copied, resta_name)
    recommended_df = df[df['name'].isin(recommended_restaurants)]

    return recommended_df


# 파라미터로 음식점 이름이 들어갑니다 ! (음식점 이름 변경 시 여기에 들어가는 파라미터를 변경해야 함)
#recommended_restaurants = get_recommendations(df_copied, 'Spice Elephant')
# 결과 출력
#print(recommended_restaurants)
    
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

    select_restaurants = df['name'].sample(10, random_state=42)  # 더미

    container1= st.empty()
    with container1.expander(f"Choice", expanded=True):
        selected_restaurant_name = st.selectbox("레스토랑을 선택하세요", select_restaurants)

        selected_restaurant = df[df['name'] == selected_restaurant_name]
        st.write(f"선택한 식당: {selected_restaurant['name'].values[0]}")
        st.write(f"리뷰: {selected_restaurant['reviews_list'].values[0]}")
        user_favorite = [selected_restaurant]

    next_button_1 = st.button("결과 확인", key="next_button_1")
    if next_button_1 and not selected_restaurant.empty:
        st.session_state.page_number += 1
        recommended_df = recommended_1(selected_restaurant)

if st.session_state.page_number == 3:
    container1.expander(f"Choice")

    st.write("---")
    Answer_name = st.empty()
    Answer_name.subheader(f"{user_name} 님께서 선택하신 곳과 비슷한 식당이에요")

    container2= st.empty()
    with container2.expander(f"Recommend", expanded=True):
        for i in range(5):
            col1, col2 = st.columns(2, gap="small")
            with col1:
                st.write(f"식당: {recommended_df['name'].values[i]}")
                st.write(f"주소: {recommended_df['address'].values[i]}")
                st.write(f"cuisines: {recommended_df['cuisines'].values[i]}")
                st.write(f"리뷰: {recommended_df['reviews_list'].values[i]}")
            with col2:
                geolocator = Nominatim(user_agent="my_geocoder")
                location = geolocator.geocode(recommended_df['address'].values[0])
                
                if location:
                    latitude, longitude = location.latitude, location.longitude
                else:
                    latitude, longitude = None, None

                recommended_df.loc[i, 'Latitude'] = latitude
                recommended_df.loc[i, 'Longitude'] = longitude

                m = folium.Map(location=recommended_df.iloc[i][['Latitude', 'Longitude']], zoom_start=15)
                folium.Marker(recommended_df.iloc[i][['Latitude', 'Longitude']], popup=f"{recommended_df['Address'].iloc[0]}").add_to(m)
                folium_static(m, width=350, height=150)

    next_button_2 = st.button("다시 선택", key="next_button_2")
    if next_button_2 and not selected_restaurant.empty:
        st.session_state.page_number -= 1
        Answer_name.empty()

