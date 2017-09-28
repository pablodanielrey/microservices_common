import etcd
import os
import logging
import time

class RegistrarServicio:
    host = os.environ['ETCD_HOST']

    @classmethod
    def register(cls, name='web', domain='localhost', path = '/', server='127.0.0.1:8080'):
        server_name = f'{name}_{server}'.replace(':','_')

        to_register = [
            (f'/services/{name}/location', domain),
            (f'/services/{name}/path', path),
            (f'/services/{name}/upstream/{server_name}', server)
        ]

        c = etcd.Client(host=cls.host, port=2379, protocol='http')
        while True:
            try:
                for k,v in to_register:
                    try:
                        print(c.refresh(k, ttl=13))
                    except etcd.EtcdKeyNotFound:
                        print(c.write(k, v, ttl=13))

            except Exception as e:
                logging.exception(e)

            try:
                time.sleep(5)
            except Exception as e:
                logging.exception(e)
