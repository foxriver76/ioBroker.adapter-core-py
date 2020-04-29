#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 16 15:39:52 2020

@author: moritz
"""

import re

reg_user = '^system\.user\.'
reg_group = '^system\.group\.'
reg_check_id = '[*?\[\]]|\$%\$'

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

async def check_object_rights(objects:dict=None, id:str=None, obj:dict={}, options:dict={}, flag:str=None):
    """check object rights - throw PermissionError if not granted"""
    if 'user' not in options.keys():
        options = {
                'user': SYSTEM_ADMIN_USER,
                'params': options,
                'group': SYSTEM_ADMIN_GROUP,
                'groups': [SYSTEM_ADMIN_GROUP],
                'acl': get_default_admin_rights()
                }
        
    if 'acl' not in options.keys():
        _user, groups, acl = get_user_group(objects, options['user'])
        options['acl'] = {} if acl is None else acl
        options['groups'] = groups
        options['group'] = None if groups is None else groups[0]
        return await check_object_rights(objects, id, obj, options, flag)
        
    if (options['user'] == SYSTEM_ADMIN_USER or options['group'] == SYSTEM_ADMIN_GROUP
        or ('groups' in options.keys() and SYSTEM_ADMIN_GROUP in options['groups'])):
        # ADMIN has all rights
        return
    
    # if user or group objects
    if re.match(reg_user, id) or re.match(reg_group, id):
        if flag == ACCESS_WRITE and not options['acl']['users']['write']:
            raise PermissionError()
        
        if flag == ACCESS_READ and not options['acl']['users']['read']:
            raise PermissionError()
            
        if flag == ACCESS_DELETE and not options['acl']['users']['delete']:
            raise PermissionError()
            
        if flag == ACCESS_LIST and not options['acl']['users']['list']:
            raise PermissionError()
            
        if flag == ACCESS_CREATE and not options['acl']['users']['create']:
            raise PermissionError()
            
        # if user may write he may delete
        if flag == ACCESS_DELETE:
            flag = ACCESS_WRITE
        
   
    if flag == ACCESS_WRITE and not options['acl']['object']['write']:
        raise PermissionError()
        
    if flag == ACCESS_READ and not options['acl']['object']['read']:
        raise PermissionError()
        
    if flag == ACCESS_DELETE and not options['acl']['object']['delete']:
        raise PermissionError()
        
    if flag == ACCESS_LIST and not options['acl']['object']['list']:
        raise PermissionError()
        
    if flag == ACCESS_DELETE:
        flag = ACCESS_WRITE
        
    if id is not None:
        check_object(obj, options, flag)
        return
    else: 
        return

def check_object(obj:dict={}, options:dict={}, flag:str=None) -> None:
    """check if access to object should be granted, else throw PermissionError"""
    if 'acl' not in obj.keys() or 'common' not in 'acl' not in obj.keys() or flag == ACCESS_LIST:
        # no acl configured for this object or no common
        return
    
    if 'user' in options.keys():
        if options['user'] == SYSTEM_ADMIN_USER:
            # admin has all perms
            return
            
    if 'group' in options.keys():
        if options['group'] == SYSTEM_ADMIN_GROUP:
            # admin group has all perms
            return
            
    if 'groups' in options.keys():
        if SYSTEM_ADMIN_GROUP in options['group']:
            # admin group has all perms
            return
        
    if 'user' not in options or obj['acl']['owner'] != options['user']:
        # owner is not user who wants access, maybe group fits
        if 'group' in options.keys() and options['group'] == obj['acl']['ownerGroup'] or 'groups' in options.keys() and obj['acl']['ownerGroup'] in options['groups']:
            if not (obj['acl']['object'] & (flag << 4)):
                raise PermissionError()
            elif not (obj['acl']['object'] & flag):
                raise PermissionError()
    elif not (obj['acl']['object'] &  (flag << 8)):
        # check group rights
        raise PermissionError()
        
def get_default_admin_rights(acl:dict=None):
    acl = {} if acl is None else acl
    
    acl['file'] = {
        'list': True,
        'read': True,
        'write': True,
        'create': True,
        'delete': True
    }
    
    acl['object'] = {
        'create': True,
        'list': True,
        'read': True,
        'write': True,
        'delete': True
    }
    
    acl['users'] = {
        'create': True,
        'list': True,
        'read': True,
        'write': True,
        'delete': True
    }
    
    acl['state'] = {
        'read': True,
        'write': True,
        'delete': True,
        'create': True,
        'list': True
    }

    return acl

def get_user_group(objects:dict, user:str):
    acl = {}
    
    # TODO    
    acl['file'] = {
        'list': False,
        'read': False,
        'write': False,
        'create': False,
        'delete': False
    }
    
    acl['object'] = {
        'create': False,
        'list': False,
        'read': False,
        'write': False,
        'delete': False
    }
    
    acl['users'] = {
        'create': False,
        'list': False,
        'read': False,
        'write': False,
        'delete': False
    }
    
    acl['state'] = {
        'read': False,
        'write': False,
        'delete': False,
        'create': False,
        'list': False
    }
    
    return user, [''], acl