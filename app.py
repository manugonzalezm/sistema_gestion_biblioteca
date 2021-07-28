from logging import debug
from flask import Flask
from flask import render_template,request,redirect,url_for  # agregamos request  
from flaskext.mysql import MySQL    # para comunicacion mysql
from flask import send_from_directory
import os #para acceder a los archivos

app=Flask(__name__)     # creacion del objeto app de la clase Flask

mysql = MySQL()     # creacion de un objeto mysql de la clase MySQL
app.config['MYSQL_DATABASE_HOST'] = 'remotemysql.com'
app.config['MYSQL_DATABASE_USER'] = 'yRsT5S18UV'
app.config['MYSQL_DATABASE_PASSWORD'] = 'npWRLL9PcG'
app.config['MYSQL_DATABASE_DB'] = 'yRsT5S18UV'     # nombre de la base de datos
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
    sql="SELECT `inventario`.`id_stock`, `inventario`.`nombre_libro`, `categorias`.`categoria`, `inventario`.`autor`, `inventario`.`url_foto` FROM `inventario` INNER JOIN `categorias` ON `inventario`.`id_categoria` = `categorias`.`id_categoria` WHERE `inventario`.`disponibilidad`=1;"
    conn=mysql.connect()        # hacemos la conexion a mysql
    cursor=conn.cursor()
    cursor.execute(sql)     # ejecucion del string sql
    libros=cursor.fetchall()     #traemos toda la informacion
    print(libros)        #imprimimos los datos en la terminal
    conn.commit()

    sql="SELECT `categorias`.`categoria` FROM `inventario` INNER JOIN `categorias` ON `inventario`.`id_categoria` = `categorias`.`id_categoria` WHERE `inventario`.`disponibilidad`=1;"
    conn=mysql.connect() # hacemos la conexion a mysql
    cursor=conn.cursor()
    cursor.execute(sql) # ejecutamos el string sql
    conn.commit()

    categorias=cursor.fetchall()

    return render_template('biblioteca/inventario.html',libros=libros, categorias=categorias)

@app.route('/prestamos')
def prestamos():
    sql="SELECT `inventario`.`id_stock`, `inventario`.`nombre_libro`, `socios`.`nombre_socio`, `inventario`.`fecha_devolucion`, `inventario`.`url_foto` FROM `inventario` INNER JOIN `socios` ON `inventario`.`id_socio` = `socios`.`id_socio` WHERE `inventario`.`disponibilidad`=0;"
    conn=mysql.connect()        # hacemos la conexion a mysql
    cursor=conn.cursor()
    cursor.execute(sql)     # ejecucion del string sql
    prestamos=cursor.fetchall()     #traemos toda la informacion
    print(prestamos)        #imprimimos los datos en la terminal
    conn.commit()

    sql="SELECT categorias.categoria FROM inventario INNER JOIN categorias ON inventario.id_categoria = categorias.id_categoria WHERE `inventario`.`disponibilidad`=0;"
    conn=mysql.connect() # hacemos la conexion a mysql
    cursor=conn.cursor()
    cursor.execute(sql) # ejecutamos el string sql
    conn.commit()

    categorias=cursor.fetchall()

    return render_template('biblioteca/prestamos.html',prestamos=prestamos, categorias=categorias)

@app.route('/devolver_libro/<int:id>')
def devolver_libro(id):
    conn = mysql.connect()   #se conecta a la conexion mysql.init_app(app)
    cursor = conn.cursor()   #almacena lo que ejecutamos
    cursor.execute("SELECT inventario.id_stock, inventario.nombre_libro, socios.nombre_socio, inventario.fecha_devolucion, inventario.url_foto FROM inventario INNER JOIN socios ON inventario.id_socio = socios.id_socio WHERE id_stock=%s;", (id))     #ejecuta la sentencia SQL sobre el id
    libros=cursor.fetchall()    #traemos toda la informacion
    conn.commit()    #cerramos la conexion
    return render_template('biblioteca/confirm_devolucion.html', libros=libros)

@app.route("/devolver", methods=['POST'])
def devolver():
    id=request.form['txtID'];

    sql = "UPDATE `inventario` SET `id_socio`=null, `disponibilidad`=1, `fecha_devolucion`=null WHERE (`id_stock`=%s);"
    datos=(id)
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql,datos)
    conn.commit()
    
    return redirect('/inventario')

