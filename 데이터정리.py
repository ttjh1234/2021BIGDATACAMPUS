# -*- coding: utf-8 -*-
"""
Created on Thu Sep 30 18:21:57 2021

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

pd.set_option('display.max_columns',40)

os.chdir("C:/Users/82104/Desktop/빅캠 노인/데이터")

data=pd.read_csv("./cluster2.csv",encoding='EUC-KR')

data.head()

data=data.drop(['Unnamed: 0','Unnamed: 0.1'],axis=1)
data=data.drop('시군구명',axis=1)

data['시설cover']=data['총개수']/data['생활인구']*100

data


data['시설cover순위']=data['시설cover'].rank()

data[['자치구','시설cover순위','economic']].sort_values('시설cover순위')

data

# 어디위치에 어떤 시설을 지어야하나
# 

## 노인복지법 제 31조 - 제 39조 참고
# social <> 노인여가복지시설
# economic <> 노인일자리지원기관 & 노인주거복지시설
# health <> 노인의료복지시설, 재가노인복지시설


data['hr_survey']=data['health_survey']/(data['health_survey']+data['economic_survey']+data['social_survey'])
data['er_survey']=data['economic_survey']/(data['health_survey']+data['economic_survey']+data['social_survey'])
data['sr_survey']=data['social_survey']/(data['health_survey']+data['economic_survey']+data['social_survey'])

data[['자치구','총개수','er_survey','economic','sr_survey','hr_survey','health']].sort_values('hr_survey')

data=data.drop(['health_survey','social_survey','economic_survey','시설cover','시설cover순위'],axis=1)

data['h수요인원']=data['생활인구']*data['hr_survey']
data['e수요인원']=data['생활인구']*data['er_survey']
data['s수요인원']=data['생활인구']*data['sr_survey']

data.to_csv("./restart.csv",encoding='EUC-KR')

data['economic']=100-data['economic']

data.to_csv("./restart.csv",encoding='EUC-KR')


data=pd.read_csv("./restart.csv",encoding='EUC-KR')

data.head()

data[['자치구','er_survey','economic']]

###  ###

data=pd.read_excel("./9. 2020 지역사회조사(원시자료와 부호화 지침서).xlsx")

data=data[['GU','SQ1_3','Q6A4']]

data.columns=['자치구코드','출생연도','설문지표']

data.head()

code_list=[110,140,170,200,215,230,260,290,305,320,350,380,410,440,470,500,530,545,560,590,620,650,680,710,740]
len(code_list)

gu_list=['종로구','중구','용산구','성동구','광진구','동대문구','중랑구','성북구','강북구','도봉구','노원구','은평구',
         '서대문구','마포구','양천구','강서구','구로구','금천구','영등포구','동작구','관악구','서초구','강남구','송파구','강동구']

for i,j in zip(code_list,gu_list):
    data.at[data['자치구코드']==i,'자치구']=j


data.info()

social=data.loc[data['출생연도']<=1956,:].groupby('자치구')['설문지표'].mean()

social2=pd.DataFrame(social)

social2=social2.reset_index()

def 가중치계산(df,column1,column2):
    mid_weight=pd.read_csv("./생활이동전처리데이터.csv",encoding='EUC-KR')
    weight_dict={}
    for i in mid_weight['도착시군구'].unique():
        temp_sum=mid_weight.loc[mid_weight['도착시군구']==i,'이동인구'].sum()
        temp=0
        for j in mid_weight['출발시군구'].unique():
            temp+=mid_weight.loc[(mid_weight['도착시군구']==i)&(mid_weight['출발시군구']==j),'이동인구'].values*df.loc[df[column1]==j,column2].values
        
        weight_dict[i]=temp/temp_sum
    
        
    return weight_dict

dic_social=가중치계산(social2,'자치구','설문지표')

key_list=pd.Series(dic_social.keys())
value_list=pd.Series(dic_social.values())
value_list
social=pd.concat([key_list,value_list],axis=1)


social.columns=['자치구','social']
social['social']=social['social'].astype(float)

social.info()

(social['social']-np.mean(social['social']))/np.std(social['social'])


social['social']=social['social']*20

data=pd.read_csv("./restart.csv",encoding='EUC-KR')

data2=pd.merge(data,social,how='left',left_on='자치구',right_on='자치구')

data3=data2.drop('Unnamed: 0',axis=1)

data3.to_csv("./restart_plus_social.csv",encoding='EUC-KR')

################ 여기부터 다시 시작 10월 1일 저녁 타임. ####################
행정동코드=pd.read_excel("./행정동코드_매핑정보_20200325.xlsx",sheet_name="행정동코드")
행정동코드=행정동코드[['행자부행정동코드','시군구명','행정동명']]
행정동코드=행정동코드.iloc[1:,:]    
행정동코드['행자부행정동코드']=행정동코드['행자부행정동코드'].astype(int)

len(행정동코드['행정동명'].unique())
행정동코드.at[(행정동코드['시군구명']=='강남구')&(행정동코드['행정동명']=='신사동'),'행정동명']='강남구 신사동'

# 강남구 신사동


def 생활인구_읍면동():
    file_=os.listdir("./생활인구 - 읍면동/")
    file_path="./생활인구 - 읍면동/"
    data=pd.DataFrame()
    행정동코드=pd.read_excel("./행정동코드_매핑정보_20200325.xlsx",sheet_name="행정동코드")
    행정동코드=행정동코드[['행자부행정동코드','시군구명','행정동명']]
    행정동코드=행정동코드.iloc[1:,:]
    행정동코드.at[(행정동코드['시군구명']=='강남구')&(행정동코드['행정동명']=='신사동'),'행정동명']='강남구 신사동'
    행정동코드['행자부행정동코드']=행정동코드['행자부행정동코드'].astype(int)
    
    # 424개 행정동 있음.
    for i in range(0,len(file_)):
        file_name=file_[i]
        filepath = file_path + '/' + file_name
        temp = pd.read_csv(filepath,index_col=False)
        temp=temp[['기준일ID','시간대구분','행정동코드','남자65세부터69세생활인구수',
                   '남자70세이상생활인구수','여자65세부터69세생활인구수','여자70세이상생활인구수']]
        temp.columns=['기준일ID','시간대구분','행정동코드','남자65','남자70','여자65','여자70']
        temp['노인생활인구']=temp['남자65']+temp['남자70']+temp['여자65']+temp['여자70']        
        data=pd.concat([data,temp[['기준일ID','시간대구분','행정동코드','노인생활인구']]])
        data=data.reset_index().drop('index',axis=1)
    
    data=pd.merge(data,행정동코드,how='left',left_on='행정동코드',right_on='행자부행정동코드')
    data=data.drop('행자부행정동코드',axis=1)
    return data

data_읍면동=생활인구_읍면동()

data_읍면동=data_읍면동.loc[(data_읍면동['시간대구분']<=22)&(data_읍면동['시간대구분']>=4),:].reset_index().drop('index',axis=1)

def 이상치탐색1(df,column):
    
    # ESD 방식 이상치 index 담는 list_esd
    mean=np.mean(df[column])
    sd=np.std(df[column])
    minimum_esd=mean-3*sd
    maximum_esd=mean+3*sd
    mask_esd=(df[column]>=maximum_esd)|(df[column]<=minimum_esd)
    list_esd=list(df[mask_esd].index)

    return list_esd

def 이상치탐색2(df,column):
    
    # MAD 방식 이상치 list_mad
    median=np.median(df[column])
    mad=np.sqrt((df[column]-median)**2)
    data_mi=0.6745*np.abs(df[column]-median)/mad
    list_mad=data_mi[data_mi>=3.5].index

    return list_mad

def 이상치탐색3(df,column):
    # 사분위수 방식 이상치 list_iqr
    q1=np.quantile(df[column],0.25)
    q3=np.quantile(df[column],0.75)
    iqr=q3-q1
    minimum_iqr=q1-1.5*iqr
    maximum_iqr=q3+1.5*iqr
    mask_iqr=(df[column]<=minimum_iqr) | (df[column]>=maximum_iqr)
    list_iqr=list(df[mask_iqr].index)
    
    return list_iqr


def 이상치제거_생활인구_읍면동(df):
    temp=pd.DataFrame()
    for i in df['행정동명'].unique():
        for j in df['시간대구분'].unique():
            mask=(df['행정동명']==i)&(df['시간대구분']==j) 
            data=df.loc[mask,:]
        
            s1=set(이상치탐색1(data,'노인생활인구'))
            s2=set(이상치탐색2(data,'노인생활인구'))
            s3=set(이상치탐색3(data,'노인생활인구'))
            
            result1=s1.intersection(s2)
            result2=s1.intersection(s3)
            result3=s2.intersection(s3)
            
            result=result1|result2|result3
            list_outlier=list(result)
            data=data.drop(list_outlier,axis=0)
            temp=pd.concat([temp,data])
            temp=temp.reset_index().drop('index',axis=1)
    return temp

data_읍=이상치제거_생활인구_읍면동(data_읍면동)

data_읍.info()
data51=data_읍.groupby(['행정동명','시군구명'])['노인생활인구'].mean()

data6=pd.DataFrame(data51)
data6.info()
data6=data6.reset_index()
data6.to_csv("./행정동생활인구.csv",encoding='EUC-KR',index=False)



#### 생활인구 자치구 오류 데이터 수정 ####


data=pd.read_csv("./restart_plus_social.csv",encoding='EUC-KR')

data

data5=data5.reset_index()

data_rev=pd.merge(data,data5,how='left',left_on='자치구',right_on='자치구')

data_rev.columns
data_rev['생활인구_x']=data_rev['생활인구_y']
data_rev=data_rev.drop(['Unnamed: 0','생활인구_y'],axis=1)

data_rev.columns=['자치구', '생활인구', '총개수', '노인의료복지시설', '재가노인복지시설', '노인여가복지시설', '노인일자리지원기관',
       '노인주거복지시설', 'economic', 'health', 'hr_survey', 'er_survey', 'sr_survey',
       'h수요인원', 'e수요인원', 's수요인원', 'social']

data_rev['h수요인원']=data_rev['생활인구']*data_rev['hr_survey']
data_rev['e수요인원']=data_rev['생활인구']*data_rev['er_survey']
data_rev['s수요인원']=data_rev['생활인구']*data_rev['sr_survey']

data_rev

data_rev.to_csv("./restart_revise.csv",encoding='EUC-KR',index=False)


data6.loc[data6['시군구명']=='송파구','노인생활인구'].sum()
i='강남구'

hangjungdong=pd.DataFrame()
for i in data6['시군구명'].unique():
    temp=data6.loc[data6['시군구명']==i,['시군구명','행정동명','노인생활인구']]
    sum_=temp['노인생활인구'].sum()
    temp['비율']=temp['노인생활인구']/sum_
    hangjungdong=pd.concat([hangjungdong,temp[['시군구명','행정동명','비율']]],axis=0)
    hangjungdong.reset_index().drop('index',axis=1)
    
    
hangjungdong

data_rev
hangjung_expect=pd.DataFrame()
for i in data6['시군구명'].unique():
    temp=hangjungdong.loc[hangjungdong['시군구명']==i,['시군구명','행정동명','비율']]
    temp2=data_rev.loc[data_rev['자치구']==i,['자치구','h수요인원','e수요인원','s수요인원']]
    temp['h수요인원']=temp['비율']*float(temp2['h수요인원'].values)
    temp['s수요인원']=temp['비율']*float(temp2['s수요인원'].values)
    temp['e수요인원']=temp['비율']*float(temp2['e수요인원'].values)
    hangjung_expect=pd.concat([hangjung_expect,temp[['시군구명','행정동명','h수요인원','e수요인원','s수요인원']]],axis=0)
    hangjung_expect.reset_index().drop('index',axis=1)

hangjung_expect

hangjung_expect=hangjung_expect.reset_index().drop('index',axis=1)

hangjung_expect.info()

hangjung_expect.to_csv("./행정동데이터.csv",encoding='EUC-KR',index=False)

data=pd.read_csv('시설처리0919.csv',encoding='EUC-KR')

## 경제 : 동작구 ,영등포구, 은평구
## 건강 : 강북구 강서구 구로구 금천구 노원구 도봉구 동대문구 성북구 송파구 양천구
## 여가 : 강북구 동대문구 종로구 

## 강북구 강서구 구로구  금천구 노원구 도봉구 동대문구 성북구 송파구 양천구 영등포구 동작구 은평구 종로구 
## 14개만.


list1=['강북구' ,'강서구' ,'구로구' ,'금천구' ,'노원구' ,'도봉구' ,'동대문구' ,'성북구' ,'송파구', '양천구' ,'영등포구' ,'동작구' ,'은평구' ,'종로구']

data2=data.loc[data['시군구명'].isin(list1),:]

data2=data2.reset_index().drop('index',axis=1)


data2


data_geo2=gpd.read_file("./Z_SOP_BND_ADM_DONG_PG/Z_SOP_BND_ADM_DONG_PG.shp",encoding='EUC-KR')
data_geo2.crs

data_geo2['geometry'].to_crs(epsg=4326)

data10=pd.read_csv("./행정동데이터.csv",encoding='EUC-KR')

행정동코드=pd.read_excel("./행정동코드_매핑정보_20200325.xlsx",sheet_name="행정동코드")
행정동코드=행정동코드.iloc[1:,:]

행정동코드.at[((행정동코드['시군구명']=='강남구')&(행정동코드['행정동명']=='신사동'))==True,'행정동명']='강남구 신사동'

data10=pd.merge(data10,행정동코드[['통계청행정동코드','행정동명']],how='left',left_on='행정동명',right_on='행정동명')

# data10 : 행정동데이터에 통계청 행정동코드 매핑함.
# 한 이유 : 이 매핑한 코드를 지리데이터에 연결



list_code=data10['통계청행정동코드'].astype(str)
list_name=data10['행정동명']

data_geo



data_geo=data_geo.loc[(data_geo['ADM_DR_CD'].isin(list_code))==True,:]
data_geo.info()
set1=set(data_geo['ADM_DR_CD'])
set2=set(data10['통계청행정동코드'].astype(str))

data_geo2=data_geo2.set_crs(epsg=4326)



data10.loc[data10['통계청행정동코드'].astype(str)=='1117068',:]
set2-set1

data10
data_geo2.loc[data_geo2['ADM_DR_NM']=='오류2동',:]

data_geo3=pd.concat([data_geo,data_geo2.loc[data_geo2['ADM_DR_NM']=='오류2동',:]],axis=0)

data_geo3.info()

data_geo3.at[data_geo3['ADM_DR_NM']=='오류2동','ADM_DR_CD']='1117068'

data_geo3=data_geo3.reset_index().drop('index',axis=1)

data

from shapely.geometry import Point

geometry = [Point(xy) for xy in zip(data['시설경도'], data['시설위도'])]

data=pd.read_csv("./시설처리0919.csv",encoding='EUC-KR')
geometry = [Point(xy) for xy in zip(data['시설경도'], data['시설위도'])]
data = gpd.GeoDataFrame(data, geometry=geometry)


data_geo3
gdf=gpd.GeoDataFrame(data_geo3.iloc[:,:4],geometry=data_geo3.iloc[:,4])
gdf.set_crs(epsg=5181,inplace=True)

gdf=gdf.to_crs(epsg=4326)

gdf

data10

#gdf.to_file("./행정동행정경계.shp",encoding='UTF-8')

len(data)

data

name=[]
for j in range(len(data)):
    for i in range(len(gdf['geometry'])):
        if (gdf['geometry'][i]).contains(data['geometry'][j]):
            name.append(gdf.iloc[i,2]) 

len(name)


data_시설=pd.read_csv("시설처리0919.csv",encoding='EUC-KR')

data_시설=data_시설.drop('Unnamed: 0',axis=1)

data_시설.loc[data_시설['시군구명']=='서울특별시',]
data_시설=data_시설.drop([364,673],axis=0).reset_index().drop('index',axis=1)


data_총개수=data_시설['시군구명'].value_counts()

data_시설.at[data_시설['시군구명']=='서울특별시','시군구명']='동작구'

data_시설.info()
data_시설.head()


data_시설['시설종류상세명(시설종류)'].unique()

data_시설=data_시설.reset_index().drop('index',axis=1)

geometry = [Point(xy) for xy in zip(data_시설['시설경도'], data_시설['시설위도'])]
data_시설 = gpd.GeoDataFrame(data_시설, geometry=geometry)

name=[]
for j in range(len(data_시설)):
    t=0
    for i in range(len(gdf['geometry'])):
        if (gdf['geometry'][i]).contains(data_시설['geometry'][j]):
            t=1
            name.append(gdf.iloc[i,2]) 
    
    if t==0:
        name.append('*')
        
        
len(name)

data_시설['행정동']=name

data_시설.info()

data_시설

data_시설=data_시설.drop(data_시설.loc[data_시설['행정동']=='*',:].index,axis=0).reset_index().drop('index',axis=1)


data_시설=data_시설.drop(data_시설.loc[data_시설['시설종류상세명(시설종류)']=='노인기타',:].index,axis=0).reset_index().drop('index',axis=1)

data_시설

data11=pd.read_csv("./행정동데이터.csv",encoding='EUC-KR')

data10


list_=[0,0,0,0,0]
empty_list=pd.Series(list_,index=['노인의료복지시설','노인여가복지시설','재가노인복지시설','노인주거복지시설','노인일자리지원기관'])

data_시설종류=pd.DataFrame(columns=['노인의료복지시설','노인여가복지시설','재가노인복지시설','노인주거복지시설','노인일자리지원기관'])
len(data_시설['행정동'].unique())
i=data_시설['행정동'].unique()[400]
data_시설.loc[data_시설['행정동']==i,'시설종류상세명(시설종류)'].value_counts()

for i in data_시설['행정동'].unique():
    if data_시설.loc[data_시설['행정동']==i,'시설종류상세명(시설종류)'].value_counts().all():
        data_시설종류=pd.concat([data_시설종류,data_시설.loc[data_시설['행정동']==i,'시설종류상세명(시설종류)'].value_counts()],axis=1)
    else:
        data_시설종류=pd.concat([data_시설종류,empty_list],axis=1)
data_시설종류=data_시설종류.transpose()

data_시설종류.index=data_시설['시군구명'].unique()

################################
######## 코드 정리 ##############
#################################

data_geo=gpd.read_file("./Z_SOP_BND_ADM_DONG_PG/Z_SOP_BND_ADM_DONG_PG.shp",encoding='EUC-KR')

data10=pd.read_csv("./행정동데이터.csv",encoding='EUC-KR')

행정동코드=pd.read_excel("./행정동코드_매핑정보_20200325.xlsx",sheet_name="행정동코드")
행정동코드=행정동코드.iloc[1:,:]

행정동코드.at[((행정동코드['시군구명']=='강남구')&(행정동코드['행정동명']=='신사동'))==True,'행정동명']='강남구 신사동'

data10=pd.merge(data10,행정동코드[['통계청행정동코드','행정동명']],how='left',left_on='행정동명',right_on='행정동명')

# 424개 구가 정확히 나옴

## 
data_geo.at[(data_geo['ADM_DR_NM']=='신사동')&(data_geo['ADM_DR_CD']=='1123051'),'ADM_DR_NM']='강남구 신사동'

# 신사동이 두개라 관악구 신사동 : 신사동 , 강남구 신사동 : 강남구 신사동 으로 변환

data_geo.loc[(data_geo['ADM_DR_NM']=='신사동')&(data_geo['ADM_DR_CD']=='1123051'),:]
# none
# 잘 바뀐거 확인.

list_code=data10['통계청행정동코드'].astype(str)
list_name=data10['행정동명']

data_geo



data_geo=data_geo.loc[(data_geo['ADM_DR_CD'].isin(list_code))==True,:]
data_geo.info()

# 423 개 , 1개가 안들어간거.
set1=set(data_geo['ADM_DR_CD'])
set2=set(data10['통계청행정동코드'].astype(str))

set2-set1
# 코드가 잘못들어감 . 따라서 이 코드에 해당하는 동이 어딘지 확인.

data10.loc[data10['통계청행정동코드'].astype(str)=='1117068',:]
# 오류 2동


data10
data_geo2.loc[data_geo2['ADM_DR_NM']=='오류2동',:]
# data

data_geo3=pd.concat([data_geo,data_geo2.loc[data_geo2['ADM_DR_NM']=='오류2동',:]],axis=0)

data_geo3.info()

# 424개가 잘들어감.

data_geo3.at[data_geo3['ADM_DR_NM']=='오류2동','ADM_DR_CD']='1117068'

data_geo3=data_geo3.reset_index().drop('index',axis=1)

data_geo3
# 424개로 잘처리됌.

from shapely.geometry import Point


geometry = [Point(xy) for xy in zip(data['시설경도'], data['시설위도'])]

data=pd.read_csv("./시설처리0919.csv",encoding='EUC-KR')
geometry = [Point(xy) for xy in zip(data['시설경도'], data['시설위도'])]
data = gpd.GeoDataFrame(data, geometry=geometry)

data_geo3.info()

gdf=gpd.GeoDataFrame(data_geo3.iloc[:,:4],geometry=data_geo3.iloc[:,4])
gdf.set_crs(epsg=5181,inplace=True)

gdf=gdf.to_crs(epsg=4326)


# gdf.to_file("./행정동행정경계.shp",encoding='UTF-8')


data_시설=pd.read_csv("시설처리0919.csv",encoding='EUC-KR')

data_시설=data_시설.drop('Unnamed: 0',axis=1)

data_시설.loc[data_시설['시군구명']=='서울특별시',]
data_시설=data_시설.drop([364,673],axis=0).reset_index().drop('index',axis=1)

data_시설.at[data_시설['시군구명']=='서울특별시','시군구명']='동작구'

data_시설.info()
data_시설.head()


data_시설['시설종류상세명(시설종류)'].unique()

data_시설=data_시설.reset_index().drop('index',axis=1)

geometry = [Point(xy) for xy in zip(data_시설['시설경도'], data_시설['시설위도'])]
data_시설 = gpd.GeoDataFrame(data_시설, geometry=geometry)

name=[]
for j in range(len(data_시설)):
    t=0
    for i in range(len(gdf['geometry'])):
        if (gdf['geometry'][i]).contains(data_시설['geometry'][j]):
            t=1
            name.append(gdf.iloc[i,2]) 
    
    if t==0:
        name.append('*')
        
        
len(name)

data_시설['행정동']=name

data_시설

data_시설=data_시설.drop(data_시설.loc[data_시설['행정동']=='*',:].index,axis=0).reset_index().drop('index',axis=1)

data_시설=data_시설.drop(data_시설.loc[data_시설['시설종류상세명(시설종류)']=='노인기타',:].index,axis=0).reset_index().drop('index',axis=1)

data_시설

# 총 1324 개

data_시설.to_csv("./시설1002.csv",encoding='EUC-KR')


#
len(data10['행정동명'].unique())
# 424

list_=[0,0,0,0,0]

empty_list=pd.Series(list_,index=['노인의료복지시설','노인여가복지시설','재가노인복지시설','노인주거복지시설','노인일자리지원기관'])

data_시설종류=pd.DataFrame()

len(data_시설['행정동'].unique())

data_시설

for i in data10['행정동명'].unique():
    if data_시설.loc[data_시설['행정동']==i,'시설종류상세명(시설종류)'].value_counts().all():
        data_시설종류=pd.concat([data_시설종류,data_시설.loc[data_시설['행정동']==i,'시설종류상세명(시설종류)'].value_counts()],axis=1)
    else:
        data_시설종류=pd.concat([data_시설종류,empty_list],axis=1)

data_시설종류=data_시설종류.transpose()

data_시설종류.index=data10['행정동명'].unique()

data_시설종류=data_시설종류.fillna(0)
data_시설종류=data_시설종류.reset_index()
data_시설종류.columns=['행정동명','재가노인복지시설','노인의료복지시설','노인주거복지시설','노인여가복지시설','노인일자리지원기관']

data10
data_hang=pd.merge(data10,data_시설종류,how='left',left_on='행정동명',right_on='행정동명')

data_hang.to_csv("행정동중간.csv",encoding='EUC-KR',index=False)

data_hang['h시설']=data_hang['노인의료복지시설']+data_hang['재가노인복지시설']
data_hang['e시설']=data_hang['노인주거복지시설']+data_hang['노인일자리지원기관']
data_hang['s시설']=data_hang['노인여가복지시설']

data_hang['h수요충족']=data_hang['h수요인원']/(data_hang['h시설']+0.5)
data_hang['e수요충족']=data_hang['e수요인원']/(data_hang['e시설']+0.5)
data_hang['s수요충족']=data_hang['s수요인원']/(data_hang['s시설']+0.5)

data_hang['h수요충족'].mean()

## 경제 : 동작구 ,영등포구, 은평구
## 건강 : 강북구 강서구 구로구 금천구 노원구 도봉구 동대문구 성북구 송파구 양천구
## 여가 : 강북구 동대문구 종로구 

list_e=['동작구','영등포구','은평구']
list_h=['강북구' ,'강서구' ,'구로구' ,'금천구' ,'노원구' ,'도봉구' ,'동대문구' ,'성북구' ,'송파구' ,'양천구']
list_s=['강북구','동대문구','종로구']
data_e=data_hang.loc[data_hang['시군구명'].isin(list_e)==True,:].reset_index().drop('index',axis=1)
data_s=data_hang.loc[data_hang['시군구명'].isin(list_s)==True,:].reset_index().drop('index',axis=1)
data_h=data_hang.loc[data_hang['시군구명'].isin(list_h)==True,:].reset_index().drop('index',axis=1)

economic_region=data_e.sort_values('e수요충족',ascending=False).iloc[:5,:]
social_region=data_s.sort_values('s수요충족',ascending=False).iloc[:5,:]
health_region=data_h.sort_values('h수요충족',ascending=False).iloc[:5,:]


hmean=data_hang['h수요충족'].mean()
emean=data_hang['e수요충족'].mean()
smean=data_hang['s수요충족'].mean()


economic_region['e필요개수']=(economic_region['e수요인원']/emean)-0.5
social_region['e필요개수']=(social_region['s수요인원']/smean)-0.5
health_region['e필요개수']=(health_region['h수요인원']/hmean)-0.5

economic_region
social_region
health_region

economic_region.to_csv("경제입지행정동.csv",encoding='EUC-KR',index=False)
social_region.to_csv("여가입지행정동.csv",encoding='EUC-KR',index=False)
health_region.to_csv("건강입지행정동.csv",encoding='EUC-KR',index=False)


##########################
data_hang=pd.read_csv("행정동중간.csv",encoding='EUC-KR')

data_hang['h시설']=data_hang['노인의료복지시설']+data_hang['재가노인복지시설']
data_hang['e시설']=data_hang['노인주거복지시설']+data_hang['노인일자리지원기관']
data_hang['s시설']=data_hang['노인여가복지시설']

data_hang['h수요충족']=data_hang['h수요인원']/(data_hang['h시설']+0.01)
data_hang['e수요충족']=data_hang['e수요인원']/(data_hang['e시설']+0.01)
data_hang['s수요충족']=data_hang['s수요인원']/(data_hang['s시설']+0.01)

data_hang['h수요충족'].mean()

list_e=['동작구','영등포구','은평구']
list_h=['강북구' ,'강서구' ,'구로구' ,'금천구' ,'노원구' ,'도봉구' ,'동대문구' ,'성북구' ,'송파구' ,'양천구']
list_s=['강북구','동대문구','종로구']
data_e=data_hang.loc[data_hang['시군구명'].isin(list_e)==True,:].reset_index().drop('index',axis=1)
data_s=data_hang.loc[data_hang['시군구명'].isin(list_s)==True,:].reset_index().drop('index',axis=1)
data_h=data_hang.loc[data_hang['시군구명'].isin(list_h)==True,:].reset_index().drop('index',axis=1)

economic_region=data_e.sort_values('e수요충족',ascending=False).iloc[:5,:]
social_region=data_s.sort_values('s수요충족',ascending=False).iloc[:5,:]
health_region=data_h.sort_values('h수요충족',ascending=False).iloc[:5,:]

emean=data_hang['e수요충족'].mean()
hmean=data_hang['h수요충족'].mean()
smean=data_hang['s수요충족'].mean()


economic_region['e필요개수']=(economic_region['e수요인원']/emean)-0.01
social_region['e필요개수']=(social_region['s수요인원']/smean)-0.01
health_region['e필요개수']=(health_region['h수요인원']/hmean)-0.01

####
data=gpd.read_file("./빅캠_서울시도로명주소기반/TL_SPBD_BULD.shp")

data['EMD_CD']
## 코드가없음.


data_bus=pd.read_csv("./빅캠데이터2/빅캠 신청데이터2/TB_E_BUSSTOP_201810.txt",sep='|')
data_sub=pd.read_csv("./빅캠데이터2/빅캠 신청데이터2/TB_O_SB_STATN.txt",sep='|')

data_geo=gpd.read_file("./행정동행정경계.shp")
# WGS 84 : EPSG : 4326

data_bus.columns=['YYYY_NM','LINE_NO_EXP','LINE_NO','LINE_EXP','SEQ_NO','BUS_STA_NM','X_COORD','Y_COORD','ARSID']

data_bus.info()
data_bus['X_COORD']=data_bus['X_COORD'].str.replace('`','')
data_bus['X_COORD']=data_bus['X_COORD'].astype(float)
data_bus['Y_COORD']=data_bus['Y_COORD'].str.replace('`','')
data_bus['Y_COORD']=data_bus['Y_COORD'].astype(float)

from shapely.geometry import Point
geometry = [Point(xy) for xy in zip(data_bus['X_COORD'], data_bus['Y_COORD'])]
data_bus = gpd.GeoDataFrame(data_bus, geometry=geometry)


data_bus.set_crs(epsg=4326,inplace=True)

data_bus.crs

data_sub.columns=['GU_NM','GU_CD','SUB_STA_SN','KOR_SUM_NM','POINT_X','POINT_Y']

data_sub['POINT_X']=data_sub['POINT_X'].str.replace('`','')
data_sub['POINT_X']=data_sub['POINT_X'].astype(float)
data_sub['POINT_Y']=data_sub['POINT_Y'].str.replace('`','')
data_sub['POINT_Y']=data_sub['POINT_Y'].astype(float)

data_sub

geometry2 = [Point(xy) for xy in zip(data_sub['POINT_X'], data_sub['POINT_Y'])]

data_sub = gpd.GeoDataFrame(data_sub, geometry=geometry2)

data_sub.set_crs(epsg=5181,inplace=True)
data_sub=data_sub.to_crs(epsg=4326)

data_sub['GU_NM']=data_sub['GU_NM'].str.replace('`','')
data_sub['KOR_SUB_NM']=data_sub['KOR_SUM_NM'].str.replace('`','')
data_sub=data_sub.drop(['KOR_SUM_NM','GU_CD','SUB_STA_SN'],axis=1)

data_bus=data_bus.drop(['YYYY_NM','LINE_NO_EXP','LINE_NO','LINE_EXP','SEQ_NO','ARSID'],axis=1)

data_bus['BUS_STA_NM']=data_bus['BUS_STA_NM'].str.replace('`','')

data_geo

# 건강 : 상계 6.7동 중계2.3동 송천동 잠실3동 상계3.4동
# 경제 :여의동 상도1동 진관동 대방동 사당2동
# 여가 : 종로1.2.3.4가동 송중동 용신동 제기동 송천동

health_sub=['송천동' ,'잠실3동' ,'개봉2동','목2동','월계2동'] ## 바뀜.
economic_sub=['여의동', '상도1동' ,'진관동','대방동' ,'사당2동'] ## 경제는 안바뀜.
social_sub=['송중동' ,'용신동' ,'제기동' ,'송천동','전농1동'] ## 바뀜

data_geo['ADM_DR_NM'].unique()

data_sub.geometry
h_name=[]

h_name=[]
for j in range(len(data_sub)):
    t=0
    for i in range(len(data_geo['geometry'])):
        if t==1:
            break;
        if (data_geo['geometry'][i]).contains(data_sub['geometry'][j]):
            t=1
            h_name.append(data_geo.iloc[i,2]) 
    
    if t==0:
        h_name.append('*')
        
len(h_name)

data_sub['행정동']=h_name

data_use_h=data_sub.loc[data_sub['행정동'].isin(health_sub),:]
data_use_e=data_sub.loc[data_sub['행정동'].isin(economic_sub),:]
data_use_s=data_sub.loc[data_sub['행정동'].isin(social_sub),:]


data_bus

b_name=[]
for j in range(len(data_bus)):
    t=0
    for i in range(len(data_geo['geometry'])):
        if t==1:
            break;
        if (data_geo['geometry'][i]).contains(data_bus['geometry'][j]):
            t=1
            b_name.append(data_geo.iloc[i,2]) 
    
    if t==0:
        b_name.append('*')


# 실행시간 김.. -> 데이터가 38423개 있어서 그런 듯.

len(b_name)
# 38423

data_bus['행정동']=b_name
data_use_hb=data_bus.loc[data_bus['행정동'].isin(health_sub),:]
data_use_eb=data_bus.loc[data_bus['행정동'].isin(economic_sub),:]
data_use_sb=data_bus.loc[data_bus['행정동'].isin(social_sub),:]

data_use_h.to_csv("./건강지하철위치.csv",encoding='EUC-KR',index=False)
data_use_e.to_csv("./경제지하철위치.csv",encoding='EUC-KR',index=False)
data_use_s.to_csv("./여가지하철위치.csv",encoding='EUC-KR',index=False)
data_use_hb.to_csv("./건강버정위치.csv",encoding='EUC-KR',index=False)
data_use_eb.to_csv("./경제버정위치.csv",encoding='EUC-KR',index=False)
data_use_sb.to_csv("./여가버정위치.csv",encoding='EUC-KR',index=False)


data=gpd.read_file("./빅캠_서울시도로명주소기반/TL_SPBD_BULD.shp")

data.info()
data.head()

data['BULD_NM'].unique()
len(data['ADMI_CD'].unique())

data.crs

data_bulid=data[['BDTYP_CD','BULD_NM','X_AXIS','Y_AXIS']]

data_bulid.info()
data_bulid.columns=['건물용도','건물이름','경도','위도']
data_bulid['주거지역']=0
data_bulid.at[data_bulid['건물용도'].isin(['01000','01001','01002','01003','01004','02000','02001','02002','02003']),'주거지역']=1



# 건강 : 상계 6.7동 중계2.3동 송천동 잠실3동 상계3.4동
# 경제 :여의동 상도1동 진관동 대방동 사당2동
# 여가 : 종로1.2.3.4가동 송중동 용신동 제기동 송천동

health_sub=['상계6·7동', '중계2·3동' ,'송천동' ,'잠실3동' ,'상계3.4동']
economic_sub=['여의동', '상도1동' ,'진관동','대방동' ,'사당2동']
social_sub=['종로1·2·3·4가동' ,'송중동' ,'용신동' ,'제기동' ,'송천동']


data_geo=gpd.read_file("./행정동행정경계.shp")
# WGS 84 : EPSG : 4326

data_geo.crs

from shapely.geometry import Point
geometry = [Point(xy) for xy in zip(data_bulid['경도'], data_bulid['위도'])]
data_bulid = gpd.GeoDataFrame(data_bulid, geometry=geometry)

data_bulid.crs
data_bulid.set_crs(epsg=5181,inplace=True)
data_bulid=data_bulid.to_crs(epsg=4326)

data_bulid.head()


len(data_bulid)


bh_name=[]
for j in range(len(data_bulid)):
    t=0
    for i in range(len(data_geo['geometry'])):
        if t==1:
            break;
        if (data_geo['geometry'][i]).contains(data_bulid['geometry'][j]):
            t=1
            bh_name.append(data_geo.iloc[i,2]) 
    
    if t==0:
        bh_name.append('*')




data_bulid['행정동']=bh_name

data_bulid[data_bulid['행정동']=='*']



health_sub=['상계6·7동', '중계2·3동' ,'송천동' ,'잠실3동' ,'상계3.4동']
economic_sub=['여의동', '상도1동' ,'진관동','대방동' ,'사당2동']
social_sub=['종로1·2·3·4가동' ,'송중동' ,'용신동' ,'제기동' ,'송천동']

data_bulid_hb=data_bulid.loc[data_bulid['행정동'].isin(health_sub),:]
data_bulid_hb=data_bulid_hb.reset_index().drop('index',axis=1)

data_bulid_hb['경도']=data_bulid_hb['geometry'].x
data_bulid_hb['위도']=data_bulid_hb['geometry'].y

data_bulid_hb.to_csv("./건강건물.csv",encoding='EUC-KR',index=False)

data_bulid_eb=data_bulid.loc[data_bulid['행정동'].isin(economic_sub),:]
data_bulid_eb=data_bulid_eb.reset_index().drop('index',axis=1)
data_bulid_eb['경도']=data_bulid_eb['geometry'].x
data_bulid_eb['위도']=data_bulid_eb['geometry'].y
data_bulid_eb.to_csv("./경제건물.csv",encoding='EUC-KR',index=False)



data_bulid_sb=data_bulid.loc[data_bulid['행정동'].isin(social_sub),:]
data_bulid_sb=data_bulid_sb.reset_index().drop('index',axis=1)
data_bulid_sb['경도']=data_bulid_sb['geometry'].x
data_bulid_sb['위도']=data_bulid_sb['geometry'].y
data_bulid_sb.to_csv("./여가건물.csv",encoding='EUC-KR',index=False)


data_hs=pd.read_csv("./건강지하철위치.csv",encoding='EUC-KR')
data_es=pd.read_csv("./경제지하철위치.csv",encoding='EUC-KR')
data_ss=pd.read_csv("./여가지하철위치.csv",encoding='EUC-KR')

geometry = [Point(xy) for xy in zip(data_hs['POINT_X'], data_hs['POINT_Y'])]


data_hs = gpd.GeoDataFrame(data_hs, geometry=geometry)

data_hs.crs
data_hs.set_crs(epsg=5181,inplace=True)
data_hs=data_hs.to_crs(epsg=4326)

data_hs['경도']=data_hs['geometry'].x
data_hs['위도']=data_hs['geometry'].y

data_hs.to_csv("./건강지하철위치2.csv",encoding='EUC-KR',index=False)


geometry = [Point(xy) for xy in zip(data_es['POINT_X'], data_es['POINT_Y'])]


data_es = gpd.GeoDataFrame(data_es, geometry=geometry)

data_es.crs
data_es.set_crs(epsg=5181,inplace=True)
data_es=data_es.to_crs(epsg=4326)

data_es['경도']=data_es['geometry'].x
data_es['위도']=data_es['geometry'].y


data_es.to_csv("./경제지하철위치2.csv",encoding='EUC-KR',index=False)

geometry = [Point(xy) for xy in zip(data_ss['POINT_X'], data_ss['POINT_Y'])]


data_ss = gpd.GeoDataFrame(data_ss, geometry=geometry)

data_ss.crs
data_ss.set_crs(epsg=5181,inplace=True)
data_ss=data_ss.to_crs(epsg=4326)

data_ss['경도']=data_ss['geometry'].x
data_ss['위도']=data_ss['geometry'].y

data_ss.to_csv("./여가지하철위치2.csv",encoding='EUC-KR',index=False)

data_sisul=pd.read_csv("./시설1002.csv",encoding='EUC-KR')

data_sisul.loc[data_sisul['행정동']=='상계6·7동']

data_sisul['행정동']=data_sisul['행정동'].str.replace('·','.')






list_=[0,0,0,0,0]

empty_list=pd.Series(list_,index=['노인의료복지시설','노인여가복지시설','재가노인복지시설','노인주거복지시설','노인일자리지원기관'])

data_시설종류=pd.DataFrame()

len(data_sisul['행정동'].unique())

data10=pd.read_csv("./행정동데이터.csv",encoding='EUC-KR')

data10['행정동명'].unique()
data_sisul

for i in data10['행정동명'].unique():
    if data_sisul.loc[data_sisul['행정동']==i,'시설종류상세명(시설종류)'].value_counts().all():
        data_시설종류=pd.concat([data_시설종류,data_sisul.loc[data_sisul['행정동']==i,'시설종류상세명(시설종류)'].value_counts()],axis=1)
    else:
        data_시설종류=pd.concat([data_시설종류,empty_list],axis=1)

data_시설종류=data_시설종류.transpose()

data_시설종류.index=data10['행정동명'].unique()

data_시설종류=data_시설종류.fillna(0)
data_시설종류=data_시설종류.reset_index()
data_시설종류.columns=['행정동명','재가노인복지시설','노인의료복지시설','노인주거복지시설','노인여가복지시설','노인일자리지원기관']

data10
data_hang=pd.merge(data10,data_시설종류,how='left',left_on='행정동명',right_on='행정동명')

data_hang.to_csv("행정동중간.csv",encoding='EUC-KR',index=False)

data_hang['h시설']=data_hang['노인의료복지시설']+data_hang['재가노인복지시설']
data_hang['e시설']=data_hang['노인주거복지시설']+data_hang['노인일자리지원기관']
data_hang['s시설']=data_hang['노인여가복지시설']

data_hang['h수요충족']=data_hang['h수요인원']/(data_hang['h시설']+0.5)
data_hang['e수요충족']=data_hang['e수요인원']/(data_hang['e시설']+0.5)
data_hang['s수요충족']=data_hang['s수요인원']/(data_hang['s시설']+0.5)

data_hang['h수요충족'].mean()

## 경제 : 동작구 ,영등포구, 은평구
## 건강 : 강북구 강서구 구로구 금천구 노원구 도봉구 동대문구 성북구 송파구 양천구
## 여가 : 강북구 동대문구 종로구 

list_e=['동작구','영등포구','은평구']
list_h=['강북구' ,'강서구' ,'구로구' ,'금천구' ,'노원구' ,'도봉구' ,'동대문구' ,'성북구' ,'송파구' ,'양천구']
list_s=['강북구','동대문구','종로구']
data_e=data_hang.loc[data_hang['시군구명'].isin(list_e)==True,:].reset_index().drop('index',axis=1)
data_s=data_hang.loc[data_hang['시군구명'].isin(list_s)==True,:].reset_index().drop('index',axis=1)
data_h=data_hang.loc[data_hang['시군구명'].isin(list_h)==True,:].reset_index().drop('index',axis=1)

economic_region=data_e.sort_values('e수요충족',ascending=False).iloc[:5,:]
social_region=data_s.sort_values('s수요충족',ascending=False).iloc[:5,:]
health_region=data_h.sort_values('h수요충족',ascending=False).iloc[:5,:]


hmean=data_hang['h수요충족'].mean()
emean=data_hang['e수요충족'].mean()
smean=data_hang['s수요충족'].mean()


economic_region['e필요개수']=(economic_region['e수요인원']/emean)-0.5
social_region['e필요개수']=(social_region['s수요인원']/smean)-0.5
health_region['e필요개수']=(health_region['h수요인원']/hmean)-0.5

economic_region
social_region
health_region

economic_region.to_csv("경제입지행정동.csv",encoding='EUC-KR',index=False)
social_region.to_csv("여가입지행정동.csv",encoding='EUC-KR',index=False)
health_region.to_csv("건강입지행정동.csv",encoding='EUC-KR',index=False)

####### 
# 생활이동 가중치 # 
# 
## 경제 : 동작구 ,영등포구, 은평구
## 건강 : 강북구 강서구 구로구 금천구 노원구 도봉구 동대문구 성북구 송파구 양천구
## 여가 : 강북구 동대문구 종로구 


def 생활이동_2021():
    file_=os.listdir("./생활이동_행정동/")
    path1="./생활이동_행정동/"
    data=pd.DataFrame()
    for i in range(0,len(file_)):
        path2=file_[i]
        path=path1+path2
        file_list=os.listdir(path)
        for j in range(0,len(file_list)):
            file_name=file_list[j]
            filepath = path + '/' + file_name
            temp = pd.read_csv(filepath,encoding='EUC-KR')
            temp=temp.loc[temp.나이>=65,]
            mask=(temp['출발 행정동 코드']>=1101053)&(temp['출발 행정동 코드']<=1125074)&(temp['도착 행정동 코드']<=1125074)&(temp['도착 행정동 코드']>=1101053)
            temp=temp.loc[mask,:].reset_index().drop('index',axis=1)
            temp=temp[['대상연월','도착시간','출발 행정동 코드','도착 행정동 코드','성별','이동인구(합)']]
            data=pd.concat([data,temp])
            data=data.reset_index().drop('index',axis=1)
    return data


def 행정동_202107():
    file_=os.listdir("./생활이동_행정동_202107/")
    file_path="./생활이동_행정동_202107/"
    data=pd.DataFrame()
    for i in range(0,len(file_)):
        file_name=file_[i]
        filepath = file_path + '/' + file_name
        temp = pd.read_csv(filepath,encoding='EUC-KR')
        temp=temp.loc[temp.나이>=65,]
        temp=temp[['대상연월','도착시간','출발 행정동 코드','도착 행정동 코드','성별','이동인구(합)']]
        data=pd.concat([data,temp])
        data=data.reset_index().drop('index',axis=1)
    return data


def 이상치탐색_1(df,column):
    
    # ESD 방식 이상치 index 담는 list_esd
    mean=np.mean(df[column])
    sd=np.std(df[column])
    minimum_esd=mean-3*sd
    maximum_esd=mean+3*sd
    mask_esd=(df[column]>=maximum_esd)|(df[column]<=minimum_esd)
    list_esd=list(df[mask_esd].index)

    return list_esd

def 이상치탐색_2(df,column):
    
    # MAD 방식 이상치 list_mad
    median=np.median(df[column])
    mad=np.sqrt((df[column]-median)**2)
    data_mi=0.6745*np.abs(df[column]-median)/mad
    list_mad=list(data_mi[data_mi>=3.5].index)
    return list_mad

def 이상치탐색_3(df,column):
    
    # 사분위수 방식 이상치 list_iqr
    q1=np.quantile(df[column],0.25)
    q3=np.quantile(df[column],0.75)
    iqr=q3-q1
    minimum_iqr=q1-1.5*iqr
    maximum_iqr=q3+1.5*iqr
    mask_iqr=(df[column]<=minimum_iqr) | (df[column]>=maximum_iqr)
    list_iqr=list(df[mask_iqr].index)
    
    return list_iqr
 

def 이상치제거_생활이동(df):
    temp=pd.DataFrame()
    for i in df['출발행정동'].unique():
        for j in df['도착행정동'].unique():
            mask=(df['출발행정동']==i)&(df['도착행정동']==j) 
            data=df.loc[mask,:]
        
            s1=set(이상치탐색_1(data,'이동인구'))
            s2=set(이상치탐색_2(data,'이동인구'))
            s3=set(이상치탐색_3(data,'이동인구'))
            
            result1=s1.intersection(s2)
            result2=s1.intersection(s3)
            result3=s2.intersection(s3)
            
            result=result1|result2|result3
            list_outlier=list(result)
            data=data.drop(list_outlier,axis=0)
            temp=pd.concat([temp,data])
            temp=temp.reset_index().drop('index',axis=1)
    return temp

data.info()


data['이동인구(합)']=data['이동인구(합)'].astype(float)
data2['이동인구(합)']=data2['이동인구(합)'].astype(float)


mask=(data['출발 행정동 코드']>=1101053)&(data['출발 행정동 코드']<=1125074)
data=data[mask]

data=data.reset_index().drop('index',axis=1)

mask2=(data2['출발 행정동 코드']>=1101053)&(data2['출발 행정동 코드']<=1125074)
data2=data2[mask2]

data2=data2.reset_index().drop('index',axis=1)


data3=pd.read_excel("./서울생활이동데이터_행정동코드_20210907.xlsx")

data3=data3[['읍면동','name']]

data2

data4=pd.merge(data,data3,how='left',left_on='출발 행정동 코드',right_on='읍면동')
data5=pd.merge(data2,data3,how='left',left_on='출발 행정동 코드',right_on='읍면동')

mask3=(data4['도착 행정동 코드']>=1101053)&(data4['도착 행정동 코드']<=1125074)
mask4=(data5['도착 행정동 코드']>=1101053)&(data5['도착 행정동 코드']<=1125074)

data4=data4[mask3]
data5=data5[mask4]

data4=data4.reset_index().drop('index',axis=1)
data5=data5.reset_index().drop('index',axis=1)

data4=data4.drop('읍면동',axis=1)
data5=data5.drop('읍면동',axis=1)


data4.columns=['대상연월','도착시간','출발코드','도착코드','성별','이동인구','출발행정동']
data5.columns=['대상연월','도착시간','출발코드','도착코드','성별','이동인구','출발행정동']

data4=pd.merge(data4,data3,how='left',left_on='도착코드',right_on='읍면동')
data5=pd.merge(data5,data3,how='left',left_on='도착코드',right_on='읍면동')

data4=data4.drop(['출발코드','도착코드','읍면동'],axis=1)
data5=data5.drop(['출발코드','도착코드','읍면동'],axis=1)

data4.columns=['대상연월','도착시간','성별','이동인구','출발행정동','도착행정동']
data5.columns=['대상연월','도착시간','성별','이동인구','출발행정동','도착행정동']


data6=data4.groupby(['대상연월','도착시간','출발행정동','도착행정동'])['이동인구'].sum()
data7=data5.groupby(['대상연월','도착시간','출발행정동','도착행정동'])['이동인구'].sum()

data8=pd.DataFrame(data6)

data8=data8.reset_index()

data9=pd.DataFrame(data7)

data9=data9.reset_index()


#################################################

data=생활이동_2021()

data.loc[data['이동인구(합)']=='*',:]
data['이동인구(합)']=data['이동인구(합)'].astype(float)
data.info()
data.head()

data2=pd.read_excel("./서울생활이동데이터_행정동코드_20210907.xlsx")
data3=pd.merge(data,data2,how='left',left_on='출발 행정동 코드',right_on='읍면동')
data3.columns=['대상연월','도착시간','출발코드','도착코드','성별','이동인구','출발행정동']
data3=pd.merge(data3,data2,how='left',left_on='도착코드',right_on='읍면동')
data3.columns=['대상연월','도착시간','성별','이동인구','출발행정동','도착행정동']





