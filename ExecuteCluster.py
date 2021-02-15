import LibDB
import numpy as np
import uuid
import datetime


###########################

def SetRunInfo(jobId, args, infCnt, machines, guid):
    msConn = LibDB.DbConnectorMS('kkhproj-db.czuxn57jn8hk.ap-northeast-2.rds.amazonaws.com', 'admin', 'kkh198400', 'proj')

    # 디비1 : RunInfo
    # 잡이름, guid, time, argus("인포스아이디 시나리오아이디")

    timenow = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    line = []
    line.append(jobId)
    line.append(guid)
    line.append(timenow)
    line.append(args)

    arr = np.array([line])

    query = 'delete from RunInfo where id = \'' + jobId + '\''
    msConn.ExecuteSQL(query)
    msConn.Insert(arr, 'RunInfo')


    # 디비2 : RunStatus
    # 잡이름, guid, 시작인포스, 끝인포스, 상태

    infCntByMachine = round(infCnt / len(machines))
    lastMachine = machines[len(machines)-1]
    seqNow = 1

    lines = []
    for i in machines:
        line = []
        line.append(jobId)
        line.append(guid)
        line.append('m' + str(i).zfill(2))
        line.append(seqNow) # 시작인포스번호
        line.append(infCnt if i == lastMachine else seqNow + infCntByMachine - 1) # 종료인포스번호
        seqNow = seqNow + infCntByMachine 
        line.append("Ready")
        lines.append(line)

    arr = np.array(lines)

    query = 'delete from RunStatus where id = \'' + jobId + '\''
    msConn.ExecuteSQL(query)
    msConn.Insert(arr, 'RunStatus')



###### 런정보 입력 ############################

# jobRange = range(1,7+1)

# infId = 'T2011_2_TestSet'
# infCnt = 20000
# machineCnt = 5

# for i in jobRange:        
#     jobId = 'T201129_TestSet_Scen' + str(i).zfill(2) + 'Val'
#     scenId = 'T2011_' + str(i).zfill(2) + '_val' 
#     args = infId + ' ' + scenId # "인포스이름 시나리오이름"    
#     guid = str(uuid.uuid4())
#     print(guid)
#     SetRunInfo(jobId,args,infCnt,machineCnt,guid)


# jobTag = '201213'
# infIDs = ['T2011_2_TrainingSet_P1', 'T2011_2_TrainingSet_P2', 'T2011_2_TrainingSet_P3' ,'T2011_2_TrainingSet_P4']
# scnIDs = ['T2011_01','T2011_02','T2011_03','T2011_04','T2011_05','T2011_06','T2011_07']
# infCnt = 1000
# machineCnt = 1

# for inf in infIDs:
#     for scen in scnIDs:                    
#         jobId = jobTag + '###' + inf + '###' + scen
#         args = inf + ' ' + scen # "인포스이름 시나리오이름"    
#         guid = str(uuid.uuid4())
#         print(guid)
#         SetRunInfo(jobId,args,infCnt,machineCnt,guid)


infCnt = 20000
machines = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
SetRunInfo('201216_T2012_Test_S1_Scen01', 'T2012_Test_S1 T2011_01', infCnt, machines, str(uuid.uuid4()))
SetRunInfo('201216_T2012_Test_S2_Scen02', 'T2012_Test_S2 T2011_02', infCnt, machines, str(uuid.uuid4()))
SetRunInfo('201216_T2012_Test_S3_Scen03', 'T2012_Test_S3 T2011_03', infCnt, machines, str(uuid.uuid4()))
SetRunInfo('201216_T2012_Test_S4_Scen04', 'T2012_Test_S4 T2011_04', infCnt, machines, str(uuid.uuid4()))
SetRunInfo('201216_T2012_Test_S5_Scen05', 'T2012_Test_S5 T2011_05', infCnt, machines, str(uuid.uuid4()))
SetRunInfo('201216_T2012_Test_S6_Scen06', 'T2012_Test_S6 T2011_06', infCnt, machines, str(uuid.uuid4()))
SetRunInfo('201216_T2012_Test_S7_Scen07', 'T2012_Test_S7 T2011_07', infCnt, machines, str(uuid.uuid4()))
SetRunInfo('201216_T2012_Test_S1_Scen08', 'T2012_Test_S1 T2011_08', infCnt, machines, str(uuid.uuid4()))
SetRunInfo('201216_T2012_Test_S2_Scen09', 'T2012_Test_S2 T2011_09', infCnt, machines, str(uuid.uuid4()))
SetRunInfo('201216_T2012_Test_S3_Scen10', 'T2012_Test_S3 T2011_10', infCnt, machines, str(uuid.uuid4()))
SetRunInfo('201216_T2012_Test_S4_Scen11', 'T2012_Test_S4 T2011_11', infCnt, machines, str(uuid.uuid4()))
SetRunInfo('201216_T2012_Test_S5_Scen12', 'T2012_Test_S5 T2011_12', infCnt, machines, str(uuid.uuid4()))
SetRunInfo('201216_T2012_Test_S6_Scen13', 'T2012_Test_S6 T2011_13', infCnt, machines, str(uuid.uuid4()))
SetRunInfo('201216_T2012_Test_S7_Scen14', 'T2012_Test_S7 T2011_14', infCnt, machines, str(uuid.uuid4()))


