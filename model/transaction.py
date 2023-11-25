from datetime import time
import model.bd as query

class Cursor:
    pass

def queryListtypeTransac():
    sql="SELECT * FROM transacciontipo"
    query.Cursor.execute(sql)
    tranzacciones = query.Cursor.fetchall()
    query.conn.commit()
    return tranzacciones