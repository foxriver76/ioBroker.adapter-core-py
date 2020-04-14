#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 14 11:08:36 2020

@author: moritz
"""

import redis
import json

class StatesDB:
    
    def __init__(self, port:int=6379, namespace:str='io'):
        self.port = port
        self.namespace = f'{namespace}.'
        
        self.redis = redis.Redis(host='localhost', port=6379, db=0)
        self.pub_sub = self.redis.pubsub()
        
    def set_state(self, id:str=None, state:dict={}) -> None:
        """Set state in db and publish"""
        # set object as string
        self.redis.set(f'{self.namespace}{id}', json.dumps(state))
        # publish object
        self.redis.publish(f'{self.namespace}{id}', json.dumps(state))
        
    def get_state(self, id:str=None) -> dict:
        """get object out of redis db and parse"""
        state:dict = json.loads(self.redis.get(f'{self.namespace}{id}'))
        return state
    
    def subscribe(self, pattern:str) -> None:
        """subscribe to state changes"""
        self.pub_sub.psubscribe(f'{self.namespace}{pattern}')
        
    def get_message(self) -> dict:
        """get subscribed messages if some there"""
        msg:dict = self.pub_sub.get_message(ignore_subscribe_messages=True)
        if msg != None:
            msgId = msg['channel'][len(self.namespace):]
            msg = json.loads(msg['data'])
            msg['id'] = msgId
        return msg        