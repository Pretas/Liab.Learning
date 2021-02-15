import pandas as pd
import LibDB
from sklearn.model_selection import train_test_split
import LibUtils, LibEE

def GetXYBase(label):
    conn = LibDB.DbConnectorMS('kkhproj-db.czuxn57jn8hk.ap-northeast-2.rds.amazonaws.com', 'admin', 'kkh198400', 'proj')
    query = 'select * from proj_total where id =\'' + label + '\''
    dt = pd.DataFrame(conn.GetSqlResult(query), columns=GetColNames())
    #dt = conn.GetSqlResultOfDataFrame(query)
    #query = 'select top ' + str(cnt) + ' * from proj_total where id =\'' + label + '\' order by ROW_NUMBER() over (order by newid())'

    dt.drop(['ID'], axis=1, inplace=True)
    dt.drop(['Seq'], axis=1, inplace=True)
    dt.drop(['ProdSeg'], axis=1, inplace=True)
    
    y = pd.concat([dt['pv_fee'], dt['pv_claim']], axis=1)
    x = dt.drop(['pv_fee', 'pv_claim'], axis=1)

    return x, y

# scaling + onehot encoding
def GetXY_s_o(label):
    x,y = GetXYBase(label)
    
    # 스케일링
    cols_toScaling = ['ElapsedMth', 'ContAge', 'Sex', 'Prem', 'PremYr', 'AccumPrem', 'ContAmt', 'StartAge', 'SumFund', 'FundVal01', 'FundVal02', 'FundVal03', 'FundAllo01', 'FundAllo02', 'FundAllo03', 'IR01', 'IR02', 'IR03', 'IR04', 'IR05', 'IR06', 'IR07', 'IR08', 'IR09', 'IR10', 'IR11', 'IR12', 'IR13', 'IR14']
    model, x_s = LibUtils.ScaleStandard(x[cols_toScaling])

    # 원핫인코딩은 스케일링 하면 안됨
    cols_toOneHot = ['ProdCode']
    x_o = pd.get_dummies(x[cols_toOneHot], columns=cols_toOneHot, prefix='prd')

    x = pd.concat([x_s, x_o], axis=1)

    return x, y

# scaling
def GetXY_s(label):
    x,y = GetXYBase(label)

     # 스케일링
    cols_toScaling = ['ElapsedMth', 'ContAge', 'Sex', 'Prem', 'PremYr', 'AccumPrem', 'ContAmt', 'StartAge', 'SumFund', 'FundVal01', 'FundVal02', 'FundVal03', 'FundAllo01', 'FundAllo02', 'FundAllo03', 'IR01', 'IR02', 'IR03', 'IR04', 'IR05', 'IR06', 'IR07', 'IR08', 'IR09', 'IR10', 'IR11', 'IR12', 'IR13', 'IR14']
    model, x_s = LibUtils.ScaleStandard(x[cols_toScaling])
    
    cols_notScaled = ['ProdCode']

    x = pd.concat([x_s, x[cols_notScaled]], axis=1)

    return x, y

# one hot encoding
def GetXY_o(label):
    x,y = GetXYBase(label)
   
    # 원핫인코딩은 스케일링 하면 안됨
    cols_toOneHot = ['ProdCode']
    x = pd.get_dummies(x, columns=cols_toOneHot, prefix='prd')

    return x, y

def TrainingDataFinal(jobName):
    
    # 트레이닝
    x, y = GetXYBase(jobName)
    x = GetMoneyness(x)
    x = GetAttainedAge(x)
    x = GetIrReduction(x)
    x, embs = LibEE.GetXEmbApplied(3, x, y, ['ProdCode'])
    scaler, x = LibUtils.ScaleStandard(x)

    colsSelected = ['ElapsedMth', 'Sex', 'Prem', 'PremYr', 'AccumPrem', 'ContAmt', 'StartAge', 'FundAllo03', 'IR06', 'IR09', 'IR12', 'IR14', 'Moneyness', 'AttainedAge', 'ee_ProdCode_00', 'ee_ProdCode_01', 'ee_ProdCode_02']
    x = x[colsSelected]

    return x, y, embs, scaler

