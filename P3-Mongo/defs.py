import pymongo

client = pymongo.MongoClient('mongodb://127.0.0.1:27017/')
mydb = client['Practica3']
rutas = mydb["tabla_rutas"]
estac = mydb["tabla_estaciones"]
users = mydb["tabla_usuario"]


def identificar_usuario():
    usuario = str(input("Nombre de Usuario: "))
    return usuario


def main_menu() -> int:
    print("Menú Principal")
    print("Ingrese el número según la operación que desee realizar")
    opcion = 0
    while not opcion:
        print("1 - Planear viaje")
        print("2 - Buscar estaciones cercanas")
        print("3 - Añadir ubicación")
        opcion = int(input())

        if opcion not in (1, 2, 3):
            print("Entrada no válida")
            opcion = 0

    return opcion


def lanzar_proceso(numproc, usuario):
    if numproc == 1:
        planear_viaje(usuario)
    elif numproc == 2:
        estac_cerc(usuario)
    elif numproc == 3:
        add_loc(usuario)


def ask_salir():
    print("Salir? Y/N \n")
    out = input()
    if out == "Y" or out == "y":
        return 0
    return 1


def registro_usuario(usuario):
    print("Se requiere una ubicación para nuevos usuarios:")
    add_loc(usuario)


def planear_viaje(usuario):
    from datetime import datetime
    import re

    #Preguntar tiempo de inicio
    print('Hora de inicio: (HH:MM)')
    hr = str(input())

    while not re.match('(([0-1][\d])|(2[0-3])):(([0-5][\d])|(60))', hr):
        print('Formato no válido.')
        hr = str(input())

    starttime = datetime(year=2014, month=2, day=20, hour=int(hr[:2]),minute=int(hr[3:]),second=0)

    #Preguntar lugar de inicio.
    usr_locs, locnames = find_locnames(usuario)

    print('Desde dónde? Escribe el nombre o presiona enter para introducir manualmente el nombre de la estación de inicio.')
    print(locnames)

    startname = str(input())

    while startname not in locnames and len(startname) != 0:
        print('Entrada no válida')
        startname = str(input())

    if len(startname) != 0:
        idx = locnames.index(startname)
        var = estcerc(usr_locs[idx]['lon'], usr_locs[idx]['lat'])
        stations = [thing[0] for thing in var]
        print('Estaciones de inicio recomendadas: ')
        for st in stations:
            print(st)

    all_stations = [onedoc['start station name'] for onedoc in list(estac.find())]
    print('Introduce el nombre de la estación de inicio: ')
    ststart = str(input())

    while ststart not in all_stations:
        print("Entrada no válida.")
        ststart = str(input())

    #Preguntar tiempo estimado
    print("Cuánto tiempo quieres que dure el paseo?")
    t_est = int(input())

    #Preguntar redondo
    print('Viaje redondo? S/N')
    redondo = str(input())

    ynverif = ['s', 'n', 'S', 'N']
    while redondo not in ynverif:
        print("Entrada no válida.")
        redondo = str(input())

    rutas_rec = viaje(starttime, ststart, t_est, redondo)

    print("Viajes recomendados: ")
    print(rutas_rec.iloc[:, 1:])

def estac_cerc(usuario):

    print('Buscando estaciones cercanas:')

    #jalar las loc del usuario
    usr_locs, locnames = find_locnames(usuario)

    idx = 0
    if len(locnames) > 1:
        print('Cercanas a cuál de tus lugares guardados?')
        print(locnames)

        choice = str(input())
        while choice not in locnames:
            print('Opción no válida')
            choice = str(input())
        idx = locnames.index(choice)

    print('Ubicaciones cercanas a ' + locnames[idx])

    estcerc(usr_locs[idx]['lon'], usr_locs[idx]['lat'])




def find_locnames(usuario):
    global users
    usr_locs = list(users.find({'username': usuario}, {'locations': 1}))

    locnames = []
    if len(usr_locs) > 0:
        usr_locs = usr_locs[0]['locations']

        if usr_locs is not None:
            locnames = [doc['n_loc'] for doc in usr_locs]
        else:
            usr_locs = []

    return usr_locs, locnames

def add_loc(usuario):

    usr_locs, locnames = find_locnames(usuario)

    print(
        'Las entradas son por latitud y longitud. En una implementación real debería '
        'obtenerse desde una interfaz de busqueda como google maps.')
    print('Nombre de la ubicación: ')

    # Name location
    locname = 0
    while not locname:
        locname = str(input())
        if locname in locnames:
            print('Esa ubicación ya existe:')
            locname = 0

    # Add location
    lat = None
    lon = None
    while lat is None or lon is None:
        lat = float(input("Latitud: "))
        lon = float(input("Longitud: "))

        if not ((-90 <= lat <= 90) and (-180 <= lon <= 180)):
            print('Ubicación no válida')
            lat = lon = None

    loc_doc = dict(n_loc=locname, lat=lat, lon=lon)
    usr_locs.append(loc_doc)
    f_doc = {'$set': dict(username=usuario, locations=usr_locs)}
    query = dict(username=usuario)
    users.update_one(query, f_doc, upsert=True)


def estcerc(iniciolon, iniciolat):
    from heapq import nsmallest
    import numpy as np
    import pandas as pd
    x1 = float(iniciolat)
    y1 = float(iniciolon)
    b = np.array((y1, x1))
    disttot = []

    consulta = []
    for j in estac.find():
        consulta.append(j)

    locali2 = pd.DataFrame.from_dict(consulta)

    for i in range(len(locali2['start station longitude'])):
        np.array((locali2['start station latitude'][i], locali2['start station longitude'][i]))
        dist = np.linalg.norm(
            np.array((locali2['start station latitude'][i], locali2['start station longitude'][i])) - b)
        disttot.append(dist)
    dic = {locali2['start station name'][i]: disttot[i] for i in range(len(locali2['start station longitude']))}
    lista = dic.items()
    vad = nsmallest(3, lista)

    print('Las 3 estaciones  más cercanas de tu ubicación son:', vad)

    return vad

def viaje(tiempo_inicio, lugar_inicio, tiempo_de_viaje,redondo=False):
    """
    tiempo_inicio: String que indica el dia y hora en el que se planea hacer el viaje
    usuario_id: String id del usuario en la base de datos
    lugar_inicio: String nombre que pusiste a tu lugar de salida
    tiempo_de_viaje: Int El tiempo aproximado que quieres que dure tu viaje en segundos
    Redondo: Booleano True si el viaje lo quieres redondo y False si no es redondo
    """
    import pandas as pd
    from datetime import timedelta
    tiempo2 = tiempo_inicio + timedelta(minutes=30)

    consulta = []
    for j in rutas.find({'tripduration':{'$lt':tiempo_de_viaje},
                        'starttime':{'$gt':tiempo_inicio,
                        '$lt':tiempo2},
                        'start station name':lugar_inicio}):
        consulta.append(j)


    df2 = pd.DataFrame.from_dict(consulta)

    df2 = df2.groupby(["start station id","start station name","end station id","end station name"])["tripduration"].mean().round()
    df2 = pd.DataFrame(df2).rename(columns={"tripduration":"Tiempo Estimado"}).reset_index()

    if not redondo:
        df2 = df2.loc[(df2["Tiempo Estimado"] <= tiempo_de_viaje)]
    else:
        df2 = df2.loc[(df2["Tiempo Estimado"] <= (tiempo_de_viaje/2))]
        df2["Tiempo Estimado"] = 2*df2["Tiempo Estimado"]

    return df2[["start station name","end station name","Tiempo Estimado"]]
