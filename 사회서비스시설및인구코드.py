####################################


# 자료 import 및 export시 EUC-KR로 함.


####################################

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

# 각자 API KEY 설정.

gmaps_key='--'


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
        temp=temp[['기준일ID','시간대구분','자치구코드','남자65세부터69세생활인구수',
                   '남자70세이상생활인구수','여자65세부터69세생활인구수','여자70세이상생활인구수']]
        temp.columns=['기준일ID','시간대구분','자치구코드','남자65','남자70','여자65','여자70']
        temp['노인생활인구']=temp['남자65']+temp['남자70']+temp['여자65']+temp['여자70']       
        data=pd.concat([data,temp[['기준일ID','시간대구분','자치구코드','노인생활인구']]])
        data=data.reset_index().drop('index',axis=1)
    
    data=pd.merge(data,행정동코드,how='left',left_on='자치구코드',right_on='RESD_CD')
    data=data.drop('RESD_CD',axis=1)
    return data

data=자치구_2021()
data.loc[data['이동인구(합)']=='*',:]
data['이동인구(합)']=data['이동인구(합)'].astype(float)
data.info()
data.head()

data=서울이동인구_행정동코드(data)

data_생활인구=생활인구()

data_생활인구.info()

# data.to_csv("./생활이동인구.csv",encoding='EUC-KR')

# x 입력으로 시리즈를 받길 원함. n=3 3개씩 평균. 
def moving_avg(x, n=3):
    cumsum=np.cumsum(np.insert(x.values, len(x) ,[x[0],x[1]]))
    temp=(cumsum[n:]-cumsum[:-n])/float(n)
    return np.where(temp>np.quantile(x,0.25))



mov_data1=data.groupby('시간')['이동인구'].mean()
mov_data2=data.groupby('시간')['이동인구'].sum()

data_re=pd.read_csv("./생활이동인구.csv",encoding='EUC-KR')
data_re.info()
data_re.head()
data2=data_re.drop(['Unnamed: 0'],axis=1)

data2=data2.drop(['요일','이동유형','출발 시군구 코드','도착 시군구 코드'],axis=1)

data2.info()
data2.columns=['대상연월','시간','성별','나이','이동시간','이동인구','출발시군구','도착시군구']

data2=data2.groupby(['대상연월','시간','출발시군구','도착시군구'])['이동인구'].mean()
data2=pd.DataFrame(data2).reset_index()

mov_data1=data2.groupby('시간')['이동인구'].mean()
mov_data2=data2.groupby('시간')['이동인구'].sum()

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


# 그룹화를 하고 나니, 요일을 안남겨두고 sum 형식으로 가다보면 이게 이상치 탐색을 할 수가없음.
# 데이터의 개수가 시간대별로 월 개수만 남음. 

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

data_강남강남=data.loc[(data['출발시군구']=='강남구')&(data['도착시군구']=='강남구'),:]
data_강남강남.info()

### 다시 하기.

data_re=pd.read_csv("./생활이동인구.csv",encoding='EUC-KR')
data_re.info()
data_re.head()
data_re=data_re.loc[(data_re['도착시간']>=4)&(data_re['도착시간']<=22),:]
data_re=data_re.reset_index().drop('index',axis=1)
data.info()
data2=data_re.drop(['Unnamed: 0'],axis=1)

data2=data2.drop(['이동유형','출발 시군구 코드','도착 시군구 코드'],axis=1)

data2.info()
data2.columns=['대상연월','요일','시간','성별','나이','이동시간','이동인구','출발시군구','도착시군구']

data2.head()
data_group=data2.groupby(['대상연월','요일','시간','출발시군구','도착시군구'])['이동인구'].sum()
data_g=pd.DataFrame(data_group)

data=data_g.reset_index()



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
 

def 이상치제거_생활이동(df):
    temp=pd.DataFrame()
    for i in df['출발시군구'].unique():
        for j in df['도착시군구'].unique():
            mask=(df['출발시군구']==i)&(df['도착시군구']==j) 
            data=df.loc[mask,:]
        
            s1=set(이상치탐색1(data,'이동인구'))
            s2=set(이상치탐색2(data,'이동인구'))
            s3=set(이상치탐색3(data,'이동인구'))
            
            result1=s1.intersection(s2)
            result2=s1.intersection(s3)
            result3=s2.intersection(s3)
            
            result=result1|result2|result3
            list_outlier=list(result)
            data=data.drop(list_outlier,axis=0)
            temp=pd.concat([temp,data])
            temp=temp.reset_index().drop('index',axis=1)
    return temp


data3=이상치제거_생활이동(data)

data.info()

data3.info()

data3.head()

data_final=data3.groupby(['출발시군구','도착시군구'])['이동인구'].mean()
data_f=pd.DataFrame(data_final)

weight_data=data_f.reset_index()

weight_data.to_csv("./생활이동전처리데이터.csv",encoding='EUC-KR')

data=pd.read_csv("./생활이동전처리데이터.csv",encoding='EUC-KR')

data2=data_생활인구

data2.info()

data2=data2.loc[(data2['시간대구분']<=22)&(data2['시간대구분']>=4),:].reset_index().drop('index',axis=1)

data2.head()
data2.columns=['기준일','시간','자치구코드','생활인구','자치구']

