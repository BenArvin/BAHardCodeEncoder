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
										'%C', '%s', '%S', '%p', '%a', '%A', '%F']

Encode_Escape_Characters_Key = ['\\\n', '\\n', '\\a', '\\b', '\\f', '\\r', '\\t', '\\v', '\\"', '\\0', '\\\\']
Encode_Escape_Characters_Value = ['', '\n', '\a', '\b', '\f', '\r', '\t', '\v', '\"', '', '\\']

Decode_Escape_Characters_Key = ['\\', '\n', '\a', '\b', '\f', '\r', '\t', '\v', '\"']
Decode_Escape_Characters_Value = ['\\\\', '\\n', '\\a', '\\b', '\\f', '\\r', '\\t', '\\v', '\\"']

#**********************************************************************


import sys, os, re, hashlib, json
# from Utils.BACommonFileUtil import BACommonFileUtil
# from Utils.BACommonEncryptUtil import BACommonEncryptUtil
# from BAClangUtils.RawTokenUtil import RawTokenUtil
from Service.BAFileDecoder import BAFileDecoder
from Service.BAFileEncoder import BAFileEncoder
from Service.BAExceptionHelper import BAExceptionHelper
from Utils.BAFileUtil import BAFileUtil
from Utils.BAErrorUtil import BAErrorUtil, BAErrorGrade
from Utils.BAEncryptUtil import BAEncryptUtil

class BAHardCodeDecoder(object):

	def __init__(self):
		super(BAHardCodeDecoder, self).__init__()
		self.__projectRootPath = ''
		self.__decryptedDefenitionsDic = {}

	def convertEscapeCharacter(self, source):
		result = source
		for i in range(len(Decode_Escape_Characters_Key)):
			result = result.replace(Decode_Escape_Characters_Key[i], Decode_Escape_Characters_Value[i])
		return result

	def analyzeFile(self, fileName, filePath):
		if BAHardCodeFileHelper.checkNeedSkip(fileName, filePath, False) == True:
			return

		#read original file content
		fileHandler = open(filePath, 'r')
		if fileHandler == None:
			return
		fileContent = fileHandler.read()
		fileHandler.close()

		#replace
		results = re.finditer(r'\[BAHCKey(.)*? BAHC_Decrypt\]', fileContent)
		needRewrite = False
		newFileContent = ''
		indexStart = 0
		for result in results:
			#get content and contentIndex
			resultStart = result.start()
			resultEnd = result.end()
			key = fileContent[resultStart + 1 : resultEnd - 14]
			# decryptedContent = self.convertEscapeCharacter(self.__decryptedDefenitionsDic[key])
			decryptedContent = self.__decryptedDefenitionsDic[key]

			newFileContent = newFileContent + fileContent[indexStart: resultStart] + '@"' + decryptedContent + '"'
			indexStart = resultEnd
			needRewrite = True

		newFileContent = newFileContent + fileContent[indexStart: len(fileContent)]

		if needRewrite == True:
			#print log
			relativePath = filePath
			relativePath = relativePath.replace(self.__projectRootPath, "/")
			print('✅ ' + relativePath + '\n')

			#write new content into file
			newFileHandler = open(filePath, 'w')
			newFileHandler.seek(0)
			newFileHandler.truncate()
			newFileHandler.write(newFileContent)
			newFileHandler.close()

	def ergodicPaths(self, rootName, rootDir):
		if BAHardCodeFileHelper.checkNeedSkip(rootName, rootDir, True) == True:
			return

		for fileName in os.listdir(rootDir):
			filePath = os.path.join(rootDir, fileName)
			if (os.path.isdir(filePath)):
				self.ergodicPaths(fileName, filePath)
			else:
				self.analyzeFile(fileName, filePath)

	def start(self, projectRootPath):
		print('👉 Decode action, here we go!\n')

		if projectRootPath == None:
			print('⚠️ ERROR: Project root path None!')
			return

		self.__projectRootPath = projectRootPath + '/'
		self.__projectRootPath = self.__projectRootPath.replace("//", "/")

		#check key and iv length
		if AES_key == None or AES_iv == None:
			print("⚠️ ERROR: Key and iv for encrypt action can't be null!")
			return
		if len(AES_key) % 16 != 0 or len(AES_iv) % 16 != 0:
			print('⚠️ ERROR: Length of key and iv for encrypt action must be a multiple of 16!')
			return

		#check key & value of escape characters
		if isinstance(Decode_Escape_Characters_Key, list) == False or isinstance(Decode_Escape_Characters_Value, list) == False:
			print("⚠️ ERROR: List escape characters key or value can't be None!")
			return
		if len(Decode_Escape_Characters_Key) != len(Decode_Escape_Characters_Value):
			print("⚠️ ERROR: Length of escape characters key and value list must be equal!")
			return

		#find BAHCDefenitions.h file
		possiblePaths = BACommonFileUtil.findTargetPaths(DefenitionFileName, False, self.__projectRootPath)
		if possiblePaths == None or len(possiblePaths) == 0:
			print("⚠️ ERROR: Can't find BAHCDefenitions.h !")
			return
		defenitionFilePath = possiblePaths[0]

		#read contents in BAHCDefenitions.h file
		defenitionFileHandler = open(defenitionFilePath, 'r')
		if defenitionFileHandler == None:
			print("⚠️ ERROR: Can't read BAHCDefenitions.h !")
			return
		defenitionsContent = defenitionFileHandler.read()
		defenitionFileHandler.close()

		if re.match('^[ |\n]*$', defenitionsContent, re.S) != None:
			print("⚠️ ERROR: BAHCDefenitions.h file invalid!")
			return

		defenitionsContent = defenitionsContent.replace('#define ', '"')
		defenitionsContent = defenitionsContent.replace(' @"', '":"')
		defenitionsContent = defenitionsContent.replace('\n', ',')
		defenitionsContent = defenitionsContent[0 : len(defenitionsContent) - 2]
		defenitionsContent = '{' + defenitionsContent + '"}'
		defenitionsDic = json.loads(defenitionsContent)

		#decrypt all contents
		for key, value in defenitionsDic.items():
			self.__decryptedDefenitionsDic[key] = BACommonEncryptUtil.AESDecrypt(value, AES_key, AES_iv)

		#start decode
		self.ergodicPaths('', self.__projectRootPath)

		print('👌 Finished!\n')

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
				
				BAErrorUtil.printError(BAErrorGrade.success, 'Resolved: ' + filePath)
			else:
				BAErrorUtil.printError(BAErrorGrade.normal, 'None changed: '+filePath)

