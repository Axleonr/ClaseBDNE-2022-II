import redis

# connect to redis
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


def revisar_urls(usuario):
    print(">>>Tus enlaces guardados<<<")
    print("-----------------------------------------")
    urlkeys = client.lrange(usuario + ":hash", 0, -1)

    for hkey in urlkeys:
        showentry(hkey)


def revisar_wishlist(usuario):
    print("*** Wishlist ***")
    urlkeys = client.lrange(usuario + ":wishlist", 0, -1)

    for hkey in urlkeys:
        showentry(hkey)


revisar_urls("alex")
# revisar_wishlist("alex")
