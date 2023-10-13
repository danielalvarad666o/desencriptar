import os
from flask import Flask, render_template, request, flash, redirect, jsonify
import requests

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
    host="127.0.0.1",
    user="root",
    password="",
    database="encriptacion"
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
   
websocket_clients = set()

@app.route('/')
def index():
    # cursor = db.cursor()
    # consulta= cursor.execute("SELECT * FROM mensajes ORDER BY id DESC LIMIT 1")
    
    # ultimo_mensaje = cursor.fetchone()
    
    response = requests.get('http://25.6.197.168:8000/api/ultimo-mensaje')
    response.raise_for_status()  # Lanza una excepción si la solicitud falla

        # Obtiene el JSON de la respuesta
    json_data = response.json()

    ultimo_mensaje = json_data.get('Mensaje', '')
    print (ultimo_mensaje)
    print("*"*10)
    
    # print(ultimo_mensaje)
    # cursor.close()
    mensaje_desencriptado = ""
    
    if ultimo_mensaje:
        try:
            
            desencriptar_mensaje(ultimo_mensaje)
        except Exception as e:
            mensaje_desencriptado = f"Error al desencriptar el mensaje: {str(e)}"
        
    return render_template('index.html', mensaje_desencriptado=ultimo_mensaje)

def genera_Clave(clave):
    print(clave)
    print("*"*10)
    with open("Clave.key", "wb") as archivo_clave:
        archivo_clave.write(clave)



# Nueva ruta para manejar la desencriptación cuando se recibe un mensaje encriptado
@app.route('/encrypt_server', methods=['POST'])
def encrypt_server():
    try:
        mensaje_encriptado = request.form.get('mensaje_encriptado')
        respaldo= request.form.get('mensaje_encriptado')
        clave=request.files.get('archivo_clave')
        print(request.files)     
        if clave:
          clave_content = clave.read()
          clave_str = clave_content.decode('utf-8')
    
    
          clave_str = clave_str.strip("b")
          clave_str = clave_str.strip("''")
    
    
          print(clave_str)
          clave=clave_str
        
          #genera_Clave(clave)
          with open('Clave.key', 'wb') as archivo_clave:
            archivo_clave.write(clave_content)
          #clave.save('Clave.key')
        
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
    app.run(host='127.0.0.1', port=8081, debug=True)
    
   




