# -*- coding: utf-8 -*-
"""
Created on Tue Sep 14 01:10:37 2021

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

data=pd.read_csv('./생활이동_자치구_202106/생활이동_자치구_202106_00시.csv',encoding='EUC-KR')

data.info()

data.head()

data.나이.unique()

data_00시=data.loc[data.나이>=60,]

data_00시.info()

data_00시.head()

# 자치구에서 특정 자치구 까지의 이동경로를 안다면, 거주인구를 포함한 특정 시간 당시의
# 실제인구를 알 수 있음.
# 평균을 내서 사용할것인가? 
# 시간대를 정해서 생활 시간을 반영한 지표를 만들어야함.
# ex ) 5시~22시까지를 생활시간이라고 생각하면 나머지 시간은 거주인구라고 볼 수 있고
# 시간대의 평균의 비가 실제 그 지역의 생활인구를 유추할 수 있음 . 

# 더 나아가 생활인구 데이터와 거주인구 데이터가 존재하면, 비율계산이 가능할 것으로 판단됌. 

# 모형적 비율? 가중치, 특정 구의 인구를 설명하는 회귀 예측 모델 -> 단지, 예측 인구를 위함이 아닌
# 가중치를 통한 각 자치구별 생활인구와 거주인구의 비를 설명할 수 있는 비율이 형성됌. 

# 두 데이터 유형 모두 존재. 
# 1. 자치구별 생활인구 2. 행정동별 생활인구 3. 자치구별 생활이동 4. 행정동별 생활이동.

# 먼저 자치구에 대한 모형을 설정하면, 생활인구 = a * 거주인구 +  b * 생활이동인구 
# 시간 평균을 어떤식으로 잡을것인지.
# 위 식이 구해지면 (a+b) : a 이게맞는건가? 아니면 1:a 가 맞는건가 ..?

# 거주인구와 생활이동인구중 특정 시간 대를 잘 설명하는 시간대 찾기.

# 우선 생활인구 데이터 불러오는 함수 생성


def 자치구_202106():
    file_=os.listdir("./생활이동_자치구_202106/")
    file_path="./생활이동_자치구_202106/"
    data=pd.DataFrame()

    for i in range(0,len(file_)):
        file_name=file_[i]
        filepath = file_path + '/' + file_name
        temp = pd.read_csv(filepath,encoding='EUC-KR')
        temp=temp.loc[temp.나이>=60,]
        data=pd.concat([data,temp])
        data=data.reset_index().drop('index',axis=1)
    return data


def 자치구_202107():
    file_=os.listdir("./생활이동_자치구_202107/")
    file_path="./생활이동_자치구_202107/"
    data=pd.DataFrame()

    for i in range(0,len(file_)):
        file_name=file_[i]
        filepath = file_path + '/' + file_name
        temp = pd.read_csv(filepath,encoding='EUC-KR')
        temp=temp.loc[temp.나이>=60,]
        data=pd.concat([data,temp])
        data=data.reset_index().drop('index',axis=1)
    return data

data_자치구06=자치구_202106()
data_자치구07=자치구_202107()

data_자치구06.info()
data_자치구07.info()

# 대략 630~640만개 있음

# -----------------------------------------------------------------------#
def 주소위도경도변환1(df):
   # 각자 API KEY 설정
    gmaps_key='Your Key'
    gmaps=googlemaps.Client(key=gmaps_key)
    
    시설주소=[]
    시설위도=[]
    시설경도=[]
    
    for address in df.시설주소:
        temp=gmaps.geocode(address,language='ko')
        if not temp:
            시설주소.append('?')
            시설위도.append(0)
            시설경도.append(0)
            continue
        
        시설주소.append(temp[0].get('formatted_address'))
        temp_loc=temp[0].get('geometry')
        시설위도.append(temp_loc['location']['lat'])
        시설경도.append(temp_loc['location']['lng'])
    
    df['시설주소API']=시설주소
    df['시설위도']=시설위도
    df['시설경도']=시설경도

    return df

def 주소위도경도변환2(df):
    gmaps_key='Your Key'
    gmaps=googlemaps.Client(key=gmaps_key)
    
    시설주소=[]
    시설위도=[]
    시설경도=[]
    
    data=df.loc[df.시설위도==0,:]
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
    data['시설위도']=시설위도
    data['시설경도']=시설경도
    data['시설주소API']=시설주소
    df=pd.merge(df,data,how='left',left_on='시설명',right_on='시설명')
    
    return df

# --------------------------------------------------------------------------#
# 점선 사이 함수는 잘못만듦. 안쓸거임.



def 노인서비스시설병합():
    file_=os.listdir("./사회복지시설/")
    file_path="./사회복지시설/"
    
    data=pd.DataFrame()
    
    for i in range(0,len(file_)):
        file_name=file_[i]
        filepath=file_path+'/'+file_name
        temp=pd.read_csv(filepath,encoding='EUC-KR')
        temp=temp.drop('시설장명',axis=1)
        data=pd.concat([data,temp])
        data=data.reset_index().drop('index',axis=1)
    
    return data


# ------------------------------------------------------------------------ #
data_노인서비스=노인서비스시설병합()
data_노인서비스=주소위도경도변환1(data_노인서비스)

data_노인서비스.info()

data_노인서비스.loc[data_노인서비스.시설위도==0,]

# 데이터 주소가 오입된 경우도 있음. 
# 이 경우 정규표현식으로 $층 제거하고, 괄호제거하기.
# 앞의 전처리를 처리하면서 더 완성도 있는 좌표변환 하기. 




data_노인서비스.loc[re.search(data_노인서비스.시군구명,data_노인서비스.시설주소)]

data2=주소위도경도변환2(data_노인서비스)

data2.loc[data2['시설코드_y'].isnull()==False,:]



for check,gu,nline in zip(data_노인서비스['시설주소'],data_노인서비스['시군구명'],range(len(data_노인서비스['시설주소API']))):
    check_error=re.search(str(gu),str(check))
    if not check_error:
        data_노인서비스.iloc[nline,8]='?'
        data_노인서비스.iloc[nline,9]=0
        data_노인서비스.iloc[nline,10]=0
        continue

len(data_노인서비스.loc[data_노인서비스['시설주소API']!='?',:])
# 1330
# 틀린거 14개. 
# 사회복지법인 이나 재단이 서울임에도 시설주소가 서울이 아닌경우도 있었음. 
# 이 경우는 추가로, 빅캠 데이터를 가져와서 비교해봐야 할 듯.
# 시설주소가 서울특별시가 아닌 경우 제거하는 방법도 고려해볼 필요성 있음.
# 주제의 명확성을 위해 본 분석에서의 제외 요인이라고 판단 가능함.

# 주소에서 괄호가 들어간 주소가 얼마나 많은지 체크
# 우선적으로 245번 청담노인복지센터는 주소가 중복 저건 수기로 오류 제거하기.
# 주소에 층이 들어간 경우 #층 2글자 제거하는 방법도 고려해볼만함. 
# 몇개나 있는지 체크하기.


# 주소에 서울특별시가 없는 경우 몇 가지인가 체크.
서울not=[]
for check,nline in zip(data_노인서비스['시설주소'],range(len(data_노인서비스['시설주소API']))):
    check_error=re.search('서울특별시',str(check))
    if not check_error:
        서울not.append(nline)
        continue

data_노인서비스.iloc[서울not,:]
len(서울not)
# 10개 존재.

괄호=[]
for check,nline in zip(data_노인서비스['시설주소'],range(len(data_노인서비스['시설주소API']))):
    check_error=re.search('\(',str(check))
    if check_error:
        괄호.append(nline)
        continue

len(data_노인서비스.iloc[괄호,:])
## 1105개나 괄호가 있음. 
# 먼저 층과 호를 제거하고 얼마나 제거되나 봐야함. 
층=[]
for check,nline in zip(data_노인서비스['시설주소'],range(len(data_노인서비스['시설주소API']))):
    check_error=re.search("[0-9]층",str(check))
    if check_error:
        층.append(nline)
        continue

len(data_노인서비스.iloc[층,:])

# 720개??.
data_노인서비스.iloc[층,:]

data_노인서비스.info()


제거문자=re.compile("[0-9]층|[0-9]{1,3}호")
for check,nline in zip(data_노인서비스['시설주소'],range(len(data_노인서비스['시설주소API']))):
    check_error=re.search(제거문자,str(check))
    if check_error:
        data_노인서비스.iloc[nline,7]=제거문자.sub("",str(check))
        continue

data_노인서비스['시설주소']

# ------------------------------------------------------------------------ #
# 위에거 안씀. 코드 확인용으로 돌려본 거.  



# 윗 부분 코드 참고해서 다시 함수를 만듦.
# ---------------------------------------------------------------------------#

data2=노인서비스시설병합()

def 주소오류처리(df):
    제거문자=re.compile("[0-9]층|[0-9]{1,3}호")
    for check,nline in zip(df['시설주소'],range(len(df['시설명']))):
        check_error=re.search(제거문자,str(check))
        # 245번 청당노인복지센터의 주소가 중복되서 적혀있어 이부분만 따로처리
        # 데이터가 바뀌면 수정 필요.
        # 865 재가노인지원서비스센터 <=> 은평어르신돌봄통합지원센터
        if nline==245:
            df.iloc[nline,7]="서울특별시 금천구 금하로29길 36"
        if nline==865:
            df.iloc[nline,0]="은평어르신돌봄통합지원센터"
        if check_error:
            df.iloc[nline,7]=제거문자.sub("",str(check))
            continue
    
    df['시설주소'].fillna(value='*',inplace=True)
    
    return df

data2=주소오류처리(data2)

data2.info()
data2.tail()

def 주소위도경도변환(df):
   # 각자 API KEY 설정
    gmaps_key='Your Key'
    gmaps=googlemaps.Client(key=gmaps_key)
    
    시설주소=[]
    시설위도=[]
    시설경도=[]
    
    for address,name in zip(df.시설주소,df.시설명):
        if address!='*':
            temp=gmaps.geocode(address,language='ko')
            if not temp:
                시설주소.append('?')
                시설위도.append(0)
                시설경도.append(0)
                continue
        
        else:
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
    
    df['시설주소API']=시설주소
    df['시설위도']=시설위도
    df['시설경도']=시설경도

    return df


data2=주소위도경도변환(data2)

error=[]
for check,gu,nline in zip(data2['시설주소API'],data2['시군구명'],range(len(data2['시설주소API']))):
    check_error=re.search(str(gu),str(check))
    if not check_error:
        error.append(nline)
        continue


## 1044, 1081 해피데이케어센터 구로미가데이케어센터 2개는 주소 변환시 오류발생.
# 1044 해피데이케어센터 주소 : 서울특별시 은평구 진흥로 91-1
# 구로미가데이케어센터 주소 : 서울특별시 구로구 천왕동 277


def 주소예외처리(df):
    df.iloc[1044,7]="서울특별시 은평구 진흥로 91-1"
    df.iloc[1081,7]="서울특별시 구로구 천왕동 277"

    gmaps_key='Your Key'
    gmaps=googlemaps.Client(key=gmaps_key)
    
    for i in [1044,1081]:
        temp=gmaps.geocode(df.iloc[i,7],language='ko')
        df.iloc[i,8]=temp[0].get('formatted_address')
        temp_loc=temp[0].get('geometry')
        df.iloc[i,9]=temp_loc['location']['lat']
        df.iloc[i,10]=temp_loc['location']['lng']

    return df

data3=주소예외처리(data2)


def 인구데이터병합():
    
def 시설이용률계산(df1):

def 인구가중치계산(df):

def 이상치탐색(df):
    list1=[]
    list2=[]
    list3=[]
    list_outlier=[]
    
    # ESD 방식 이상치 index 담는 list1
    
    # Histogram 방식 이상치 list2

    # 사분위수 방식 이상치 list3

    # 3개 중 2개 이상 겹치는 인덱스에 한해 제거해서 최종 결과 list_outlier    

    return list_outlier


def 클러스터링1(df):
    
def 클러스터링2(df):
    
def 입지선정(df1,df2):

    
# 시각화 및 클러스터링 입지선정은 R로 할 수 있음. 거의 70%이상 R로 할 듯.