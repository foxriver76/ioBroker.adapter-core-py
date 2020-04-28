#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 14 11:08:04 2020

@author: moritz
"""

import aioredis
import json
import time
import object_utils as utils

class ObjectsDB:
    
    def __init__(self, port:int=6379, namespace:str='cfg'):
        self.port = port
        self.objectNamespace = f'{namespace}.o.'
        self.fileNamespace = f'{namespace}.f.'
        
    async def init_db(self) -> None:
        self.redis = await aioredis.create_redis(('localhost', self.port))
        self.redis_sub = await aioredis.create_redis(('localhost', self.port))
        self.subs_receiver = aioredis.pubsub.Receiver()
        
    async def set_object(self, id:str=None, obj:dict={}, options:dict={}) -> None:
        """Set object in db and publish"""
        # check if access to object should be granted
        await utils.check_object_rights(self, id, obj, options, utils.ACCESS_WRITE)
        
        if 'ts' not in obj.keys():
            obj['ts'] = int(time.time())
            
        # on objects we save id as attribute
        obj['_id'] = id
        
        # set object as string
        await self.redis.set(f'{self.objectNamespace}{id}', json.dumps(obj))
        # publish object
        await self.redis.publish(f'{self.objectNamespace}{id}', json.dumps(obj))
        
    async def get_object(self, id:str=None, options:dict={}) -> dict:
        """get object out of redis db and parse"""
        try:
            obj:dict = json.loads(await self.redis.get(f'{self.objectNamespace}{id}'))
        except TypeError:
            # obj is not a valid json, probably non existing
            obj:dict = {}
        # check if access to object should be granted
        await utils.check_object_rights(self, id, obj, options, utils.ACCESS_READ)
        
        return obj
    
    async def subscribe(self, pattern:str, options:dict={}) -> None:
        """subscribe to object changes, if permissions allow it"""
        await utils.check_object_rights(self, None, None, options, 'list')
        await self.redis_sub.psubscribe(self.subs_receiver.pattern(f'{self.objectNamespace}{pattern}'))
        
    async def unsubscribe(self, pattern:str) -> None:
        """unsubscribe from state chamges"""
        await self.redis_sub.punsubscribe(f'{self.objectNamespace}{pattern}')
        
    async def get_message(self) -> dict:
        """get subscribed messages if some there"""
        while await self.subs_receiver.wait_message():
            sender, msg = await self.subs_receiver.get()
            if type(msg) == tuple:
                obj:dict = json.loads(msg[1])
                id:str = msg[0][len(self.objectNamespace):]
                return id, obj
            
    async def get_object_list(self, params, options):
        """returns all objects matching params.starkey to params.endkey"""
        # TODO
        pass