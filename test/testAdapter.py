 #!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 14 11:57:49 2020

@author: moritz
"""

from iobcore.adapter import Adapter
import asyncio
import unittest

# Helper method for async testing
def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)

def _async_task(coro):
    asyncio.run(coro)
    return asyncio.create_task(coro)

class TestAdapter(unittest.TestCase):
    
    def setUp(self):
        self.adapter = Adapter('hm-rpc', 'hm-rpc.0')
        _run(self.adapter.prepare_for_use())
        
    def test_set_object_invalid(self):
        obj:dict = {
            'type': 'state',
            'common': {}
            }
        
        self.assertRaises(ValueError, _run, 
                          self.adapter.set_object('testObj.', obj))
        
    def test_set_get_object_valid(self):
        set_obj:dict = {
            'type': 'state',
            'common': {}
            }

        _run(self.adapter.set_object('testObj1', set_obj))
        get_obj = _run(self.adapter.get_object('testObj1'))
        self.assertDictEqual(set_obj, get_obj)
        
    def test_set_get_state(self):
        set_state:dict = {
                'val': 'here'
                } 
        
        _run(self.adapter.set_state('testState1', set_state))
        
        get_state:dict = _run(self.adapter.get_state('testState1'))
        self.assertEqual(get_state['ack'], False)
        self.assertEqual(get_state['val'], 'here')
        self.assertEqual(type(get_state['ts']), int)
        
    def test_get_object_permissions(self):
        self.assertRaises(PermissionError, _run, self.adapter.get_object('testObj1', {'user': 'system.user.max'}))
        
    def test_subscribe_foreign_states(self):
        async def subscribe_froeign_states():
            await self.adapter.subscribe_foreign_states('hm-rpc.0.*')
            
            set_state:dict = {'val': 5, 'expire': 1}
            await self.adapter.set_state('test', set_state)
            await self.adapter.set_foreign_state('hm-rega.0.test', {'val': '3'})
            
            count:int = 0
            
            while (True):
                state_id, state = await self.adapter.get_state_updates()
                
                # check if correct state or expire
                if state_id == 'hm-rpc.0.test' and (set_state == state or state == {}):
                    count += 1
                    if count == 2:
                        loop.stop()   
                else:
                    self.assertTrue(False, f'hm-rpc.0.* subscribed, but got {state_id}')
            
        loop = asyncio.get_event_loop()
        loop.create_task(subscribe_froeign_states())
        loop.run_forever()
        
    def test_subscribe_foreign_objects(self):
        async def subscribe_foreign_objects():
            await self.adapter.subscribe_objects('tes*')
            
            set_object:dict = {'type': 'state', 
                              'common': {
                                      'name': 'hello',
                                      'type': 'string'
                                      }
                              }
                              
            await self.adapter.set_object('testing', set_object)
            await self.adapter.set_object('notMatching', {'type' : 'meta'})

            while (True):
                obj_id, obj = await self.adapter.get_object_updates()
                # check if correct state or expire
                if obj_id == 'hm-rpc.0.testing' and set_object == obj:
                        loop.stop()   
                else:
                    self.assertTrue(False, f'hm-rpc.0.* subscribed, but got {obj_id}')
            
        loop = asyncio.get_event_loop()
        loop.create_task(subscribe_foreign_objects())
        loop.run_forever()
        
if __name__ == '__main__':
    unittest.main()