
import os
USUARIOS_URL = os.environ['USUARIOS_URL']

def _get_user_uuid(uuid, token=None):
    query = '{}/usuarios/{}'.format(USUARIOS_URL, uuid)
    r = api.get(query, token=token)
    if not r.ok:
        return None
    usr = r.json()
    if len(usr) > 0:
        return usr[0]
    return None

def _get_users_uuid(uuids=[], token=None):
    uids = '+'.join(uuids)
    query = '{}/usuarios/{}'.format(USUARIOS_URL, uids)
    r = api.get(query, token=token)
    if not r.ok:
        return None
    usrs = r.json()        
    return usrs

def _get_user_dni(dni, token=None):
    query = '{}/usuario_por_dni/{}'.format(USUARIOS_URL, dni)
    r = api.get(query, token=token)
    if not r.ok:
        return None
    for usr in r.json():
        return usr        
    return None
