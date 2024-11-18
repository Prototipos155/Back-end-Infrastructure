import os

current_dir = os.path.dirname(os.path.abspath(__file__))

cert_path = os.path.join(current_dir,'utiles', 'server.crt')
key_path = os.path.join(current_dir,'utiles', 'server.key')

# Verifica si los archivos existen
if not os.path.exists(cert_path):
    print(f"El archivo de certificado no se encuentra: {cert_path}")
else:
    print(f"El archivo de certificado se encuentra: {cert_path}")

if not os.path.exists(key_path):
    print(f"El archivo de clave no se encuentra: {key_path}")
else:
    print(f"El archivo de clave se encuentra: {key_path}")
