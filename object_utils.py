#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 16 15:39:52 2020

@author: moritz
"""

SYSTEM_ADMIN_USER  = 'system.user.admin'
SYSTEM_ADMIN_GROUP = 'system.group.administrator'

ERROR_PERMISSION   = 'permissionError'
ERROR_NOT_FOUND    = 'Not exists'
ERROR_DB_CLOSED    = 'DB closed'

ACCESS_EVERY_EXEC  = 0x1
ACCESS_EVERY_WRITE = 0x2
ACCESS_EVERY_READ  = 0x4
ACCESS_EVERY_RW    = ACCESS_EVERY_WRITE | ACCESS_EVERY_READ
ACCESS_EVERY_ALL   = ACCESS_EVERY_WRITE | ACCESS_EVERY_READ | ACCESS_EVERY_EXEC

ACCESS_GROUP_EXEC  = 0x10
ACCESS_GROUP_WRITE = 0x20
ACCESS_GROUP_READ  = 0x40
ACCESS_GROUP_RW    = ACCESS_GROUP_WRITE | ACCESS_GROUP_READ
ACCESS_GROUP_ALL   = ACCESS_GROUP_WRITE | ACCESS_GROUP_READ | ACCESS_GROUP_EXEC

ACCESS_USER_EXEC   = 0x100
ACCESS_USER_WRITE  = 0x200
ACCESS_USER_READ   = 0x400
ACCESS_USER_RW     = ACCESS_USER_WRITE | ACCESS_USER_READ
ACCESS_USER_ALL    = ACCESS_USER_WRITE | ACCESS_USER_READ | ACCESS_USER_EXEC

ACCESS_WRITE       = 0x2
ACCESS_READ        = 0x4
ACCESS_LIST        = 'list'
ACCESS_DELETE      = 'delete'
ACCESS_CREATE      = 'create'

def check_object(object, options:dict, flag) -> None:
    """check if access to object should be granted, else throw PermissionError"""
    #todo
    if ('user' in options.keys()):
        raise PermissionError(f'{options.user} does not have permission')