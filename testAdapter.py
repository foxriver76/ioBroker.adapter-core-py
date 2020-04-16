 #!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 14 11:57:49 2020

@author: moritz
"""

from adapter import Adapter
import json
import asyncio

async def main():
    adapter = Adapter('hm-rpc', 'hm-rpc.0')
    await adapter.prepare_for_use()
    
    await adapter.set_object('testObj', json.loads('{\
            "type": "state",\
            "common": {\
                    }\
            }'
            ))
    
    try:
        testObj = await adapter.get_foreign_object('hm-rpc.0.testObj.')
        print(testObj)
    except Exception as e:
        print(e)
        
    await adapter.set_state('testing', {'val1': True})
    testState = await adapter.get_state('testing')
    
    print(testState)
    
    await adapter.subscribe_objects('*')
    await adapter.subscribe_states('*')
    
    async def handle_object_updates():
        # listen to object changes
        while (True):
            objId, obj = await adapter.get_object_updates()
            print(f'object change of {objId}:\n{obj}')
            
    async def handle_state_updates():
        # listen to state changes
        while (True):
            stateId, state = await adapter.get_state_updates()
            print(f'state change of {stateId}:\n{state}')
    
    # register your state handlers
    asyncio.create_task(handle_object_updates())
    asyncio.create_task(handle_state_updates())
    
    while (True):
        # Do what you like here
        await asyncio.sleep(0.2)
                     
asyncio.run(main())