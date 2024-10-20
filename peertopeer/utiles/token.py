import secrets
def crear_token():
    return secrets.token_hex(16)