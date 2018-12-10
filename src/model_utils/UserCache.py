
import redis

class UserCache:
    
    def __init__(self, host, port, user_getter, users_getter, user_getter_dni, timeout=60 * 60 * 24 * 7):
        self.redis_ = redis.StrictRedis(host=host, port=port, decode_responses=True)
        self.getter_usuario = user_getter
        self.getter_usuarios = users_getter
        self.getter_usuario_dni = user_getter_dni
        self.timeout = timeout

    def _setear_usuario_cache(self, usr):
        uk = 'usuario_uid_{}'.format(usr['id'])
        self.redis_.hmset(uk, usr)
        self.redis_.expire(uk, self.timeout)

        uk = 'usuario_dni_{}'.format(usr['dni'].lower().replace(' ',''))
        self.redis_.hset(uk, 'uid', usr['id'])
        self.redis_.expire(uk, self.timeout)

    def obtener_usuario_por_uid(self, uid, token=None):
        usr = self.redis_.hgetall('usuario_uid_{}'.format(uid))
        if len(usr.keys()) > 0:
            return usr
        usr = self.getter_usuario(uid, token=token)
        if not usr:
            return None
        self._setear_usuario_cache(usr)
        return usr

    def obtener_usuarios_por_uids(self, uids=[], token=None):
        usuarios = []
        faltantes = []
        for uid in uids:
            if uid:
                usr = cls.redis_assistance.hgetall('usuario_uid_{}'.format(uid))
                if len(usr.keys()) > 0:
                    usuarios.append(usr)
                else:
                    faltantes.append(uid)
        if len(faltantes) > 0:
            ulen = len(faltantes[0])
            cantidad_maxima_por_query = int((2048 / ulen) - 2)
            while len(faltantes) > 0:
                uids_a_pedir = faltantes[:cantidad_por_query]
                faltantes = faltantes[cantidad_por_query:]
                obtenidos = self.getter_usuarios(uids_a_pedir, token=token)
                for usuario in obtenidos:
                    self._setear_usuario_cache(usuario)
                usuarios.extend(obtenidos)
        return usuarios  

    def obtener_usuario_por_dni(self, dni, token=None):
        key = 'usuario_dni_{}'.format(dni.lower().replace(' ',''))
        if self.redis_.hexists(key,'uid'):
            uid = self.redis_.hget(key,'uid')
            return self.obtener_usuario_por_uid(uid, token=token)
        usr = self.getter_usuario_dni(dni, token=token)
        if not usr:
            return None
        self._setear_usuario_cache(usr)
        return usr

