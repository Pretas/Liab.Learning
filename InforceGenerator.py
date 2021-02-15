import numpy
import copy

class InforceRec:
    ContNo = ""
    ElapsedMth = 0
    ContAge = 0
    Sex = 0
    ProdSeg = ""
    ProdCode = 0
    Prem = 0.0
    PremYr = 0
    AccumPrem = 0.0
    ContAmt = 0.0
    StartAgeOfSomething = 0
    SumFund = 0.0
    FundVal01 = 0.0
    FundVal02 = 0.0
    FundVal03 = 0.0
    FundAllo01 = 0.0
    FundAllo02 = 0.0
    FundAllo03 = 0.0

    def GetArr(self):
        lst = []
        lst.append(self.ContNo)
        lst.append(self.ElapsedMth)
        lst.append(self.ContAge)
        lst.append(self.Sex)
        lst.append(self.ProdSeg)
        lst.append(self.ProdCode)
        lst.append(self.Prem)
        lst.append(self.PremYr)
        lst.append(self.AccumPrem)
        lst.append(self.ContAmt)
        lst.append(self.StartAgeOfSomething)
        lst.append(self.SumFund)
        lst.append(self.FundVal01)
        lst.append(self.FundVal02)
        lst.append(self.FundVal03)
        lst.append(self.FundAllo01)
        lst.append(self.FundAllo02)
        lst.append(self.FundAllo03)

        return lst


def GetNumpyArr(startV, endV, step):
    return numpy.arange(startV, endV + step * 0.1, step)

def GetArr(startV, endV, step):
    return range(startV, endV + 1, step)



EndAge = 100
SmallDouble = 0.0000000001


