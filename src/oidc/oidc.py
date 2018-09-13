"""
    Implementa oauth y OpenIDConnect
    el flujo normal para una aplicación cliente web es:
    1 - register_in_flask
    2 - petición al sitio --> @require_login --> auth_code --> callback --> access_token --> petición original

    el flujo normal para una app que exporta una api
    1 - usa solamente ResourceServer
    2 - petición al sitio --> @require_valid_token --> instrospect_token --> peticion original
"""

import os
import logging
import requests
from requests.auth import HTTPBasicAuth
import urllib
from urllib import parse
import json

import uuid
from functools import wraps
import flask
from flask import redirect, url_for


class ClientCredentialsGrant:
    '''
        https://tools.ietf.org/html/rfc6749
        sección 4.4
    '''

    token_url = os.environ['OIDC_HOST'] + '/oauth2/token'

    def __init__(self, oidc_url, client_id, client_secret, verify=False):
        self.oidc_url = oidc_url
        self.verify = verify
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = '{}/oauth2/token'.format(self.oidc_url)
        self.introspect_url = '{}/oauth2/introspect'.format(self.oidc_url)

    def access_token(self, scopes=[]):
        auth = HTTPBasicAuth(self.client_id, self.client_secret)
        data = {
            'client_id': self.client_id,
            'grant_type': 'client_credentials'
        }
        if len(scopes) > 0:
            data['scope'] = ' '.join(scopes)

        # application/x-www-form-urlencoded
        r = requests.post(self.token_url, verify=self.verify, allow_redirects=False, auth=auth, data=data)
        return r

    def get_token(self, r):
        if r.ok:
            return r.json()['access_token']
        return None


class TokenIntrospection:

    def __init__(self, oidc_url, client_id, client_secret, realm='', verify=False):
        self.oidc_url = oidc_url
        self.realm = realm
        self.verify = verify
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = '{}/oauth2/token'.format(self.oidc_url)
        self.introspect_url = '{}/oauth2/introspect'.format(self.oidc_url)


    """
    def require_valid_token_for(self, resource, action):
        def wraped_f(*args):
            def decorated_function(*args, **kwargs):
                '''
                    Recupera y chequea el token por validez
                '''
                token = self.bearer_token(flask.request.headers)
                if not token:
                    return self.invalid_token()
                #tk = self.verify_token(token)
                #if not tk:
                #    return self.invalid_request()
                acc = self.introspect_warden(token, resource, action)
                if not acc:
                    return self.invalid_request()
                    #return self.insufficient_scope()
                kwargs['token'] = tk
                kwargs['access'] = acc
                return f(*args, **kwargs)
            return decorated_function
        return wraped_f

    def introspect_warden(self, token, resource, action):
        cc = ClientCredentialsGrant(self.client_id, self.client_secret, True)
        tkr = cc.access_token(['hydra.warden'])
        tk = cc.get_token(tkr)

        #auth = HTTPBasicAuth(self.client_id, self.client_secret)
        data = {
            'token':token,
            #'action':action,
            'resource':resource
        }
        headers = {
            'Authorization': 'Bearer {}'.format(tk),
            'Accept':'application/json'
        }
        #r = requests.post(self.warden_url, verify=self.verify, allow_redirects=False, auth=auth, headers=headers, data=data)
        r = requests.post(self.warden_url, verify=self.verify, allow_redirects=False, headers=headers, data=data)
        if r.ok:
            js = r.json()
            if js['allowed'] == True:
                return js
        return None
    """

    def require_token_scopes(self, scopes=[]):
        def real_decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                token = self.bearer_token(flask.request.headers)
                if not token:
                    return self.invalid_token()
                tk = self.verify_token(token)
                if not tk:
                    return self.invalid_request()
                if scopes and len(scopes) > 0:
                    tscopes = tk['scope'].lower().split(' ')
                    for s in scopes:
                        if s not in tscopes:
                            return self.insufficient_scope()
                kwargs['token'] = tk
                #kwargs['access'] = acc
                return f(*args, **kwargs)
            return wrapper
        return real_decorator

    def require_valid_token(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            '''
                Recupera y chequea el token por validez
            '''
            token = self.bearer_token(flask.request.headers)
            if not token:
                return self.invalid_token()
            tk = self.verify_token(token)
            if not tk:
                return self.invalid_request()
            kwargs['token'] = tk
            return f(*args, **kwargs)

        return decorated_function

    def bearer_token(self, headers):
        if 'Authorization' in headers:
            auth = headers['Authorization'].split(' ')
            if auth[0].lower() == 'bearer':
                return auth[1]
        return None

    def introspect_token(self, token, scopes=[]):
        auth = HTTPBasicAuth(self.client_id, self.client_secret)
        data = {
            'token':token
        }
        if len(scopes) > 0:
            data['scope'] = ' '.join(scopes)
        headers = {
            'Accept':'application/json'
        }
        r = requests.post(self.introspect_url, verify=self.verify, allow_redirects=False, auth=auth, headers=headers, data=data)
        if not r.ok:
            return None
        return r.json()

    def verify_token(self, token, scopes=[]):
        tk = self.introspect_token(token)
        logging.debug(tk)
        if not tk or not tk['active']:
            return None
        return tk

    def invalid_request(self):
        return self.require_auth(text='Bad Request', error='invalid_request', status=400)

    def invalid_token(self):
        return self.require_auth(text='Unauthorized', error='invalid_token', status=401)

    def insufficient_scope(self):
        return self.require_auth(text='Forbidden', error='insufficient_scope', status=403)

    def require_auth(self, text='Unauthorized', error=None, status=401, error_description=''):
        headers = None
        if error:
            headers = {
                'WWW-Authenticate': 'Basic realm=\"{}\", error=\"{}\", error_description:\"{}\"'.format(self.realm, error, error_description)
            }
        else:
            headers = {
                'WWW-Authenticate': 'Basic realm=\"{}\"'.format(self.realm)
            }
        return (text, status, headers)

