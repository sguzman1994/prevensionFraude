from datetime import time
import model.bd as query
from decouple import config
import os
class Cursor:
    pass

def getRulers():
    sql="SELECT * FROM reglasnegocio;"
    query.Cursor.execute(sql)
    reglas = query.Cursor.fetchall()
    query.conn.commit()
    return reglas

def enableRuler(idCliente):
    sql="UPDATE reglasnegocio SET estadoReglasBegocio = 1 WHERE idReglasBegocio =  %s;"
    datos = (idCliente)
    query.Cursor.execute(sql,datos)
    query.conn.commit()


def disableRuler(idRuler):
    sql="UPDATE reglasnegocio SET estadoReglasBegocio = 0 WHERE idReglasBegocio =  %s;"
    datos = (idRuler)
    query.Cursor.execute(sql,datos)
    query.conn.commit()
    os.environ["RESTRICCIONHORA"] = "NA"
    os.environ["RESTRICCIONMONTO"] = "NA"
    os.environ["RESTRICCIONINTENTOS"] = "NA"
    os.environ["RESTRICCIONBLOQUEO"] = "NA"

def aplicRulers():
    sql="SELECT * FROM reglasnegocio WHERE estadoReglasBegocio = 1;"
    query.Cursor.execute(sql)
    reglas = query.Cursor.fetchall()
    for fila in reglas:
        descripcionServicio= str(fila[5])
        if(descripcionServicio == "intentos"):
            os.environ["RESTRICCIONINTENTOS"] = str(fila[2])
        elif(descripcionServicio == "monto"):
            os.environ["RESTRICCIONMONTO"] = str(fila[2])
        elif(descripcionServicio == "hora"):
            os.environ["RESTRICCIONHORA"] = str(fila[2])
        elif(descripcionServicio == "bloqueo"):
            os.environ["RESTRICCIONBLOQUEO"] = str(fila[2])
    query.conn.commit()
    return reglas

