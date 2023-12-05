import sys
import csv

csv.field_size_limit(sys.maxsize)

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns

import warnings
warnings.filterwarnings('ignore')

df = pd.read_csv('/Users/martinkim/Desktop/zomato.csv',
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
# 파라미터로 음식점 이름이 들어갑니다 ! (음식점 이름 변경 시 여기에 들어가는 파라미터를 변경해야 함)
recommended_restaurants = get_recommendations(df_copied, 'Spice Elephant')

# 결과 출력
print(recommended_restaurants)
