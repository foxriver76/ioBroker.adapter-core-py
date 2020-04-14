#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 14 11:57:49 2020

@author: moritz
"""

from adapter import Adapter
import json
import time

adapter = Adapter('hm-rpc', 'hm-rpc.1')

adapter.set_object('testObj', json.loads('{\
        "type": "state",\
        "common": {\
                }\
        }'
        ))

testObj = adapter.get_foreign_object('hm-rpc.1.testObj')

adapter.subscribe_objects('*')
adapter.subscribe_states('*')

while (True):
    new_object_update = adapter.get_object_updates()
    if new_object_update != None:
        print(f'new objects update: \n {new_object_update}')
    
    new_state_update = adapter.get_state_updates()
    if (new_state_update != None):
        print(f'new state update: \n {new_state_update}')
       
    # this is important, because of cpu usage
    time.sleep(0.2)