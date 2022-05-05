from defs import *
import pymongo

if __name__ == '__main__':

    client = pymongo.MongoClient('mongodb://127.0.0.1:27017/')
    mydb = client['Practica3']
    rutas = mydb["tabla_rutas"]
    estac = mydb["tabla_estaciones"]
    users = mydb["tabla_usuario"]

    usr = identificar_usuario()
    usr_info = list(users.find({'username': usr}))

    if len(usr_info) < 1:
        registro_usuario(usr)
        usr_info = list(users.find({'username': usr}))

    running = 1
    while running:
        lanzar_proceso(main_menu(), usr)
        running = bool(ask_salir())