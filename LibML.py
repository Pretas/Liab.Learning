import LibUtils
import LibData

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split

from sklearn.linear_model import Ridge, Lasso
from xgboost import XGBRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR

import datetime
import gc
import copy

# Cross-Validaton 평균 성적 반환
def GetScoresCV(x, y, model, cvCnt):
    if cvCnt==1:
        print('no cvCnt 1. error!!!')
        return None

    # fold만큼 데이터 분리
    l_x, l_y = LibData.GetSplited(x, y, cvCnt)
    list_scores = []

    # fold만큼 iteration
    for i in range(0, cvCnt):

        # 학습
        xTrain, xTest, yTrain, yTest = LibData.GetTrainTest(l_x, l_y, i)
        print('start learning ' + str(i+1) + ' ' 
            + datetime.datetime.now().strftime('%Y-%m-%d %H:%M'), end='... ')        
        
        # 학습 & 스코어(MAE, MAPE, R2)
        pred = GetPredBase(xTrain, yTrain, xTest, model)        
        scores = GetScoresOV(yTest, pred)
        list_scores.append(scores)
        
        print(scores, end='... ')
        print('end learning ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
        
    # 평균 스코어 반환
    list_scores = np.array(list_scores)
    avgScores = [round(np.average(list_scores[:,0]),2),
        round(np.average(list_scores[:,1]),4),
        round(np.average(list_scores[:,2]),4)]
    
    return avgScores


# HoldOut의 스코어 
def GetScoresHoldOut(x, y, model, testRatio):
    x, x_, y, y_ = train_test_split(x, y, test_size=testRatio)
    pred = GetPredBase(x, y, x_, model)
    return GetScoresOV(y_, pred)


# 학습(Fee, Claim 별도)
def GetPredBase(x, y, xTest, model):

    # fee 학습 및 예측        
    model_fee = copy.deepcopy(model) 
    model_fee.fit(x, y['pv_fee'])
    pred_f = pd.Series(model_fee.predict(xTest), index=xTest.index)
    model_fee = None
    gc.collect()

    # claim 학습 및 예측
    model_claim = copy.deepcopy(model) 
    model_claim.fit(x, y['pv_claim'])
    pred_c = pd.Series(model_claim.predict(xTest), index=xTest.index)
    model_claim = None
    gc.collect()

    pred = pd.concat([pred_f, pred_c], axis=1)
    pred.columns=['pv_fee', 'pv_claim']
    return pred


# 스코어 반환(MAE, MAPE, R2)
def GetScoresOV(y, pred):

    pred.columns = ['pv_fee', 'pv_claim']
    pred.pv_fee = pred.apply(lambda row: 0.0 if row.pv_fee < 0.0 else row.pv_fee, axis=1)
    pred.pv_claim = pred.apply(lambda row: 0.0 if row.pv_claim < 0.0 else row.pv_claim, axis=1)
    
    # ov값 생성
    pred_ov = pred.apply(lambda row: row['pv_fee'] - row['pv_claim'], axis=1)
    yTest_ov = y.apply(lambda row: row['pv_fee'] - row['pv_claim'], axis=1)
    
    # 스코어 가져오기
    s = LibUtils.GetScores(yTest_ov, pred_ov)
    
    pred = None
    yTest_ov = None
    gc.collect()

    return s






def GetMaesCV(reals, preds, yLabel):
    cvCnt = len(preds)
    maes = []
    for i in range(0, cvCnt):
        real = reals[i]
        pred = preds[i]
        maes.append(mean_absolute_error(real[yLabel], pred))
    
    return maes

def GetMinZero(arrs):
    cvCnt = len(arrs)
    arrs2 = []
    for i in range(0, cvCnt):
        arrs2.append(arrs[i].apply(lambda row: 0.0 if row < 0.0 else row))
        
    return arrs2

def GetDeduct(arrs1, arrs2):
    cvCnt = len(arrs1)
    arrs3 = []
    for i in range(0, cvCnt):
        cc = pd.concat([arrs1[i], arrs2[i]], axis=1)
        cc.columns = ['pv_fee', 'pv_claim']
        cc['pv_ov'] = cc.apply(lambda row: row['pv_fee'] - row['pv_claim'], axis=1)
        arrs3.append(cc['pv_ov'])
        
    return arrs3

def XGBoostDefault():
    model = XGBRegressor(gamma=0,
    learning_rate=0.1,
    max_depth=5,
    min_child_weight=1,
    n_estimators=1000,    
    subsample=0.8,
    nthread=2, objective = 'reg:squarederror')
    
    return model

def XGBoostTuned():
    model = XGBRegressor(gamma = 0.00898,
                        learning_rate=0.01728,
                        max_depth=11,
                        min_child_weight=1,
                        n_estimators=4511,
                        subsample=0.32,
                        nthread=2, objective = 'reg:squarederror')
    return model

def RandomForestDefault(featureCnt):
    # model = RandomForestRegressor(n_estimators = 700, max_features = min(25, featureCnt), min_samples_leaf = 2)
    model = RandomForestRegressor()
    return model

def RandomForestTuned(featureCnt):    
    model = RandomForestRegressor(n_estimators = 1002, max_features = featureCnt, min_samples_leaf = 1)
    return model


# # 모델 훈련 & 예측값
# def GetAvgMae(l_x, l_y, model, yLabel):
#     cvCnt = len(l_x)
#     maes = []
#     for i in range(0, cvCnt):
#         xTrain, xTest, yTrain, yTest = LibData.GetTrainTest(l_x, l_y, i)
#         model.fit(xTrain, yTrain[yLabel])
#         y_pred= model.predict(xTest)
#         maes.append(mean_absolute_error(yTest[yLabel], y_pred))
    
#     return sum(maes)/cvCnt    


# # 모델 훈련 & 예측값
# def GetPredCV(l_x, l_y, model, yLabel):
#     cvCnt = len(l_x)
#     preds = []
#     for i in range(0, cvCnt):
#         xTrain, xTest, yTrain, yTest = LibData.GetTrainTest(l_x, l_y, i)
#         print('start learning ' + str(i+1) + ' ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M'), end='... ')
#         model.fit(xTrain, yTrain[yLabel])        
#         y_pred = pd.Series(model.predict(xTest), index=yTest.index)
#         print('end learning ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
#         preds.append(y_pred)
    
#     return preds
