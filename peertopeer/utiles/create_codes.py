import random
import string

def generate_random_codes():
    characters = string.ascii_letters + string.digits + string.punctuation
    code = ''.join(random.choice(characters) for _ in range(12))
    return code

# Ejemplo de uso
random_code = generate_random_codes()
print(random_code)
