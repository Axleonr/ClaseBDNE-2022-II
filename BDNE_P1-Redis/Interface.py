def identificar_usuario():
    usuario = str(input("Nombre de Usuario: "))
    return usuario


def main_menu() -> int:
    print("Menú Principal")
    print("Ingrese el número según la operación que desee realizar")
    opcion = 0
    while not opcion:
        print("1 - Añadir URL")
        print("2 - Revisar URLs")
        print("3 - Revisar Wishlist")
        opcion = int(input())

        if opcion not in (1, 2, 3):
            print("Entrada no válida")
            opcion = 0

    return opcion


def lanzar_proceso(numproc):
    if numproc == 1:
        aniadir_url()
    elif numproc == 2:
        revisar_urls()
    elif numproc == 3:
        revisar_wishlist()


def aniadir_url():
    print("añadiendo url")
    pass


def revisar_urls():
    print("revisando urls")
    pass


def revisar_wishlist():
    print("Revisando wishlist")
    pass


def ask_salir():
    print("Salir? Y/N \n")
    out = input()
    if out == "Y" or out == "y":
        return 0
    return 1



# Entra el menú principal

usr = identificar_usuario()

running = 1

while running:
    lanzar_proceso(main_menu())
    running = ask_salir()