@app.route('/socios')
def socios():
    conn = mysql.connect()   #se conecta a la conexion mysql.init_app(app)
    cursor = conn.cursor()   #almacena lo que ejecutamos
    cursor.execute("SELECT * FROM `socios`")    #ejecuta la sentencia SQL sobre el id
    socios=cursor.fetchall()    #traemos toda la informacion
    conn.commit()    #cerramos la conexion
    return render_template('biblioteca/socios.html', socios=socios)

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

    sql = "INSERT INTO `inventario` (`id_stock`,`nombre_libro`,`id_categoria`, `autor`, `url_foto`, `disponibilidad`) VALUES (null,%s,%s,%s,%s,1);"
    datos = (_nombre,_categoria,_autor,nuevoNombreFoto)
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql,datos)       #ejecuta la sentencia sql
    conn.commit()

    return redirect('/inventario')

@app.route('/prestar/<int:id>')       #para el ruteo de create.html
def prestar(id):
    conn = mysql.connect()   #se conecta a la conexion mysql.init_app(app)
    cursor = conn.cursor()   #almacena lo que ejecutamos
    cursor.execute("SELECT * FROM `inventario` WHERE id_stock=%s", (id))     #ejecuta la sentencia SQL sobre el id
    libros=cursor.fetchall()    #traemos toda la informacion
    conn.commit()    #cerramos la conexion

    conn = mysql.connect()   #se conecta a la conexion mysql.init_app(app)
    cursor = conn.cursor()   #almacena lo que ejecutamos
    cursor.execute("SELECT * FROM `socios`")    #ejecuta la sentencia SQL sobre el id
    socios=cursor.fetchall()    #traemos toda la informacion
    conn.commit()    #cerramos la conexion
    return render_template('biblioteca/new_prestamo.html', libros=libros, socios=socios)

@app.route("/store_prestamo", methods=['POST'])  #cuando el formulario de create.html hace el submit envia los datos a la pagina /store
def storage_prestamo():
    id = request.form['txtID']     #toma los datos que envio el form en txtNombre
    _fecha = request.form['txtFecha']
    _idLibro = request.form['txtIdLibro']

    sql = "UPDATE `inventario` SET `id_socio`=%s, `fecha_devolucion`=%s, `disponibilidad`='0' WHERE id_stock=%s;"
    datos=(id,_fecha,_idLibro)

    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql,datos)
    conn.commit()

    return redirect('/prestamos')      #y renderiza el index.html

@app.route('/nuevo_socio')
def nuevo_socio():
    return render_template('biblioteca/create_socio.html')

@app.route("/store_socio", methods=['POST'])  #cuando el formulario de create.html hace el submit envia los datos a la pagina /store
def storage_socio():
    _nombre = request.form['txtNombre']     #toma los datos que envio el form en txtNombre
    _correo = request.form['txtCorreo']     #toma los datos del form

    sql = "INSERT INTO `socios` (`id_socio`,`nombre_socio`,`correo_socio`) VALUES (null,%s,%s);"
    datos = (_nombre,_correo)
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql,datos)       #ejecuta la sentencia sql
    conn.commit()

    return redirect('/socios')

@app.route('/search', methods=['POST'])
def search():
    _busq="%"+request.form['titulo']+"%"
    datos=(_busq)
    sql="SELECT inventario.id_stock, inventario.nombre_libro, categorias.categoria, inventario.autor, inventario.url_foto FROM inventario INNER JOIN categorias ON inventario.id_categoria = categorias.id_categoria WHERE inventario.nombre_libro LIKE %s; "
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql,datos)
    conn.commit()

    libros=cursor.fetchall()
    if (len(_busq) == 0):
        return inventario()
    else:
        return render_template('biblioteca/inventario.html',libros=libros)

@app.route('/filter', methods=['POST'])
def fltr():
    _fil=request.form['categoria']
    if (_fil == "Todos"):
        return inventario()
    datos=(_fil)
    sql="SELECT inventario.id_stock, inventario.nombre_libro, categorias.categoria, inventario.autor, inventario.url_foto FROM inventario INNER JOIN categorias ON inventario.id_categoria = categorias.id_categoria WHERE categorias.categoria LIKE %s; "
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql,datos)
    conn.commit()

    libros=cursor.fetchall()

    sql="SELECT categorias.categoria FROM inventario INNER JOIN categorias ON inventario.id_categoria = categorias.id_categoria WHERE `inventario`.`disponibilidad`=1;"
    conn=mysql.connect() # hacemos la conexion a mysql
    cursor=conn.cursor()
    cursor.execute(sql) # ejecutamos el string sql
    conn.commit()

    categorias=cursor.fetchall()

    return render_template('biblioteca/inventario.html',libros=libros, categorias=categorias)

