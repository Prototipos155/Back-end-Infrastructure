from .conexion import Conexion
test = False
class Admin():
    SQLFile='DB.sql'
    db='EducamEsta'
    def __init__(self):
        self.cx=Conexion(self.db,1,self.SQLFile)
    
    def execute(self,query):
        return self.cx.execute_query(query)

    def existsDataInTable(self,table,rows_to_return,row_compairing_name,value):
        self.execute(f"select {rows_to_return} from {table} were {row_compairing_name} = {value}")
        return self.cx.getFetch()
        
    def existsDataInPerfiles(self,correo,numcontrol,telefono,contraseña):
        datos=(
            [correo,'numeroControl'],
            [numcontrol,'correoInstitucional'],
            [telefono,'telefono'],
            [contraseña,'contraseña']
            )

        c=0
        while c<len(datos):
            if(self.existsDataInTable('perfil',datos[c][1],datos[c][1],datos[c][0])[0] != None):
                return c
            c+=1
        
        return -1
        
    def logInUser(self,numControl,correoInst,telefono,psw,
            nickName,grado,grupo,
            nombres,apellidos,numTarjetaBienestar,nombreEscuela,idGradoAvance
            ):
        self.cx.callProcedure()

    def logInAlumn(self,numControl,correoInst,telefono,psw,nickName,grado,grupo):
        print('PROCEDIMIENTO ALUMNO')
        self.cx.callProcedure('InsertIntoAlumno',(numControl,correoInst,telefono,psw,nickName,grado,grupo))
        
    def logInTutor(self,numControl,correoInst,telefono,psw,nombres,apellidos,numTarjetaBienestar,nombreEscuela,idGradoAvance):
        print('PROCEDIMIENTO TUTOR')
        self.cx.callProcedure('InsertIntoTutor',(numControl,correoInst,telefono,psw,nombres,apellidos,numTarjetaBienestar,nombreEscuela,idGradoAvance))

    def close(self):
        self.cx.close()

if(test):
    a=Admin()

    a.logInAlumn('22301061553360','22301061553360@cetis155.edu.mx','7839123848','contraseñ','pepito',3,'A')
    a.logInTutor('22301061553361','22301061553361@cetis155.edu.mx','7839120048','contraseñ','oscar','guzaman alvedo','1234123340989301','josefa ortiz de dominguez','bachillerato')