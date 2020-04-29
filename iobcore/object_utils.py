#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 16 15:39:52 2020

@author: moritz
"""

import re
import copy

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

users = {}
groups = {}

default_acl:dict = {
    'groups': [],
    'acl': {
        'file': {
            'list': False,
            'read': False,
            'write': False,
            'create': False,
            'delete': False
        },
        'object': {
            'list': False,
            'read': False,
            'write': False,
            'create': False,
            'delete': False
        },
        'state': {
            'list': False,
            'read': False,
            'write': False,
            'create': False,
            'delete': False
        },
        'users': {
            'list': False,
            'read': False,
            'write': False,
            'create': False,
            'delete': False
        }
    }
}

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
        _user, groups, acl = await get_user_group(objects, options['user'])
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

async def get_user_group(objects:dict, user:str):
    global users
    global groups
    
    if not re.match(reg_user, user):
        raise ValueError(f'Invalid username {user}')
        
    if user in users:
        return user, users[user]['groups'], users[user]['acl']
    
    res:dict = await objects.get_object_list({'startkey': 'system.group.', 'endkey': 'system.group.\u9999'}, {'checked': True})
    
    groups = []
    
    for i in range(len(res['rows'])):
        groups.append(res['rows'][i]['value'])
        if groups[i]['_id'] == SYSTEM_ADMIN_GROUP:
            groups[i]['common']['acl'] = get_default_admin_rights(groups[i]['common']['acl'])
            
    res:dict = await objects.get_object_list({'startkey': 'system.user.', 'endkey': 'system.user.\u9999'}, {'checked': True})
        
    users = {}
    
    for row in res['rows']:
        users[row['value']['_id']] = copy.deepcopy(default_acl)
      
    users[SYSTEM_ADMIN_USER] = users[SYSTEM_ADMIN_USER] if SYSTEM_ADMIN_USER in users else copy.deepcopy(default_acl)
    users[SYSTEM_ADMIN_USER]['acl'] = get_default_admin_rights(users[SYSTEM_ADMIN_USER]['acl'])
    
    for group in groups:
        if 'common' not in group or 'members' not in group['common']:
            continue
        
        for member in group['common']['members']:
            if not member in users:
                raise ValueError(f'Unknown user {member} in group {group}')
                
            users[member]['groups'].append(group['_id'])
            
            if 'common' in group and 'acl' in group['common'] and 'file' in group['common']['acl']:
                if 'acl' not in users[member] or 'file' not in users[member]['acl']:
                    users[member]['acl'] = {} if 'acl' not in users[member] else users[member]['acl']
                    users[member]['acl']['file'] = {} if 'file' not in users[member]['acl'] else users[member]['acl']['file']
                    
                    users[member]['acl']['file']['create'] = group['common']['acl']['file']['create']
                    users[member]['acl']['file']['read'] = group['common']['acl']['file']['read']
                    users[member]['acl']['file']['write'] = group['common']['acl']['file']['write']
                    users[member]['acl']['file']['delete'] = group['common']['acl']['file']['delete']
                    users[member]['acl']['file']['list'] = group['common']['acl']['file']['list']
                else:
                    users[member]['acl']['file']['create'] = users[member]['acl']['file']['create'] if 'create' in  users[member]['acl']['file'] and users[member]['acl']['file']['create'] is True else group['common']['acl']['file']['create'] 
                    users[member]['acl']['file']['read'] = users[member]['acl']['file']['read'] if 'read' in  users[member]['acl']['file'] and users[member]['acl']['file']['read'] is True else group['common']['acl']['file']['read']
                    users[member]['acl']['file']['write'] = users[member]['acl']['file']['write'] if 'write' in  users[member]['acl']['file'] and users[member]['acl']['file']['write'] is True else group['common']['acl']['file']['write']
                    users[member]['acl']['file']['delete'] = users[member]['acl']['file']['delete'] if 'delete' in  users[member]['acl']['file'] and users[member]['acl']['file']['delete'] is True else group['common']['acl']['file']['delete']
                    users[member]['acl']['file']['list'] = users[member]['acl']['file']['list'] if 'list' in  users[member]['acl']['file'] and users[member]['acl']['file']['list'] is True else group['common']['acl']['file']['list']

                if 'acl' not in users[member] or 'object' not in users[member]['acl']:
                    users[member]['acl'] = {} if 'acl' not in users[member] else users[member]['acl']
                    users[member]['acl']['file'] = {} if 'object' not in users[member]['acl'] else users[member]['acl']['file']
                    
                    users[member]['acl']['object']['create'] = group['common']['acl']['object']['create']
                    users[member]['acl']['object']['read'] = group['common']['acl']['object']['read']
                    users[member]['acl']['object']['write'] = group['common']['acl']['object']['write']
                    users[member]['acl']['object']['delete'] = group['common']['acl']['object']['delete']
                    users[member]['acl']['object']['list'] = group['common']['acl']['object']['list']
                else:
                    users[member]['acl']['object']['create'] = users[member]['acl']['object']['create'] if 'create' in  users[member]['acl']['object'] and users[member]['acl']['object']['create'] is True else group['common']['acl']['object']['create'] 
                    users[member]['acl']['object']['read'] = users[member]['acl']['object']['read'] if 'read' in  users[member]['acl']['object'] and users[member]['acl']['object']['read'] is True else group['common']['acl']['object']['read']
                    users[member]['acl']['object']['write'] = users[member]['acl']['object']['write'] if 'write' in  users[member]['acl']['object'] and users[member]['acl']['object']['write'] is True else group['common']['acl']['object']['write']
                    users[member]['acl']['object']['delete'] = users[member]['acl']['object']['delete'] if 'delete' in  users[member]['acl']['object'] and users[member]['acl']['object']['delete'] is True else group['common']['acl']['object']['delete']
                    users[member]['acl']['object']['list'] = users[member]['acl']['object']['list'] if 'list' in  users[member]['acl']['object'] and users[member]['acl']['object']['list'] is True else group['common']['acl']['object']['list']
                    
                if 'acl' not in users[member] or 'users' not in users[member]['acl']:
                    users[member]['acl'] = {} if 'acl' not in users[member] else users[member]['acl']
                    users[member]['acl']['users'] = {} if 'users' not in users[member]['acl'] else users[member]['acl']['file']
                    
                    users[member]['acl']['users']['create'] = group['common']['acl']['users']['create']
                    users[member]['acl']['users']['read'] = group['common']['acl']['users']['read']
                    users[member]['acl']['users']['write'] = group['common']['acl']['users']['write']
                    users[member]['acl']['users']['delete'] = group['common']['acl']['users']['delete']
                    users[member]['acl']['users']['list'] = group['common']['acl']['users']['list']
                else:
                    users[member]['acl']['users']['create'] = users[member]['acl']['users']['create'] if 'create' in  users[member]['acl']['users'] and users[member]['acl']['users']['create'] is True else group['common']['acl']['users']['create'] 
                    users[member]['acl']['users']['read'] = users[member]['acl']['users']['read'] if 'read' in  users[member]['acl']['users'] and users[member]['acl']['users']['read'] is True else group['common']['acl']['users']['read']
                    users[member]['acl']['users']['write'] = users[member]['acl']['users']['write'] if 'write' in  users[member]['acl']['users'] and users[member]['acl']['users']['write'] is True else group['common']['acl']['users']['write']
                    users[member]['acl']['users']['delete'] = users[member]['acl']['users']['delete'] if 'delete' in  users[member]['acl']['users'] and users[member]['acl']['users']['delete'] is True else group['common']['acl']['users']['delete']
                    users[member]['acl']['users']['list'] = users[member]['acl']['users']['list'] if 'list' in  users[member]['acl']['users'] and users[member]['acl']['users']['list'] is True else group['common']['acl']['users']['list']
                    
                if 'acl' not in users[member] or 'state' not in users[member]['acl']:
                    users[member]['acl'] = {} if 'acl' not in users[member] else users[member]['acl']
                    users[member]['acl']['state'] = {} if 'state' not in users[member]['acl'] else users[member]['acl']['file']
                    
                    users[member]['acl']['state']['create'] = group['common']['acl']['state']['create']
                    users[member]['acl']['state']['read'] = group['common']['acl']['state']['read']
                    users[member]['acl']['state']['write'] = group['common']['acl']['state']['write']
                    users[member]['acl']['state']['delete'] = group['common']['acl']['state']['delete']
                    users[member]['acl']['state']['list'] = group['common']['acl']['state']['list']
                else:
                    users[member]['acl']['state']['create'] = users[member]['acl']['state']['create'] if 'create' in  users[member]['acl']['state'] and users[member]['acl']['state']['create'] is True else group['common']['acl']['state']['create'] 
                    users[member]['acl']['state']['read'] = users[member]['acl']['state']['read'] if 'read' in  users[member]['acl']['state'] and users[member]['acl']['state']['read'] is True else group['common']['acl']['state']['read']
                    users[member]['acl']['state']['write'] = users[member]['acl']['state']['write'] if 'write' in  users[member]['acl']['state'] and users[member]['acl']['state']['write'] is True else group['common']['acl']['state']['write']
                    users[member]['acl']['state']['delete'] = users[member]['acl']['state']['delete'] if 'delete' in  users[member]['acl']['state'] and users[member]['acl']['state']['delete'] is True else group['common']['acl']['state']['delete']
                    users[member]['acl']['state']['list'] = users[member]['acl']['state']['list'] if 'list' in  users[member]['acl']['state'] and users[member]['acl']['state']['list'] is True else group['common']['acl']['state']['list']
                    
    return user, [''], users[user]['acl'] if user in users else default_acl['acl']