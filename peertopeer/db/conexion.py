import pymysql
from colorama import init, Fore, Back, Style
from .open import SQLFile
import sqlite3
import re

class Conexion:
    conn=None
    archivoVersion='dbVersion.txt'
    print=True
    cursor=True
    db=None
    fetch= True

    instrucciones=["use","insert","select","update","delete",'create',"drop"]
    
    
    def __init__(self,database=None,version=None,archivoSQL=None):
        if(database==None and version==None and archivoSQL==None):
            print(self.detectar_Instruccion('use schema infinito'))
            return 
        
        self.makeConexionSQL()
        self.db=database

        self.version=version
        self.archivoSQL=archivoSQL
        
        self.cursor = self.conn.cursor()


        self.conectarDB(self.getArchivoVersionDB())
    
    def getArchivoDir(self,archivo):
        return f'peertopeer/db/{archivo}'
    
    def getArchivoVersionDB(self):
        try:
            return open(self.getArchivoDir(self.archivoVersion),'r').read()
        except Exception:
            open(self.getArchivoDir(self.archivoVersion),'x')
            #open(self.getArchivoDir(self.archivoVersion),'w').write()
            return ''
    
    def setNewFileVersion(self,version):
        open(self.getArchivoDir(self.archivoVersion),'w').write(f'{version}')
    
    def makeConexionSQL(self):
        try:
            self.conn= pymysql.connect(host='localhost', user='root', password="risemivicio125")
            #    print("Conexion 1")
        except Exception:
            self.conn= pymysql.connect(host='localhost', user='root', password="")
            #    print("Conexion 2")
            
    def execute_query(self,query):
        try:
            #print(Back.MAGENTA+query+Back.RESET)
            if( self.print):
                print(query)
            else:
                print(query[:20])
            ##Ejecuta la consulta
            self.cursor.execute(query)
            #continua si la expresion es posible
            
            #detecta la instruccion principal de la consulta
            c=self.detectar_Instruccion(query)
            print(f"{Back.CYAN}___Consulta exitosa{Back.RESET}")

            #    print(f"c={c}")
            if c==2:
                self.fetch=self.cursor.fetchall()
            else:
                self.conn.commit()
                
            return 1
        except Exception as e:
            ##consulta mal formulada o imposible
            if( self.print==False):
                print(f'!========{query}!=======')
            print(f"{Back.RED}____________>Fallo La consulta{Back.RESET}({e})")
            print()
            return -1
    
    def callProcedure(self,procedureName,parametersTuple=None,returnFetch=False):
        try:
            if parametersTuple!=None: 
                self.cursor.callproc(procedureName,parametersTuple)            
            else:
                self.cursor.callproc(procedureName)
            self.conn.commit()

        except Exception as e:
            print(e)
            return e
        
        if (returnFetch):
            return self.cursor.fetchall()
    
    def detectar_Instruccion(self,query):
        #    print("  __det consult")
        query=query.lower()    
        SinEspacios=query.replace(" ","").replace('\n','')

        c=0       
        
        for instrucc in self.instrucciones:
            if((SinEspacios.split(instrucc))[0]==""):
                return c
            c+=1
    
    def executeSQLFile(self,extension):
        self.file=SQLFile()
        #self.print=True
        self.showQuery(False)

        with open(self.getArchivoDir(self.archivoSQL), "r",encoding="utf-8") as archivo:
            c=0
            #print('EXTENSION:',extension)
            while True:
                
                self.SqlQueries=self.file.getSQLines(archivo) 

                # print(f'{Back.GREEN}QUERYS:[')
                # print("\n.--".join(self.SqlQueries))
                # print(f'======<FIN{Back.RESET}')

                for i in self.SqlQueries:
                    #ubicamos la instuccion
                    #print(f'__i={i}')
                    i=i.lower().replace('database','schema',1)
                    indexDB=i.lower().find(self.db.lower())

                    # if(extension !=''):
                    #     print(f'{Back.WHITE}EXECUTE SIN PROBLEMAS__{Back.RESET}')
                    #     self.execute_query(i)

                    inst=self.detectar_Instruccion(i)
                    # if(indexDB!=-1):
                    #     # hay que hacer una operacion en la db ya que nuestra DB tuvo que ser renombrada por una extension          
                    #     print('EXECUTE CON UNA PEQUEÑA MODIFICACION')

                    divididos=i.split('begin')

                    if (len(divididos)>1 and extension !='' and indexDB!=-1):
                        dbChanged=[]
                        #estamos trabajando una funcion/ bloque begin...end
                        # a su vez la db tiene un nombre repetido
                        # y aqui aparece el nombre de la db en algun lado

                        for instOfBlock in divididos[1].split(';'):
                            #recorremos las insrtrucciones del bloque y hay que remplazar las bd en caso de usarlas
                            # instOfBlock.lower().split(self.db.lower())
                            
                            dbChanged.append(self.corregirDB(instOfBlock,extension))
                        self.execute_query(divididos[0]+'begin\n'+';'.join(dbChanged))

                    else:
                        if(inst ==6 or inst ==5) and indexDB!=-1 and len(divididos)==1:
                            # requiere crear o borrar la db
                            # res=re.search('create schema',i,re.IGNORECASE)
                            print(f'{Back.MAGENTA}NEL PERRO, NO DEJARE QUE LE HAGAS {self.instrucciones[inst]}{Back.RESET}')
                        else:
                            if(extension==''):
                                self.execute_query(i)
                            else:
                                self.execute_query(i.lower().replace(self.db.lower(),f'{self.db}{extension}'))    
                
                if self.SqlQueries==[''] or self.SqlQueries==[]:
                    #print('PM:{',self.file.primera_mitad,'}')
                    print(f'{Back.RED}FIN DE LA LECTURA{Back.RESET}')
                    if(len(self.file.primera_mitad)>1):
                        self.execute_query(self.file.primera_mitad)
                    break
                c+=1
        self.showQuery(True)

    def corregirDB(self,query,extension):
        # aqui deberia de instanciar un objeto DBLocator cuando le de un algoritmo que funcione
        divd=query.lower().split(self.db.lower())
        #print(divd)
        c=0
        index=0
        queryAdapted=''
        while index < len(divd):
            x=divd[index]
            print(f'{c}:({c+len(x)})')
            queryAdapted+=query[c:(c+len(x))]
            if(index!=len(divd)-1):
                queryAdapted+=self.db+extension
            c+=len(x)+10
            index+=1
        return queryAdapted

    def crear_DB(self,extension):
        if(extension!=''):
            extension=f'_{extension}'
        self.execute_query(f"drop schema if exists {self.db+extension}")
        #self.execute_query(f"create schema {self.db+extension}")
        self.execute_query(f"create schema {self.db+extension}")

        self.execute_query(f"use {self.db+extension}")
        

        self.executeSQLFile(extension)

        query='create table version( version int not null);'
        self.execute_query(query)
        query='insert into version values(%s);'%(self.version)
        self.execute_query(query)

    def getFromVersion(self):
        r=self.execute_query('select version from version')
        if r==-1:
            return None
        return self.getFetch()[0]
        
    def conectarDB(self,extension):
        # print("\n\n\n CONECTAR")
        print('conectar')
        use="use "+self.db
        if extension!='':
            #no es un nombre unico para una bd, asi que agregemosle el numero de spiderman que somos
            use+=f'_{extension}'

        if self.execute_query(use)==-1:
            print('No existe la db')
            #fallo la conexion a la db
            #no existe
            if self.getArchivoVersionDB()!=extension:
                # la extension/version libre de la db no concuerda con la marcada en el archivo de Version

                self.setNewFileVersion(extension if extension!='' else 1)

            self.crear_DB(extension)
            return 
        #existe la db
        print("EXISTE LA DB")

        #select a la tabla version en la DB
        ver=self.getFromVersion()
        if ver ==None:
            print('no es nuestra db(no existe tabla version)')
            #no esta agregada la tabla de version, es decir, no es nuestra base de datos
            if extension=="": 
                #es el primer fallo
                self.conectarDB("1")
            else: 
                #ya van varias bd a las que se intento conectar
                self.conectarDB(str(int(extension)+1))
            return
        print(f'VERSION ={ver[0]}')
        print(f'VERSION 2 ={self.version}')

        if int(ver[0])!=int(self.version):
            print('la db esta desactualizada')
            # el campo version en la DB no concuerda con el que deberia ser
            self.crear_DB(extension)
            return 
        else:
            print('DB ACTUAL SIN NECESIDAD DE CAMBIOS')

    def getFetch(self):
        return self.fetch
    
    def reiniciarContatorAuto(self,tabla):
        self.execute_query(f"ALTER TABLE {tabla} AUTO_INCREMENT=0")
    
    def close(self):
        self.conn.close()
        self.cursor.close()
    
    def showQuery(self,booleano):
        self.print=booleano


#cx=Conexion('EducamEsta',1,'DB.sql')