# -*- coding: utf-8 -*-
"""
Created on Tue Sep  7 22:22:11 2021

@author: 82104
"""

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

data=pd.read_csv("./사회복지시설현황(좌표추가).csv",encoding=('EUC-KR'))

data

data.info()

check_list=[]
for i,j,k in zip(data['시군구'],data['시설주소'],range(len(data))):
    check_error=re.search(str(i),str(j))
    if not check_error:
        check_list.append(k)
    
check_list

data_error=data.iloc[check_list,:]

data_error

gmaps_key='Your Key'
gmaps=googlemaps.Client(key=gmaps_key)


data['시설명_시군구']=data['시군구']+" "+data['시설명']

data.iloc[1663:,9]=data.iloc[1663:,1]

시설주소=[]
시설위도=[]
시설경도=[]


for name in data["시설명_시군구"]:
    temp=gmaps.geocode(name,language='ko')
    if not temp:
        시설주소.append('?')
        시설위도.append(0)
        시설경도.append(0)
        continue
    시설주소.append(temp[0].get('formatted_address'))
    temp_loc=temp[0].get('geometry')
    시설위도.append(temp_loc['location']['lat'])
    시설경도.append(temp_loc['location']['lng'])
    

data['시설주소']=시설주소
data['시설위도']=시설위도
data['시설경도']=시설경도

# 케어링 복지용구센터 강남구 , 장생시니어타운 서초구


check_list=[]
for i,j,k in zip(data['시군구'],data['시설주소'],range(len(data))):
    check_error=re.search(str(i),str(j))
    if not check_error:
        check_list.append(k)

len(check_list)
# 106개 


data.iloc[check_list,:]

okay_list=[]
for i,j,k in zip(data['시군구'],data['시설주소'],range(len(data))):
    check_error=re.search(str(i),str(j))
    if check_error:
        okay_list.append(k)

data2=data.iloc[okay_list,:]

data2.info()

data3=data2.reset_index().drop(['index','Unnamed: 0'],axis=1)

data3.info()

import folium

center = [37.541, 126.986]
m = folium.Map(location = center, zoom_start = 12)

df=data3
for i in df.index:
  df_lat = df.loc[i,'시설위도']
  df_long = df.loc[i,'시설경도']

  title = df.loc[i, '시설명']

  folium.CircleMarker([df_lat, df_long], radius = 5).add_to(m)

m.save('./test.html')

plt.figure(figsize=(20,15))
sns.scatterplot(data=data3,x="시설경도",y="시설위도")

# import geopandas as gpd

data3.to_csv("./수정후시설현황.csv")