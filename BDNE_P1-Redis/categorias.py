import redis

# Conexión
usuario = 'alex'

client = redis.Redis(host='localhost', port=6379)


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
    print(f'\t\t{categoria}')
    print("-----------------------------------------")
    for hkey in matches:
        showentry(bytes(hkey, 'UTF-8'))

    return matches

def add_entry(hkey):
    print(f"Sitio: {client.hget(f'Hash:{hkey}', 'url_completa').decode()}")
    cont = str(input("Añadir a la wishlist? Y/N/Exit: ")).upper()

    if cont == "Y":
        client.rpush(usuario + ":wishlist", hkey)

    if cont == "EXIT":
        return 1

    return 0

def wishlist_proc(matches):
    for hkey in matches:
        if add_entry(hkey):
            break

if __name__ == '__main__':
    wishlist_proc(busqueda_cat())

