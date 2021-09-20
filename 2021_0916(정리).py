
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

data_자치구06.head()

def 생활인구():
    file_=os.listdir("./생활인구 - 자치구/")
    file_path="./생활인구 - 자치구/"
    data=pd.DataFrame()
    행정동코드=pd.read_excel("./행정동코드_매핑정보_20200325.xlsx",sheet_name="유입지코드")
    행정동코드=행정동코드[['RESD_CD','RESC_CT_NM']]
    
    for i in range(0,len(file_)):
        file_name=file_[i]
        filepath = file_path + '/' + file_name
        temp = pd.read_csv(filepath,encoding='EUC-KR')
        temp=temp[['기준일ID','시간대구분','자치구코드','남자60세부터64세생활인구수','남자65세부터69세생활인구수','남자70세이상생활인구수','여자60세부터64세생활인구수','여자65세부터69세생활인구수','여자70세이상생활인구수']]
        temp.columns=['기준일ID','시간대구분','자치구코드','남자60','남자65','남자70','여자60','여자65','여자70']
        temp['노인생활인구']=temp['남자60']+temp['남자65']+temp['남자70']+temp['여자60']+temp['여자65']+temp['여자70']        
        data=pd.concat([data,temp[['기준일ID','시간대구분','자치구코드','노인생활인구']]])
        data=data.reset_index().drop('index',axis=1)
    
    data=pd.merge(data,행정동코드,how='left',left_on='자치구코드',right_on='RESD_CD')
    data=data.drop('RESD_CD',axis=1)
    return data


data_생활인구=생활인구()

data_생활인구.info()

data_자치구06.info()

def 서울이동인구_행정동코드(df):
    행정동코드=pd.read_excel("./서울생활이동데이터_자치구코드_20210907.xlsx",sheet_name="Sheet1")
    행정동코드=행정동코드.drop(['시도','full name'],axis=1)
    name_list=df.columns
    temp=pd.merge(df,행정동코드,how='left',left_on="출발 시군구 코드",right_on="시군구")
    temp=pd.merge(temp,행정동코드,how='left',left_on="도착 시군구 코드",right_on="시군구")
    temp.columns=list(name_list)+['시군구1','출발','시군구2','도착']
    temp=temp.drop(["시군구1","시군구2"],axis=1)    
    
    return temp

data2=서울이동인구_행정동코드(data_자치구06)
data3=서울이동인구_행정동코드(data_자치구07)

data2=data2.loc[(data2['도착 시군구 코드']<=11250)&(data2['출발 시군구 코드']<=11250),:].reset_index().drop('index',axis=1)
data3=data3.loc[(data3['도착 시군구 코드']<=11250)&(data3['출발 시군구 코드']<=11250),:].reset_index().drop('index',axis=1)

data2.head()


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

#error=[]
#for check,gu,nline in zip(data2['시설주소API'],data2['시군구명'],range(len(data2['시설주소API']))):
#    check_error=re.search(str(gu),str(check))
#    if not check_error:
#        error.append(nline)
#        continue


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




data2=노인서비스시설병합()
data2=주소오류처리(data2)
data2=주소위도경도변환(data2)
data3=주소예외처리(data2)


def 인구데이터병합():

def 시설이용률계산(df1):
    
def 인구가중치계산(df):

def 이상치탐색(df):
    
    # ESD 방식 이상치 index 담는 list_esd
    mean=np.mean(df['생활인구'])
    sd=np.std(df['생활인구'])
    minimum_esd=mean+3*sd
    maximum_esd=mean-3*sd
    mask_esd=(df['생활인구']>=maximum_esd)&(df['생활인구']<=minimum_esd)
    list_esd=list(df[mask_esd].index)
    
    
    # isolation 방식 이상치 list_mad
    median=np.median(df['생활인구'])
    mad=np.sqrt((df['생활인구']-median)**2)
    data_mi=0.6745*np.abs(df['생활인구']-median)/mad
    list_mad=data_mi[data_mi>=3.5].index
    
    # 사분위수 방식 이상치 list_iqr
    q1=np.quantile(df['생활인구'],0.25)
    q3=np.quantile(df['생활인구'],0.75)
    iqr=q3-q1
    minimum_iqr=q1-1.5*iqr
    maximum_iqr=q3+1.5*iqr
    mask_iqr=(df['생활인구']<=minimum_iqr) & (df['생활인구']>=maximum_iqr)
    list_iqr=list(df[mask_iqr].index)
    
    
    # 3개 중 2개 이상 겹치는 인덱스에 한해 제거해서 최종 결과 list_outlier    
    s1=set(list_esd)
    s2=set(list_mad)
    s3=set(list_iqr)
    
    result1=s1.intersection(s2)
    result2=s1.intersection(s3)
    result3=s2.intersection(s3)
    
    result=result1|result2|result3
    list_outlier=list(result)
    
    return list_outlier


def 클러스터링1(df):
    
def 클러스터링2(df):
    
def 입지선정(df1,df2):

    
# 시각화 및 클러스터링 입지선정은 R로 할 수 있음. 거의 70%이상 R로 할 듯.
