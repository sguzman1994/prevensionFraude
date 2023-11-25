from flask import Flask
from flask import render_template,request,redirect,url_for,flash
from flaskext.mysql import MySQL
from dotenv import load_dotenv
from decouple import config
import os
import controller.ml as ml
import datetime
from model.user import cambiarContrasenia
from model.user import inicioSession
from model.ruler import getRulers,enableRuler,disableRuler,aplicRulers
import model.val as val
import logging
import datetime

logger = logging.getLogger('werkzeug')
logger.setLevel(logging.WARNING)
# Eliminar todos los handlers existentes
for handler in logger.handlers[:]:
    logger.warning(' * Running on http://127.0.0.1:5000')
    logger.removeHandler(handler)
    
# Agregar un nuevo handler
handler = logging.StreamHandler()
logger.addHandler(handler)

app = Flask(__name__)
app.secret_key='asl'
load_dotenv('.env')
horaTransaccion = datetime.datetime.now()
hora_formateada = horaTransaccion.strftime('%H:%M:%S')
mysql=MySQL()
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'db_controlriesgos'
mysql.init_app(app)
conn = mysql.connect()
Cursor = conn.cursor()

@app.route("/")
def index():
    restriccionSession = config("IDSESSION")
    tipoCliente = config("TIPOCLIENTE")
    if(restriccionSession == "1" and int(tipoCliente) ==1):
        sql='SELECT * FROM detalletransaccioncuenta ORDER BY fechaTransaccion DESC ,idDetalleTransaccionCuenta DESC LIMIT 15;'
        Cursor.execute(sql)
        conn.commit()
        tranzacciones = Cursor.fetchall()
        reportes = val.reporteGenerado()
        montomes = val.montoMes()
        return render_template('tranzaccion/index.html',tranzacciones=tranzacciones, reportes=reportes, montomes=montomes)
    elif(restriccionSession == "1" and int(tipoCliente) ==2):
        sql='SELECT * FROM detalletransaccioncuenta WHERE  idCliente = '+str(config("IDCLIENTEP"))+' ORDER BY idDetalleTransaccionCuenta DESC LIMIT 15;'
        Cursor.execute(sql)
        conn.commit()
        tranzacciones = Cursor.fetchall()
        return render_template('tranzaccion/indexc.html',tranzacciones=tranzacciones)
    return render_template('tranzaccion/login.html')

@app.route("/getinto", methods=['POST'])
def login():
    try:
        _idUsuario = request.form['txtUsuario']
        _Contrasenia = request.form['txtContrasenia']
        if(_idUsuario =="" or _Contrasenia == ""):
            flash('Recuerda ingresar todos los datos')
            return render_template('tranzaccion/login.html')
        elif(_idUsuario.isdigit() == False or _Contrasenia.isnumeric() == False):
            flash('Recuerda que los datos deben ser solo numero')
            return render_template('tranzaccion/login.html')
        else:
            reportes = inicioSession(_idUsuario,_Contrasenia)
            print(len(reportes))
            if(len(reportes)==1):
                os.environ["IDSESSION"]="1"
                return redirect("/")
            else:
                flash('Datos ingresados no son correctos')
                return render_template('tranzaccion/login.html')
    except ZeroDivisionError:
        flash("Error: División por cero.")
    except ValueError:
        flash("Error: Entrada no válida. Debes ingresar un número.")
    except Exception as e:
        flash("Ocurrió una excepción:", e)
    else:
        flash("No se generó ninguna excepción.")

@app.route("/close")
def close():
    os.environ["IDSESSION"]="0"
    return redirect("/")

@app.route("/restore")
def restore():
    return render_template('tranzaccion/change.html')

@app.route("/back")
def back():
    return render_template('tranzaccion/login.html')

@app.route('/change', methods=['POST'])
def change():
    _contraseniaA = request.form['txtContraseniaA']
    _contraseniaN = request.form['txtContraseniaN']
    _documento = request.form['txtDocumento']
    _pinSeguridad = request.form['txtPinSeguridad']
    cambiarContrasenia(_contraseniaN, _documento, _pinSeguridad)
    os.environ["IDSESSION"]="1"
    return redirect('/')

@app.route("/destroy/<int:id>")
def destroy(id):
    conn = mysql.connect()
    Cursor = conn.cursor()
    Cursor.execute('DELETE FROM detalletransaccioncuenta WHERE idDetalleTransaccionCuenta = %s',(id))
    Cursor.execute('DELETE FROM detalletransaccioncuentacomparativa WHERE idDetalleTransaccionCuenta = %s',(id))
    conn.commit()
    os.environ["IDSESSION"]="1"
    return redirect("/")

@app.route('/edit/<int:id>')
def edit(id):
    conn = mysql.connect()
    Cursor = conn.cursor()
    Cursor.execute('SELECT * FROM detalletransaccioncuenta WHERE idDetalleTransaccionCuenta = %s',(id))
    tranzacciones = Cursor.fetchall()
    conn.commit()
    os.environ["IDSESSION"]="1"
    return render_template('tranzaccion/edit.html',tranzacciones=tranzacciones)

