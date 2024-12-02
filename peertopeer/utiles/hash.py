from Crypto.Cipher import AES
from dotenv import load_dotenv
import os
import base64
import hashlib

load_dotenv()


class Encrypt:
        
    def encrypted_gcm(self, encriptar: str, password: str = os.getenv("PASSWORD3")) -> str:
        salt = os.urandom(AES.block_size)
        private_key = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1, dklen=32)

        cipher = AES.new(private_key, AES.MODE_GCM)
        ciphertext, tag = cipher.encrypt_and_digest(encriptar.encode())

        # Combina nonce, salt, tag y ciphertext en un solo mensaje en Base64
        encrypted_data = base64.b64encode(cipher.nonce + salt + tag + ciphertext).decode('utf-8')
        
        return encrypted_data

    
    
    def decrypt_gcm(self, encriptar:str, password : str = os.getenv("PASSWORD3")):
        decode_data = base64.b64decode(encriptar)

        nonce = decode_data[:AES.block_size]
        salt = decode_data[AES.block_size:AES.block_size*2]
        tag = decode_data[:AES.block_size*2:AES.block_size*2+16]
        ciphertext = decode_data[AES.block_size*2+16]
        
        private_key = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1, dklen=32)

        cipher = AES.new(private_key, AES.MODE_GCM, nonce = nonce)
        return cipher.decrypt_and_verify(ciphertext, tag).decode('utf-8')


    def verify_gcm(self, encriptar: str, encrypted_data: str, password: str = os.getenv("PASSWORD3")) -> bool:
        # Asegura que encrypted_data tenga el padding adecuado para ser decodificado
        encrypted_data += "=" * ((4 - len(encrypted_data) % 4) % 4)
        
        # Decodifica los datos en Base64
        encrypted_bytes = base64.b64decode(encrypted_data)

        # Extrae nonce, salt, tag y ciphertext
        nonce = encrypted_bytes[:16]
        salt = encrypted_bytes[16:32]
        tag = encrypted_bytes[32:48]
        ciphertext = encrypted_bytes[48:]

        # Deriva la clave privada usando el salt y la password
        private_key = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1, dklen=32)

        # Cifra y verifica con el nonce
        cipher = AES.new(private_key, AES.MODE_GCM, nonce=nonce)

        try:
            # Desencripta y verifica el tag
            decrypted = cipher.decrypt_and_verify(ciphertext, tag)
            return encriptar == decrypted.decode('utf-8')
        except (ValueError, KeyError):
            return False
            
"""
encryption_manager = Encrypt()

texto_original = input("Ingresa el texto que deseas cifrar: ")
password = os.getenv("PASSWORD3")  # Asegúrate de tener "PASSWORD3" en las variables de entorno

encrypted_text = encryption_manager.encriptar_gcm(texto_original, password)
print("Texto cifrado:", encrypted_text)

resultado_verificacion_correcta = encryption_manager.verificar_gcm(texto_original, encrypted_text, password)
print("Verificación correcta:", resultado_verificacion_correcta)  # Espera True

if resultado_verificacion_correcta:
    print("La verificación fue exitosa.")
else:
    print("La verificación falló.")"""

