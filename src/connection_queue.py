import pika
import time

class ConnectionQueue:
    def _createConnection(self, wait=0.5):
        print('_createConnection')
        try: 
           return pika.BlockingConnection(pika.ConnectionParameters(host=self._host, port=self._port))
   
        except:
           print('ERRO : ConnectionQueue')
           time.sleep(wait)
           return self._createConnection(wait=(wait+0.5)) 

        # credentials = pika.PlainCredentials('guest', 'guest')

    def __init__(self, exchange='', queue='', host='localhost', port=5672):
        self._host = host
        self._port = port
        self._exchange = exchange
        self._connection = self._createConnection()
        self._channel = self._connection.channel()
        self._channel.queue_declare (queue = queue, durable=True)
        # self._channel.exchange_declare(exchange=self._exchange, exchange_type='fanout')

    def send(self, queue, message):
        self._channel.basic_publish(exchange='', routing_key=queue, body=message)

    def close(self):
        print('stop consume')
        self._connection.close()

    def consume(self, callback, queue=''):
        print('start consume')
        self._channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=True)
        self._channel.start_consuming()
