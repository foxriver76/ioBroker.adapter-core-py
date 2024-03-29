#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 29 21:43:34 2020

@author: moritz
"""

import logging

class IobLogger(logging.Logger):
    
    def __init__(self, namespace:str, loglevel:str, cb, logfile:str):
        super().__init__(self)
        if loglevel.upper() == 'SILLY':
            loglevel = 'DEBUG'
        elif loglevel.upper() == 'WARN':
            loglevel = 'WARNING'
    
        self.cb = cb
        self.d = {'namespace': namespace}
        FORMAT = '%(asctime)s.%(msecs)03d  - %(loglevel)s: %(namespace)s %(message)s'
        self.setLevel(loglevel.upper())
        
        formatter = logging.Formatter(FORMAT, datefmt='%Y-%m-%d %H:%M:%S')
        
        # stream handler
        ch = logging.StreamHandler()
        ch.setLevel(loglevel.upper())
        ch.setFormatter(formatter)
        
        self.addHandler(ch)
        
        # file handler
        fh = logging.FileHandler(filename=logfile)
        fh.setLevel(loglevel.upper())
        fh.setFormatter(formatter)
        
        self.addHandler(fh)
        
        # compatibility to javascripts versions
        self.silly = self.debug
        self.warn = self.warning
        
    def setLevel(self, level):
        """
        Set the logging level of this logger.  level must be an int or a str.
        """
        if level.upper() == 'SILLY':
            level = 'DEBUG'
        elif level.upper() == 'WARN':
            level = 'WARNING'
       
        # adjust all our handlers
        for handler in self.handlers:
            handler.setLevel(level.upper())
            
        self.level = logging._checkLevel(level.upper())
        self.manager._clear_cache()
        
    def debug(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'DEBUG'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.debug("Houston, we have a %s", "thorny problem", exc_info=1)
        """
        self.d['loglevel'] = 'debug'
        kwargs = {'extra': self.d}
        msg = str(msg)
        if self.isEnabledFor(logging.DEBUG):
            self._log(logging.DEBUG, msg, args, **kwargs)
            self.cb(msg, 'debug')

    def info(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'INFO'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.info("Houston, we have a %s", "interesting problem", exc_info=1)
        """
        self.d['loglevel'] = 'info'
        kwargs = {'extra': self.d}
        msg = str(msg)
        if self.isEnabledFor(logging.INFO):
            self._log(logging.INFO, msg, args, **kwargs)
            self.cb(msg, 'info')

    def warning(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'WARNING'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.warning("Houston, we have a %s", "bit of a problem", exc_info=1)
        """
        self.d['loglevel'] = 'warn'
        kwargs = {'extra': self.d}
        msg = str(msg)
        if self.isEnabledFor(logging.WARNING):
            self._log(logging.WARNING, msg, args, **kwargs)
            self.cb(msg, 'warn')

    def error(self, msg, *args):
        """
        Log 'msg % args' with severity 'ERROR'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.error("Houston, we have a %s", "major problem", exc_info=1)
        """
        self.d['loglevel'] = 'error'
        kwargs = {'extra': self.d}
        msg = str(msg)
        if self.isEnabledFor(logging.ERROR):
            self._log(logging.ERROR, msg, args, **kwargs)
            self.cb(msg, 'error')