def __encode(rootPath):
	BAErrorUtil.printError(BAErrorGrade.normal, '👉 Encode action, Here we go!\n')

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
	encoder.excFileNames = Exception_File_Names
	encoder.excFilePrefixes = Exception_File_Prefix
	encoder.excFileSuffixes = Exception_File_Suffix
	encoder.encryptFunc = __encryptFunc

	exceptionHelper = BAExceptionHelper()
	exceptionHelper.excFolderNames = Exception_Folder_Names
	exceptionHelper.excFolderPrefixes = Exception_Folder_Prefix
	exceptionHelper.excFolderSuffixes = Exception_Folder_Suffix

	defenitionFilePathHandler = open(defenitionFilePath, 'w+')
	logFilePathHandler = open(logFilePath, 'w+')
	logFilePathHandler.write('[')
	__encodeAction('', rootPathTmp, defenitionFilePathHandler, logFilePathHandler, encoder, exceptionHelper)
	logFilePathHandler.write(']')
	logFilePathHandler.close()
	defenitionFilePathHandler.close()

	BAErrorUtil.printError(BAErrorGrade.normal, '👌 Finished!\n')

if __name__ == '__main__':
	if len(sys.argv) < 2:
		quit()
	firstParam = sys.argv[1]

	if firstParam == '--help':
		print('\033[1;32m' + instructions + '\033[0m')
		quit()

	# if firstParam == '--encrypt':
	# 	content = input('\033[1;32mContent: \033[0m')
	# 	key = input('\033[1;32mKey: \033[0m')
	# 	iv = input('\033[1;32mIV: \033[0m')
	# 	print(BACommonEncryptUtil.AESEncrypt(content, key, iv))
	# 	quit()

	# if firstParam == '--decrypt':
	# 	 content = input('\033[1;32mContent: \033[0m')
	# 	 key = input('\033[1;32mKey: \033[0m')
	# 	 iv = input('\033[1;32mIV: \033[0m')
	# 	 print(BACommonEncryptUtil.AESDecrypt(content, key, iv))
	# 	 quit()

	if len(sys.argv) >= 3:
		if firstParam == '--decode':
			#  decoder = BAHardCodeDecoder()
			#  decoder.start(sys.argv[2])
			pass
		elif firstParam == '--encode':
			__encode(sys.argv[2])