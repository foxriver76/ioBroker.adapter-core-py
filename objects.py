#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 14 11:08:04 2020

@author: moritz
"""

import aioredis
import json
import time

class ObjectsDB:
    
    def __init__(self, port:int=6379, namespace:str='cfg'):
        self.port = port
        self.objectNamespace = f'{namespace}.o.'
        self.fileNamespace = f'{namespace}.f.'
        
    async def init_db(self) -> None:
        self.redis = await aioredis.create_redis(('localhost', self.port))
        self.subs_receiver = aioredis.pubsub.Receiver()
        
    async def set_object(self, id:str=None, obj:dict={}) -> None:
        """Set object in db and publish"""
        obj['ts'] = int(time.time())
        # set object as string
        await self.redis.set(f'{self.objectNamespace}{id}', json.dumps(obj))
        # publish object
        await self.redis.publish(f'{self.objectNamespace}{id}', json.dumps(obj))
        
    async def get_object(self, id:str=None) -> dict:
        """get object out of redis db and parse"""
        obj:dict = json.loads(await self.redis.get(f'{self.objectNamespace}{id}'))
        return obj
    
    async def subscribe(self, pattern:str) -> None:
        """subscribe to state changes"""
        await self.redis.psubscribe(self.subs_receiver.pattern(f'{self.objectNamespace}{pattern}'))
        
    async def unsubscribe(self, pattern:str) -> None:
        """unsubscribe from state chamges"""
        await self.redis.punsubscribe(f'{self.objectNamespace}{pattern}')
        
    async def get_message(self) -> dict:
        """get subscribed messages if some there"""
        while await self.subs_receiver.wait_message():
            sender, msg = await self.subs_receiver.get()
            if type(msg) == tuple:
                obj:dict = json.loads(msg[1])
                id:str = msg[0][len(self.objectNamespace):]
                return id, obj