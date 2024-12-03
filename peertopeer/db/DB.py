import pymysql
from colorama import Back,Fore
import re
import os
from hashlib import sha256
if(__name__=="__main__"):
    from bdTablas import *
else:
    from .bdTablas import *

def abrirArchivo(archivo,modo):
    try:
        #intenta abrir el archivo
        return open(archivo,modo)
    except:
        #no existe o se ingreso un modo invalido
        return None
    
class CC():
    def __init__(self,auto_destruir=None):
        try:
            self.connection = pymysql.connect(host='localhost', user=self.usuarioXampp, passwd='', port=self.puertoXampp, db='knowledgefield')
            self.cursor = self.connection.cursor()
            print("\n Conexion exitosa")

            try:
                if(auto_destruir!=None):
                    self.auto_destruccion(auto_destruir)
                self.crearTablas()
                self.crearProcedimientos()
                self.hacerInserts()

            except pymysql.Error as err:
                print("\n error al intentar crear las tablas o procedimientos: " .format(err))
            
        except pymysql.Error as err:
            self.connection = pymysql.connect(host='localhost', user=self.usuarioXampp, passwd='', port=self.puertoXampp)
            self.cursor = self.connection.cursor()
            self.cursor.execute("CREATE DATABASE IF NOT EXISTS knowledgefield")
            self.connection.commit()
            self.cursor.execute("USE knowledgefield")
            print("\nCreacion exitosa")

            try:
                self.crearTablas()
                self.crearProcedimientos()

            except pymysql.Error as err:
                print("\n error al intentar crear las tablas o procedimientos: " .format(err))

    def auto_destruccion(self,tablas_excepcion=()):
        print("GOKUUUUUUUUUUUUUUUUUUUUUUUAH!")
        adicional=""
        for tabla in tablas_excepcion:
            # and table_name!='perfil'
            adicional+=f"and table_name!='{tabla}' "

        try:
            self.cursor.execute(f"select table_name from INFORMATION_SCHEMA.tables where table_schema='knowledgefield' {adicional} order by create_time desc ;")
        except Exception as ex:
            print("Error en InformationSChema ",ex)
        tablas_borrar=self.cursor.fetchall()
        for tabla in tablas_borrar:
            print(f"----drop table {tabla[0]}")
            try:
                self.cursor.execute(f'drop table {tabla[0]}')
                print("se pudo borrar la tabla ",tabla[0])
            except Exception as ex:
                print("no se pudo borrar la tabla ",tabla[0],ex)
        
        abrirArchivo("inserts.txt","w") # reinicia el txt para que haga inserts de nuevo

    def detectarPuertosXampp(rutaXampp='C:/xampp/mysql/bin/my.ini'):
        try:
            with open(rutaXampp, 'r') as archivo:
                contenido = archivo.read()


            resultado_puerto = re.search(r'port[ ]*=[ ]*(\d+)', contenido)
            if resultado_puerto:
                puerto = int(resultado_puerto.group(1))  
                
            else:
                print("No hay puerto predeterminado")
                puerto =  None
            

            resultado_usuario = re.search(r'user[ ]*=[ ]*(\w+)', contenido)
            if resultado_usuario:
                usuario = resultado_usuario.group(1)
                
            else:
                print("No se encontró un nombre de usuario")
                usuario = "root"
            return puerto, usuario

        except FileNotFoundError:
            print(f"No se encontro Xampp en la ruta {rutaXampp}")
            return None, None
        

    # def detectarPuertoApache(rutaApache='C:/xampp/apache/conf/httpd.conf'):
    #     try:
    #         with open(rutaApache, 'r') as archivo:
    #             contenido = archivo.read()


    #         resultados = re.findall(r'^Listen[ ]+(\d+)', contenido, re.MULTILINE)
    #         if resultados:
    #             return [int(puerto) for puerto in resultados]
    #         else:
    #             print("No se encontraron datos 'Listen' en el archivo")
    #             return None
    #     except FileNotFoundError:
    #         print(f"No se pudo encontrar el archivo de configuración en {rutaApache}.")
    #         return None


    puertoXampp, usuarioXampp = detectarPuertosXampp()
    if puertoXampp:
        print(f"\nEl puerto de MySQL es {puertoXampp}")
        print(f"El nombre de usuario de MySQL es {usuarioXampp}")
    else:
        print("No se pudo encontrar el puerto de Xampp")


    # puertoApache = detectarPuertoApache()
    # if puertoApache:
    #     print(f"El puerto de Apache es {puertoApache}")
    # else:
    #     print("No se pudo encontrar")

    def ejecutarCreaciones(self,lista_funciones,confirmarCommit=False):
        if(not isinstance(lista_funciones,tuple)):
            #en caso de solo recibir una sola funcion(sin tupla) la convierte en iterable
            lista_funciones=(lista_funciones),
        
        for funciones in lista_funciones :
            try:
                #ejecuta la consulta
                self.cursor.execute(funciones())
                if(confirmarCommit):
                    #la confirma si asi se desea(pensado para los inserts)
                    self.connection.commit()
                print("+",funciones.__name__," se ha ejecutado con exito")
            except Exception as ex:
                print("-",funciones.__name__," ha tenido un error: ",ex)

    def crearTablas(self):
        try:
            print("##########empezo la creacion de tablas")
            #funciones que crearan las tablas
            tablas=(codigo_tabla_foto_perfil,codigo_tabla_rol,codigo_tabla_perfil,codigo_tabla_buzon_quejas,codigo_tabla_categoria,codigo_tabla_tema,codigo_tabla_subtema,codigo_tabla_sala,codigo_tabla_mensaje,codigo_tabla_peticiones,codigo_tabla_documentos,codigo_tabla_links,codigo_tabla_articulo,codigo_tabla_articulo_calificado,codigo_tabla_calificacion_comentario,codigo_tabla_comentario_articulo)

            self.ejecutarCreaciones(tablas)
            # self.tabla_perfil()
            # self.tabla_buzon_quejas()
            # self.tabla_categoria()
            # self.tabla_tema()
            # self.tabla_subtema()
            # self.tabla_sala()
            # self.tabla_mensaje()
            # self.tabla_peticiones()
            # self.tabla_documentos()
            # self.tabla_links()

            # self.tabla_articulo()
            # self.tabla_articulo_calificado()
            # self.tabla_calificacion_comentario()
            # self.tabla_comentario_articulo()
            

        except pymysql.Error as err:
            print("\n error al intentar crear las tablas " .format(err))
    def crearProcedimientos(self):
        try:
            print("##########empezo la creacion de procedimientos")
            # funciones que crearan los stored procedures sql
            funciones =(codigo_funcion_CrearSoloMateria,codigo_funcion_CrearSoloTema,codigo_funcion_CrearSoloSubtema,codigo_funcion_CrearMateriaCompleta,codigo_funcion_sacarPromedio,codigo_funcion_crearArticulo,codigo_funcion_calificarArticulo)

            self.ejecutarCreaciones(funciones)
            # self.funcion_CrearSoloMateria()
            # self.funcion_CrearSoloTema()
            # self.funcion_CrearSoloSubtema()
            # self.funcion_CrearMateriaCompleta()

            # self.funcion_sacarPromedio()
            # self.funcion_crearArticulo()
            # self.funcion_calificarArticulo()
            

        except pymysql.Error as err:
            print("\n error al intentar crear los procedimientos " .format(err))
    
    def hacerInserts(self):
        # txt="" o None->debe hacer inserts
        # txt="False" ->No debe hacer nada
        hacerInserts=abrirArchivo("inserts.txt","r") #abrimos el txt
        if(hacerInserts==None or hacerInserts.read()==""):
            #debe insertar
            abrirArchivo("inserts.txt","w").write("False")
        else:
            #hacerInserts.read() debe ser "False"
            #no quiero que insertes
            return 
        
        print("############ermpezaron los inserts")
        #funiones que haran los inserts
        inserts=(codigo_insert_Imagenes)
        # inserts=(codigo_insert_Roles,codigo_insert_Imagenes)
        self.ejecutarCreaciones(inserts,True)

    @staticmethod
    def crearHashParaBd(data):
        # Datos a hashear
        data = data.encode()
        # Crear hash
        hash_object = sha256(data)
        hash_hex = hash_object.hexdigest()

        print(f"Hash SHA-256: {hash_hex}")
        return hash_hex

    def crearMateriaCompleta(self,nombre_Materia,descripcion):
        tema=self.crearHashParaBd(f"{nombre_Materia}-General")
        subtema=self.crearHashParaBd(f"{nombre_Materia}-General-General")
        # print(f"('{nombre_Materia}',' desc ','{tema}','{subtema}')")
        self.cursor.callproc("crearCategoria",(nombre_Materia,descripcion))

    def ejecutarQuery(self,query,commit=False,fetch=None):
        try:
            self.cursor.execute(query)
            if(commit):
                self.connection.commit()
            if(fetch==None):
                return True
            
            if(fetch==1):
                return self.cursor.fetchone()
            if(fetch==0):
                return self.cursor.fetchall()
            if(fetch>0):
                return self.cursor.fetchmany(fetch)
        except Exception as ex:
            print("#--",ex)
            return False

cx=None


if(__name__=="__main__"):
    # cx=CC(('perfil','categoria','tema','subtema')) # con esta linea eliminas todo con excepcion de las tablas ahi mencionadas
    # cx=CC(('perfil')) # con esta linea reinicias todo, con excepcion de la tabla 'perfil'
    # # cx=CC(('')) #con esta linea restauras toda la bd
    cx=CC() # inicio normal sin autodestruccion
    input("Eviando que sierre...")
    # from io import BytesIO
    # from PIL import Image

    # res=cx.ejecutarQuery("select * from fotos_perfil",fetch=0)
    # for r in res:
    #     print("-",r[1][:20],"...")
    #     try:
    #         Image.open(BytesIO(r[1])).show()
    #     except Exception as ex:
    #         print("fallido")
    #         pass