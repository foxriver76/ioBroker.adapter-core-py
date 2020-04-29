#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 14 11:08:48 2020

@author: moritz
"""

# TODOs:
# use real logger

from iobcore.states import StatesDB
from iobcore.objects import ObjectsDB
import asyncio
import fnmatch
import time
from iobcore.logger import IobLogger

class Adapter:
    
    def __init__(self, name:str, namespace:str, state_cb=None, obj_cb=None, logfile:str='log.log', loglevel='info') -> None:
        self.name = name
        self.namespace = namespace
        
        self.state_cb = state_cb
        self.obj_cb = obj_cb
        self.loglevel = loglevel
        
        self.log_list = []
        self.log = IobLogger(self.namespace, self.loglevel, self._log_push)

        self._objects = ObjectsDB()
        self._states = StatesDB(logger=self.log)
    
    async def prepare_for_use(self):
        await self._states.init_db()
        await self._objects.init_db()
        
        # adapter is alive
        await self._states.set_state(f'system.adapter.{self.namespace}.alive', {
                'val': True, 
                'ack': True,
                'expire': 30,
                'from': f'system.adapter.{self.namespace}'
                })

        # tell that we are connected to objects db
        await self._states.set_state(f'system.adapter.{self.namespace}.connected', {
                'val': True,
                'ack': True,
                'expire': 30,
                'from': f'system.adapter.{self.namespace}'
                })
    
        await self.init_logging()
                
        asyncio.create_task(self.handle_object_changes())
        asyncio.create_task(self.handle_state_changes())
        
    async def handle_state_changes(self) -> None:
        while (True):
            state_id, state = await self._states.get_message()
            self.log.debug(f'state change {state_id}:\n{state}')
            if fnmatch.fnmatch(state_id, '*.logging'):
                adapter_name:str = state_id[:-len(".logging")]
                if state['val'] is True and adapter_name not in self.log_list:
                    # add to log list
                    self.log_list.append(adapter_name)
                elif state['val'] is False and adapter_name in self.log_list:
                    self.log_list.remove(adapter_name)             
                continue
            if self.state_cb is not None:
                self.state_cb(state_id, state)
            
    async def handle_object_changes(self) -> None:
        while (True):
            obj_id, obj = await self._objects.get_message()
            self.log.debug(f'object change {obj_id}:\n{obj}')
            if self.obj_cb is not None:
                self.obj_cb(obj_id, obj)
            
    async def init_logging(self) -> None:
        """init logging, store who wants our logs"""
        # get all logging states
        keys:list = await self._states.get_keys('*.logging')
        states:list = await self._states.get_states(keys)
        
        for i in range(len(keys)):
            # all True states want our log
            if states[i]['val'] is True and keys[i] not in self.log_list:
                self.log_list.append(keys[i][:-len(".logging")])
                
        # now we subscribe to changes on logging        
        await self.subscribe_foreign_states('*.logging')
        
    def change_object_cb(self, obj_cb):
        self.obj_cb = obj_cb
        
    def change_state_cb(self, state_cb):
        self.state_cb = state_cb
        
    async def get_object(self, id:str, options:dict={}) -> dict:
        """returns object of adapters namespace"""
        id:str = f'{self.namespace}.{id}'
        return await self.get_foreign_object(id, options)
    
    async def get_object_list(self, params:dict={}, options:dict={}):
        """get all objects matching the startkey and endkey"""
        return await self._objects.get_object_list(params, options)        
    
    async def get_foreign_object(self, id:str, options:dict={}) -> dict:
        """returns object"""
        #  validate that id does not violate our db pattern
        self._validate_id(id)
        
        return await self._objects.get_object(id, options)
    
    async def set_object(self, id:str, obj:dict) -> None:
        """set object to adapters namespace"""
        id:str = f'{self.namespace}.{id}'
        return await self.set_foreign_object(id, obj)
    
    async def set_foreign_object(self, id:str, obj:dict) -> None:
        """set object in DB"""
        #  validate that id does not violate our db pattern
        self._validate_id(id)
        
        # add from attribute if not given
        if 'from' not in obj.keys():
            obj['from'] = f'system.adapter.{self.namespace}'
            
        await self._objects.set_object(id, obj)
        
    async def get_state(self, id:str) -> dict:
        """returns state of adapters namespace"""
        id:str = f'{self.namespace}.{id}'
        return await self.get_foreign_state(id)
    
    async def get_states(self, keys:list) -> list:
        return await self._states.get_states(keys)
    
    async def get_foreign_state(self, id:str) -> dict:
        """returns state"""
        #  validate that id does not violate our db pattern
        self._validate_id(id)
        
        return await self._states.get_state(id)
    
    async def set_state(self, id:str, state:dict) -> None:
        """set state to adapters namespace"""
        id:str = f'{self.namespace}.{id}'
        return await self.set_foreign_state(id, state)
    
    async def set_foreign_state(self, id:str, state:dict) -> None:
        """set state in DB"""
        #  validate that id does not violate our db pattern
        self._validate_id(id)
        
        # add from attribute if not given
        if 'from' not in state.keys():
            state['from'] = f'system.adapter.{self.namespace}'

        await self._states.set_state(id, state)
    
    async def subscribe_states(self, pattern:str) -> None:
        """subscribe to state changes"""
        await self.subscribe_foreign_states(f'{self.namespace}.{pattern}')
        
    async def subscribe_foreign_states(self, pattern:str) -> None:
        """subscribe to foreign state changes"""
        await self._states.subscribe(pattern)

    async def subscribe_objects(self, pattern:str) -> None:
        """subscribe to object changes"""
        await self.subscribe_foreign_objects(f'{self.namespace}.{pattern}')
        
    async def subscribe_foreign_objects(self, pattern:str) -> None:
        """subscribe to foreign state changes"""
        await self._objects.subscribe(pattern)
        
    async def unsubscribe_states(self, pattern:str) -> None:
        """unsubscribe to state changes"""
        await self.unsubscribe_foreign_states(f'{self.namespace}.{pattern}')
        
    async def unsubscribe_foreign_states(self, pattern:str) -> None:
        """unsubscribe to foreign state changes"""
        await self._states.unsubscribe(pattern)

    async def unsubscribe_objects(self, pattern:str) -> None:
        """unsubscribe to object changes"""
        await self.unsubscribe_foreign_objects(f'{self.namespace}.{pattern}')
        
    async def unsubscribe_foreign_objects(self, pattern:str) -> None:
        """unsubscribe to foreign state changes"""
        await self._objects.unsubscribe(pattern)
        
    async def get_keys(self, pattern:str) -> list:
        """get keys as list matching the pattern"""
        return await self._states.get_keys(pattern)
        
    async def get_state_updates(self) -> dict:
        """get subscribed state changes"""
        return await self._states.get_message()
    
    async def get_object_updates(self) -> dict:
        """get subscribed state changes"""
        return await self._objects.get_message()
    
    def _log_push(self, message:str, severity:str='info') -> None:
        for id in self.log_list:
            log_obj:dict = {'message': str(message), 'severity': severity, 'from': self.namespace, 'ts': int(time.time() * 1000)}
            self._states.push_log(id, log_obj)
        
    def _validate_id(self, id:str) -> None:
        """validate that id fits our restrictions
            if id is invalid an error is raised
        """
        if type(id) is not str:
            raise TypeError(f'The id has an invalid type! Expected "string", received "{type(id)}".')
            
        if id == '':
            raise ValueError('The id is empty! Please provide a valid id.')
            
        if id.endswith('.'):
            raise ValueError('The id is invalid. Ids are not allowed to end in "."')