import mysql.connector
import os
from dotenv import load_dotenv

# .env 파일에서 환경 변수를 로드합니다.
load_dotenv()

def getDbConnection():
    """ 
    MySQL 데이터베이스에 연결하고 연결 객체를 반환합니다. 
    """
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            port=int(os.getenv("DB_PORT", 3307))
        )
        return connection
    except Exception as e:
        print(f"Connection error: {e}")
        return None

def executeSelectQuery(query, params=None):
    """ 
    SELECT 쿼리를 실행하고 결과를 리스트로 반환합니다. 
    """
    try:
        db = getDbConnection()
        if db is None:
            return {"success": False, "message": "데이터베이스 연결에 실패하였습니다."}
            
        cursor = db.cursor(dictionary=True)
        if params is not None:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
            
        rows = cursor.fetchall()
        cursor.close()
        db.close()
        return rows
    except Exception as e:
        return {"success": False, "message": str(e)}

def executeInsertUpdateQuery(query, params=None):
    """ 
    INSERT, UPDATE, DELETE 쿼리를 실행합니다. 
    """
    try:
        db = getDbConnection()
        if db is None:
            return {"success": False, "message": "데이터베이스 연결에 실패하였습니다."}
            
        cursor = db.cursor()
        if params is not None:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
            
        db.commit()
        rowCount = cursor.rowcount
        cursor.close()
        db.close()
        return {"success": True, "rowCount": rowCount}
    except Exception as e:
        return {"success": False, "message": str(e)}
