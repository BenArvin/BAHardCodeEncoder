#!/usr/bin/python
# -*- coding: UTF-8 -*-

instructions = '''
Encode all hard code string in objective-c project.

How to use:
1. put files in /oc-class into your project
2. edit key & iv for encrypt and decrypt action in this script and NSString+BAHCCategory.h
3. edit exception settings in this script: file name, file prefix, file suffix, folder name, folder prefix, folder suffix, string format specifiers
4. pipenv install
5. start encode/decode action by command: python param1 --encode/--decode param2
	param1: path of this script
	param2: root path of project
6. import NSString+BAHCCategory.h and BAHCDefenitions.h globally

PS:
   1. length of Key and iv for encrypt action must be a multiple of 16
   2. you must skip these files: NSString+BAHCCategory.h, NSString+BAHCCategory.m, BAHCDefenitions.h, GTMBase64.h, GTMBase64.m, GTMDefines.h
   3. use option --encrypt/--decrypt to encrypt/decrypt individual content
'''
#****************  Settings for defenitions & log file  ***************

DefenitionFileName = 'BAHCDefenitions.h'
EncodeLogFileName = 'BAHCEncodeLog.json'

#**********************************************************************

#****************  Settings for encrypt & decrypt  ********************

Key_salt = 'abcdef'
AES_key = '9Jvae2bFOYL$JoTt'
AES_iv = 'yg@t2lLZXmP8&J7r'

#**********************************************************************


#********************  Settings for exception  ************************

Exception_File_Names = ['NSString+BAHCCategory.h',
						'NSString+BAHCCategory.m',
						'BAHCDefenitions.h',
						'GTMBase64.h',
						'GTMBase64.m',
						'GTMDefines.h']
Exception_File_Prefix = []
Exception_File_Suffix = [r'\.a', r'\.framework']

Exception_Folder_Names = ['node_modules',
							'.idea',
							'.git',
							'Pods']
Exception_Folder_Prefix = []
Exception_Folder_Suffix = []

Exception_String_Format_Specifiers = ['%@', '%%', '%d', '%D', '%u', '%U', '%x', '%X',
										'%o', '%O', '%f', '%e', '%E', '%g', '%G', '%c',
										'%C', '%s', '%S', '%p', '%a', '%A', '%F', '%zd']

Encode_Escape_Characters_Key = ['\\\n', '\\n', '\\a', '\\b', '\\f', '\\r', '\\t', '\\v', '\\"', '\\0', '\\\\']
Encode_Escape_Characters_Value = ['', '\n', '\a', '\b', '\f', '\r', '\t', '\v', '\"', '', '\\']

#**********************************************************************


import sys, os, hashlib, json
from Service.BAFileDecoder import BAFileDecoder
from Service.BAFileEncoder import BAFileEncoder
from Service.BAExceptionHelper import BAExceptionHelper
from Utils.BAFileUtil import BAFileUtil
from Utils.BAErrorUtil import BAErrorUtil, BAErrorGrade
from Utils.BAEncryptUtil import BAEncryptUtil
from BAAlgorithmUtils.SBOMUtil import SBOMUtil

def __decodeAction(rootName, rootDir, stringSearchUtil, replaceDic, exceptionHelper):
	if stringSearchUtil == None:
		return
	if replaceDic == None or len(replaceDic) == 0:
		return
	if exceptionHelper.shouldSkipFolder(rootName, rootDir) == True:
		return

	for fileName in os.listdir(rootDir):
		filePath = os.path.join(rootDir, fileName)
		if (os.path.isdir(filePath)):
			__decodeAction(fileName, filePath, stringSearchUtil, replaceDic, exceptionHelper)
		else:
			if exceptionHelper.shouldSkipFile(fileName, filePath) == True:
				BAErrorUtil.printError(BAErrorGrade.normal, 'Skip file: ' + filePath)
				continue
			fileHandler = open(filePath, 'r')
			newFileContent = fileHandler.read()
			fileHandler.close()
			searchResult = stringSearchUtil.search(newFileContent)
			if searchResult == None or len(searchResult) == 0:
				BAErrorUtil.printError(BAErrorGrade.normal, 'Skip file: ' + filePath)
				continue
			needRewrite = False
			for key, indexs in searchResult.items():
				if indexs != None and len(indexs) > 0 and key in replaceDic:
					newFileContent = newFileContent.replace(key, '@"' + replaceDic[key] + '"')
					needRewrite = True
				else:
					BAErrorUtil.printError(BAErrorGrade.normal, 'Skip file: ' + filePath)
			if needRewrite == True:
				BAErrorUtil.printError(BAErrorGrade.success, 'Decoded: ' + filePath)
				newFileHandler = open(filePath, 'w')
				newFileHandler.seek(0)
				newFileHandler.truncate()
				newFileHandler.write(newFileContent)
				newFileHandler.close()

