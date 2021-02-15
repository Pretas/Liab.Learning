import csv
import numpy as np

class LibFile:

    def WriteFile(self, dt, tableName):
        # dt 파일저장
        filePath = r"C:\ProgramData\MySQL\MySQL Server 8.0\Uploads" + r"\file_" + str(uuid.uuid4()) + r".csv"  
        
        f = open(filePath, "w")
        
        lenths = np.shape(dt)
        for row in range(lenths[0]):
            lineStr = ""
            comma = ''
            for col in range(lenths[1]):
                if col == 1:
                    lineStr = dt[row,col]
                else:
                    lineStr += (',' + dt[row,col])
            
            f.write(lineStr + '\r\n')
    
        f.close()