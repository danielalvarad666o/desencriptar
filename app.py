import os
from flask import Flask, render_template, request, flash, redirect, jsonify

from cryptography.fernet import Fernet
import mysql.connector

app = Flask(__name__)

# Función para cargar la clave desde un archivo
def leerclave():
    archivo = "Clave.key"
    clave=""
    if os.path.exists(archivo):
        with open(archivo, "rb") as archivo_clave:
            clave = archivo_clave.read()
    return clave

# Configura la conexión a la base de datos MySQL
db = mysql.connector.connect(
    host="192.168.1.17",
    user="root",
    password="",
    database="encrypt"
)

def desencriptar_mensaje(mensaje):
    clave_temporal = leerclave()
    if (clave_temporal!=""):
        try:
            f = Fernet(clave_temporal)
            mensaje_desencriptado = f.decrypt(mensaje)
            mensaje_desencriptado_str = mensaje_desencriptado.decode()
            return mensaje_desencriptado_str
        except Exception as e:
            # Capturamos y manejamos la excepción
            mensaje_desencriptado_str="la llave es incorrecta"
            return mensaje_desencriptado_str
            
    else:
       mensaje_desencriptado_str=""
       return mensaje_desencriptado_str

@app.route('/')
def index():
    cursor = db.cursor()
    consulta=cursor.execute("SELECT mensaje_encriptado FROM mensajes ORDER BY id DESC LIMIT 1")
    ultimo_mensaje = cursor.fetchone()
    print(ultimo_mensaje)
    cursor.close()
    mensaje_desencriptado = ""
    
    if ultimo_mensaje:
        try:
            mensaje_encriptado = ultimo_mensaje[0]
            cadena_sin_comillas = mensaje_encriptado.strip("()")
            mensaje_desencriptado = ultimo_mensaje
            desencriptar_mensaje(cadena_sin_comillas)
        except Exception as e:
            mensaje_desencriptado = f"Error al desencriptar el mensaje: {str(e)}"
        
    return render_template('index.html', mensaje_desencriptado=cadena_sin_comillas)





# Nueva ruta para manejar la desencriptación cuando se recibe un mensaje encriptado
@app.route('/encrypt_server', methods=['POST'])
def encrypt_server():
    try:
        mensaje_encriptado = request.form.get('mensaje_encriptado')
        respaldo= request.form.get('mensaje_encriptado')
        mensaje_desencriptado = desencriptar_mensaje(mensaje_encriptado)
        if mensaje_desencriptado=="":
            
             return render_template('index.html', mensaje_desencriptado=mensaje_encriptado,mensajedealerta="no tienes la llave")
        elif  mensaje_desencriptado=="la llave es incorrecta": 
             
             return render_template('index.html', mensaje_desencriptado=mensaje_encriptado,mensajedealerta="la llave es incorrecta")   
        else:
         return render_template('index.html', mensaje_desencriptado=mensaje_desencriptado)
    except Exception as e:
        flash(f"Error al desencriptar el mensaje: {str(e)}")
        return render_template('index.html', mensaje_desencriptado=mensaje_encriptado)

if __name__ == '__main__':
    app.run(host='192.168.1.17', port=8080, debug=True)
    
    #example
    # if __name__ == '__main__':
    # app.run(host='192.168.1.17', port=8080, debug=True)





