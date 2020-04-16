#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 14 11:08:48 2020

@author: moritz
"""

from states import StatesDB
from objects import ObjectsDB

class Adapter:
    
    def __init__(self, name:str, namespace:str) -> None:
        self.name = name
        self.namespace = namespace
          
        self._objects = ObjectsDB()
        self._states = StatesDB()
    
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
        
    async def get_object(self, id:str) -> dict:
        """returns object of adapters namespace"""
        id = f'{self.namespace}.{id}'
        return await self.get_foreign_object(id)
    
    async def get_foreign_object(self, id:str) -> dict:
        """returns object"""
        return await self._objects.get_object(id)
    
    async def set_object(self, id:str, obj:dict) -> None:
        """set object to adapters namespace"""
        id = f'{self.namespace}.{id}'
        return await self.set_foreign_object(id, obj)
    
    async def set_foreign_object(self, id:str, obj:dict) -> None:
        """set object in DB"""
        if 'from' not in obj.keys():
            obj['from'] = f'system.adapter.{self.namespace}'
        await self._objects.set_object(id, obj)
        
    async def get_state(self, id:str) -> dict:
        """returns state of adapters namespace"""
        id = f'{self.namespace}.{id}'
        return await self.get_foreign_state(id)
    
    async def get_foreign_state(self, id:str) -> dict:
        """returns state"""
        return await self._states.get_state(id)
    
    async def set_state(self, id:str, state:dict) -> None:
        """set state to adapters namespace"""
        id = f'{self.namespace}.{id}'
        return await self.set_foreign_state(id, state)
    
    async def set_foreign_state(self, id:str, state:dict) -> None:
        """set state in DB"""
        if 'from' not in state.keys():
            state['from'] = f'system.adapter.{self.namespace}'
        await self._states.set_state(id, state)
    
    async def subscribe_states(self, pattern:str) -> None:
        """subscribe to state changes"""
        await self.subscribe_foreign_states(f'{self.namespace}{pattern}')
        
    async def subscribe_foreign_states(self, pattern:str) -> None:
        """subscribe to foreign state changes"""
        await self._states.subscribe(pattern)

    async def subscribe_objects(self, pattern:str) -> None:
        """subscribe to object changes"""
        await self.subscribe_foreign_objects(f'{self.namespace}{pattern}')
        
    async def subscribe_foreign_objects(self, pattern:str) -> None:
        """subscribe to foreign state changes"""
        await self._objects.subscribe(pattern)
        
    async def unsubscribe_states(self, pattern:str) -> None:
        """unsubscribe to state changes"""
        await self.unsubscribe_foreign_states(f'{self.namespace}{pattern}')
        
    async def unsubscribe_foreign_states(self, pattern:str) -> None:
        """unsubscribe to foreign state changes"""
        await self._states.unsubscribe(pattern)

    async def unsubscribe_objects(self, pattern:str) -> None:
        """unsubscribe to object changes"""
        await self.unsubscribe_foreign_objects(f'{self.namespace}{pattern}')
        
    async def unsubscribe_foreign_objects(self, pattern:str) -> None:
        """unsubscribe to foreign state changes"""
        await self._objects.unsubscribe(pattern)
        
    async def get_state_updates(self) -> dict:
        """get subscribed state changes"""
        return await self._states.get_message()
    
    async def get_object_updates(self) -> dict:
        """get subscribed state changes"""
        return await self._objects.get_message()