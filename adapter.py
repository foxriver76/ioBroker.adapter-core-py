#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 14 11:08:48 2020

@author: moritz
"""

from states import StatesDB
from objects import ObjectsDB

class Adapter:
    
    def __init__(self, name:str, namespace:str):
        self.name = name
        self.namespace = namespace
          
        self._objects = ObjectsDB()
        self._states = StatesDB()
        
        # adapter is alive
        self._states.set_state(f'system.adapter.{self.namespace}.alive', {
                'val': True, 
                'ack': True,
                'expire': 30,
                'from': f'system.adapter.{self.namespace}'
                })

        # tell that we are connected to objects db
        self._states.set_state(f'system.adapter.{self.namespace}.connected', {
                'val': True,
                'ack': True,
                'expire': 30,
                'from': f'system.adapter.{self.namespace}'
                })
        
    def get_object(self, id:str) -> dict:
        """returns object of adapters namespace"""
        id = f'{self.namespace}.{id}'
        return self.get_foreign_object(id)
    
    def get_foreign_object(self, id:str) -> dict:
        """returns object"""
        return self._objects.get_object(id)
    
    def set_object(self, id:str, obj:dict) -> None:
        """set object to adapters namespace"""
        id = f'{self.namespace}.{id}'
        return self.set_foreign_object(id, obj)
    
    def set_foreign_object(self, id:str, obj:dict) -> None:
        """set object in DB"""
        self._objects.set_object(id, obj)
        
    def get_state(self, id:str) -> dict:
        """returns state of adapters namespace"""
        id = f'{self.namespace}.{id}'
        return self.get_foreign_state(id)
    
    def get_foreign_state(self, id:str) -> dict:
        """returns state"""
        return self._states.get_state(id)
    
    def set_state(self, id:str, state:dict) -> None:
        """set state to adapters namespace"""
        id = f'{self.namespace}.{id}'
        return self.set_foreign_state(state)
    
    def set_foreign_state(self, id:str, state:dict) -> None:
        """set state in DB"""
        self._state.set_state(id, state)
    
    def subscribe_states(self, pattern:str) -> None:
        """subscribe to state changes"""
        self.subscribe_foreign_states(f'{self.namespace}{pattern}')
        
    def subscribe_foreign_states(self, pattern:str) -> None:
        """subscribe to foreign state changes"""
        self._states.subscribe(pattern)

    def subscribe_objects(self, pattern:str) -> None:
        """subscribe to object changes"""
        self.subscribe_foreign_objects(f'{self.namespace}{pattern}')
        
    def subscribe_foreign_objects(self, pattern:str) -> None:
        """subscribe to foreign state changes"""
        self._objects.subscribe(pattern)
        
    def unsubscribe_states(self, pattern:str) -> None:
        """unsubscribe to state changes"""
        self.unsubscribe_foreign_states(f'{self.namespace}{pattern}')
        
    def unsubscribe_foreign_states(self, pattern:str) -> None:
        """unsubscribe to foreign state changes"""
        self._states.unsubscribe(pattern)

    def unsubscribe_objects(self, pattern:str) -> None:
        """unsubscribe to object changes"""
        self.unsubscribe_foreign_objects(f'{self.namespace}{pattern}')
        
    def unsubscribe_foreign_objects(self, pattern:str) -> None:
        """unsubscribe to foreign state changes"""
        self._objects.unsubscribe(pattern)
        
    def get_state_updates(self) -> str:
        """get subscribed state changes"""
        return self._states.get_message()
    
    def get_object_updates(self) -> str:
        """get subscribed state changes"""
        return self._objects.get_message()