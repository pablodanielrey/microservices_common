import etcd
import os
import logging
import time

class RegistrarServicio:
    # host = os.environ['ETCD_HOST']
    host = '163.10.56.56'

    @classmethod
    def registryFlask(cls):
        # service_name = os.environ['ETCD_SERVICE_NAME']
        service_name = 'login_web'
        # url = os.environ['ETCD_SERVICE_URL']
        url = 'login.econo.unlp.edu.ar'
        # server_name = os.environ['ETCD_SERVER_NAME']
        server_name = 'login_web_1'
        # service_host = os.environ['ETCD_SERVICE_HOST']
        service_host = '163.10.56.56:5000'
        # service_path =  os.environ['ETCD_SERVICE_PATH']
        service_path = '/'

        c = etcd.Client(host=cls.host, port=2379, protocol='http')
        try:
            while True:
                x = c.write('/services/{}/location'.format(service_name),url,ttl=13)
                print("generated key: " + x.key)
                print("stored value: " + x.value)

                x = c.write('/services/{}/path'.format(service_name), service_path,ttl=13)
                print("generated key: " + x.key)
                print("stored value: " + x.value)

                x = c.write('/services/{}/upstream/{}'.format(service_name, server_name), service_host,ttl=13)
                print("generated key: " + x.key)
                print("stored value: " + x.value)

                time.sleep(10)


        except Exception as e:
            logging.exception(e)

    @classmethod
    def registryRest(cls, service_name, domain, path, service_host):
        server_name = service_name + '_' + service_host.replace('.','_').replace(':','_')

        c = etcd.Client(host=cls.host, port=2379, protocol='http')
        try:
            while True:
                key = '/services/{}/location'.format(service_name)
                try:
                    r = c.read(key)
                    c.refresh(key,ttl=13)
                    print("Se actualizo la clave " + key)
                except etcd.EtcdKeyNotFound:
                    c.write(key, domain, ttl=13)
                    print("Se creo la clave " + key)

                key = '/services/{}/path'.format(service_name)
                try:
                    r = c.read(key)
                    c.refresh(key,ttl=13)
                    print("Se actualizo la clave " + key)
                except etcd.EtcdKeyNotFound:
                    c.write(key, path, ttl=13)
                    print("Se creo la clave " + key)

                key = '/services/{}/upstream/{}'.format(service_name, server_name)
                try:
                    r = c.read(key)
                    c.refresh(key,ttl=13)
                    print("Se actualizo la clave " + key)
                except etcd.EtcdKeyNotFound:
                    c.write(key, service_host, ttl=13)
                    print("Se creo la clave " + key)

                time.sleep(10)

            '''
            while True:
                servicios = c.get('/services').children
                for c in servicios:
                    print(c.key)

                x = c.write('/services/{}/location'.format(service_name), domain, ttl=13)
                x = c.write('/services/{}/path'.format(service_name), path, ttl=13)
                x = c.write(, service_host, prevExist=False, ttl=13)

                time.sleep(10)
            '''

        except Exception as e:
            logging.exception(e)
