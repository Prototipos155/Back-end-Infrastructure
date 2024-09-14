db='irrepe'
class DbLocator():
    nextIno=False
    def __init__(self,sentencia):
        self.isDB(sentencia)
    
    def isDB(self,s):
        s2=s.split(db)
        
        for a in s2[1::]:
            self.locateDB(a)

    def locateDB(self,bloqueSeccc):
        if(self.nextIno==True):
            #bucle pasado encontro que este bloque es inocente de ser una DB
            self.nextIno=False
            return False

        div=bloqueSeccc.split('.')

        if(len (div)==1):
            #no hubo punto alguno, es decir, corto en una db(probablemente)
                #el siguiente bulce debe confirmar o desmentirlo
            return True
        
        if(div[-1]==''):
            #la instruccion fue cortada por un punto a final, que estaba seguido
                # del nombre de la DB
            #la instruccion que sigue es inocente
            self.nextIno=True

        # if(div[1]==' '):       
        if div[0].replace(' ','')=='':
            print(f'aqui es una db({a})')

s="""

select * from irrepe .kol join irrepe.col2 where irrepe. kol.campo=
irrepe .col2.irrepe

"""

"""
#[select * from ]
[  .kol join ]
[.col2 where ]
[. kol.campo= ]
[.col2.]

[insert into ]irrepe
[_12 values(a,b,c),(a,b,c)]

[insert into ]irrepe
[_12 values(a,b,c),(a,b,c)]

[select * from ]irrepe
[ .irre]

[select * from ]irrepe
[_12 .irrepe ]
"""

DbLocator(s)