# !pip install pymysql
# !pip install pymssql

import LibData
import LibUtils
import LibML
import LibFile

import pandas as pd
import numpy as np

jobName = '201216_Train_pilot'
# jobName = '201216_Train_split1'
x, y = LibData.GetXY_s_o(jobName)

# ov 컬럼 생성
ovName = 'pv_ov'
y[ovName] = y.apply(lambda line: line['pv_fee'] - line['pv_claim'], axis=1)

rf = LibML.RandomForestDefault(len(x.columns))
xgb = LibML.XGBoostDefault()


# 각각
print(LibML.GetScoresHoldOut(x,y,rf,0.2), LibML.GetScoresHoldOut(x,y,xgb,0.2))

# 한번에
from xgboost import XGBRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

x, x_, y, y_ = train_test_split(x, y, test_size=0.2)

rf.fit(x,y[ovName])
pred_ov = pd.Series(rf.predict(x_), index=x_.index)
scoresRF = LibUtils.GetScores(y_[ovName], pred_ov)

xgb.fit(x,y[ovName])
pred_ov = pd.Series(xgb.predict(x_), index=x_.index)
scoresXGB = LibUtils.GetScores(y_[ovName], pred_ov)

print(scoresRF, scoresXGB)

a=1
