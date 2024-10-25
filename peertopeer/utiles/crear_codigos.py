import random
import string

def generar_codigo_aleatorio():
    caracteres = string.ascii_letters + string.digits + string.punctuation
    codigo = ''.join(random.choice(caracteres) for _ in range(12))
    return codigo

# Ejemplo de uso
codigo_aleatorio = generar_codigo_aleatorio()
print(codigo_aleatorio)