def TestDataFinal(jobName, embs, scaler):

    # 트레이닝
    x, y = GetXYBase(jobName)
    x = GetMoneyness(x)
    x = GetAttainedAge(x)
    x = GetIrReduction(x)
    x = LibEE.GetXofEmb(x, 'ProdCode', embs[0])
    x = pd.DataFrame(scaler.transform(x), index=x.index, columns=x.columns)
    colsSelected = ['ElapsedMth', 'Sex', 'Prem', 'PremYr', 'AccumPrem', 'ContAmt', 'StartAge', 'FundAllo03', 'IR06', 'IR09', 'IR12', 'IR14', 'Moneyness', 'AttainedAge', 'ee_ProdCode_00', 'ee_ProdCode_01', 'ee_ProdCode_02']
    x = x[colsSelected]

    return (x, y)


def GetOneHot(x, y):
    x = pd.get_dummies(x, columns=['ProdCode'], prefix='prd')
    return x, y

def GetScaled(x, y):
    # 스케일링
    cols_toScaling = ['ElapsedMth', 'ContAge', 'Sex', 'Prem', 'PremYr', 'AccumPrem', 'ContAmt', 'StartAge', 'SumFund', 'FundVal01', 'FundVal02', 'FundVal03', 'FundAllo01', 'FundAllo02', 'FundAllo03', 'IR01', 'IR02', 'IR03', 'IR04', 'IR05', 'IR06', 'IR07', 'IR08', 'IR09', 'IR10', 'IR11', 'IR12', 'IR13', 'IR14']
    model, x_s = LibUtils.ScaleStandard(x[cols_toScaling])
    


def GetColNames():
    return ['ID', 'Seq', 'ElapsedMth', 'ContAge', 'Sex', 'ProdSeg', 'ProdCode', 'Prem', 'PremYr', 'AccumPrem', 'ContAmt', 'StartAge', 'SumFund', 'FundVal01', 'FundVal02', 'FundVal03', 'FundAllo01', 'FundAllo02', 'FundAllo03', 'IR01', 'IR02', 'IR03', 'IR04', 'IR05', 'IR06', 'IR07', 'IR08', 'IR09', 'IR10', 'IR11', 'IR12', 'IR13', 'IR14', 'pv_fee', 'pv_claim']

from sklearn.model_selection import train_test_split

def GetSplited(x, y, foldCnt):
    list_x = []; list_y = []    

    if foldCnt==1:
        list_x.append(x); list_y.append(y) 
        return x, y
    
    r = 1/foldCnt
    for i in range(1, foldCnt+1):
        if(i<foldCnt):
            a = (1-r*i) / (1-r*(i-1))
            x, x_, y, y_ = train_test_split(x, y, test_size= 1.0 - round(a,10))
            list_x.append(x_); list_y.append(y_) 
        else:
            list_x.append(x); list_y.append(y)

    return list_x, list_y

def GetTrainTest(l_x, l_y, idx):    
    xTest = None; yTest = None
    xTrain = None; yTrain = None
    inityn = True

    for i in range(0, len(l_x)):
        xTemp = pd.DataFrame(l_x[i])
        yTemp = pd.DataFrame(l_y[i])

        if(i==idx):
            xTest = xTemp
            yTest = yTemp
        else:
            if inityn:
                xTrain = xTemp
                yTrain = yTemp
                inityn = False
            else:
                xTrain = pd.concat([xTrain, xTemp])    
                yTrain = pd.concat([yTrain, yTemp])

    return xTrain, xTest, yTrain, yTest    

import copy

def GetMoneyness(x):
    x_ = x.copy(True)
    x_['Moneyness'] = x_.apply(lambda row: row['SumFund']/row['AccumPrem']*100 if row['AccumPrem'] > 0 else 0, axis=1)
    x_['FundVal01'] = x_.apply(lambda row: row['FundVal01']/row['SumFund']*100 if row['SumFund'] > 0 else 0, axis=1)
    x_['FundVal02'] = x_.apply(lambda row: row['FundVal02']/row['SumFund']*100 if row['SumFund'] > 0 else 0, axis=1)
    x_['FundVal03'] = x_.apply(lambda row: row['FundVal03']/row['SumFund']*100 if row['SumFund'] > 0 else 0, axis=1)
    del x_['SumFund']
    return x_


