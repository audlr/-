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

# 추천 시스템 2
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix

array_sizes = df['reviews_list'].str.count(r'Rated \d\.\d')

# 50명 이상이 평가한 식당만 사용 (총 50명이 있다고 가정)
df_filtered = df[array_sizes >= 50]

ratings_list = df_filtered['reviews_list'].str.findall(r'Rated (\d\.\d)').explode().dropna()
ratings_list = ratings_list.astype(float)
user_ids = np.repeat(np.arange(len(df_filtered)), df_filtered['reviews_list'].str.count(r'Rated \d\.\d')).astype(int)

ratings_list = ratings_list.groupby(user_ids).head(50)
user_ids = np.repeat(np.arange(len(df_filtered)), 50)

ratings_df = pd.DataFrame({
    'user_id': user_ids,
    'restaurant_id': np.tile(np.arange(len(df_filtered)), ratings_list.groupby(user_ids).size().max()),
    'rating': ratings_list.values
}).dropna()

ratings_pivot = ratings_df.pivot_table(index='user_id', columns='restaurant_id', values='rating', fill_value=0)
ratings_matrix = csr_matrix(ratings_pivot.values)
user_similarity = cosine_similarity(ratings_matrix)

restaurant_names = df['name'].tolist()

# top_n => 추천해줄 음식점 개수
def recommend_items(user_id, user_similarity, ratings_pivot, top_n=5):
    similar_users = user_similarity[user_id].argsort()[::-1]
    similar_users = similar_users[1:]

    recommendations = np.dot(user_similarity[user_id, :].reshape(1, -1), ratings_pivot.values).reshape(-1)

    already_rated = np.nonzero(ratings_pivot.iloc[user_id].to_numpy())[0]
    recommendations[already_rated] = 0

    recommendation_ids = recommendations.argsort()[::-1][:top_n]

    recommended_item_names = [restaurant_names[i] for i in recommendation_ids]

    return recommended_item_names

def recommended_2(user_id):
    recommended_items = recommend_items(user_id, user_similarity, ratings_pivot)
    recommended_df = df[df['name'].isin(recommended_items)]

    return recommended_df

    
st.set_page_config(page_title="경험 기반 음식점 추천 서비스", page_icon="🍔", layout="wide")

# 세션 상태 초기화
if "page_number" not in st.session_state:
    st.session_state.page_number = 1
if "user_name" not in st.session_state:
    st.session_state.user_name = ""

user_favorite = []
user_ID = 0

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
    Hello_choice.subheader(f"{user_ID} 님께서 가장 최근에 다녀오신 곳이에요")

    select_restaurants = ['Spice Elephant', 'Flavours - Octave Hotel & Spa', 'Paprica', "Palki'S", 'The Onyx - The Hhi Select Bengaluru', 'Nouvelle Garden']

    container1= st.empty()
    with container1.expander(f"Went", expanded=True):
        st.write(f"{select_restaurants[0]}")
        
        next_button_3 = st.button("다음", key="next_button_3")
        if next_button_3:
            st.session_state.page_number += 1

if st.session_state.page_number == 3:
    container1.expander(f"Choice")

    st.write("---")
    Answer_name = st.empty()
    Answer_name.subheader(f"이번엔 여기 어떠세요?")
    selected_restaurant = recommended_2(user_ID)

    if selected_restaurant is not None:
        container2= st.empty()
        with container2.expander(f"Recommend", expanded=True):
            for i in range(5):
                col1, col2 = st.columns(2, gap="small")
                with col1:
                    st.write(f"식당: {selected_restaurant['name'].values[i]}")
                    st.write(f"주소: {selected_restaurant['address'].values[i]}")
                    st.write(f"cuisines: {selected_restaurant['cuisines'].values[i]}")
                    st.write(f"리뷰: {selected_restaurant['reviews_list'].values[i]}")
                with col2:
                    geolocator = Nominatim(user_agent="my_geocoder")
                    location = geolocator.geocode(selected_restaurant['address'].values[issubclass])
                    
                    if location:
                        latitude, longitude = location.latitude, location.longitude
                    else:
                        latitude, longitude = None, None
    
                    selected_restaurant.loc[i, 'Latitude'] = latitude
                    selected_restaurant.loc[i, 'Longitude'] = longitude
                    
                    m = folium.Map(location=selected_restaurant.iloc[i][['Latitude', 'Longitude']], zoom_start=15)
                    folium.Marker(selected_restaurant.iloc[i][['Latitude', 'Longitude']], popup=f"{selected_restaurant['address'].iloc[i]}").add_to(m)
                    folium_static(m, width=350, height=150)
    else:
        st.warning("User not found. Please provide a valid user ID.")