class InforceRecGenerator:

    def GetInforceBySex(self, records, rg):
        
        pListNew = []

        for rec in records:            
            for sex in rg:
                recNew = copy.deepcopy(rec)            
                recNew.Sex = sex
                pListNew.append(recNew)

        return pListNew


    def GetElapsedMth(self, rec):
        
        maxYr=0
        
        if rec.ProdCode < 4:
            maxYr = rec.StartAgeOfSomething - rec.ContAge - 1            
        else:
            maxYr = 30
        
        return min(maxYr, max(0, round(numpy.random.normal(10, 8)/1))) * 12        

    def GetInforceByPremPrd(self, records, *args):

        pListNew = []

        minPrd = args[0]
        maxPrd = args[1]
        maxAge = args[2]
        step = args[3]

        for rec in records:

            maxPrd2 = min(maxPrd, maxAge - rec.ContAge)

            for premPrd in GetArr(minPrd, maxPrd2, step):
                recNew = copy.deepcopy(rec)            
                recNew.PremYr = premPrd
                pListNew.append(recNew) 

        return pListNew
    
    def GetInforceByProduct(self, records, pCode):
        
        pListNew = []

        for rec in records:          
            recNew = copy.deepcopy(rec)         
            
            if pCode < 8:
                recNew.ProdSeg = "Annuity"                                    
            else:
                recNew.ProdSeg = "Life" 
            
            recNew.ProdCode = pCode
            
            pListNew.append(recNew)

        return pListNew

    def GetInforceByPremAndContAmt(self, records):
        
        pListNew = []

        for rec in records:          
            recNew = copy.deepcopy(rec)         
            
            prem, contAmt = GetPremAndContAmt(recNew)
            recNew.Prem = prem
            recNew.ContAmt = contAmt

            pListNew.append(recNew)

        return pListNew

    def GetPremAndContAmt(self, rec):

        prem = 0.0
        contAmt = 0.0

        if rec.ProdCode < 8:
                # 연금의 경우 일괄적으로 보험료는 100
                prem = 100  
        else:
            # 가입금액: 종신의 경우 일괄적으로 가입금액은 1000
            contAmt = 10000
            
            if rec.ProdCode < 12:
                # 일반형인 경우 가입금액의 50%로 나이에 따라 선형적으로 증가
                prem = 0.5 * contAmt * (1.0 + rec.ContAge/200.0) / (rec.PremYr * 12)
            else:
                # 체증형인 경우 가입금액의 55%로 나이에 따라 선형적으로 증가
                prem = 0.55 * contAmt * (1.0 + rec.ContAge/200.0) / (rec.PremYr * 12)
    
        return round(prem/1), contAmt

    def GetMoneyness(self, rec):
        
        invYield = 0.0
        if rec.ProdCode < 8:
            invYield = rec.ElapsedMth/12 * 0.02
        else:
            invYield = rec.ElapsedMth/12 * 0.01
        
        moneyness = numpy.random.normal(1.0 + invYield, invYield)
        moneyness = min(5.0, max(0.3, moneyness))
        return moneyness

    def GetInforceByContAge(self, records, *args):
        
        pListNew = []

        prodCode = args[0]
        step = args[1]

        # GLWB는 20~50 가능, 기타는 20~60 가능,
        minAge = 20
        maxAge = 60     
        if(prodCode >= 4 and prodCode <= 7):
            maxAge = 50

        for rec in records:            
            for age in GetArr(minAge, maxAge, step):
                recNew = copy.deepcopy(rec)  
                recNew.ContAge = age
                pListNew.append(recNew)

        return pListNew

    def GetContAge(self, rec):
 
        maxAge = 0

        if(rec.ProdCode <= 7):
            maxAge = 50
        else:
            maxAge = 60

        return round(numpy.random.uniform(20, maxAge)/1)

    # 상품타입 Annuity-Rop, Annuity-GLWB인 경우는 연금개시시점을 세팅
    # 상품타입 Life-Increasing인 경우는 사망보험금 체증시작나이 세팅    
    def GetInforceByStartAgeOfSomething(self, records, *args):
        
        step = args[0]        
        recListNew = []

        for rec in records:            
            
            # Ann, Life_Increasing 인 경우
            if rec.ProdCode < 8 or rec.ProdCode >= 12:
                
                # Ann_rop, Life_Increasing 인 경우
                # 가입연령 + max(10년, 납입기간) <= 특정나이 <= 70세
                if rec.ProdCode < 4 or rec.ProdCode >= 12:
                    sAge = rec.ContAge + max(10, rec.PremYr)
                    eAge = 70
                # ann_glwb 인 경우
                # max(가입나이+30년, 65) <= 특정나이 <= 80세
                else:    
                    sAge = max(rec.ContAge + 30, 65)
                    eAge = 80
                
                for startAge in GetArr(sAge, eAge, step):
                    recNew = copy.deepcopy(rec)
                    recNew.StartAgeOfSomething = startAge
                    recListNew.append(recNew)
                    
            # life_fixed 인 경우
            else:
                recNew = copy.deepcopy(rec)
                recListNew.append(recNew)

        return recListNew

    

    def GetStartAgeOfSomething(self, rec):

        minAge=0
        maxAge=0

        if(rec.ProdCode <= 7):
            minAge = rec.ContAge + max(rec.PremYr, 10)
            maxAge = min(minAge + 20, 70)
        elif (rec.ProdCode >= 12):
            minAge = rec.ContAge + max(rec.PremYr, 10)
            maxAge = min(minAge + 20, 80)
        
        return min(maxAge, max(minAge, round(numpy.random.normal((minAge+maxAge)/2, 10)/1)))


    def GetInforceByElapsedYr(self, records, isZero, step):

        recListNew = []

        for rec in records:
            
            if isZero:
                recNew = copy.deepcopy(rec)
                recNew.ElapsedMth = 0
                recListNew.append(recNew)
            else:
                rg = []
                # 상품타입 Annuity-Rop인 경우는 연금개시시점까지
                if rec.ProdCode < 4:
                    rg = GetArr(step, rec.StartAgeOfSomething - rec.ContAge, step)
                # 기타 상품이면 종국연령(100세)까지
                else:
                    rg = GetArr(step, EndAge - rec.ContAge, step)

                for eYr in rg:
                    recNew = copy.deepcopy(rec)
                    recNew.ElapsedMth = eYr * 12
                    recListNew.append(recNew)

        return recListNew

    def GetInforceByMoneyness(self, records, moneyness):

        recListNew = []
                
        for rec in records:

            # 이미 납입한 보험료 계산
            accumPrem = min(rec.PremYr * 12, rec.ElapsedMth) * rec.Prem
           
            if rec.ElapsedMth > 0 and accumPrem > SmallDouble:            
                accountValueByFund = round((accumPrem * moneyness) / 3.0, 0)
                recNew = copy.deepcopy(rec)
                recNew.FundVal01 = accountValueByFund
                recNew.FundVal02 = accountValueByFund
                recNew.FundVal03 = accountValueByFund                
                recListNew.append(recNew)
            else:
                recNew = copy.deepcopy(rec)
                recListNew.append(recNew)

        return recListNew

    def GetInforceByAccountValueAllo(self, records, *args):

        recListNew = []

        f1Proportion = args[0]
        sProp = args[1]
        eProp = args[2]
        step = args[3]

        for rec in records:

            # 현재 적립금            
            accountValue = rec.FundVal01 + rec.FundVal02 + rec.FundVal03
          
            if accountValue > SmallDouble:
                fv01 = int(f1Proportion * accountValue)                
                residual = 1.0 - f1Proportion
                
                for f02 in GetNumpyArr(sProp, min(residual - sProp, eProp), step):
                    fv02 = int(f02 * accountValue)
                    
                    recNew = copy.deepcopy(rec)
                    recNew.FundVal01 = fv01
                    recNew.FundVal02 = fv02
                    recNew.FundVal03 = accountValue - fv01 - fv02
                    recListNew.append(recNew)
            else:
                recNew = copy.deepcopy(rec)
                recListNew.append(recNew)
                    
        return recListNew

    def GetInforceByPremAllo(self, records, *args):

        recListNew = []

        f1Proportion = args[0]
        sProp = args[1]
        eProp = args[2]
        step = args[3]
        
        for rec in records:
                
            fAllo01 = int(f1Proportion * 100)
            residual = 1.0 - f1Proportion
            
            for f02 in GetNumpyArr(sProp, min(residual - sProp, eProp), step):
                fAllo02 = int(f02 * 100)
                
                recNew = copy.deepcopy(rec)
                recNew.FundAllo01 = fAllo01
                recNew.FundAllo02 = fAllo02
                recNew.FundAllo03 = 100 - fAllo01 - fAllo02
                recListNew.append(recNew)
                
        return recListNew
