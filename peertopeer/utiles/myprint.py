from colorama import Fore,Back

def myprint(*args): 
    print(f"{Back.RED}", end=" ")
    for arg in args:
        print(arg , end=" ")
    print(f'{Back.GREEN}', end="\n")