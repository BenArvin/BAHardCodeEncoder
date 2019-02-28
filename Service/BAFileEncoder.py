#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys, os, re, hashlib
sys.path.append('../')
from Utils.BAFileUtil import BAFileUtil
from Utils.BAEncryptUtil import BAEncryptUtil
from Service.BAExceptionHelper import BAExceptionHelper
from BAClangUtils.RawTokenUtil import RawTokenUtil
from BAAlgorithmUtils.HorspoolUtil import HorspoolUtil
from Utils.BAErrorUtil import BAErrorUtil, BAErrorGrade

class BAFileEncoder(object):

    def __init__(self):
        super(BAFileEncoder, self).__init__()
        self.encryptFunc = self.defaultEncryptFunc
        self.__exceptionHelper = BAExceptionHelper()
        self.__rawTokenUtil = RawTokenUtil()
        self.__horspoolUtil = HorspoolUtil()
        self.__horspoolUtil.setMatcher('\\n')

    @property
    def excChars(self):
        return self.__exceptionHelper.excChars
    
    @excChars.setter
    def excChars(self, value):
        self.__exceptionHelper.excChars = value
    
    def __parseStringCodes(self, filePath):
        output, error = self.__rawTokenUtil.parse(filePath)
        stringCodes = []
        stringSuffixFinded = False
        atCodeInfo = None
        for infoItem in error:
            if infoItem['class'] == 'at':
                stringSuffixFinded = True
                atCodeInfo = infoItem
            else:
                if stringSuffixFinded == True and infoItem['class'] == 'string_literal':
                    contentLen = len(infoItem['content'])
                    tmpContent = infoItem['content'][1: contentLen - 1]
                    unCleanContentLen = len(infoItem['unCleanContent'])
                    unCleanUtf8ContentLen = len(infoItem['unCleanContent'].encode('UTF-8', 'ignore'))
                    tmpUnCleanContent = infoItem['unCleanContent'][1: unCleanContentLen - 1]
                    tmpResult = {
                        'line': atCodeInfo['line'],
                        'column': atCodeInfo['column'],
                        'codeLen': unCleanUtf8ContentLen + 1,
                        'stringContent': tmpContent,
                        'stringUnCleanContent': tmpUnCleanContent
                    }
                    stringCodes.append(tmpResult)
                atCodeInfo = None
                stringSuffixFinded = False
        return stringCodes

    def defaultEncryptFunc(self, content, unCleanContent, filePath, line, column):
        if content == None or len(content) == 0:
            return None, None
        key = 'BAHCKey' + hashlib.md5(('NEW_NAME_FOR_' + content + '_OF_' + filePath + '_AT_' + str(line) + ':' + str(column)).encode(encoding='UTF-8')).hexdigest()
        newContent = '@"' + content + '"'
        return key, newContent
    
    def encode(self, fileName, filePath):
        stringCodes = self.__parseStringCodes(filePath)
        if stringCodes == None or len(stringCodes) == 0:
            return None, None, BAErrorUtil.buildErrorModel(BAErrorGrade.normal, 'Skip file: '+filePath)
        
        linesSize = BAFileUtil.getLinesSize(filePath)
        if linesSize == None or len(linesSize) == 0:
            return None, None, BAErrorUtil.buildErrorModel(BAErrorGrade.normal, 'Skip file: '+filePath)
        
        if self.encryptFunc == None:
            return None, None, BAErrorUtil.buildErrorModel(BAErrorGrade.normal, 'Skip file: '+filePath)
        
        oldFileHandler = open(filePath, 'r')
        oldFileContent = oldFileHandler.read().encode('UTF-8', 'ignore')
        oldFileHandler.close()

        encodeLog = []
        newFileContent = ''.encode('UTF-8')
        shouldRewrite = False
        lastOffset = 0
        for i in range(0, len(stringCodes), 1):
            stringCodeItem = stringCodes[i]
            lineTmp = stringCodeItem['line']
            columnTmp = stringCodeItem['column']
            offset = BAFileUtil.convertToOffset(linesSize, lineTmp - 1, columnTmp)
            newFileContent = newFileContent + oldFileContent[lastOffset: offset]
            oldContent = stringCodeItem['stringContent']
            oldUnCleanContent = stringCodeItem['stringUnCleanContent']
            if self.__exceptionHelper.shouldSkipContent(oldUnCleanContent) == True:
                lastOffset = offset + stringCodeItem['codeLen']
                newFileContent = newFileContent + oldFileContent[offset: lastOffset]
                continue
            shouldRewrite = True
            newKey, newContent = self.encryptFunc(oldContent, oldUnCleanContent, filePath, lineTmp, columnTmp)
            if newKey != None and newContent != None:
                newFileContent = newFileContent + newKey.encode('UTF-8')
                lastOffset = offset + stringCodeItem['codeLen']
                encodeLog.append({
                    'path': filePath,
                    'line': lineTmp,
                    'column': columnTmp,
                    'oldContent': oldContent,
                    'oldUnCleanContent': oldUnCleanContent,
                    'key': newKey,
                    'newContent': newContent
                })
            else:
                newFileContent = newFileContent + oldUnCleanContent
        newFileContent = newFileContent + oldFileContent[lastOffset: len(oldFileContent)]
        return encodeLog, newFileContent.decode('UTF-8', 'ignore'), None