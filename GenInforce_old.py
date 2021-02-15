import numpy
import InforceGenerator as ig
import LibDB
import time

def GenerateInforce(dbId, prodRange):

    ########### 작업순서 ############
    #     (1)성별 
    # --> (2)상품
    # --> (3)가입나이
    # --> (4)납입기간
    # --> (3)보험료&가입금액 : (2)가 선행되어야함
    # --> (5)연금/증액 시작나이 : (2),(3),(4)가 선행되어야함
    # --> (6)경과년도: (4),(5)가 선행되어야함
    # --> (7)Moneyness : (2),(6)가 선행되어야함
    # --> (8)적립금의 펀드별금액 : (7)가 선행되어야함
    # --> (9)보험료의 펀드별 투입비율 

    infGen = ig.InforceRecGenerator()
    infs = [ig.InforceRec()] # 시작점

    # 성별(남자0, 여자1)
    infs = infGen.GetInforceBySex(infs, [0,1])
    print(f'<<<<< 성별 인포스 생성완료 : {len(infs)}개')

    # 상품(16개)
    for prodCode in prodRange:

        # 상품(16개), 보험료 세팅
        infsOneProd = infGen.GetInforceByProduct(infs, prodCode)
        print(f'<<<<< 상품코드 {prodCode} 인포스 생성완료 : {len(infsOneProd)}개')
        
        # 가입나이별        
        step = 5
        infsOneProd = infGen.GetInforceByContAge(infsOneProd, prodCode, step)
        print(f'<<<<< 가입나이별 인포스 생성완료 : {len(infsOneProd)}개')
       
        # 보험료납입기간(5,10,15,20년), 최대 70세까지
        최소보험료납입기간 = 5
        최대보험료납입기간 = 20
        최대보험료납입나이 = 70
        step = 5
        infsOneProd = infGen.GetInforceByPremPrd(infsOneProd, 최소보험료납입기간, 최대보험료납입기간, 최대보험료납입나이, step)
        print(f'<<<<< 보험료납입기간별 인포스 생성완료 : {len(infs)}개')
        
        # 보험료 및 가입금액 세팅
        infsOneProd = infGen.GetInforceByPremAndContAmt(infsOneProd)
        print(f'<<<<< 보험료 & 가입금액별 인포스 생성완료 : {len(infs)}개')

        # 연금개시나이(Annuity), 보험금체증나이(Life-Increasing)
        step = 5
        infsOneProd = infGen.GetInforceByStartAgeOfSomething(infsOneProd, step)
        print(f'<<<<< 연금개시나이 & 사망보험금체증나이 별 인포스 생성완료 : {len(infsOneProd)}개')

        contNoNow = 1
        
        최소펀드비율 = 0.1
        최대펀드비율 = 0.8
        step_fundAllo = 0.2

        # 프로젝션 시작시 경과년도 = 신계약 
        isNewBiz = True
        step = 5
        infsOneProd_NB = infGen.GetInforceByElapsedYr(infsOneProd, isNewBiz, step)
        print(f'<<<<< 신계약 인포스 생성완료 : {len(infsOneProd_NB)}개')
        
        for i_fund1Proportion in ig.GetNumpyArr(최소펀드비율, 최대펀드비율, step_fundAllo):

            # 보험료의 펀드별 투입비율
            infsOneProd_NB = infGen.GetInforceByPremAllo(infsOneProd_NB, i_fund1Proportion, 최소펀드비율, 최대펀드비율, step_fundAllo)
        
            # 디비입력
            dbId2 = dbId + '_' + str(prodCode).zfill(2)
            InsertToDB(dbId2, infsOneProd_NB, 0, 0, i_fund1Proportion, contNoNow)
            contNoNow += (len(infsOneProd_NB) + 1)
         


        # 프로젝션 시작시 경과년도 = 보유계약
        isNewBiz = False
        infsOneProd_IB = infGen.GetInforceByElapsedYr(infsOneProd, isNewBiz, step)
        print(f'<<<<< 보유계약(경과기간 0이상) 인포스 생성완료 : {len(infsOneProd_IB)}개')
       
        sMoneyness = 0.5
        eMoneyness = 3.0
        step_moneyness = 0.5

        for money in ig.GetNumpyArr(sMoneyness, eMoneyness, step_moneyness):
          
            infsTemp0 = infGen.GetInforceByMoneyness(infsOneProd_IB, money)

            for i_fund1Proportion in ig.GetNumpyArr(최소펀드비율, 최대펀드비율, step_fundAllo):
                
                # 적립금을 펀드에 배분
                infsTemp1 = infGen.GetInforceByAccountValueAllo(infsTemp0, i_fund1Proportion, 최소펀드비율, 최대펀드비율, step_fundAllo)

                for j_fund1Proportion in ig.GetNumpyArr(최소펀드비율, 최대펀드비율, step_fundAllo):

                    # 보험료의 펀드별 투입비율
                    infsTemp2 = infGen.GetInforceByPremAllo(infsTemp1, j_fund1Proportion, 최소펀드비율, 최대펀드비율, step_fundAllo)

                    # 디비입력
                    dbId2 = dbId + '_' + str(prodCode).zfill(2)
                    InsertToDB(dbId2, infsTemp2, money, i_fund1Proportion, j_fund1Proportion, contNoNow)
                    contNoNow += (len(infsTemp2) + 1)


def DeleteDB(dbId):
    query = f"delete from records where id like '{dbId}%';"

    addr = 'localhost'
    id = 'root'
    pw = '3355'
    dbName = 'proj'

    conn = LibDB.DbConnector(addr, id, pw, dbName)
    conn.ExecuteSQL(query)


def InsertToDB(dbId, infs, i,j,k, sContNo):
        
    print(f'<<<<< 성별 {infs[0].Sex}, 납기 {infs[0].PremYr}, 상품코드 {infs[0].ProdCode}')
    print(f'      가입나이 {infs[0].ContAge}, 특정나이 {infs[0].StartAgeOfSomething}, 경과기간 {infs[0].ElapsedMth/12}')
    print(f'      Moneyness {int(i*100)}, 펀드1 적립금 비중 {int(j*100)}, 펀드1 보험료투입비율 {int(k*100)} 조건의')                    
    print(f'      {len(infs)}개의 인포스 생성완료, 디비입력 시작 ContNo시작 : {sContNo}')
    
    addr = 'localhost'
    id = 'root'
    pw = '3355'
    dbName = 'proj'

    conn = LibDB.DbConnector(addr, id, pw, dbName)

    arrInfs = []
    for seq in range(len(infs)):
        infs[seq].ContNo = sContNo + seq        
        arrInfs.append([dbId] + infs[seq].GetArr())

    dt = numpy.array(arrInfs)
    
    conn.Insert(dt, 'records')

    
    timeNow = time.strftime(r'%Y-%m-%d %p%I:%M', time.localtime(time.time()))
    print(f'      디비 입력완료! { timeNow }')


prodRange = range(4, 8)
GenerateInforce('MP2011', prodRange)
