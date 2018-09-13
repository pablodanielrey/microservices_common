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
    
    def __init__(self, oidc_url, client_id, client_secret, verify=False):
        self.oidc_url = oidc_url
        self.verify = verify
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = '{}/oauth2/token'.format(self.oidc_url)

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


