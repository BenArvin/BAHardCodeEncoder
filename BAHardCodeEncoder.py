#!/usr/bin/python
# -*- coding: UTF-8 -*-

instructions = '''
Encode all hard code string in objective-c project.

How to use:
1. pip install pycrypto
2. put files in /oc-class into project
3. edit key & iv for encrypt and decrypt action in this script and NSString+BAHCCategory.h
4. edit exception settings in this script: file name, file prefix, file suffix, folder name, folder prefix, folder suffix, string format specifiers
5. run script by command: python param1 param2
	param1: path of this script
	param2: root path of project
6. import NSString+BAHCCategory.h and BAHCDefenitions.h globally

PS:
   1. length of Key and iv for encrypt action must be a multiple of 16
   2. you must skip these files: NSString+BAHCCategory.h, NSString+BAHCCategory.m, BAHCDefenitions.h, GTMBase64.h, GTMBase64.m, GTMDefines.h
   3. python 2.7 support
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
Exception_File_Suffix = []

Exception_Folder_Names = []
Exception_Folder_Prefix = []
Exception_Folder_Suffix = []

Exception_String_Format_Specifiers = ['%@', '%%', '%d', '%D', '%u', '%U', '%x', '%X',
										'%o', '%O', '%f', '%e', '%E', '%g', '%G', '%c',
										'%C', '%s', '%S', '%p', '%a', '%A', '%F']

#**********************************************************************


import sys, os, re, hashlib, base64
from Crypto.Cipher import AES
reload(sys)
sys.setdefaultencoding("utf-8")

class BAHardCodeEncoder:

	BAHCDefenitionsFileName = 'BAHCDefenitions.h'
	BAHCDefenitionsFilePath = ''
	GlobalFileHandler = None
	RegPatternStringFormatSpec = None
	RegPatternFolderPrefix = None
	RegPatternFolderSuffix = None
	RegPatternFilePrefix = None
	RegPatternFileSuffix = None

	def buildRegPatterns(self):
		specsCount = len(Exception_String_Format_Specifiers)
		if specsCount > 0 :
			self.RegPatternStringFormatSpec = '(.)*('
			for i in range(specsCount):
				self.RegPatternStringFormatSpec = self.RegPatternStringFormatSpec + Exception_String_Format_Specifiers[i]
				if i != specsCount - 1:
					self.RegPatternStringFormatSpec = self.RegPatternStringFormatSpec + '|'
			self.RegPatternStringFormatSpec = self.RegPatternStringFormatSpec + ')(.)*'

		folderPrefixCount = len(Exception_Folder_Prefix)
		if folderPrefixCount > 0 :
			self.RegPatternFolderPrefix = '^('
			for i in range(folderPrefixCount):
				self.RegPatternFolderPrefix = self.RegPatternFolderPrefix + Exception_Folder_Prefix[i]
				if i != folderPrefixCount - 1:
					self.RegPatternFolderPrefix = self.RegPatternFolderPrefix + '|'
			self.RegPatternFolderPrefix = self.RegPatternFolderPrefix + ')(.)*'

		folderSuffixCount = len(Exception_Folder_Suffix)
		if folderPrefixCount > 0 :
			self.RegPatternFolderSuffix = '^(.)*('
			for i in range(folderSuffixCount):
				self.RegPatternFolderSuffix = self.RegPatternFolderSuffix + Exception_Folder_Suffix[i]
				if i != folderSuffixCount - 1:
					self.RegPatternFolderSuffix = self.RegPatternFolderSuffix + '|'
			self.RegPatternFolderSuffix = self.RegPatternFolderSuffix + ')'

		filePrefixCount = len(Exception_File_Prefix)
		if filePrefixCount > 0 :
			self.RegPatternFilePrefix = '^('
			for i in range(filePrefixCount):
				self.RegPatternFilePrefix = self.RegPatternFilePrefix + Exception_File_Prefix[i]
				if i != filePrefixCount - 1:
					self.RegPatternFilePrefix = self.RegPatternFilePrefix + '|'
			self.RegPatternFilePrefix = self.RegPatternFilePrefix + ')(.)*'

		fileSuffixCount = len(Exception_File_Suffix)
		if fileSuffixCount > 0 :
			self.RegPatternFileSuffix = '^(.)*('
			for i in range(fileSuffixCount):
				self.RegPatternFileSuffix = self.RegPatternFileSuffix + Exception_File_Suffix[i]
				if i != fileSuffixCount - 1:
					self.RegPatternFileSuffix = self.RegPatternFileSuffix + '|'
			self.RegPatternFileSuffix = self.RegPatternFileSuffix + ')'

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
			if self.RegPatternFolderPrefix != None and re.match(self.RegPatternFolderPrefix, name, re.S) != None:
				return True
			if self.RegPatternFolderSuffix != None and re.match(self.RegPatternFolderSuffix, name, re.S) != None:
				return True
			return False
		else:
			if os.path.isdir(path) == True:
				return True
			if re.match('^(.)+.(h|m|pch)', name, re.S) == None:
				return True
			if name in Exception_File_Names:
				return True
			if self.RegPatternFilePrefix != None and re.match(self.RegPatternFilePrefix, name, re.S) != None:
				return True
			if self.RegPatternFileSuffix != None and re.match(self.RegPatternFileSuffix, name, re.S) != None:
				return True
			return False

	def analyzeFile(self, fileName, filePath):
		if self.checkNeedSkip(fileName, filePath, False) == True:
			return

		#read original file content
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

			#check if need skip
			if len(trueContent) == 0:
				continue
			if self.RegPatternStringFormatSpec != None and re.match(self.RegPatternStringFormatSpec, trueContent, re.S) != None:
				continue

			#get new key and new value
			key = 'BAHCKey' + hashlib.md5(('NEW_NAME_FOR_' + trueContent + '_OF_' + filePath).encode(encoding='UTF-8')).hexdigest()
			value = self.encrypt(trueContent)

			#write defenition
			if self.GlobalFileHandler:
				self.GlobalFileHandler.write('#define ' + key + ' @"' + value + '"\n')

			#print log
			print('✅ ' + filePath + ' : ' + trueContent + ' -> ' + key + '\n')

			#replace content in source file
			newFileContent = newFileContent + fileContent[indexStart: resultStart] + '[' + key + ' BAHC_Decrypt]'
			indexStart = resultEnd

		#write new content into file
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

		#check key and iv length
		if AES_key == None or AES_iv == None:
			print("⚠️ERROR: Key and iv for encrypt action can't be null!")
			return
		if len(AES_key) % 16 != 0 or len(AES_iv) % 16 != 0:
			print('⚠️ERROR: Length of Key and iv for encrypt action must be a multiple of 16')
			return

		#build patterns for reg check
		self.buildRegPatterns()

		#creat defenition file
		self.BAHCDefenitionsFilePath = projectRootPath + '/' + self.BAHCDefenitionsFileName
		self.BAHCDefenitionsFilePath.replace("//", "/");
		if os.path.exists(self.BAHCDefenitionsFilePath):
			os.remove(self.BAHCDefenitionsFilePath)

		print('👉 Here we go!\n')

		#start analyze
		self.GlobalFileHandler = open(self.BAHCDefenitionsFilePath, 'w+')
		self.ergodicPaths('', projectRootPath)
		if self.GlobalFileHandler:
			self.GlobalFileHandler.close()

		print('👌 Finished!\n')

if __name__ == '__main__':
	firstParam = sys.argv[1];
	if firstParam == '--help':
		print('\033[1;32m' + instructions + '\033[0m');
		quit();

	projectRootPath = firstParam;
	BAHardCodeEncoder = BAHardCodeEncoder()
	BAHardCodeEncoder.start(projectRootPath)