
import googlemaps
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
import re

pd.set_option('display.max_columns',30)

os.chdir("C:/Users/-----/Desktop/빅캠 노인/데이터")

data = pd.read_excel("./사회복지시설현황.xlsx")

data.head()
data.info()

gmaps_key='Your Key'
gmaps=googlemaps.Client(key=gmaps_key)

# 한 번 체크 
#gmaps.geocode('금광1동 행정복지센터',language='ko')

data=data.drop(['시도','연락처'],axis=1)

시설주소=[]
시설위도=[]
시설경도=[]



for name in data.시설명:
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

len(시설경도)

data['시설주소']=시설주소
data['시설위도']=시설위도
data['시설경도']=시설경도

data.info()
data.tail()
#data=data[:-1]

## 구글 API로 처리못한 93개 데이터
len(data.loc[data['시설주소']=='?',:])
# 93

## 이외에도 이상한 주소로 된 데이터 다시 주소, 위도,경도 설정

data2=data

data2.info()

#data2=data2[:-1]

for check,nline in zip(data2['시설주소'],range(len(data2['시설주소']))):
    check_error=re.search('대한민국 서울특별시',check)
    if not check_error:
        data2.iloc[nline,5]='?'
        data2.iloc[nline,6]=0
        data2.iloc[nline,7]=0
        continue

## 이상한 주소 처리 후 개수
len(data2.loc[data['시설주소']=='?',:])
# 621

# 총 1689 개중 621개의 위치정보 오류 발생
# 이 데이터들은 네이버 API, 네이버 지도를 사용하여 다시 처리.



data3=data2.loc[data['시설주소']=='?',:].reset_index().drop('index',axis=1)

# data3=data3[:-1]

data3

name_google2=data3.시설명+' '+data3.시군구

시설주소2=[]
시설위도2=[]
시설경도2=[]

for name in name_google2:
    temp=gmaps.geocode(name,language='ko')
    if not temp:
        시설주소2.append('?')
        시설위도2.append(0)
        시설경도2.append(0)
        continue
    시설주소2.append(temp[0].get('formatted_address'))
    temp_loc=temp[0].get('geometry')
    시설위도2.append(temp_loc['location']['lat'])
    시설경도2.append(temp_loc['location']['lng'])

data3['시설주소']=시설주소2
data3['시설위도']=시설위도2
data3['시설경도']=시설경도2

len(data3.loc[data3['시설주소']=='?',:])
# 1 개
data3.loc[data3['시설주소']=='?',:]

# 장생시니어타운 (서초구)
data3.info()

for check,nline in zip(data3['시설주소'],range(len(data3['시설주소']))):
    check_error=re.search('대한민국 서울특별시',check)
    if not check_error:
        data3.iloc[nline,5]='?'
        data3.iloc[nline,6]=0
        data3.iloc[nline,7]=0
        continue

len(data3.loc[data3['시설주소']=='?',:])
# 38개

data3.loc[data3['시설주소']=='?',:]
data3.info()
data4=data3[['시설명','시군구','시설주소','시설위도','시설경도']]
data4.columns=['시설명','시군구','시설주소2','시설위도2','시설경도2']
data4.info()
data5=data4.drop_duplicates()
data2.info()

data6=data2.drop_duplicates()

data7=pd.merge(data6,data5,how='left',left_on=['시설명','시군구'],right_on=['시설명','시군구'])
data7.info()

for num in range(len(data7)):
    if (data7.iloc[num,5]=='?')&(data7.iloc[num,8]!='?'):
        data7.iloc[num,5]=data7.iloc[num,8]
        data7.iloc[num,6]=data7.iloc[num,9]
        data7.iloc[num,7]=data7.iloc[num,10]

주소좌표=data7.drop(['시설주소2','시설위도2','시설경도2'],axis=1)

주소좌표.info()

len(주소좌표.loc[주소좌표.시설주소=='?',:])

주소좌표.to_csv("./사회복지시설현황(좌표추가).csv",encoding='EUC-KR')

## 37개는 해결 못함. 
