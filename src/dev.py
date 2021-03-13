from datetime import datetime
from connection_queue import ConnectionQueue
from modelo import Classificador
from database_mongo import DatabaseMongo

import cv2

import json
from os import getenv

DATABASE = getenv('DATABASE', 'tcc-db')
DATABASE_HOST = getenv('DATABASE_HOST', 'localhost')
DATABASE_USERNAME = getenv('DATABASE_USERNAME', 'root')
DATABASE_PASSWORD = getenv('DATABASE_PASSWORD', 'MongoDB2019!')
DATABASE_PORT = int(getenv('DATABASE_PORT', '27017'))

COLLECTION_EXAME = 'item_exame'

ATRIBUTO_ID = '_id'
ATRIBUTO_ID_SOLICITAR_EXAME = 'idExame'
ATRIBUTO_EXAMES = 'exames'
ATRIBUTO_IMAGE = 'raioX' 
ATRIBUTO_ANALISE_SISTEMA = 'analise_normal'

QUEUE_NAME = getenv('QUEUE_NAME', 'fila.analise.exame')
QUEUE_OUT_NAME = getenv('QUEUE_OUT_NAME', 'fila.consolidar.exame')
QUEUE_HOST = 'localhost'
QUEUE_PORT = int(getenv('QUEUE_PORT', '5672'))

print('#################################')
print('CONFIGURACAO')
print('##############')
print('DATABASE: ', DATABASE)
print('DATABASE_HOST:',DATABASE_HOST)
print('DATABASE_USERNAME: ',DATABASE_USERNAME)
print('DATABASE_PASSWORD: ',DATABASE_PASSWORD)
print('DATABASE_PORT:', DATABASE_PORT)
print('##############')
print('QUEUE_NAME: ', QUEUE_NAME)
print('QUEUE_HOST: ', QUEUE_HOST)
print('##############')
print('QUEUE_OUT_NAME: ', QUEUE_OUT_NAME)
print('QUEUE_HOST: ', QUEUE_HOST)
print('#################################')

db = DatabaseMongo(database=DATABASE, host=DATABASE_HOST, username=DATABASE_USERNAME, password=DATABASE_PASSWORD, port=DATABASE_PORT)
cr = Classificador()

def obterExames( id ):
    exames = db.get(collection=COLLECTION_EXAME, find={ATRIBUTO_ID_SOLICITAR_EXAME : id})
    return exames

def atualizarExame( exame, analise ):
    print('update base : ', exame[ATRIBUTO_ID])
    db.update(collection=COLLECTION_EXAME,
        query={ATRIBUTO_ID: exame[ATRIBUTO_ID]}, 
        value={ATRIBUTO_ANALISE_SISTEMA:analise.tolist()}) 

def callback(ch, method, properties, body):
    print('begin')
    print('READ : ', body)
    msg = json.loads(body)
    print(ATRIBUTO_ID_SOLICITAR_EXAME, msg[ATRIBUTO_ID_SOLICITAR_EXAME])
    exames = obterExames(msg[ATRIBUTO_ID_SOLICITAR_EXAME])

    for exame in exames:
        result = cr.predicao(image_bytes=exame[ATRIBUTO_IMAGE])
        atualizarExame(exame, result)
        print('PREDICAO :', result)
        sendOut(json = json.dumps(msg))

def sendOut(json = ''):
    try:
        queueOut = ConnectionQueue(queue=QUEUE_OUT_NAME, host=QUEUE_HOST, port=QUEUE_PORT)
        queueOut.send(queue=QUEUE_OUT_NAME,message=json)
    except:
        sendOut(json=json)

queue = ConnectionQueue(queue=QUEUE_NAME, host=QUEUE_HOST)
queue.consume(callback=callback)