def __decode(rootPath):
	BAErrorUtil.printError(BAErrorGrade.normal, '👉 Decode action, here we go!')

	if rootPath == None:
		BAErrorUtil.printError(BAErrorGrade.error, 'ERROR: Project root path None!')
		return

	tmpRootPath = rootPath + '/'
	tmpRootPath = tmpRootPath.replace("//", "/")

	#check key and iv length
	if AES_key == None or AES_iv == None:
		BAErrorUtil.printError(BAErrorGrade.error, "ERROR: Key and iv for encrypt action can't be null!")
		return
	if len(AES_key) % 16 != 0 or len(AES_iv) % 16 != 0:
		BAErrorUtil.printError(BAErrorGrade.error, 'ERROR: Length of key and iv for encrypt action must be a multiple of 16!')
		return

	#find encode log file
	possiblePaths = BAFileUtil.findTargetPaths(EncodeLogFileName, False, tmpRootPath)
	if possiblePaths == None or len(possiblePaths) == 0:
		BAErrorUtil.printError(BAErrorGrade.error, "ERROR: Can't find BAHCDefenitions.h !")
		return
	encodeLogFilePath = possiblePaths[0]

	#read contents in encode log file
	encodeLogFileFileHandler = open(encodeLogFilePath, 'r')
	if encodeLogFileFileHandler == None:
		BAErrorUtil.printError(BAErrorGrade.error, "ERROR: Can't read BAHCDefenitions.h !")
		return
	encodeLogContent = encodeLogFileFileHandler.read()
	encodeLogFileFileHandler.close()
	encodeLog = json.loads(encodeLogContent)

	replaceDic = {}
	sbomUtil = SBOMUtil()
	for logItem in encodeLog:
		key = logItem['key']
		sbomUtil.train(key)
		replaceDic[key] = logItem['oldUnCleanContent']
	sbomUtil.prepare()

	exceptionHelper = BAExceptionHelper()
	exceptionHelper.excFolderNames = Exception_Folder_Names
	exceptionHelper.excFolderPrefixes = Exception_Folder_Prefix
	exceptionHelper.excFolderSuffixes = Exception_Folder_Suffix
	exceptionHelper.excFileNames = Exception_File_Names
	exceptionHelper.excFilePrefixes = Exception_File_Prefix
	exceptionHelper.excFileSuffixes = Exception_File_Suffix

	#start decode
	__decodeAction('', tmpRootPath, sbomUtil, replaceDic, exceptionHelper)

	BAErrorUtil.printError(BAErrorGrade.normal, '👌 Finished!')

def __convertEscapeCharacterForEncode(source):
	result = source
	for i in range(len(Encode_Escape_Characters_Key)):
		result = result.replace(Encode_Escape_Characters_Key[i], Encode_Escape_Characters_Value[i])
	return result

def __encryptFunc(content, unCleanContent, filePath, line, column):
	if content == None or len(content) == 0:
		return None, None
	key = 'BAHCKey' + hashlib.md5((Key_salt + 'NEW_NAME_FOR_' + content + '_OF_' + filePath + '_AT_' + str(line) + ':' + str(column)).encode(encoding='UTF-8')).hexdigest()
	newContent = '[@"' + BAEncryptUtil.AESEncrypt(__convertEscapeCharacterForEncode(content), AES_key, AES_iv) + '" BAHC_Decrypt]'
	return key, newContent

def __encodeAction(rootName, rootDir, outputFileHandler, logFileHandler, encoder, exceptionHelper):
	if exceptionHelper.shouldSkipFolder(rootName, rootDir) == True:
		return

	for fileName in os.listdir(rootDir):
		filePath = os.path.join(rootDir, fileName)
		if (os.path.isdir(filePath)):
			__encodeAction(fileName, filePath, outputFileHandler, logFileHandler, encoder, exceptionHelper)
		else:
			if exceptionHelper.shouldSkipFile(fileName, filePath) == True:
				BAErrorUtil.printError(BAErrorGrade.normal, 'Skip file: ' + filePath)
				continue
			logs, newContent, error = encoder.encode(fileName, filePath)
			if error != None:
				BAErrorUtil.printErrorModel(error)
			elif len(logs) > 0:
				tmpFileHandler = open(filePath, 'w')
				tmpFileHandler.seek(0)
				tmpFileHandler.truncate()
				tmpFileHandler.write(newContent)
				tmpFileHandler.close()

				if outputFileHandler:
					for logItem in logs:
						outputFileHandler.write('#define ' + logItem['key'] + ' ' + logItem['newContent'] + '\n')
				
				if logFileHandler:
					logString = json.dumps(logs)
					logFileHandler.write(logString[1: len(logString) - 1])
				
				BAErrorUtil.printError(BAErrorGrade.success, 'Encoded: ' + filePath)
			else:
				BAErrorUtil.printError(BAErrorGrade.normal, 'Skip file: '+filePath)

