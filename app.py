from logging import debug
from flask import Flask
from flask import render_template,request,redirect,url_for  # agregamos request  
from flaskext.mysql import MySQL    # para comunicacion mysql
from datetime import datetime       #para darle nombre a las fotos
from flask import send_from_directory
import os #para acceder a los archivos

app=Flask(__name__)     # creacion del objeto app de la clase Flask

mysql = MySQL()     # creacion de un objeto mysql de la clase MySQL
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'biblioteca'     # nombre de la base de datos
mysql.init_app(app)     # Llamamos al metodo init_app de mysql con el objeto de flask como parametro

CARPETA=os.path.join('uploads')     #referencia a la carpeta
app.config['CARPETA']=CARPETA   #indicamos que vamos a guardar esta ruta de la carpeta

@app.route('/uploads/<nombreFoto>')
def uploads(nombreFoto):
    return send_from_directory(app.config['CARPETA'],nombreFoto)

@app.route('/')
def index():
    return render_template('biblioteca/index.html')

@app.route('/inventario')
def inventario():
    sql="SELECT `libro`.`id_libro`, `libro`.`nombre_libro`, `categorias`.`categoria`, `libro`.`autor_libro`, `libro`.`url_foto` FROM `biblioteca`.`libro` INNER JOIN `categorias` ON `libro`.`id_categoria` = `categorias`.`id_categoria`;"
    conn=mysql.connect()        # hacemos la conexion a mysql
    cursor=conn.cursor()
    cursor.execute(sql)     # ejecucion del string sql
    libros=cursor.fetchall()     #traemos toda la informacion
    print(libros)        #imprimimos los datos en la terminal
    conn.commit()
    return render_template('biblioteca/inventario.html', libros=libros)      # permite renderizar index.html en el navegador

@app.route('/prestamos')

@app.route('/historial_prestamos')

@app.route('/nuevo_libro')
def nuevo_libro():
    return render_template('biblioteca/create_libro.html')

@app.route("/store_libro", methods=['POST'])  #cuando el formulario de create.html hace el submit envia los datos a la pagina /store
def storage_libro():
    _nombre = request.form['txtNombre']     #toma los datos que envio el form en txtNombre
    _categoria = request.form['txtCategoria']     #toma los datos del form
    _autor = request.form['txtAutor']     #toma los datos del form    
    _foto = request.files['txtFoto']        #toma los datos del form

    if _foto.filename !='':
        nuevoNombreFoto=_foto.filename   #concatena el nombre
        _foto.save("uploads/"+nuevoNombreFoto)  #lo guarda en la carpeta

    sql = "INSERT INTO `biblioteca`.`libro` (`id_libro`,`nombre_libro`,`id_categoria`, `autor_libro`,`url_foto`) VALUES (null,%s,%s,%s,%s);"
    datos = (_nombre,_categoria,_autor,nuevoNombreFoto)
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql,datos)       #ejecuta la sentencia sql
    conn.commit()

    return redirect('/inventario')

@app.route('/nuevo_prestamo')       #para el ruteo de create.html
def nuevo_prestamo():
    return render_template('biblioteca/create_prestamo.html')

@app.route("/store_prestamo", methods=['POST'])  #cuando el formulario de create.html hace el submit envia los datos a la pagina /store
def storage_prestamo():
    _nombre = request.form['txtNombre']     #toma los datos que envio el form en txtNombre
    _correo = request.form['txtCorreo']     #toma los datos del form
    _foto = request.files['txtFoto']        #toma los datos del form
    now=datetime.now()
    tiempo=now.strftime("%Y%H%S")    #años, horas, minutos y segundos

    if _foto.filename !='':
        nuevoNombreFoto=tiempo+_foto.filename   #concatena el nombre
        _foto.save("uploads/"+nuevoNombreFoto)  #lo guarda en la carpeta

    sql = "INSERT INTO `sistema`.`empleados` (`id`,`nombre`,`correo`,`foto`) VALUES (null,%s,%s,%s)"
    datos = (_nombre,_correo,nuevoNombreFoto)
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql,datos)       #ejecuta la sentencia sql
    conn.commit()
    return redirect('/')      #y renderiza el index.html

@app.route('/destroy_libro/<int:id>')     #recibe como parametro el id del registro
def destroy_libro(id):
    conn = mysql.connect()   #se conecta a la conexion mysql.init_app(app)
    cursor = conn.cursor()   #almacena lo que ejecutamos

    cursor.execute("SELECT url_foto FROM `biblioteca`.`libro` WHERE id_libro=%s",(id))
    fila=cursor.fetchall()
    os.remove(os.path.join(app.config['CARPETA'],fila[0][0]))

    cursor.execute("DELETE FROM `biblioteca`.`libro` WHERE id_libro=%s", (id))   #en vez de pasarle el string la escribimos
    conn.commit()      #cerramos la conexion
    return redirect('/inventario')    #regresamos de donde vinimos

@app.route("/update", methods=['POST'])
def update():
    _nombre=request.form['txtNombre']
    _correo=request.form['txtCorreo']
    _foto=request.files['txtFoto']
    id=request.form['txtID']

    sql = "UPDATE `sistema`.`empleados` SET `nombre`=%s, `correo`=%s WHERE id=%s;"
    datos=(_nombre,_correo,id)

    conn=mysql.connect()
    cursor=conn.cursor()

    now=datetime.now()
    tiempo=now.strftime("%Y%H%M%S")

    if _foto.filename !='':
        nuevoNombreFoto=tiempo+_foto.filename
        _foto.save("uploads/"+nuevoNombreFoto)

        cursor.execute("SELECT foto FROM `sistema`.`empleados` WHERE id=%s",(id))
        fila=cursor.fetchall()

        os.remove(os.path.join(app.config['CARPETA'],fila[0][0]))
        cursor.execute("UPDATE empleados SET foto=%s WHERE id=%s",(nuevoNombreFoto,id))
        conn.commit()

    cursor.execute(sql,datos)
    conn.commit()
    
    return redirect('/')

@app.route('/edit_libro/<int:id>')
def edit_libro(id):
    conn = mysql.connect()   #se conecta a la conexion mysql.init_app(app)
    cursor = conn.cursor()   #almacena lo que ejecutamos
    cursor.execute("SELECT * FROM `biblioteca`.`libro` WHERE id=%s", (id))     #ejecuta la sentencia SQL sobre el id
    libros=cursor.fetchall()    #traemos toda la informacion
    conn.commit()    #cerramos la conexion
    return render_template('empleados/edit.html', libros=libros)

if __name__=='__main__':
    app.run(debug=True)
