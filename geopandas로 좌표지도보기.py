# -*- coding: utf-8 -*-
"""
Created on Sun Sep 12 21:32:02 2021

@author: 82104
"""

## 지도 그려보기.

import googlemaps
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
import re
import geopandas as gpd


pd.set_option('display.max_columns',30)

os.chdir("C:/Users/-----/Desktop/빅캠 노인/데이터")

data=pd.read_csv("./수정후시설현황.csv")

data.head()


import folium

center = [37.541, 126.986]
m = folium.Map(location = center, zoom_start = 11)
folium.GeoJson(data3).add_to(m)

df=data
for i in df.index:
  df_lat = df.loc[i,'시설위도']
  df_long = df.loc[i,'시설경도']

  title = df.loc[i, '시설명']

  folium.CircleMarker([df_lat, df_long], radius = 3).add_to(m)

m.save('./test.html')

plt.figure(figsize=(20,15))
sns.scatterplot(data=data,x="시설경도",y="시설위도")

data2=gpd.read_file("./행정구역/LARD_ADM_SECT_SGG_서울/LARD_ADM_SECT_SGG_11.shp",encoding='EUC-KR')

data2.crs
data_4326.crs
data2.info()
data_4326=data2.to_crs(epsg=4326)
data3=data_4326.to_json()

import folium

center = [37.541, 126.986]
m = folium.Map(location = center, zoom_start = 11)
folium.GeoJson(data3).add_to(m)

df=data
for i in df.index:
  df_lat = df.loc[i,'시설위도']
  df_long = df.loc[i,'시설경도']

  title = df.loc[i, '시설명']

  folium.CircleMarker([df_lat, df_long], radius = 3).add_to(m)

m.save('./test.html')
