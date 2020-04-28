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
        
    def subscribe_foreign_states(self):
        _run(self.adapter.subscribe_foreign_states('hm-rpc.0.*'))
        loop = asyncio.get_event_loop()
        
        async def handle_state_changes():
            print('now waiting')
            stateId, state = await self.adapter.get_state_updates()
            print(f'state change of {stateId}:\n{state}')
            return
            if not stateId.startswith('hm-rpc.0'):
                self.assertTrue(False, msg=f'Only hm-rpc.0* is subscribed, but got {stateId}')
                    
        _run(self.adapter.set_foreign_state('test.0.testing', {'val': 5}))
        _run(self.adapter.set_foreign_state('hm.rpc.0.device.ch.state', 
                                            {'val': 3}))
        
        loop = asyncio.get_event_loop()
        loop.create_task(handle_state_changes())
            
        loop.run_forever()
         
        """
    async def main(self):                            
        await self.adapter.subscribe_objects('*')
        await self.adapter.subscribe_states('*')
        
        await self.adapter.set_state('test', {'val': 5, 'expire': 2})
        
        async def handle_object_updates():
            # listen to object changes
            while (True):
                objId, obj = await self.adapter.get_object_updates()
                print(f'object change of {objId}:\n{obj}')
                
        async def handle_state_updates():
            # listen to state changes
            while (True):
                stateId, state = await self.adapter.get_state_updates()
                print(f'state change of {stateId}:\n{state}')
        
        # register your state handlers
        asyncio.create_task(handle_object_updates())
        asyncio.create_task(handle_state_updates())
            
        while (True):
            # Do what you like here
            await asyncio.sleep(0.2)"""
        
if __name__ == '__main__':
    unittest.main()