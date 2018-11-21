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

#****************  Settings for encrypt & decrypt  ********************

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
from BACommonUtils.BACommonFileUtil import BACommonFileUtil
from BACommonUtils.BACommonEncryptUtil import BACommonEncryptUtil

DefenitionFileName = 'BAHCDefenitions.h'

class BAHardCodeFileHelper(object):

	regPatternsBuilded = False
	regPatternStringFormatSpec = None
	regPatternFolderPrefix = None
	regPatternFolderSuffix = None
	regPatternFilePrefix = None
	regPatternFileSuffix = None

	def __buildRegPatterns(self):
		if self.regPatternsBuilded == True:
			return
		self.regPatternsBuilded = True

		specsCount = len(Exception_String_Format_Specifiers)
		if specsCount > 0 :
			self.regPatternStringFormatSpec = '(.)*('
			for i in range(specsCount):
				self.regPatternStringFormatSpec = self.regPatternStringFormatSpec + Exception_String_Format_Specifiers[i]
				if i != specsCount - 1:
					self.regPatternStringFormatSpec = self.regPatternStringFormatSpec + '|'
			self.regPatternStringFormatSpec = self.regPatternStringFormatSpec + ')(.)*'

		folderPrefixCount = len(Exception_Folder_Prefix)
		if folderPrefixCount > 0 :
			self.regPatternFolderPrefix = '^('
			for i in range(folderPrefixCount):
				self.regPatternFolderPrefix = self.regPatternFolderPrefix + Exception_Folder_Prefix[i]
				if i != folderPrefixCount - 1:
					self.regPatternFolderPrefix = self.regPatternFolderPrefix + '|'
			self.regPatternFolderPrefix = self.regPatternFolderPrefix + ')(.)*$'

		folderSuffixCount = len(Exception_Folder_Suffix)
		if folderPrefixCount > 0 :
			self.regPatternFolderSuffix = '^(.)*('
			for i in range(folderSuffixCount):
				self.regPatternFolderSuffix = self.regPatternFolderSuffix + Exception_Folder_Suffix[i]
				if i != folderSuffixCount - 1:
					self.regPatternFolderSuffix = self.regPatternFolderSuffix + '|'
			self.regPatternFolderSuffix = self.regPatternFolderSuffix + ')$'

		filePrefixCount = len(Exception_File_Prefix)
		if filePrefixCount > 0 :
			self.regPatternFilePrefix = '^('
			for i in range(filePrefixCount):
				self.regPatternFilePrefix = self.regPatternFilePrefix + Exception_File_Prefix[i]
				if i != filePrefixCount - 1:
					self.regPatternFilePrefix = self.regPatternFilePrefix + '|'
			self.regPatternFilePrefix = self.regPatternFilePrefix + ')(.)*$'

		fileSuffixCount = len(Exception_File_Suffix)
		if fileSuffixCount > 0 :
			self.regPatternFileSuffix = '^(.)*('
			for i in range(fileSuffixCount):
				self.regPatternFileSuffix = self.regPatternFileSuffix + Exception_File_Suffix[i]
				if i != fileSuffixCount - 1:
					self.regPatternFileSuffix = self.regPatternFileSuffix + '|'
			self.regPatternFileSuffix = self.regPatternFileSuffix + ')$'

	def __init__(self):
		super(BAHardCodeFileHelper, self).__init__()
		self.__buildRegPatterns()

	@classmethod
	def checkNeedSkip(cls, name, path, isDir):
		if os.path.exists(path) == False:
			return True
		if isDir == True:
			if os.path.isdir(path) == False:
				return True
			if name in Exception_Folder_Names:
				return True
			if cls.regPatternFolderPrefix != None and re.match(cls.regPatternFolderPrefix, name, re.S) != None:
				return True
			if cls.regPatternFolderSuffix != None and re.match(cls.regPatternFolderSuffix, name, re.S) != None:
				return True
			return False
		else:
			if os.path.isdir(path) == True:
				return True
			if re.match('^(.)+\\.(h|m|pch)$', name, re.S) == None:
				return True
			if name in Exception_File_Names:
				return True
			if cls.regPatternFilePrefix != None and re.match(cls.regPatternFilePrefix, name, re.S) != None:
				return True
			if cls.regPatternFileSuffix != None and re.match(cls.regPatternFileSuffix, name, re.S) != None:
				return True
			return False

