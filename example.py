 #!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 14 11:57:49 2020

@author: moritz
"""

from iobcore.adapter import Adapter
import asyncio

async def main():
    
    def handle_object_updates(obj_id, obj):
        adapter.log.info(f'got obj {obj_id} {obj}')
      
    def handle_state_updates(state_id, state):
        adapter.log.info(f'got state {state_id} {state}')
    
    adapter = Adapter('hm-rpc', 'hm-rpc.0', handle_state_updates, handle_object_updates)
    await adapter.prepare_for_use()
    
    await adapter.set_object('testObj', {
            'type': 'state',
            'common': {}
            })
    
    try:
        testObj = await adapter.get_foreign_object('hm-rpc.0.testObj.')
        adapter.log.error(testObj)
    except Exception as e:
        adapter.log.error(e)
        
    await adapter.set_state('testing', {'val1': True})
    testState = await adapter.get_state('testing')
    
    adapter.log.info(testState)
    
    await adapter.subscribe_objects('*')
    await adapter.subscribe_states('*')
    
    await adapter.set_state('test', {'val': 5, 'expire': 2})
        
    while (True):
        # Do what you like here
        await asyncio.sleep(0.2)
                     
asyncio.run(main())