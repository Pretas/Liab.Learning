import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import r2_score
import LibDB
import datetime
import pprint


def WriteNote(tag, tag2, obj):
    memo = pprint.pformat(obj, indent=4)
    memo = memo.replace("'", " ")
    timenow = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    dt = [[timenow, tag, tag2, memo.replace("'", " ")]]
    conn = LibDB.DbConnectorMS('kkhproj-db.czuxn57jn8hk.ap-northeast-2.rds.amazonaws.com', 'admin', 'kkh198400', 'proj')
    conn.Insert(dt, 'Note')



def GetScores(real, pred):
    mae = round(mean_absolute_error(real, pred), 2)    
    #mape = SymmetricMAPE(real, pred)
    mape = round(AdjMAPE(real, pred), 4)
    r2 = round(r2_score(real, pred), 4)
    return [mae, mape, r2]

def SymmetricMAPE(dtReal, dtPredicted):
    return 100/len(dtReal) * np.sum(2 * np.abs(dtPredicted - dtReal) / (np.abs(dtReal) + np.abs(dtPredicted)))

def AdjMAPE(dtReal, dtPredicted):
    pred = np.array(dtPredicted)
    real = np.array(dtReal)
    a = np.sum(np.abs(pred-real))
    b = np.sum(np.abs(real))
    return a/b

from sklearn.ensemble import RandomForestRegressor

def RFFit(xTrain, yTrain, xVal, yVal):
    # 베스트 : RandomForestRegressor(max_depth=15, min_samples_leaf=3, n_estimators=500)
    forest = RandomForestRegressor(n_estimators = 100, max_depth=15, min_samples_leaf=3)
    forest.fit(xTrain, yTrain)
    y_pred = pd.DataFrame(forest.predict(xVal))
    y_pred.index = yVal.index
    return forest, y_pred

import time

def ELoop():
    # 유지
    print("start empty loop.", end='')
    while True:
        time.sleep(60); print(".", end='') # 5초 슬립, press ctr+c to out




from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import MaxAbsScaler
from sklearn.preprocessing import RobustScaler

def ScaleStandard(train_data):        
    # 평균을 제거하고 데이터를 단위 분산으로 조정함. 이상치가 있으면 평균/분산에 영향이 많이 미침
    standardScaler = StandardScaler()
    standardScaler.fit(train_data)
    dt = standardScaler.transform(train_data)
    return standardScaler, pd.DataFrame(dt, index=train_data.index, columns=train_data.columns)

def ScaleMinMax(train_data):
    # 0~1로 변환, 이상치가 있으면 취약해짐
    minMaxScaler = MinMaxScaler()
    minMaxScaler.fit(train_data)
    dt = minMaxScaler.transform(train_data)
    return minMaxScaler, pd.DataFrame(dt, index=train_data.index, columns=train_data.columns)

def ScaleMaxAbs(train_data):
    # minMaxScaler와 유사 : -1 ~ 1사이에 값을 위치시킴
    maxAbsScaler = MaxAbsScaler()
    maxAbsScaler.fit(train_data)
    dt = maxAbsScaler.transform(train_data)
    return maxAbsScaler, pd.DataFrame(dt, index=train_data.index, columns=train_data.columns)

def ScaleRobust(train_data):
    # 중앙값(median)과 IQR(interquartile range)을 이용 --> 이상치에 강함
    robustScaler = RobustScaler()
    robustScaler.fit(train_data)
    dt = robustScaler.transform(train_data)
    return robustScaler, pd.DataFrame(dt, index=train_data.index, columns=train_data.columns)

    