class BAHardCodeEncoder(object):

	def __init__(self):
		super(BAHardCodeEncoder, self).__init__()
		self.__projectRootPath = ''
		self.__defenitionFilePath = ''
		self.__globalFileHandler = None
		self.__fileHelper = BAHardCodeFileHelper()

	def convertEscapeCharacter(self, source):
		result = source
		for i in range(len(Encode_Escape_Characters_Key)):
			result = result.replace(Encode_Escape_Characters_Key[i], Encode_Escape_Characters_Value[i])
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

		results = re.finditer('@"(.|(\\\\\n))*?[^\\\\]"( |\t|\n)*(\n|;|,|])', fileContent)
		needRewrite = False
		newFileContent = ''
		indexStart = 0
		relativePath = filePath
		relativePath = relativePath.replace(self.__projectRootPath, "/")
		for result in results:
			#get content and contentIndex
			resultContent = result.group()
			stringEndTag = re.finditer('[^\\\\]"( |\t|\n)*(\n|;|,|])', resultContent)
			for item in stringEndTag:
				stringEndTag = item
				break
			resultStart = result.start()
			resultEnd = stringEndTag.start() + resultStart + 2
			trueContent = resultContent[2: resultEnd - resultStart - 1]

			#check if need skip
			if len(trueContent) == 0:
				continue
			if self.__fileHelper.regPatternStringFormatSpec != None and re.match(self.__fileHelper.regPatternStringFormatSpec, trueContent, re.S) != None:
				continue

			#get new key and new value
			# convertedContent = self.convertEscapeCharacter(trueContent)
			convertedContent = trueContent
			key = 'BAHCKey' + hashlib.md5(('NEW_NAME_FOR_' + trueContent + '_OF_' + relativePath + '_AT_' + str(resultStart) + ':' + str(resultEnd)).encode(encoding='UTF-8')).hexdigest()
			value = BACommonEncryptUtil.AESEncrypt(convertedContent, AES_key, AES_iv)

			#write defenition
			if self.__globalFileHandler:
				self.__globalFileHandler.write('#define ' + key + ' @"' + value + '"\n')

			#print log
			print('✅ ' + relativePath + '(' + str(resultStart) + ':' + str(resultEnd) + '): ' + trueContent + ' -> ' + key + '\n')

			#replace content in source file
			newFileContent = newFileContent + fileContent[indexStart: resultStart] + '[' + key + ' BAHC_Decrypt]'
			indexStart = resultEnd
			needRewrite = True

		newFileContent = newFileContent + fileContent[indexStart: len(fileContent)]

		#write new content into file
		if needRewrite == True:
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
		print('👉 Encode action, Here we go!\n')

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
		if isinstance(Encode_Escape_Characters_Key, list) == False or isinstance(Encode_Escape_Characters_Value, list) == False:
			print("⚠️ ERROR: List escape characters key or value can't be None!")
			return
		if len(Encode_Escape_Characters_Key) != len(Encode_Escape_Characters_Value):
			print("⚠️ ERROR: Length of escape characters key and value list must be equal!")
			return

		#creat defenition file
		self.__defenitionFilePath = self.__projectRootPath + '/' + DefenitionFileName
		self.__defenitionFilePath = self.__defenitionFilePath.replace("//", "/")
		if os.path.exists(self.__defenitionFilePath):
			os.remove(self.__defenitionFilePath)

		#start analyze
		self.__globalFileHandler = open(self.__defenitionFilePath, 'w+')
		self.ergodicPaths('', self.__projectRootPath)
		if self.__globalFileHandler:
			self.__globalFileHandler.close()

		print('👌 Finished!\n')

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

if __name__ == '__main__':
	if len(sys.argv) < 2:
		quit()
	firstParam = sys.argv[1]

	if firstParam == '--help':
		print('\033[1;32m' + instructions + '\033[0m')
		quit()

	if firstParam == '--encrypt':
		content = input('\033[1;32mContent: \033[0m')
		key = input('\033[1;32mKey: \033[0m')
		iv = input('\033[1;32mIV: \033[0m')
		print(BACommonEncryptUtil.AESEncrypt(content, key, iv))
		quit()

	if firstParam == '--decrypt':
		content = input('\033[1;32mContent: \033[0m')
		key = input('\033[1;32mKey: \033[0m')
		iv = input('\033[1;32mIV: \033[0m')
		print(BACommonEncryptUtil.AESDecrypt(content, key, iv))
		quit()

	if len(sys.argv) >= 3:
		if firstParam == '--decode':
			decoder = BAHardCodeDecoder()
			decoder.start(sys.argv[2])
		elif firstParam == '--encode':
			encoder = BAHardCodeEncoder()
			encoder.start(sys.argv[2])