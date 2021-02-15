import numpy as np
import InforceGenerator as ig
import LibDB
import time

def GetRandomRecords(cnt, startContNo):

    infGen = ig.InforceRecGenerator()
    premYrCase = [5,10,15,20] # 보험료납입기간 분포
    premYrProb = [0.1, 0.3, 0.3, 0.3] # 보험료납입기간 확률

    infs = []

    for i in range(cnt):

        inf = ig.InforceRec()
        
        inf.ContNo = startContNo + i
        inf.Sex = np.random.binomial(1, 0.4)    
        inf.ProdCode = round(np.random.uniform(0, 15)/1)
        inf.ProdSeg = "Annuity" if inf.ProdCode < 8 else "Life"
        inf.ContAge = infGen.GetContAge(inf)
        inf.PremYr = np.random.choice(premYrCase, p=premYrProb)
        inf.StartAgeOfSomething = infGen.GetStartAgeOfSomething(inf)
        inf.ElapsedMth = infGen.GetElapsedMth(inf)
        prem, contAmt = infGen.GetPremAndContAmt(inf)
        inf.Prem = prem
        inf.ContAmt = contAmt

        inf.AccumPrem = min(inf.PremYr * 12, inf.ElapsedMth) * inf.Prem
        
        moneyness = infGen.GetMoneyness(inf)
        inf.SumFund = round(moneyness * inf.AccumPrem/1)

        inf.FundAllo01 = min(20, max(5, round(np.random.normal(10, 5)/5) * 5))
        inf.FundAllo02 = min(70, max(5, round(np.random.normal(50, 30)/5) * 5))
        inf.FundAllo03 = 100 - inf.FundAllo01 - inf.FundAllo02
        
        mmf = inf.AccumPrem * inf.FundAllo01 / 100
        inf.FundVal01 = min(inf.SumFund, max(0, round(np.random.normal(mmf, mmf*0.05)/1)))
        fi = inf.AccumPrem * inf.FundAllo02 / 100
        inf.FundVal02 = min(inf.SumFund - inf.FundVal01, max(0, round(np.random.normal(fi, fi*0.1)/1)))
        inf.FundVal03 = inf.SumFund - inf.FundVal01 - inf.FundVal02

        infs.append(inf)

    return infs


cnt = 1000
batchCnt = 100
startContNo = 1

for seq in range(7,8):
    infId = "T2012_Train_S" + str(seq)
    startContNo = 1

    for i in range(batchCnt):

        infs = GetRandomRecords(cnt, startContNo)
        
        arrInfs = []
        for seq in range(len(infs)):
            arrInfs.append([infId] + infs[seq].GetArr())

        dt = np.array(arrInfs)

        conn = LibDB.DbConnectorMS('kkhproj-db.czuxn57jn8hk.ap-northeast-2.rds.amazonaws.com', 'admin', 'kkh198400', 'proj')
        conn.Insert(dt, 'records')
        print('insert infs ' + infId + ' batch ' + str(i+1))
        
        startContNo += cnt


#import copy
#recNew = copy.deepcopy(rec)     
