from colorama import Fore,Back
import re
#   POSIBLES ESCENARIOS

#>>> 'unidos; asdaas;asdsad'.split(";")
#['unidos', ' asdaas', 'asdsad']

#>>> 'unidos; asdaas;asdsad;'.split(";")
#['unidos', ' asdaas', 'asdsad', '']

#>>> '123333 nknk1j2 bc1k c '.split(';')
#['123333 nknk1j2 bc1k c ']

# bloque=[]
# bloque+='12341'
# bloque
# ['1', '2', '3', '4', '1']
# bloque+='12341',
# bloque
# ['1', '2', '3', '4', '1', '12341']

prueba =False

class SQLFile(): 
    # principal problematica a resolver: tomar instrucciones incompletas que cotinuan en el siguiente bloque de read()
    #debo separar por ';'
    # asi como almacear las pars incompletad y unirlas cuando se complete la instrccion
    primera_mitad=None
    bloque=None
    buscaFin=None
 
    def isLastIncomplete(self):
        if self.bloque[-1:]!="":
            #el ultimo split del texto esta lleno, es decir, el bloque no termino en ';'.Por ende,
                #tomo la mitad de una intruccion que continuara en el siguiente bloque
            self.primera_mitad=self.bloque[-1:][0]
            self.bloque=self.bloque[:-1]
            return 1
        #todas las instrucciones estan completas
        #self.primera_mitad=None
        return -1

    def esPuntoYComa(self,bloque):
        return (len(bloque)==2  and bloque[0].replace(' ','')=='' and bloque[1].replace(' ','')=='')
    
    def isMidInstruccion(self):
        return (self.primera_mitad!=None)
    
    def unirInstruccion(self):
        if self.esPuntoYComa(self.bloque) or self.isMidInstruccion() ==False:
            #solo se tomo un misero ';'
                            # O
            #en el bucle pasado no hubo instruccion incompleta al final
            #no hay necesidad de unir
                # (condicionales en order de acuerdo a lo aqui dicho)
            return -1
        
        if (len(self.bloque)==1 and self.bloque[0]!=''):
            #el bucle pasado tomo la mitad de una instruccion
            #   y el actual tomo otra parte, pero no la final
            #print('LEN =1')
            self.primera_mitad+=self.bloque[0]
            return 1
        
        #bucle pasado tomo la primer mitad de una intruccion
        #   eso significa que ya tenemos la instruccion completa
        #hay que unir ambas partes
        if self.bloque[0]=='':
            # emplieza el bloque con un ';', seguido de una instruccion, tal vez incompleta.Eso se vera en la siguiente fase
            self.bloque[0]=self.primera_mitad
            return 2
        
         
        #empieza el bloque con una instruccion, pueden ser varias
        self.bloque[0]= self.primera_mitad+self.bloque[0]
        #unidas
        return 3    

    def functionIncomplete(self,buscaFin=None):
        index=0
        for inst in self.bloque :
            if(not (self.containsAgroup(inst)==-1 and buscaFin==None)):
                #o bien encontramos un 'begin' o estamos buscando un 'end'

                if(self.containsAgroup(inst)!=-1):
                    print('INICIO DEL BEGIN :',index)
                    #este bloque contiene el inicio de un delimiter
                    buscaFin =index
                    
                if(self.containsAgroup(inst,True)!=-1):
                    #este bloque contiene el fin de un delimiter
                    if(buscaFin==index):
                        #encontramos el fin en la misma instruccion
                        print('begin...end en la misma linea')
                        buscaFin=False
                    else:
                        #encontramos el fin en otra linea
                        print(f'founded({index})')
                        index-=self.joinBlock(buscaFin,index)
                        buscaFin=None
                
            index+=1
        if (buscaFin!=None):
            print('NO SE ENCONTRO EL END EN EL BLOQUE')
            #alv, no esta el bloque end en esta lectura, hay que probar en la siguiente
            self.joinBlock(buscaFin,index)
            self.buscaFin= buscaFin

        self.buscaFin= False

    def recortarDelimiter(self,indexBegin):
        self.bloque[indexBegin]=self.bloque[indexBegin].replace('//','')
        
        for res in re.finditer('delimiter',self.bloque[indexBegin],re.IGNORECASE):
            self.bloque[indexBegin]=self.bloque[indexBegin].replace(self.bloque[indexBegin][res.start()::][:9],'')


    def joinBlock(self,indexBegin,indexEnd):
        print('JOINBLOCK')
        #begin ....     7
        #   update...;  8
        #   update...;  9
        #end;           10
        self.bloque[indexBegin]+=';'

        for times in range(indexEnd-indexBegin):
            print(f'parte{times+1}:=={self.bloque[indexBegin+1]}')
            self.bloque[indexBegin]+=self.bloque[indexBegin+1]
            if(times<(indexEnd-indexBegin-1)):
                self.bloque[indexBegin]+=';'
            self.bloque.remove(self.bloque[indexBegin+1])

        
        self.recortarDelimiter(indexBegin)
        
        print(f'final bloxk={self.bloque[indexBegin]}')
        return (indexEnd-indexBegin)

    def containsAgroup(self,inst,delimiterFin=None):
        return inst.lower().find("end" if delimiterFin else "begin")

    
    def getSQLines(self,archivo): 
        #quitamos los espacios en blanco de mas
        self.bloque= archivo.read(3500).replace('  ',' ')
        #print('Bloque sql:{',self.bloque,'}')
        
        #separamos por lineas sql
        self.bloque=self.bloque.split(";") 

        # escenarios:
        # medio o inicio
        #   ['abc']
        # fin
        #   ['abc','']
        # varias:
        #     ['abd','sads','']
        self.functionIncomplete(self.buscaFin)
        self.unirInstruccion()

        self.isLastIncomplete()
        #print('LAST(TERMINO):{',self.primera_mitad,'}')
        return self.bloque

if(prueba):
    bloque=[]
    file=SQLFile()

    archivo =open('DB2.sql', "r",encoding="utf-8")
    file.getSQLines(archivo)
    file.getSQLines(archivo)

        
