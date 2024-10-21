# NOTA: PARA DECLARAR LAS LIBRERIAS A INSTALAR SE NECESITA CREAR UN ARCHIVO TXT LLAMADA:'libs_to_install.txt'
    #parar crear dicho archivo puedes optar por ejecutar este programa una vez, lo creara automaticamente si no lo encuentra.
    #solo seria modificarlo para añadir las librerias a instalar
import subprocess
import os

os.chdir('./')

def getActualDirection():
    #obtiene la direccion de la carpeta actual
    return "/".join(__file__.split("\\")[:-1])+"/"

direccion_apertura_de_archivos=getActualDirection()

class Librerias:
    def __init__(self,librerias):
        if(librerias==None or librerias!=""):
            self.librerias=librerias.split(',')
            print(self.librerias)
            __spec__

    def ejecutarComandos(self):
        instaladas=()
        for lib in self.librerias:
            if(self.executeInTerminal(f'pip show {lib}')==-1):
                print('hay que instalar %s'%(lib))
                r=self.executeInTerminal('pip3 install %s'%(lib))
            else:
                r=3

            print(lib, end="")
            if r==-1:
                lib+="(ERROR)"
                print(" tuvo un error")
            elif r==3:
                print(" ya estaba instalada")
            else:
                print(" se ha instalado correctamente")
            instaladas+=lib,
                
                            
            print('---------------------------------')
        
        return instaladas

    def executeInTerminal(self,comando):
        try:
            r=subprocess.run(comando, shell=True, check=True)
            #print(f"El comando se ejecutó correctamente:{comando}")
            return 1
        except subprocess.CalledProcessError as e:
            #print(f"Hubo un error al ejecutar el comando: {e}\n")
            return -1
""" 
flujo de la instalacion:
    1.-existe el archivo de instalados?:
        no:
            -creamos el archivo
            -instalamos las librerias
        si:
            -leemos el archivo de libs a instalar
            -leemos el archivo de instalados
            -son inguales?
                si
                    termina el proceso, ya no hay nadad que hacer
                no
                    -instalamos la libreria


"""

def instalarLibrerias():
    try:
        libs=getLibsForInstall('r')
    except Exception:
        open(f'{direccion_apertura_de_archivos}libs_to_install.txt','x')
        getLibsForInstall('w').write(getInstallLibsTextDescription())
        print('__termino de escribir la instrucciones')

    print('empezo a leer el libs to install')
    libs=getLibsForInstall('r').replace("\n",",")
    try:
        open(f'{direccion_apertura_de_archivos}installed.txt','x')
        print('no hay libs instaladas(se acaba de crear el archivo installed.txt)')
        
        actualizarInstalados(libs)
        # no existe el archivo instalado.txt
    except Exception:
        print('ya existe el acrhivo de instalados')
        #ya existe el archivo instalado
        libs_act=getLibsInstaled('r')

        if len(libs_act.split('(ERROR)')) >1:
            print("EN TUS LIBRERIAS HUBO UN ERROR")
            return
        
        # libs_act=libs_act.split(getInstallLibsTextDescription())[1]

        # libs_act_txt=libs_act.split('sintaxis: nombre_libreria,nombre_libreria2,etc\n-')
        print(f"__{libs}==?{libs_act}")
        if libs!=libs_act:
        # if libs!=libs_act_txt:
            libs=actualizarInstalados(libs)
        print('ya estan instaladas las librerias: %s'%(libs))

def getInstallLibsTextDescription():
    return 'NOTA: por cada renglon solo debe haber una libreria\nIngresa Las Librerias a partir de la siguiente linea:\n'

def actualizarInstalados(libs_to_install):
    libreria=Librerias(libs_to_install)
    install=",".join(libreria.ejecutarComandos())
    #print(f"{install}!={libs_to_install}")
    if(install!=libs_to_install):
        print("HUBO UN ERROR EN LAS LIBRERIAS")
        
    getLibsInstaled('w').write(install)
    return install

def getLibsForInstall(accion):
    libs=open(f'{direccion_apertura_de_archivos}libs_to_install.txt', accion)
    if accion=='r':
        return libs.read().split(getInstallLibsTextDescription())[1]
    return libs

def getLibsInstaled(accion):
    libs=open(f'{direccion_apertura_de_archivos}installed.txt', accion)
    if accion=='r':
        return libs.read()
        
    return libs

if(__name__=="__main__"):
    print("install")
    instalarLibrerias()
