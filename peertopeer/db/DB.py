import pymysql
from colorama import Back,Fore
import re
import os
from hashlib import sha256
from colorama import Fore,Back
# from utiles.myprint import myprint
colorImpresion=Back.BLUE

if(__name__=="__main__"):
    from bdTablas import * 
    #from peertopeer.utiles.myprint import myprint
else:    
    from utiles.myprint import myprint
    from .bdTablas import *

def myprint(*args): 
    print(f"{colorImpresion}", end=" ")
    for arg in args:
        print(arg , end=" ")
    print(f'{Back.GREEN}', end="\n")


def abrirArchivo(archivo,modo):
    ruta=(__file__.split("peertopeer")[0]+"peertopeer\\utiles\\").replace("\\","/")+archivo

    # myprint(f"ruta={ruta}")
    try:
        #intenta abrir el archivo
        return open(ruta,modo)
    except Exception as ex:
        myprint(ex)
        #no existe o se ingreso un modo invalido
        return None
myprint("BD")

class CC():
    def __init__(self,auto_destruir=None):
        try:
            self.connection = pymysql.connect(host='localhost', user=self.usuarioXampp, passwd='', port=self.puertoXampp, db='peertopeer')
            self.cursor = self.connection.cursor()
            myprint("\n Conexion exitosa")

            try:
                if(auto_destruir!=None):
                    self.auto_destruccion(auto_destruir)
                self.crearTablas()
                self.crearProcedimientos()
                self.hacerInserts()

            except pymysql.Error as err:
                myprint("\n error al intentar crear las tablas o procedimientos: " .format(err))
            
        except pymysql.Error as err:
            self.connection = pymysql.connect(host='localhost', user=self.usuarioXampp, passwd='', port=self.puertoXampp)
            self.cursor = self.connection.cursor()
            self.cursor.execute("CREATE DATABASE IF NOT EXISTS peertopeer")
            self.connection.commit()
            self.cursor.execute("USE peertopeer")
            myprint("\nCreacion exitosa")

            try:
                self.crearTablas()
                self.crearProcedimientos()
                self.hacerInserts()


            except pymysql.Error as err:
                myprint("\n error al intentar crear las tablas o procedimientos: " .format(err))

    def auto_destruccion(self,tablas_excepcion=()):
        myprint("GOKUUUUUUUUUUUUUUUUUUUUUUUAH!")
        abrirArchivo("inserts.txt","w") # reinicia el txt para que haga inserts de nuevo

        adicional=""
        for tabla in tablas_excepcion:
            # and table_name!='perfil'
            adicional+=f"and table_name!='{tabla}' "

        if(adicional==""):
            res=self.ejecutarQuery("drop database peertopeer")
            self.ejecutarQuery("create database peertopeer")
            self.ejecutarQuery("use peertopeer")
            return res

        try:
            self.cursor.execute(f"select table_name from INFORMATION_SCHEMA.tables where table_schema='peertopeer' {adicional} order by create_time desc ;")
        except Exception as ex:
            myprint("Error en InformationSChema ",ex)
        tablas_borrar=self.cursor.fetchall()
        for tabla in tablas_borrar:
            myprint(f"----drop table {tabla[0]}")
            try:
                self.cursor.execute(f'drop table {tabla[0]}')
                myprint("se pudo borrar la tabla ",tabla[0])
            except Exception as ex:
                myprint("no se pudo borrar la tabla ",tabla[0],ex)
        
        # abrirArchivo("inserts.txt","w") # reinicia el txt para que haga inserts de nuevo

    def detectarPuertosXampp(rutaXampp='C:/xampp/mysql/bin/my.ini'):
        try:
            with open(rutaXampp, 'r') as archivo:
                contenido = archivo.read()


            resultado_puerto = re.search(r'port[ ]*=[ ]*(\d+)', contenido)
            if resultado_puerto:
                puerto = int(resultado_puerto.group(1))  
                
            else:
                myprint("No hay puerto predeterminado")
                puerto =  None
            

            resultado_usuario = re.search(r'user[ ]*=[ ]*(\w+)', contenido)
            if resultado_usuario:
                usuario = resultado_usuario.group(1)
                
            else:
                myprint("No se encontró un nombre de usuario")
                usuario = "root"
            return puerto, usuario

        except FileNotFoundError:
            myprint(f"No se encontro Xampp en la ruta {rutaXampp}")
            return None, None
        

    # def detectarPuertoApache(rutaApache='C:/xampp/apache/conf/httpd.conf'):
    #     try:
    #         with open(rutaApache, 'r') as archivo:
    #             contenido = archivo.read()


    #         resultados = re.findall(r'^Listen[ ]+(\d+)', contenido, re.MULTILINE)
    #         if resultados:
    #             return [int(puerto) for puerto in resultados]
    #         else:
    #             myprint("No se encontraron datos 'Listen' en el archivo")
    #             return None
    #     except FileNotFoundError:
    #         myprint(f"No se pudo encontrar el archivo de configuración en {rutaApache}.")
    #         return None


    puertoXampp, usuarioXampp = detectarPuertosXampp()
    if puertoXampp:
        myprint(f"\nEl puerto de MySQL es {puertoXampp}")
        myprint(f"El nombre de usuario de MySQL es {usuarioXampp}")
    else:
        myprint("No se pudo encontrar el puerto de Xampp")


    # puertoApache = detectarPuertoApache()
    # if puertoApache:
    #     myprint(f"El puerto de Apache es {puertoApache}")
    # else:
    #     myprint("No se pudo encontrar")

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
                myprint("+",funciones.__name__," se ha ejecutado con exito")
            except Exception as ex:
                myprint("-",funciones.__name__," ha tenido un error: ",ex)

    def crearTablas(self):
        try:
            myprint("##########empezo la creacion de tablas")
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
            myprint("\n error al intentar crear las tablas " .format(err))
    def crearProcedimientos(self):
        try:
            myprint("##########empezo la creacion de procedimientos")
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
            myprint("\n error al intentar crear los procedimientos " .format(err))
    
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
        
        myprint("############ermpezaron los inserts")
        #funiones que haran los inserts
        inserts=(codigo_insert_Roles,codigo_insert_Imagenes,codigo_insert_usuario)
        # inserts=(codigo_insert_Roles,codigo_insert_Imagenes)
        self.ejecutarCreaciones(inserts,True)

    @staticmethod
    def crearHashParaBd(data):
        # Datos a hashear
        data = data.encode()
        # Crear hash
        hash_object = sha256(data)
        hash_hex = hash_object.hexdigest()

        myprint(f"Hash SHA-256: {hash_hex}")
        return hash_hex

    def ejecutarProcedimiento(self,nombreProcc,args,fetch=None):
        cadUnion=""
        complemento=""
        myprint(f"{nombreProcc}({args})")
        # myprint("inicia procc")
        for arg in args:
            complemento=""
            myprint(arg)
            if(isinstance(arg,str)):
                complemento="'"
            cadUnion+=complemento+"%s"+complemento+","
        myprint(f"comp={complemento}")
        if(not fetch):
            # no devuelve fetch, por lo que la comilla sobra
            quitar=1 #quita la coma
            cadUnion=cadUnion[:-1]

        if(fetch):
            cadUnion+="%s"

        query="call %s (%s)"%(nombreProcc,cadUnion)
        tupla=()
        for elemento in args:
            tupla+=elemento,
        if(fetch):
            tupla+=fetch,
        myprint("query=",query)
        myprint("tupla=",tupla)

        myprint(query%tupla)
        self.ejecutarQuery(query%tupla)
        res=self.ejecutarQuery(f"select {fetch}",fetch=1)[-1]
        self.connection.commit()
        return res

    def crearCategoriaCompleta(self,nombre_categoria,descripcion):
        tema=self.crearHashParaBd(f"{nombre_categoria}-General")
        subtema=self.crearHashParaBd(f"{nombre_categoria}-General-General")
        # myprint(f"('{nombre_categoria}',' desc ','{tema}','{subtema}')")
        res=0
        self.ejecutarQuery("call crearCategoriaCompleta('%s','%s','%s','%s',@res)"%(nombre_categoria,descripcion,tema,subtema))
        res=self.ejecutarQuery("select @res",fetch=1)[0]
        myprint(res)
        #self.cursor.nextset()
        if(res==1):
            self.connection.commit()
        return res
    
    def crearTema(self,id_categoria,nombre_subtema,descripcion):
        # nomb,descripcion,id_categ,codigotema,res
        myprint("crear tema")
        nombre_categoria=self.ejecutarQuery("select nombre from categoria where id_categoria=%s"%(id_categoria) , fetch=1)[0]
        hash=self.crearHashParaBd(f"{nombre_categoria}-{nombre_subtema}")

        res=self.ejecutarProcedimiento("crearTema",(nombre_subtema,descripcion,id_categoria,hash),fetch="@res")
        myprint(res)
        return res
    
    def crearSubtema(self,id_tema,nombre_subtema,descripcion):
        # nomb,descripcion,idtema,codigosubtema,resultado
        nombres=self.ejecutarQuery("select t.nombre,c.nombre from tema t join categoria c on t.id_categoria=c.id_categoria where id_tema=%s"%(id_tema),fetch=1)
        hash=self.crearHashParaBd(f'{nombres[0]}-{nombres[1]}-{nombre_subtema}')
        myprint(f'{nombres[0]}-{nombres[1]}-{nombre_subtema}')
        
        res=self.ejecutarProcedimiento("crearsubtema",(nombre_subtema,descripcion,id_tema,hash),"@res")
        myprint(res)
        self.connection.commit()
        return res

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
            myprint("#--",ex)
            return False

cx=None


if(__name__=="__main__"):
    # cx=CC(('perfil','categoria','tema','subtema')) # con esta linea eliminas todo con excepcion de las tablas ahi mencionadas
    # cx=CC(('perfil')) # con esta linea reinicias todo, con excepcion de la tabla 'perfil'
    # cx=CC(('')) #con esta linea restauras toda la bd
    cx=CC() # inicio normal sin autodestruccion
    input("Eviando que sierre...")
    # from io import BytesIO
    # from PIL import Image

    # res=cx.ejecutarQuery("select * from fotos_perfil",fetch=0)
    # for r in res:
    #     myprint("-",r[1][:20],"...")
    #     try:
    #         Image.open(BytesIO(r[1])).show()
    #     except Exception as ex:
    #         myprint("fallido")
    #         pass
