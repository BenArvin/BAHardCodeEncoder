#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys, os, re
sys.path.append('../')
from Utils.BAFileUtil import BAFileUtil
from Utils.BAEncryptUtil import BAEncryptUtil
from Service.BAExceptionHelper import BAExceptionHelper

class BAFileDecoder(object):

    def __init__(self):
        super(BAFileDecoder, self).__init__()
        self.__exceptionHelper = BAExceptionHelper()

    @property
    def excChars(self):
        return self.__exceptionHelper.excChars
    
    @excChars.setter
    def excChars(self, value):
        self.__exceptionHelper.excChars = value
    
    @property
    def excFolderNames(self):
        return self.__exceptionHelper.excFolderNames
    
    @excFolderNames.setter
    def excFolderNames(self, value):
        self.__exceptionHelper.excFolderNames = value

    @property
    def excFolderPrefixes(self):
        return self.__exceptionHelper.excFolderPrefixes
    
    @excFolderPrefixes.setter
    def excFolderPrefixes(self, value):
        self.__exceptionHelper.excFolderPrefixes = value
    
    @property
    def excFolderSuffixes(self):
        return self.__exceptionHelper.excFolderSuffixes
    
    @excFolderSuffixes.setter
    def excFolderSuffixes(self, value):
        self.__exceptionHelper.excFolderSuffixes = value

    @property
    def excFileNames(self):
        return self.__exceptionHelper.excFileNames
    
    @excFileNames.setter
    def excFileNames(self, value):
        self.__exceptionHelper.excFileNames = value
    
    @property
    def excFilePrefixes(self):
        return self.__exceptionHelper.excFilePrefixes
    
    @excFilePrefixes.setter
    def excFilePrefixes(self, value):
        self.__exceptionHelper.excFilePrefixes = value
    
    @property
    def excFileSuffixes(self):
        return self.__exceptionHelper.excFileSuffixes
    
    @excFileSuffixes.setter
    def excFileSuffixes(self, value):
        self.__exceptionHelper.excFileSuffixes = value

    def decode(self, fileName, filePath):
        return None, None