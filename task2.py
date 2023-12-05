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

# 0번 사용자에 대해서 해당 사용자가 가보지 못한 장소 중 5개 추천 (즉, 맨 앞 숫자를 바꾸면 사용자 번호가 바뀜)
recommended_items = recommend_items(0, user_similarity, ratings_pivot)
print("Recommended items for user 0:", recommended_items)
