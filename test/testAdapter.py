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
        async def subscribe_foreign_states():
            await self.adapter.subscribe_foreign_states('hm-rpc.0.*')
            self.count = 0
            def state_cb(state_id, state):
                # check if correct state or expire
                if state_id == 'hm-rpc.0.test' and (set_state == state or state == {}):
                    self.count += 1
                    if self.count == 2:
                        self.count = None
                        loop.stop()   
                else:
                    self.assertTrue(False, f'hm-rpc.0.* subscribed, but got {state_id}')
            
            self.adapter.change_state_cb(state_cb)
            set_state:dict = {'val': 5, 'expire': 1}
            await self.adapter.set_state('test', set_state)
            await self.adapter.set_foreign_state('hm-rega.0.test', {'val': '3'})                
            
        loop = asyncio.get_event_loop()
        loop.create_task(subscribe_foreign_states())
        loop.run_forever()
        
    def test_subscribe_foreign_objects(self):
        async def subscribe_foreign_objects():
            await self.adapter.subscribe_objects('tes*')
            
            def obj_cb(obj_id, obj):
                # check if correct state or expire
                if obj_id == 'hm-rpc.0.testing' and set_object == obj:
                        loop.stop()   
                else:
                    self.assertTrue(False, f'hm-rpc.0.* subscribed, but got {obj_id}')
            
            self.adapter.change_object_cb(obj_cb)
            set_object:dict = {'type': 'state', 
                              'common': {
                                      'name': 'hello',
                                      'type': 'string'
                                      }
                              }
                              
            await self.adapter.set_object('testing', set_object)
            await self.adapter.set_object('notMatching', {'type' : 'meta'})

            
        loop = asyncio.get_event_loop()
        loop.create_task(subscribe_foreign_objects())
        loop.run_forever()
        
    def test_get_object_list(self):
        _run(self.adapter.set_foreign_object('hm-rpc.0.object_list_test', {'type': 'state',
                                                                           'common': {
                                                                                   'name': 'get list',
                                                                                   'type': 'string'
                                                                                   }
                                                                           }))
        objs:dict = _run(self.adapter.get_object_list({'startkey': 'hm-rpc.0', 'endkey': 'hm-rpc.0\u9999'}))
        self.assertTrue('rows' in objs)
        
        ok:bool = False
        
        for obj in objs['rows']:
            if obj['id'] == 'hm-rpc.0.object_list_test' and obj['value']['type'] == 'state':
                ok = True
                
        self.assertTrue(ok, msg='hm-rpc.0.object_list_test not found in the objects list or not of type state')
        
    def test_get_keys(self):
        for i in range(20):
            _run(self.adapter.set_foreign_state(f'hm-rpc.0.test_get_states{i}', {'val': i}))
            
        states:list = _run(self.adapter.get_keys('hm-rpc.0.test_get_states*'))
        
        for i in range(20):
            self.assertTrue(f'hm-rpc.0.test_get_states{i}' in states)

if __name__ == '__main__':
    unittest.main()