def __encode(rootPath):
	BAErrorUtil.printError(BAErrorGrade.normal, '👉 Encode action, Here we go!')

	if rootPath == None:
		BAErrorUtil.printError(BAErrorGrade.error, 'ERROR: Project root path None!')
		return

	rootPathTmp = rootPath.replace("//", "/")

	#check key and iv length
	if AES_key == None or AES_iv == None:
		BAErrorUtil.printError(BAErrorGrade.error, "ERROR: Key and iv for encrypt action can't be null!")
		return
	if len(AES_key) % 16 != 0 or len(AES_iv) % 16 != 0:
		BAErrorUtil.printError(BAErrorGrade.error, "ERROR: Length of key and iv for encrypt action must be a multiple of 16!")
		return

	#check key & value of escape characters
	if isinstance(Encode_Escape_Characters_Key, list) == False or isinstance(Encode_Escape_Characters_Value, list) == False:
		BAErrorUtil.printError(BAErrorGrade.error, "ERROR: List escape characters key or value can't be None!")
		return
	if len(Encode_Escape_Characters_Key) != len(Encode_Escape_Characters_Value):
		BAErrorUtil.printError(BAErrorGrade.error, "ERROR: Length of escape characters key and value list must be equal!")
		return

	#creat defenition file
	defenitionFilePath = rootPathTmp + '/' + DefenitionFileName
	defenitionFilePath = defenitionFilePath.replace("//", "/")
	if os.path.exists(defenitionFilePath):
		os.remove(defenitionFilePath)

	#creat log file
	logFilePath = rootPathTmp + '/' + EncodeLogFileName
	logFilePath = logFilePath.replace("//", "/")
	if os.path.exists(logFilePath):
		os.remove(logFilePath)

	#start analyze
	encoder = BAFileEncoder()
	encoder.excChars = Exception_String_Format_Specifiers
	encoder.encryptFunc = __encryptFunc

	exceptionHelper = BAExceptionHelper()
	exceptionHelper.excFolderNames = Exception_Folder_Names
	exceptionHelper.excFolderPrefixes = Exception_Folder_Prefix
	exceptionHelper.excFolderSuffixes = Exception_Folder_Suffix
	exceptionHelper.excFileNames = Exception_File_Names
	exceptionHelper.excFilePrefixes = Exception_File_Prefix
	exceptionHelper.excFileSuffixes = Exception_File_Suffix

	defenitionFilePathHandler = open(defenitionFilePath, 'w+')
	logFilePathHandler = open(logFilePath, 'w+')
	logFilePathHandler.write('[')
	__encodeAction('', rootPathTmp, defenitionFilePathHandler, logFilePathHandler, encoder, exceptionHelper)
	logFilePathHandler.write(']')
	logFilePathHandler.close()
	defenitionFilePathHandler.close()

	BAErrorUtil.printError(BAErrorGrade.normal, '👌 Finished!')

if __name__ == '__main__':
	if len(sys.argv) < 2:
		quit()
	firstParam = sys.argv[1]

	if firstParam == '--encrypt':
		content = input('\033[1;32mContent: \033[0m')
		key = input('\033[1;32mKey: \033[0m')
		iv = input('\033[1;32mIV: \033[0m')
		print(BAEncryptUtil.AESEncrypt(content, key, iv))
		quit()

	if firstParam == '--decrypt':
		content = input('\033[1;32mContent: \033[0m')
		key = input('\033[1;32mKey: \033[0m')
		iv = input('\033[1;32mIV: \033[0m')
		print(BAEncryptUtil.AESDecrypt(content, key, iv))
		quit()

	if len(sys.argv) >= 3:
		if firstParam == '--decode':
			__decode(sys.argv[2])
			pass
		elif firstParam == '--encode':
			__encode(sys.argv[2])