@app.route('/searchP', methods=['POST'])
def searchP():
    _busq="%"+request.form['titulo']+"%"
    datos=(_busq)
    sql="SELECT inventario.id_stock, inventario.nombre_libro, socios.nombre_socio, inventario.fecha_devolucion, inventario.url_foto FROM inventario INNER JOIN socios ON inventario.id_socio = socios.id_socio WHERE inventario.nombre_libro LIKE %s"
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql,datos)
    conn.commit()

    prestamos=cursor.fetchall()
    if (len(_busq) == 0):
        return prestamos()
    else:
        return render_template('biblioteca/prestamos.html', prestamos=prestamos)  

@app.route('/filterP', methods=['POST'])
def fltrP():
    _fil=request.form['categoria']
    if (_fil == "Todos"):
        return prestamos()
    datos=(_fil)
    sql="SELECT inventario.id_stock, inventario.nombre_libro, categorias.categoria, inventario.autor, inventario.url_foto FROM inventario INNER JOIN categorias ON inventario.id_categoria = categorias.id_categoria WHERE categorias.categoria LIKE %s;"
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql,datos)
    conn.commit()

    prestamo=cursor.fetchall()

    sql="SELECT categorias.categoria FROM inventario INNER JOIN categorias ON inventario.id_categoria = categorias.id_categoria WHERE inventario.disponibilidad=0;"
    conn=mysql.connect() # hacemos la conexion a mysql
    cursor=conn.cursor()
    cursor.execute(sql) # ejecutamos el string sql
    conn.commit()

    categorias=cursor.fetchall()

    return render_template('biblioteca/prestamos.html', prestamos=prestamo, categorias=categorias)

@app.route('/destroy_libro/<int:id>')     #recibe como parametro el id del registro
def destroy_libro(id):
    conn = mysql.connect()   #se conecta a la conexion mysql.init_app(app)
    cursor = conn.cursor()   #almacena lo que ejecutamos

    cursor.execute("SELECT url_foto FROM `inventario` WHERE id_stock=%s",(id))
    fila=cursor.fetchall()
    os.remove(os.path.join(app.config['CARPETA'],fila[0][0]))

    cursor.execute("DELETE FROM `inventario` WHERE id_stock=%s", (id))   #en vez de pasarle el string la escribimos
    conn.commit()      #cerramos la conexion
    return redirect('/inventario')    #regresamos de donde vinimos

@app.route('/edit_libro/<int:id>')
def edit_libro(id):
    conn = mysql.connect()   #se conecta a la conexion mysql.init_app(app)
    cursor = conn.cursor()   #almacena lo que ejecutamos
    cursor.execute("SELECT `inventario`.`id_stock`, `inventario`.`nombre_libro`, `inventario`.`autor`, `inventario`.`url_foto` FROM `inventario` WHERE id_stock=%s", (id))     #ejecuta la sentencia SQL sobre el id
    libros=cursor.fetchall()    #traemos toda la informacion
    conn.commit()    #cerramos la conexion
    return render_template('biblioteca/edit_libro.html', libros=libros)

@app.route("/update", methods=['POST'])
def update():
    _nombre=request.form['txtNombre']
    _autor=request.form['txtAutor']
    _foto=request.files['txtFoto']
    id=request.form['txtID']

    sql = "UPDATE `inventario` SET `nombre_libro`=%s, `autor`=%s WHERE id_stock=%s;"
    datos=(_nombre,_autor,id)

    conn=mysql.connect()
    cursor=conn.cursor()

    if _foto.filename !='':
        nuevoNombreFoto=_foto.filename
        _foto.save("uploads/"+nuevoNombreFoto)

        cursor.execute("SELECT url_foto FROM `inventario` WHERE id_stock=%s",(id))
        fila=cursor.fetchall()

        os.remove(os.path.join(app.config['CARPETA'],fila[0][0]))
        cursor.execute("UPDATE `inventario` SET url_foto=%s WHERE id_stock=%s",(nuevoNombreFoto,id))
        conn.commit()

    cursor.execute(sql,datos)
    conn.commit()
    
    return redirect('/inventario')

if __name__=='__main__':
    app.run(debug=True)
