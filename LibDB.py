import pymysql
import pymssql
import csv
import uuid
import numpy as np
import os
import pandas as pd

class DbConnector:

    # Address = 'localhost'
    # ID = 'kkh'
    # PW = 'kkh198400'
    # DbName = 'proj'
    
    def __init__(self, addr, idd, pw, dbName):
        self.Address = addr
        self.ID = idd
        self.PW = pw
        self.DbName = dbName    

    def ExecuteSQL(self, query):
        self.conn = pymysql.connect(host=self.Address, user=self.ID, passwd=self.PW, db=self.DbName, charset='utf8')    
        curs = self.conn.cursor()
        curs.execute(query)
        self.conn.commit()
        self.conn.close()

    def GetSqlResult(self, query):
        self.conn = pymysql.connect(host=self.Address, user=self.ID, passwd=self.PW, db=self.DbName, charset='utf8')    
        curs = self.conn.cursor()
        curs.execute(query)
        rows = curs.fetchall()
        self.conn.commit()
        self.conn.close()
        return rows

    def Insert(self, dt, tableName):
        self.conn = pymysql.connect(host=self.Address, user=self.ID, passwd=self.PW, db=self.DbName, charset='utf8')    
        # dt 파일저장, 경로 주의 역슬래시 하면 안됨...ㅜㅜ
        fileName = r"file_" + str(uuid.uuid4()) + r".csv"
        filePath = "C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/" + fileName  
        
        # string 형식만 가능(fmt='%s')
        np.savetxt(filePath, dt, fmt='%s', delimiter=',')

        # bulkinsert
        query = "LOAD DATA INFILE \"" + filePath + "\" INTO TABLE " + tableName + " FIELDS TERMINATED BY ',' LINES TERMINATED BY '\r\n'"

        curs = self.conn.cursor()
        curs.execute(query)        
        self.conn.commit()
        self.conn.close()
                
        os.remove(filePath)

class DbConnectorMS:

    # Address = ""
    # ID = ""
    # PW = ""
    # DbName = ""

    def __init__(self, addr, idd, pw, dbName):        
        self.Address = addr
        self.ID = idd
        self.PW = pw
        self.DbName = dbName        
                
    def ExecuteSQL(self, query):
        conn = pymssql.connect(host=self.Address, user=self.ID, password=self.PW, database=self.DbName, charset='UTF8')
        curs = conn.cursor()
        curs.execute(query)
        conn.commit()
        conn.close()

    def GetSqlResult(self, query):
        conn = pymssql.connect(host=self.Address, user=self.ID, password=self.PW, database=self.DbName, charset='UTF8')
        curs = conn.cursor()
        curs.execute(query)
        rows = curs.fetchall()
        conn.commit()
        conn.close()
        return rows

    def Insert(self, dt, tableName):
        
        conn = pymssql.connect(host=self.Address, user=self.ID, password=self.PW, database=self.DbName, charset='UTF8')

        query = r"insert into " + tableName + r" values "

        for i in range(len(dt)):
            row = dt[i]
            qRow = "("

            for j in range(len(row)):

                qRow = qRow + "'" + str(row[j]) + "'" + ("" if j == len(row) - 1 else ",")

            qRow = qRow + ")" + ("" if i == len(dt) - 1 else ",")
            query = query + qRow

        curs = conn.cursor()
        curs.execute(query)
        conn.commit()
        conn.close()






    #def GetSqlResultOfDataFrame(self, query):
        #sql_conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+self.Address+';DATABASE='+self.DbName+';UID='+self.ID+';PWD='+self.PW)
        #df = pd.read_sql(query, sql_conn)
        #return df