def GetAttainedAge(x):
    x_ = x.copy(True)
    x_['AttainedAge'] = x_.apply(lambda row: row['ContAge'] + row['ElapsedMth']//12, axis=1)
    del x_['ContAge']
    return x_

def GetIrReduction(x):
    x_ = x.copy(True)
    cols = ['IR01','IR02','IR03','IR04','IR05',
        'IR07','IR08',
        'IR10','IR11','IR13']
    x_.drop(cols, inplace=True, axis=1)
    return x_






# def GetSplited(x, y, cvCnt):
#     xs = []
#     ys = []
#     r = 1/cvCnt;
#     a = 1.0;

#     for i in range(1,cvCnt+1):
#         if(i==cvCnt):
#             xs.append([x])
#             ys.append([y])
#         else:
#             a = (1-r*i) / (1-r*(i-1))
#             x, x_, y, y_ = train_test_split(x, y, test_size= 1.0 - round(a,2))
#             xs.append([x_])
#             ys.append([y_])
    
#     return xs, ys





# def GetXY2(label):
#     conn = LibDB.DbConnectorMS('kkhproj-db.czuxn57jn8hk.ap-northeast-2.rds.amazonaws.com', 'admin', 'kkh198400', 'proj')
#     query = 'select * from proj_total where id =\'' + label + '\''
#     dt = conn.GetSqlResultOfDataFrame(query)

#     dt.drop(['ID'], axis=1, inplace=True)
#     dt.drop(['Seq'], axis=1, inplace=True)
#     dt.drop(['ProdSeg'], axis=1, inplace=True)
    
#     xy = pd.get_dummies(dt, columns=['ProdCode'], prefix='prd')

#     y = pd.concat([xy['pv_fee'], xy['pv_claim']], axis=1)
#     x = xy.drop(['pv_fee', 'pv_claim'], axis=1)

#     return x, y



# def GetXY(jobName):        
#     # 런인포 가져오기
#     conn = LibDB.DbConnectorMS('kkhproj-db.czuxn57jn8hk.ap-northeast-2.rds.amazonaws.com', 'admin', 'kkh198400', 'proj')
#     query = 'select * from runinfo where id =\'' + jobName + '\''
#     runInfo = pd.DataFrame(conn.GetSqlResult(query))
#     infId = runInfo['Arguments'][0].split(' ')[0]
#     scenId = runInfo['Arguments'][0].split(' ')[1]

#     # 보유계약 불러오기
#     query = 'select * from records where id =\'' + infId + '\' order by contno'
#     infs = conn.GetSqlResultOfDataFrame(query)

#     # 경제적가정(시나리오) 불러오기
#     query = 'select * from ScenSource where id =\'' + scenId + '\''
#     scenSource = conn.GetSqlResultOfDataFrame(query)

#     # 결과 불러오기
#     query = 'select polSeq, pv_fee, pv_claim from proj_result where job_name =\'' + jobName + '\' order by polseq'
#     res = conn.GetSqlResultOfDataFrame(query)
    
#     return infs, scenSource, res

# def GetProcessedProjData(jobName):
#     infs, scenSource, y = GetXY(jobName)
    
#     infs.drop(['ID'], axis=1, inplace=True)
#     infs.drop(['ContNo'], axis=1, inplace=True)
#     infs.drop(['ProdSeg'], axis=1, inplace=True)
#     scenSource.drop(['ID'], axis=1, inplace=True)
#     scenSource.drop(['EQ_Vol'], axis=1, inplace=True)
#     scenSource.drop(['HW_a'], axis=1, inplace=True)
#     scenSource.drop(['HW_sigma'], axis=1, inplace=True)

#     # 결합하기
#     x = pd.concat([infs, scenSource], axis=1, join='outer')

#     # NaN 채우기
#     cols_scenSource = scenSource.columns
#     for colName in cols_scenSource:
#         x[colName].fillna(x[colName][0], inplace=True)

#     y_new = pd.concat([y["pv_fee"], y["pv_claim"]], axis=1)

#     return pd.concat([x, y_new], axis=1)

# def GetProcessedProjData2(jobNames):
#     xy = GetProcessedProjData(jobNames[0])
#     print(len(xy))

#     for i in range(1, len(jobNames)):
#         xyTemp = GetProcessedProjData(jobNames[i])
#         xy = pd.concat([xy, xyTemp])
#         print(len(xy))

#     xy_shuffled = xy.sample(frac=1).reset_index(drop=True)

#     y = pd.concat([xy_shuffled['pv_fee'], xy_shuffled['pv_claim']], axis=1)
#     xy_shuffled.drop(['pv_fee'], axis=1, inplace=True)
#     xy_shuffled.drop(['pv_claim'], axis=1, inplace=True)
    
#     return xy_shuffled, y

