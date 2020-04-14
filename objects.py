#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 14 11:08:04 2020

@author: moritz
"""

import redis
import json

class ObjectsDB:
    
    def __init__(self, port:int=6379, namespace:str='cfg'):
        self.port = port
        self.objectNamespace = f'{namespace}.o.'
        self.fileNamespace = f'{namespace}.f.'
        
        self.redis = redis.Redis(host='localhost', port=port, db=0)
        self.pub_sub = self.redis.pubsub()
        
    def set_object(self, id:str=None, obj:dict={}) -> None:
        """Set object in db and publish"""
        # set object as string
        self.redis.set(f'{self.objectNamespace}{id}', json.dumps(obj))
        # publish object
        self.redis.publish(f'{self.objectNamespace}{id}', json.dumps(obj))
        
    def get_object(self, id:str=None) -> dict:
        """get object out of redis db and parse"""
        obj:dict = json.loads(self.redis.get(f'{self.objectNamespace}{id}'))
        return obj
    
    def subscribe(self, pattern:str) -> None:
        """subscribe to state changes"""
        self.pub_sub.psubscribe(f'{self.objectNamespace}{pattern}')
        
    def unsubscribe(self, pattern:str) -> None:
        """unsubscribe from state chamges"""
        self.pub_sub.punsubscribe(f'{self.objectNamespace}{pattern}')
        
    def get_message(self) -> dict:
        """get subscribed messages if some there"""
        msg:dict = self.pub_sub.get_message(ignore_subscribe_messages=True)
        if msg != None:
            msgId = msg['channel'][len(self.objectNamespace):]
            msg = json.loads(msg['data'])
            msg['id'] = msgId
        return msg