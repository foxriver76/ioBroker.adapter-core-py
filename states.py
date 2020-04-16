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
        if 'ts' not in state.keys():
            state['ts'] = int(time.time())
            
        if 'ack' not in state.keys():
            state['ack'] = False
        
        if 'lc' not in state.keys():
            # get old obj and check if changed
            old_state:dict = await self.get_state(id)
            curr_state = state.copy()
            
            # ignore ts and lc
            curr_state.pop('ts', None)
            curr_state.pop('lc', None)
            old_state.pop('ts', None)
            old_lc:int = old_state.pop('lc', None)
            
            if old_state != curr_state and old_lc is not None:
                # not changed and lc exists
                state['lc'] = old_lc
            else:
                state['lc'] = state['ts']

        # check if we set with expire         
        if 'expire' not in state.keys():
            # set state as string
            await self.redis.set(f'{self.namespace}{id}', json.dumps(state))
        else:
            expire:int = state['expire']
            del state['expire']
            await self.redis.setex(f'{self.namespace}{id}', expire,
                             value=json.dumps(state))
        # publish state
        await self.redis.publish(f'{self.namespace}{id}', json.dumps(state))

        
    async def get_state(self, id:str=None) -> dict:
        """get object out of redis db and parse"""
        try: 
            state:dict = json.loads(await self.redis.get(f'{self.namespace}{id}'))
        except TypeError:
            # state is not a valid json, probably non existing
            state:dict = {}
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