#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys, os
from enum import Enum

class BAErrorGrade(Enum):
    normal = 0
    success = 1
    warning = 2
    error = 3

class BAErrorUtil(object):
    def __init__(self):
        super(BAErrorUtil, self).__init__()

    @classmethod
    def buildErrorModel(cls, grade, msg):
        return {
            'grade': grade,
            'msg': msg
        }
    
    @classmethod
    def printError(cls, grade, msg):
        if grade == BAErrorGrade.error:
            print('\033[1;31m' + str(msg) + '\033[0m')
        elif grade == BAErrorGrade.warning:
            print('\033[1;33m' + str(msg) + '\033[0m')
        elif grade == BAErrorGrade.success:
            print('\033[1;32m' + str(msg) + '\033[0m')
        else:
            print(str(msg))
    
    @classmethod
    def printErrorModel(cls, model):
        if model == None or 'grade' not in model or 'msg' not in model:
            return
        cls.printError(model['grade'], model['msg'])