temp=data2.loc[data2['자치구']=='강남구','생활인구'].reset_index().drop('index',axis=1)


temp['생활인구'].sort_values()

def 생활인구_자치구_분포(df):
    try:
        os.mkdir('./생활인구_자치구_분포')
    except:
        pass
    for i in df['자치구'].unique():
        temp=df.loc[df['자치구']==i,:'생활인구'].reset_index().drop('index',axis=1)
        plt.figure(figsize=(15,5))
        plt.hist(temp['생활인구'].sort_values())
        address="./생활인구_자치구_분포/"+i+".jpeg"
        plt.savefig(address)

생활인구_자치구_분포(data2)
# 분포가 왜도가 심한게 있음. 따라서 이상치 제거를 해야하는 명분이 있음.

# 자치구, 시간대별로 이상치 제거하고, 최종 결과를 4시~22시까지 평균을 내서 생활인구로 사용.

data2.info()

def 이상치제거_생활인구(df):
    temp=pd.DataFrame()
    for i in df['자치구'].unique():
        for j in df['시간'].unique():
            mask=(df['자치구']==i)&(df['시간']==j) 
            data=df.loc[mask,:]
        
            s1=set(이상치탐색1(data,'생활인구'))
            s2=set(이상치탐색2(data,'생활인구'))
            s3=set(이상치탐색3(data,'생활인구'))
            
            result1=s1.intersection(s2)
            result2=s1.intersection(s3)
            result3=s2.intersection(s3)
            
            result=result1|result2|result3
            list_outlier=list(result)
            data=data.drop(list_outlier,axis=0)
            temp=pd.concat([temp,data])
            temp=temp.reset_index().drop('index',axis=1)
    return temp

data3=이상치제거_생활인구(data2)
data3.info()

data4=data3.groupby(['자치구'])['생활인구'].mean()

data5=pd.DataFrame(data4)

data5.to_csv("./생활인구지표.csv",encoding='EUC-KR')


# def 시설이용률계산(df1):

# 데이터가 와야 계산 가능.    
    


## 빅캠 노인복지시설 위치정보 데이터
data=pd.read_csv("./TB_O_SSL_SC.txt",sep='|')
data=gpd.read_file("./TB_O_SSL_SC_2017/TB_O_SSL_SC_2017.shp")


# 가중치

data=pd.read_csv("./생활이동전처리데이터.csv",encoding='EUC-KR')

data=data.drop('Unnamed: 0',axis=1)

data

data_선호여가=pd.read_excel("./서울시 노인의 선호여가 활동(2019).xls",skiprows=22)
data_선호여가.columns=['기간','대분류','지역','운동_건강','노래_오락','지식교육','직업관련','여행','사회봉사','사교','전통','없음']

data_선호여가=data_선호여가.drop(['기간','대분류','지식교육','여행','사회봉사','전통','없음'],axis=1)

data_선호여가.info()

data.info()

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

        
dic_health=가중치계산(data_선호여가,'지역','운동_건강')
dic_work=가중치계산(data_선호여가,'지역','직업관련')
dic_social=가중치계산(data_선호여가,'지역','노래_오락')

data_경제=pd.read_excel("./서울시 기초연금 수급자 현황 통계.xls",header=1)

data_경제=data_경제[['자치구','계.2']]
data_경제.columns=['지역','기초연금수급자율']
dic_economic=가중치계산(data_경제,'지역','기초연금수급자율')

data_건강=pd.read_excel("./건강데이터.xlsx")

data_건강=data_건강[['시군구','조율']]
data_건강.columns=['시군구','건강의식']

dic_health=가중치계산(data_건강,'시군구','건강의식')        
        
data_시설=pd.read_csv("시설처리0919.csv",encoding='EUC-KR')

data_시설=data_시설.drop('Unnamed: 0',axis=1)

data_시설.loc[data_시설['시군구명']=='서울특별시',]
data_시설=data_시설.drop([364,673],axis=0).reset_index().drop('index',axis=1)


data_총개수=data_시설['시군구명'].value_counts()

data_시설.at[data_시설['시군구명']=='서울특별시','시군구명']='동작구'

data_시설.info()
data_시설.head()


data_시설['시설종류상세명(시설종류)'].unique()


data_시설종류=pd.DataFrame()
for i in data_시설['시군구명'].unique():
    data_시설종류=pd.concat([data_시설종류,data_시설.loc[data_시설['시군구명']==i,'시설종류상세명(시설종류)'].value_counts()],axis=1)

data_시설종류=data_시설종류.transpose()

data_시설종류.index=data_시설['시군구명'].unique()

dat=pd.read_csv("./ttt.csv",encoding='EUC-KR')

data_총개수=data_총개수.reset_index()
data_시설종류=data_시설종류.reset_index()

data_bulid=pd.merge(data_총개수,data_시설종류,how='left',left_on='index',right_on='index')

data_bulid.columns=['시군구명','총개수','노인의료복지시설','재가노인복지시설','노인기타','노인여가복지시설','노인일자리지원기관','노인주거복지시설']
dat=dat.drop('Unnamed: 0',axis=1)

data10=pd.merge(dat,data_bulid,how='left',left_on='자치구',right_on='시군구명')

data10.to_csv("./fianl.csv",encoding='EUC-KR')
