
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

def 자치구_2021():
    file_=os.listdir("./생활이동_자치구/")
    path1="./생활이동_자치구/"
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
            temp=temp.loc[(temp['도착 시군구 코드']<=11250)&(temp['출발 시군구 코드']<=11250),:].reset_index().drop('index',axis=1)
            data=pd.concat([data,temp])
            data=data.reset_index().drop('index',axis=1)
    return data

def 서울이동인구_행정동코드(df):
    행정동코드=pd.read_excel("./서울생활이동데이터_자치구코드_20210907.xlsx",sheet_name="Sheet1")
    행정동코드=행정동코드.drop(['시도','full name'],axis=1)
    name_list=df.columns
    temp=pd.merge(df,행정동코드,how='left',left_on="출발 시군구 코드",right_on="시군구")
    temp=pd.merge(temp,행정동코드,how='left',left_on="도착 시군구 코드",right_on="시군구")
    temp.columns=list(name_list)+['시군구1','출발','시군구2','도착']
    temp=temp.drop(["시군구1","시군구2"],axis=1)    
    
    return temp


data=자치구_2021()
data.loc[data['이동인구(합)']=='*',:]
data['이동인구(합)']=data['이동인구(합)'].astype(float)
data.info()
data.head()

data2=서울이동인구_행정동코드(data)

data2.info()
data2.head()

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
        temp=temp[['기준일ID','시간대구분','자치구코드','남자60세부터64세생활인구수','남자65세부터69세생활인구수',
                   '남자70세이상생활인구수','여자60세부터64세생활인구수','여자65세부터69세생활인구수','여자70세이상생활인구수']]
        temp.columns=['기준일ID','시간대구분','자치구코드','남자60','남자65','남자70','여자60','여자65','여자70']
        temp['노인생활인구']=temp['남자60']+temp['남자65']+temp['남자70']+temp['여자60']+temp['여자65']+temp['여자70']        
        data=pd.concat([data,temp[['기준일ID','시간대구분','자치구코드','노인생활인구']]])
        data=data.reset_index().drop('index',axis=1)
    
    data=pd.merge(data,행정동코드,how='left',left_on='자치구코드',right_on='RESD_CD')
    data=data.drop('RESD_CD',axis=1)
    return data


data_생활인구=생활인구()

data_생활인구.info()
data=data2

data.to_csv("./생활이동인구.csv",encoding='EUC-KR')

data2.describe()

mov_data1=data2.groupby('도착시간')['이동인구(합)'].mean()
mov_data2=data2.groupby('도착시간')['이동인구(합)'].sum()


# x 입력으로 시리즈를 받길 원함. n=3 3개씩 평균. 
def moving_avg(x, n=3):
    cumsum=np.cumsum(np.insert(x.values, len(x) ,[x[0],x[1]]))
    temp=(cumsum[n:]-cumsum[:-n])/float(n)
    return np.where(temp>np.quantile(x,0.25))

moving_avg(mov_data1)
# 25% 이동량
#3 4,5,6,7,8,9,....,21,22시.

moving_avg(mov_data2,3)
#3 4,5,6,7,8,9, ... , 21,22시.
# 동일.

# 생활인구랑도 비교해볼 것.

data_생활인구.info()

mov_data3=data_생활인구.groupby('시간대구분')['노인생활인구'].mean()
mov_data4=data_생활인구.groupby('시간대구분')['노인생활인구'].sum()

plt.scatter(mov_data3.index,mov_data3.values)
plt.scatter(mov_data4.index,mov_data4.values)

moving_avg(mov_data3)
# 4시 부터 ~ 22시 까지. 

moving_avg(mov_data4)
# 4시 부터 ~ 22시 까지. 


## 두 경우 고려하여 포함관계인 4시부터 ~ 22시까지를 직접적인 생활 시간이라 규정
# 이동평균법을 사용하여 고려한 이 방식은 내가 임의로 q1보다 큰 거만 사용한다는
# 주관적인 개념이 들어가있는데, 이를 뒷받침할 근거나 다른 방법을 이용하는 것도 가능.
data=data2

data.info()

# 총 12065383 개


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




#data2=노인서비스시설병합()
#data2=주소오류처리(data2)
#data2=주소위도경도변환(data2)
#data2=주소예외처리(data2)

#data2.to_csv('./시설처리0919.csv',encoding='EUC-KR')


# 데이터는 결국 data, data_생활인구 data2 생성

data=data.loc[(data['도착시간']>=4)&(data['도착시간']<=22),:]
data=data.reset_index().drop('index',axis=1)
data.info()

data.head()

data=data.drop(['요일','이동유형'],axis=1)

data.columns=['대상연월','시간','출발','도착','성별','나이','이동시간','이동인구','출발시군구','도착시군구']
data=data.drop(['출발','도착'],axis=1)

data_group=data.groupby(['대상연월','시간','출발시군구','도착시군구'])['이동인구'].sum()

data_g=pd.DataFrame(data_group)

data=data_g.reset_index()

data

mov_data1=data.groupby('시간')['이동인구'].mean()
mov_data2=data.groupby('시간')['이동인구'].sum()

data_re=pd.read_csv("./생활이동인구.csv",encoding='EUC-KR')
data_re.info()
data_re.head()
data2=data_re.drop(['Unnamed: 0'],axis=1)

data2=data2.drop(['요일','이동유형','출발 시군구 코드','도착 시군구 코드'],axis=1)

data2.info()
data2.columns=['대상연월','시간','성별','나이','이동시간','이동인구','출발시군구','도착시군구']

data2=data2.groupby(['대상연월','시간','출발시군구','도착시군구'])['이동인구'].sum()
data2=pd.DataFrame(data2).reset_index()

mov_data1=data2.groupby('시간')['이동인구'].mean()
mov_data2=data2.groupby('시간')['이동인구'].sum()

moving_avg(mov_data1)
moving_avg(mov_data2)
## 3~22시

data2.head()


def 인구가중치계산(df):

def 시설이용률계산(df1):
    
    
# 이상치 탐색 알고리즘 문제가 생김
# 전체 4시~22시에서 이상치 제거가아닌 각각의 시간대에서 이상치를 제거해야할거같음.
# 내일 고쳐서 다시 작성할게요~!~
def 이상치탐색(df,column):
    
    # ESD 방식 이상치 index 담는 list_esd
    mean=np.mean(df[column])
    sd=np.std(df[column])
    minimum_esd=mean+3*sd
    maximum_esd=mean-3*sd
    mask_esd=(df[column]>=maximum_esd)&(df[column]<=minimum_esd)
    list_esd=list(df[mask_esd].index)
    
    
    # MAD 방식 이상치 list_mad
    median=np.median(df[column])
    mad=np.sqrt((df[column]-median)**2)
    data_mi=0.6745*np.abs(df[column]-median)/mad
    list_mad=data_mi[data_mi>=3.5].index
    
    # 사분위수 방식 이상치 list_iqr
    q1=np.quantile(df[column],0.25)
    q3=np.quantile(df[column],0.75)
    iqr=q3-q1
    minimum_iqr=q1-1.5*iqr
    maximum_iqr=q3+1.5*iqr
    mask_iqr=(df[column]<=minimum_iqr) & (df[column]>=maximum_iqr)
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

