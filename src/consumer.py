# leitura de fila 'fila.analise.exame'
# aplicando classificacao pneumonia se [0 > sim, 1 > nao] 

from datetime import datetime
from connection_queue import ConnectionQueue
from modelo import Classificador
from database_mongo import DatabaseMongo

import logging
import json
from os import getenv

DATABASE = getenv('DATABASE', 'tcc-db')
DATABASE_HOST = getenv('DATABASE_HOST', 'localhost')
DATABASE_USERNAME = getenv('DATABASE_USERNAME', 'root')
DATABASE_PASSWORD = getenv('DATABASE_PASSWORD', 'MongoDB2019!')
DATABASE_PORT = int(getenv('DATABASE_PORT', '27017'))

COLLECTION_EXAME = getenv('COLLECTION_EXAME', 'item_exame')

ATRIBUTO_ID = '_id'
ATRIBUTO_ID_EXAME = 'idExame'
ATRIBUTO_IMAGE = 'raioX' 
ATRIBUTO_ANALISE_SISTEMA = 'analisePredicao'
ATRIBUTO_DIAGNOSTICO = 'diagnostico'

ATRIBUTO_DATA_ANALISE = 'dataAnalise'

QUEUE_IN_NAME = getenv('QUEUE_IN_NAME', 'fila.analise.exame')
QUEUE_OUT_NAME = getenv('QUEUE_OUT_NAME', 'fila.consolidar.exame')

QUEUE_HOST = getenv('QUEUE_HOST', 'localhost')
QUEUE_PORT = int(getenv('QUEUE_PORT', '5672'))

db = DatabaseMongo(database=DATABASE, host=DATABASE_HOST, username=DATABASE_USERNAME, password=DATABASE_PASSWORD, port=DATABASE_PORT)
cr = Classificador()

def obterExames( id ):
    exames = db.get(collection=COLLECTION_EXAME, find={ATRIBUTO_ID_EXAME : id})
    return exames

def atualizarExame( exame, analise ):
    print('DATA ANALISE : ', datetime.now())

    diagnostico = True if analise > 0 else False
    print('DIAGNOSTICO : ',diagnostico)

    db.update(collection=COLLECTION_EXAME,
        query={ATRIBUTO_ID: exame[ATRIBUTO_ID]}, 
        value={ATRIBUTO_ANALISE_SISTEMA:analise.tolist(), ATRIBUTO_DATA_ANALISE: datetime.now(), ATRIBUTO_DIAGNOSTICO:diagnostico}) 

def callback(ch, method, properties, body):
    msg = json.loads(body)
    print('ID EXAME : ', msg[ATRIBUTO_ID_EXAME])

    exames = obterExames(msg[ATRIBUTO_ID_EXAME])

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

queue = ConnectionQueue(exchange=QUEUE_IN_NAME, host=QUEUE_HOST, port=QUEUE_PORT)
queue.consume(callback=callback, queue=QUEUE_IN_NAME)



