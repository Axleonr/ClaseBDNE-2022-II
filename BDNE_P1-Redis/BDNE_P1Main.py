import hashlib
import redis

# Conexión

client = redis.Redis(host='localhost', port=6379)

# Definiciones


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
        print("4 - Buscar URLs por Categoría")
        opcion = int(input())

        if opcion not in (1, 2, 3, 4):
            print("Entrada no válida")
            opcion = 0

    return opcion


def lanzar_proceso(numproc, usuario):
    if numproc == 1:
        aniadir_url(usuario)
    elif numproc == 2:
        revisar_urls(usuario)
    elif numproc == 3:
        revisar_wishlist(usuario)
    elif numproc == 4:
        wishlist_proc(busqueda_cat())


def showentry(hkey):
    domain = str("funny.url/")
    entry = {"Small URL": str(domain + hkey.decode()),
             "Full Link": client.hget(f'Hash:{hkey.decode()}', "url_completa").decode(),
             "Privacy": client.hget(f'Hash:{hkey.decode()}', "Tipo").decode(),
             "Category": client.hget(f'Hash:{hkey.decode()}', "categoria").decode()}

    for key in entry.keys():
        print(f'{key}: {entry[key]}')

    print("-----------------------------------------")

    return entry["Small URL"]


def aniadir_url(usuario):
    print("Añadiendo url")
    url_completa = str(input("Escribe tu URL: "))
    string = url_completa + usuario
    h = hashlib.blake2b(digest_size=5)
    h.update(string.encode("utf-8"))
    hashedkey = h.hexdigest()

    print("¿Qué tipo de url va a ser? Public/Private")
    clase_url = str(input()).upper()

    if clase_url == "PUBLIC":
        # Agregar a las urls publicas del usuario
        print("Tu url fue agregada a tus urls públicas")

        print("¿Desea Agregarle una categoria? Y/N")
        categoria = str(input()).upper()

        if categoria == "Y":
            # Agregarle una categoria a las urls
            print("Agrega el nombre de tu categoria")
            categoria_nombre = str(input())
            print("A tu url se le agrego la categoria: ", categoria_nombre)

            # AGREGAR LA URL CON LA CATEGORIA Y PUBLICAS
            client.rpush(usuario + ":hash", hashedkey)
            client.hmset("Hash:" + hashedkey, {"url_completa": url_completa,
                                               "categoria": categoria_nombre,
                                               "Tipo": "Publica"})

        elif categoria == "N":
            print("No le agregaste categoria a tu url")
            # AGREGAR LA URL SIN LA CATEGORIA Y PUBLICAS
            client.rpush(usuario + ":hash", hashedkey)
            client.hmset("Hash:" + hashedkey, {"url_completa": url_completa,
                                               "categoria": "Null",
                                               "Tipo": "Publica"})

        else:
            print("Opción NO valida, intente de nuevo")
            return None

    elif clase_url == "PRIVATE":
        # Agregar a las urls privadas del usuario
        print("Tu url fue agregada a tus urls privadas")

        print("¿Desea Agregarle una categoria? Y/N")
        categoria = str(input()).upper()

        if categoria == "Y":
            # Agregarle una categoria a las urls
            print("Agrega el nombre de tu categoria")
            categoria_nombre = str(input())
            print("A tu url se le agrego la categoria", categoria_nombre)
            # AGREGAR LA URL CON CATEGORIA Y PRIVADA
            client.rpush(usuario + ":hash", hashedkey)
            client.hmset("Hash:" + hashedkey, {"url_completa": url_completa,
                                               "categoria": categoria_nombre,
                                               "Tipo": "Privada"})

        elif categoria == "N":
            # No hacer nada
            print("No le agregaste categoria a tu url")
            # AGREGAR LA URL SIN CATEGORIA Y PRIVADA
            client.rpush(usuario + ":hash", hashedkey)
            client.hmset("Hash:" + hashedkey, {"url_completa": url_completa,
                                               "categoria": "Null", "Tipo": "Privada"})

        else:
            print("Opción NO valida, intente de nuevo")
            return None

    else:
        print("Opción NO valida, intente de nuevo")
        return None

    print("¿Quiere ingresar su url a la wishlist? Y/N")
    wishlist_true_or_false = str(input()).upper()

    if wishlist_true_or_false == "Y":
        # Agregar a la wishlist del usuario
        print("Tu url fue agregada a tu wishlist")
        # AGREGAR A LA WISHLIST
        client.rpush(usuario + ":wishlist", hashedkey)
        # client.hmset("Wishlist:" + hashedkey, {"url_completa": url_completa})

    elif wishlist_true_or_false == "N":
        print("Tu url NO fue agregada a tus wishlist")
        # NO LA AGREGAMOS A LA WISHLIST

    else:
        print("Opción NO valida, intente de nuevo")
        return None

    print("-----------------------------------------")
    url_corta = showentry(bytes(hashedkey, "UTF-8"))

    # REGRESAMOS LAS URLS
    return url_completa, url_corta


def revisar_urls(usuario):
    print(">>>Tus enlaces guardados<<<")
    print("-----------------------------------------")
    urlkeys = client.lrange(usuario+":hash", 0, -1)

    for hkey in urlkeys:
        showentry(hkey)


def revisar_wishlist(usuario):
    print("*** Wishlist ***")
    print("-----------------------------------------")
    urlkeys = client.lrange(usuario+":wishlist", 0, -1)

    for hkey in urlkeys:
        showentry(hkey)


def ask_salir():
    print("Salir? Y/N \n")
    out = input()
    if out == "Y" or out == "y":
        return 0
    return 1

# Entra el menú principal


def busqueda_cat():

    categoria = str(input("Ingrese la categoría que desea buscar: "))

    all_urls = list(map(lambda x: x.decode()[5:], client.keys("Hash:*")))

    non_private_urls = []
    for hkey in all_urls:
        if client.hget(f'Hash:{hkey}', "Tipo").decode() == "Publica":
            non_private_urls.append(hkey)

    matches = []
    for hkey in non_private_urls:
        if client.hget(f'Hash:{hkey}', "categoria").decode().upper() == categoria.upper():
            matches.append(hkey)

    print('---URLs públicas de la categoría:---')
    print(f'\t\t\t\t{categoria}')
    print(f'Hay {len(matches)} entradas que coinciden.')
    print("-----------------------------------------")
    for hkey in matches:
        showentry(bytes(hkey, 'UTF-8'))

    return matches


def add_entry(hkey):
    print(f"Sitio: {client.hget(f'Hash:{hkey}', 'url_completa').decode()}")
    cont = str(input("Añadir a la wishlist? Y/N/Exit: ")).upper()

    if cont == "Y":
        client.rpush(usr + ":wishlist", hkey)

    if cont == "EXIT":
        return 1

    else:
        return 0


def wishlist_proc(matches):
    for hkey in matches:
        if add_entry(hkey):
            break


if __name__ == '__main__':

    usr = identificar_usuario()

    running = bool(1)
    while running:
        lanzar_proceso(main_menu(), usr)
        running = bool(ask_salir())
