from Crypto.Cipher import AES
from dotenv import load_dotenv
import os
import base64
import hashlib

load_dotenv()


class Encrypt:
    
    def encrypt_gcm(self, encriptar : str, password : str = os.getenv("PASSWORD3")):
        salt = os.urandom(AES.block_size)
        private_key = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1, dklen=32)

        cipher = AES.new(private_key, AES.MODE_GCM)
        ciphertext, tag = cipher.encrypt_and_digest(encriptar.encode())


        encrypted_data = base64.b64encode(cipher.nonce + salt + tag +ciphertext).decode('utf-8')

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
        encrypted_bytes = base64.b64decode(encrypted_data)

        nonce = encrypted_bytes[:16]  
        salt = encrypted_bytes[16:32]  
        tag = encrypted_bytes[32:48]  
        ciphertext = encrypted_bytes[48:]  

        private_key = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1, dklen=32)

        cipher = AES.new(private_key, AES.MODE_GCM, nonce=nonce)

        try:
            decrypted = cipher.decrypt_and_verify(ciphertext, tag)
            return encriptar == decrypted.decode('utf-8')
        except (ValueError, KeyError):
            return False