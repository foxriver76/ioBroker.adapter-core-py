#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 14 11:08:36 2020

@author: moritz
"""

import aioredis
import json
import time

class StatesDB:
    
    def __init__(self, port:int=6379, namespace:str='io'):
        self.port = port
        self.namespace = f'{namespace}.'
        
    async def init_db(self) -> None:
        self.redis = await aioredis.create_redis(('localhost', self.port))
        self.subs_receiver = aioredis.pubsub.Receiver()
        
    async def set_state(self, id:str=None, state:dict={}) -> None:
        """Set state in db and publish"""
        state['ts'] = int(time.time())
        # check if we set with expire         
        if 'expire' not in state.keys():
            # set state as string
            await self.redis.set(f'{self.namespace}{id}', json.dumps(state))
        else:
            await self.redis.setex(f'{self.namespace}{id}', state['expire'], 
                             value=json.dumps(state))
        # publish state
        await self.redis.publish(f'{self.namespace}{id}', json.dumps(state))

        
    async def get_state(self, id:str=None) -> dict:
        """get object out of redis db and parse"""
        state:dict = json.loads(await self.redis.get(f'{self.namespace}{id}'))
        return state
    
    async def subscribe(self, pattern:str) -> None:
        """subscribe to state changes"""
        await self.redis.psubscribe(self.subs_receiver.pattern(f'{self.namespace}{pattern}'))
        
    async def unsubscribe(self, pattern:str) -> None:
        """unsubscribe from object chamges"""
        await self.redis.punsubscribe(f'{self.namespace}{pattern}')
        
    async def get_message(self) -> dict:
        """get subscribed messages if some there"""
        while await self.subs_receiver.wait_message():
            sender, msg = await self.subs_receiver.get()
            if type(msg) == tuple:
                state:dict = json.loads(msg[1])
                id:str = msg[0][len(self.namespace):]
                return id, state             