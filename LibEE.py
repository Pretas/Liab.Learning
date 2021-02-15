import pandas as pd
import numpy as np
import LibData
import LibUtils
import LibML
import LibFile


# 범주형 변수를 수치형 변수로 바꿈
def GetNumerical(dtFrom, varName):
    dt = dtFrom.copy(True)
    rowNames = np.sort(dt[varName].unique())
    numbers = np.arange(len(rowNames))
    mapping = pd.Series(numbers, index=rowNames)
    dt[varName] = dt.apply(lambda row: mapping[row[varName]], axis=1)
    return dt


# 개수만큼 전환하여 입력
def GetCardinailty(dt, varName):
    return len(dt[varName].unique())

from tensorflow.keras.layers import Input, Embedding, Dense, Reshape, Concatenate, Flatten
from tensorflow.keras.models import Model


# 임베딩 레이어 생성
def GetEmbeddingLayer(input_layer, info):
    name = info[0]; cardi = info[1]; dim = info[2]
    emb_layer = Embedding(cardi, dim, name='emb_' + name)(input_layer)
    emb_layer = Flatten()(emb_layer)
    return emb_layer


# 임베딩학습을 위한 신경망모델 생성
def GetLayers(emb_info):
    input_layers = []
    emb_layers = []

    # input_layer, emb_layer 만들기
    for i in range(len(emb_info)):
        input_layer = Input(shape=(1,))
        emb_layer = GetEmbeddingLayer(input_layer, emb_info[i])
        input_layers.append(input_layer)
        emb_layers.append(emb_layer)

    # output_layer 만들기
    if len(emb_info)==1:
        output_layer = Dense(32, activation='relu')(emb_layers[0])
    else:
        output_layer = Concatenate()(emb_layers)
        output_layer = Dense(32, activation='relu')(output_layer)

    output_layer = Dense(16, activation='relu')(output_layer)
    output_layer = Dense(1)(output_layer)

    model = Model(inputs=input_layers, outputs=output_layer)
    model.compile(optimizer = 'adam', loss='mse')

    #model.summary()

    return model


# 임베딩학습을 위한 신경망모델을 학습
def GetFitted(x, y, emb_info, model):
    from tensorflow.keras.callbacks import EarlyStopping
    import numpy as np

    early_stop = EarlyStopping(monitor='loss', patience=10)

    x_emb = [np.array(x[info[0]]) for i, info in enumerate(emb_info)]
    y_emb = [np.array(y['pv_claim'])]

    model.fit(x=x_emb, y=y_emb, epochs=100, callbacks=[early_stop], verbose=0)

    return model


# 임베딩 매핑테이블 반환
def GetEmbTable(md, info):

    colName = info[0]; cardi = info[1]; dim = info[2]
    
    keys = pd.DataFrame(range(0, cardi), columns = [colName])
    
    colNames_New = ['ee_'+colName+'_'+ str(i).zfill(2) for i in np.arange(0, dim)]    
    w = md.get_layer('emb_' + colName).get_weights()[0]
    w = pd.DataFrame(w, columns=colNames_New)
    
    mapping = pd.concat([keys, w], axis=1)
    return mapping


# 임베딩 매핑 테이블을 적용(기존컬럼 삭제)
def GetXofEmb(dtFrom, colName, emb_table):
    dt = dtFrom.copy(True)    
    dt = pd.merge(dt, emb_table, on=colName, how='left')
    dt = dt.drop(columns=[colName])
    return dt


from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor


# 엔티티임베딩 적용 전과정  
def GetXEmbApplied(maxDim, x, y, vars):

     # [컬럼이름, 카테고리수, 임베딩차원] 으로 인포테이블 만듬
    emb_info = [(col, GetCardinailty(x, col), 
        min(maxDim, (GetCardinailty(x, col)+1)//2)) for col in vars]

    # 임베딩학습을 위한 레이어만들기
    model = GetLayers(emb_info)

    # 임베딩 학습
    model = GetFitted(x, y, emb_info, model)

    embs = []
    # 임베딩 적용된 x 만들기
    for i, info in enumerate(emb_info):
        emb = GetEmbTable(model, info)
        embs.append(emb)
        x = GetXofEmb(x, info[0], emb)

    return x, embs


# 상호작용항 생성
def GetXIntersected(xBase, cols, newColName, delOrgCols=False):
    x = xBase.copy(True)
        
    x[newColName] = x.apply(lambda row: '_'.join(str(row[col]) for col in cols), axis=1)
    x = GetNumerical(x, newColName)

    if(delOrgCols):
        for col in cols: del x[col]

    return x


# 수치형 컬럼을 디지타이징
def GetDigitized(dtFrom, varName, binCnt, replace=True):
    dt = dtFrom.copy(True)
    startPoint = dt[varName].min() # 최소값
    endPoint = dt[varName].max() # 최대값
    bins = np.round(np.linspace(startPoint, endPoint, binCnt))

    name2 = ''
    if(replace): name2 = varName
    else: name2 = varName + '_'
    
    dt[name2] = np.digitize(dt[varName], bins)
    # Entity 값들은 0부터 시작해야함
    dt[name2] = np.array(dt[name2] - dt[name2].unique().min())

    return dt







## 특정컬럼을 0에서부터 시작하도록 바꿈
# def GetZeroStartX(dtFrom, varName):
#     dt = dtFrom.copy(True)
#     minVal = dt[varName].unique().min()
#     dt[varName] = np.array(dt[varName] - minVal)
#     return dt


# def GetX_Inter_EM_AA_old(xBase):
      
#     x = xBase.copy(True)

#     x['ElapsedMth_'] = x['ElapsedMth']
#     x = GetDigitized(x, 'ElapsedMth_', 20)

#     x['AttainedAge_'] = x['AttainedAge']
#     x = GetDigitized(x, 'AttainedAge_', 20)

#     x['Inter_EM_AA'] = x.apply(lambda row: str(int(row.ElapsedMth_)) + '_' + str(int(row.AttainedAge_)), axis=1)
#     del x['ElapsedMth_']
#     del x['AttainedAge_']
    
#     x = GetNumerical(x, 'Inter_EM_AA')
#     return x

# def Execute(maxDim, x, y, vars, tag):

#     x = GetXEmbApplied(maxDim, x, vars, tag)
    
#     maes = Learn(x,y)
#     summary = [str(sum(maes)/5), maes]
    
#     LibUtils.WriteNote('emb_rf700', tag, summary)
#     print('emb_rf700 ' + tag, summary)


# # 학습하여 스코어 반환
# def Learn(x,y):
#     l_x, l_y = LibData.GetSplited(x,y,5)
#     model = RandomForestRegressor(n_estimators =700, max_features=26, min_samples_leaf=2)
#     preds = LibML.GetPredCV(l_x, l_y, model, 'pv_claim')
#     return LibML.GetMaesCV(l_y, preds, 'pv_claim')