@app.route('/update', methods=['POST'])
def update():
    _id01 = request.form['txtestablecimeinto']
    _id02 = request.form['txthora']
    _id03 = request.form['txtmonto']
    id = request.form['txtidA']
    sql='UPDATE detalletransaccioncuenta SET establecimientoTransaccion =%s , horaTransaccion =%s, montoTransaccion =%s  WHERE idDetalleTransaccionCuenta =%s;'
    datos = (_id01,_id02,float(_id03),id)
    conn = mysql.connect()
    Cursor = conn.cursor() 
    Cursor.execute(sql,datos)
    conn.commit()
    os.environ["IDSESSION"]="1"
    return redirect('/')

@app.route("/create")
def create():
    restriccionSession = config("IDSESSION")
    tipoCliente = config("TIPOCLIENTE")
    sql='SELECT * FROM transacciontipo'
    Cursor.execute(sql)
    conn.commit()
    tranzacciones = Cursor.fetchall()
    cuentas= val.getaccuount(config("IDCLIENTEP"))
    if(restriccionSession == "1" and int(tipoCliente) ==1):
        return render_template('tranzaccion/create.html',tranzacciones=tranzacciones)
    elif(restriccionSession == "1" and int(tipoCliente) ==2):
        return render_template('tranzaccion/createc.html',tranzacciones=tranzacciones, cuentas=cuentas)


@app.route("/store", methods=['POST'])
def storage():
    restriccionSession = config("IDSESSION")
    tipoCliente = config("TIPOCLIENTE")
    if(restriccionSession == "1" and int(tipoCliente) ==1):
        _id0A = request.form['txtidA']
        _id0B = request.form['txtidB']
    elif(restriccionSession == "1" and int(tipoCliente) ==2):
        _id0A = request.form['selected_option1']
        _id0B = config("IDCLIENTEP")
    _id0C = request.form['selected_option']
    _id01 = request.form['txtestablecimeinto']
    _id02 = request.form['txthora']
    _id03 = request.form['txtmonto']
    _id04 = 0
    _id05 = datetime.datetime.now()

    os.environ["IDCLIENTE"]=_id0B

    aplicRulers()
    restriccionHora = config("RESTRICCIONHORA")
    restriccionMonto = config("RESTRICCIONMONTO")

    if(_id01=="" or _id02=="" or _id03==""):
        flash('Recuerda ingresar todos los datos')
        return redirect(url_for('create'))

    if(len(restriccionHora) != 2):
        if(val.formato24h(_id02) >= val.formato24h(restriccionHora)):
            flash('Hora fuera de rango')
            return redirect(url_for('create'))
        
    if(len(restriccionMonto) != 2):
        if(float(_id03) >= float(restriccionMonto)):
            flash('Monto fuera de rango')
            return redirect(url_for('create'))

    sql='INSERT INTO detalletransaccioncuenta VALUES (NULL,%s,%s,%s,%s,%s,%s,%s,%s)'
    sql1='INSERT INTO detalletransaccioncuentacomparativa VALUES (NULL,%s,%s,%s,%s,%s,%s,%s,%s)'
    datos = (int(_id0A),int(_id0B),int(_id0C),_id01,_id02,float(_id03),int(_id04),_id05)
    Cursor.execute(sql,datos)
    Cursor.execute(sql1,datos)
    conn.commit()
    os.environ["IDSESSION"]="1"
    alerta = ml.motorMachineLearning()
    return render_template('tranzaccion/create.html',alerta=alerta)

@app.route("/unlock")
def unlock():
    restriccionSession = config("IDSESSION")
    tipoCliente = config("TIPOCLIENTE")
    os.environ["IDSESSION"]="1"
    if(restriccionSession == "1" and int(tipoCliente) ==1):
        return render_template('tranzaccion/unlock.html')
    elif(restriccionSession == "1" and int(tipoCliente) ==2):
        return render_template('tranzaccion/unlockLogin.html')

@app.route('/process', methods=['POST'])
def process():
    _id01 = request.form['txtDocumento']
    _id02 = request.form['txtToken']
    sql='UPDATE cliente SET ClienteEstado = '+str(1)+', ClienteToken=Null WHERE Clientedocumentos =%s and ClienteToken =%s;'
    datos = (_id01,_id02)
    Cursor.execute(sql,datos)
    conn.commit()
    os.environ["IDSESSION"]="1"
    return redirect('/')

@app.route("/client")
def client():
    sql='SELECT * FROM cliente'
    Cursor.execute(sql)
    client = Cursor.fetchall()
    conn.commit()
    return render_template('tranzaccion/client.html',client=client)

@app.route("/ruler")
def ruler():
    reglas = getRulers()
    return render_template('tranzaccion/ruler.html', reglas=reglas)


@app.route('/enable/<int:id>')
def enable(id):
    enableRuler(id)
    return redirect('/ruler')

@app.route('/disable/<int:id>')
def disable(id):
    disableRuler(id)
    return redirect('/ruler')

@app.route("/newrulers", methods=['POST'])
def newrulers():
    _id01 = request.form['txtInicio']
    _id02 = request.form['txtFin']
    _id03 = request.form['txtDescripcion']
    _id04 = 1
    
    if(_id01=="" or _id02=="" or _id03==""):
        flash('Recuerda ingresar todos los datos')
        return redirect(url_for('ruler'))

    sql='INSERT INTO reglasnegocio VALUES (NULL,%s,%s,%s,%s)'
    datos = (int(_id01),_id02,_id03,_id04)
    Cursor.execute(sql,datos)
    conn.commit()
    os.environ["IDSESSION"]="1"
    return redirect('/ruler')

if __name__ == '__main__':
    app.run(debug = True)