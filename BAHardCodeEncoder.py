#!/usr/bin/python
# -*- coding: UTF-8 -*-

instructions = '''<How to use>
1. pip install pycrypto
2. put files into xCode project path in oc-class
3. import NSString+BAHCCategory.h globally
4. edit encrypt and decrypt key & iv
5. edit exception settings: file name, file prefix, file suffix, folder name, folder prefix, folder suffix, string format specifiers
6. run script by command: python param1 param2
	param1: path of this script
	param2: root path of xCode project
7. import BAHCDefenitions.h globally
'''

#********************  Settings  ************************

AES_key = '9Jvae2bFOYL$JoTt'
AES_iv = 'yg@t2lLZXmP8&J7r'

Exception_File_Names = ['NSString+BAHCCategory.h',
						'NSString+BAHCCategory.m',
						'BAHCDefenitions.h',
						'GTMBase64.h',
						'GTMBase64.m',
						'GTMDefines.h']
Exception_File_Prefix = []
Exception_File_Suffix = []

Exception_Folder_Names = []
Exception_Folder_Prefix = []
Exception_Folder_Suffix = []

Exception_String_Format_Specifiers = ['%@', '%%', '%d', '%D', '%u', '%U', '%x', '%X',
										'%o', '%O', '%f', '%e', '%E', '%g', '%G', '%c',
										'%C', '%s', '%S', '%p', '%a', '%A', '%F']

#********************************************************

import sys, os, re, hashlib, base64
from Crypto.Cipher import AES
reload(sys)
sys.setdefaultencoding("utf-8")

class BAHardCodeEncoder:

	BAHCDefenitionsFileName = 'BAHCDefenitions.h'
	BAHCDefenitionsFilePath = ''
	GlobalFileHandler = None
	biteLength = 16

	def encrypt(self, source):
		text = source
		cryptor = AES.new(AES_key, AES.MODE_CBC, AES_iv)
		length = 16
		count = len(text)
		if count % length != 0:
			add = (((count // length) + 1) * length - count)
			text += (chr(add) * add)
		ciphertext = cryptor.encrypt(text)
		return base64.b64encode(ciphertext)

	def checkNeedSkip(self, name, path, isDir):
		if os.path.exists(path) == False:
			return True
		if isDir == True:
			if os.path.isdir(path) == False:
				return True
			if name in Exception_Folder_Names:
				return True
			for prefix in Exception_Folder_Prefix:
				if re.match('^' + prefix + '(.)*', name, re.S) != None:
					return True
			for suffix in Exception_Folder_Suffix:
				if re.match('^(.)*' + suffix, name, re.S) != None:
					return True
			return False
		else:
			if os.path.isdir(path) == True:
				return True
			if re.match('^(.)+.(h|m|pch)', name, re.S) == None:
				return True
			if name in Exception_File_Names:
				return True
			for prefix in Exception_File_Prefix:
				if re.match('^' + prefix + '(.)*', name, re.S) != None:
					return True
			for suffix in Exception_File_Suffix:
				if re.match('^(.)*' + suffix, name, re.S) != None:
					return True
			return False

	def analyzeFile(self, fileName, filePath):
		if self.checkNeedSkip(fileName, filePath, False) == True:
			return

		fileHandler = open(filePath, 'r')
		if fileHandler == None:
			return
		fileContent = fileHandler.read()
		results = re.finditer('@"(.)*?"', fileContent)
		fileHandler.close()

		needRewrite = False
		newFileContent = ''
		indexStart = 0
		for result in results:
			needRewrite = True
			#get content and contentIndex
			resultContent = result.group()
			resultStart = result.start()
			resultEnd = result.end()
			trueContent = resultContent[2: resultEnd - resultStart - 1]

			if len(trueContent) == 0:
				continue
			needSkip = False
			for specItem in Exception_String_Format_Specifiers:
				if re.match('(.)*' + specItem + '(.)*', trueContent, re.S) != None:
					needSkip = True
					break
			if needSkip == True:
				continue

			#get new key and new value
			key = 'BAHCKey' + hashlib.md5(('NEW_NAME_FOR_' + trueContent + '_OF_' + filePath).encode(encoding='UTF-8')).hexdigest()
			value = self.encrypt(trueContent)

			#write defenition
			if self.GlobalFileHandler:
				self.GlobalFileHandler.write('#define ' + key + ' @"' + value + '"\n')

			#replace content in source file
			newFileContent = newFileContent + fileContent[indexStart: resultStart] + '[' + key + ' BAHC_Decrypt]'
			indexStart = resultEnd

		if needRewrite == True:
			newFileContent = newFileContent + fileContent[indexStart: len(fileContent)]
			os.remove(filePath)
			newFileHandler = open(filePath, 'w')
			newFileHandler.write(newFileContent)
			newFileHandler.close()

	def ergodicPaths(self, rootName, rootDir):
		if self.checkNeedSkip(rootName, rootDir, True) == True:
			return

		for fileName in os.listdir(rootDir):
			filePath = os.path.join(rootDir, fileName)
			if (os.path.isdir(filePath)):
				self.ergodicPaths(fileName, filePath)
			else:
				self.analyzeFile(fileName, filePath)

	def start(self, projectRootPath):
		if projectRootPath == None:
			print('⚠️ERROR: Project root path None!')
			return

		self.BAHCDefenitionsFilePath = projectRootPath + '/' + self.BAHCDefenitionsFileName
		self.BAHCDefenitionsFilePath.replace("//", "/");
		if os.path.exists(self.BAHCDefenitionsFilePath):
			os.remove(self.BAHCDefenitionsFilePath)

		self.GlobalFileHandler = open(self.BAHCDefenitionsFilePath, 'w+')
		self.ergodicPaths('', projectRootPath)
		if self.GlobalFileHandler:
			self.GlobalFileHandler.close()

if __name__ == '__main__':
	firstParam = sys.argv[1];
	if firstParam == '--help':
		print(instructions);
		quit();

	projectRootPath = firstParam;
	BAHardCodeEncoder = BAHardCodeEncoder()
	BAHardCodeEncoder.start(projectRootPath)