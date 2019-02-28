#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys, os, re

class BAExceptionHelper(object):

	def __init__(self):
		super(BAExceptionHelper, self).__init__()

		self.excFolderNames = None
		self.excFileNames = None

		self.__excChars = None
		self.__excCharsRegSpec = None

		self.__excFolderPrefixes = None
		self.__excFolderPrefixesRegSpec = None

		self.__excFolderSuffixes = None
		self.__excFolderSuffixesRegSpec = None

		self.__excFilePrefixes = None
		self.__excFilePrefixesRegSpec = None

		self.__excFileSuffixes = None
		self.__excFileSuffixesRegSpec = None
	
	@property
	def excChars(self):
		return self.__excChars
	
	@excChars.setter
	def excChars(self, value):
		if self.__excChars == value:
			return
		self.__excChars = value

		if self.__excChars == None:
			self.__excCharsRegSpec = None
			return

		charsCount = len(self.__excChars)
		if charsCount == 0:
			self.__excCharsRegSpec = None
			return
		
		self.__excCharsRegSpec = '(.)*('
		for i in range(charsCount):
			self.__excCharsRegSpec = self.__excCharsRegSpec + self.__excChars[i]
			if i != charsCount - 1:
				self.__excCharsRegSpec = self.__excCharsRegSpec + '|'
		self.__excCharsRegSpec = self.__excCharsRegSpec + ')(.)*'
	
	@property
	def excFolderPrefixes(self):
		return self.__excFolderPrefixes
	
	@excFolderPrefixes.setter
	def excFolderPrefixes(self, value):
		if self.__excFolderPrefixes == value:
			return
		self.__excFolderPrefixes = value

		if self.__excFolderPrefixes == None:
			self.__excFolderPrefixesRegSpec = None
			return

		count = len(self.__excFolderPrefixes)
		if count == 0:
			self.__excFolderPrefixesRegSpec = None
			return
		
		self.__excFolderPrefixesRegSpec = '^('
		for i in range(count):
			self.__excFolderPrefixesRegSpec = self.__excFolderPrefixesRegSpec + self.__excFolderPrefixes[i]
			if i != count - 1:
				self.__excFolderPrefixesRegSpec = self.__excFolderPrefixesRegSpec + '|'
		self.__excFolderPrefixesRegSpec = self.__excFolderPrefixesRegSpec + ')(.)*$'

	@property
	def excFolderPrefixes(self):
		return self.__excFolderPrefixes
	
	@excFolderPrefixes.setter
	def excFolderPrefixes(self, value):
		if self.__excFolderPrefixes == value:
			return
		self.__excFolderPrefixes = value

		if self.__excFolderPrefixes == None:
			self.__excFolderPrefixesRegSpec = None
			return

		count = len(self.__excFolderPrefixes)
		if count == 0:
			self.__excFolderPrefixesRegSpec = None
			return
		
		self.__excFolderPrefixesRegSpec = '^('
		for i in range(count):
			self.__excFolderPrefixesRegSpec = self.__excFolderPrefixesRegSpec + self.__excFolderPrefixes[i]
			if i != count - 1:
				self.__excFolderPrefixesRegSpec = self.__excFolderPrefixesRegSpec + '|'
		self.__excFolderPrefixesRegSpec = self.__excFolderPrefixesRegSpec + ')(.)*$'

	@property
	def excFolderSuffixes(self):
		return self.__excFolderSuffixes
	
	@excFolderSuffixes.setter
	def excFolderSuffixes(self, value):
		if self.__excFolderSuffixes == value:
			return
		self.__excFolderSuffixes = value

		if self.__excFolderSuffixes == None:
			self.__excFolderSuffixesRegSpec = None
			return

		count = len(self.__excFolderSuffixes)
		if count == 0:
			self.__excFolderSuffixesRegSpec = None
			return
		
		self.__excFolderSuffixesRegSpec = '^(.)*('
		for i in range(count):
			self.__excFolderSuffixesRegSpec = self.__excFolderSuffixesRegSpec + self.__excFolderSuffixes[i]
			if i != count - 1:
				self.__excFolderSuffixesRegSpec = self.__excFolderSuffixesRegSpec + '|'
		self.__excFolderSuffixesRegSpec = self.__excFolderSuffixesRegSpec + ')$'

	@property
	def excFilePrefixes(self):
		return self.__excFilePrefixes
	
	@excFilePrefixes.setter
	def excFilePrefixes(self, value):
		if self.__excFilePrefixes == value:
			return
		self.__excFilePrefixes = value

		if self.__excFilePrefixes == None:
			self.__excFilePrefixesRegSpec = None
			return

		count = len(self.__excFilePrefixes)
		if count == 0:
			self.__excFilePrefixesRegSpec = None
			return
		
		self.__excFilePrefixesRegSpec = '^('
		for i in range(count):
			self.__excFilePrefixesRegSpec = self.__excFilePrefixesRegSpec + self.__excFilePrefixes[i]
			if i != count - 1:
				self.__excFilePrefixesRegSpec = self.__excFilePrefixesRegSpec + '|'
		self.__excFilePrefixesRegSpec = self.__excFilePrefixesRegSpec + ')(.)*$'

	@property
	def excFileSuffixes(self):
		return self.__excFileSuffixes
	
	@excFileSuffixes.setter
	def excFileSuffixes(self, value):
		if self.__excFileSuffixes == value:
			return
		self.__excFileSuffixes = value

		if self.__excFileSuffixes == None:
			self.__excFileSuffixesRegSpec = None
			return

		count = len(self.__excFileSuffixes)
		if count == 0:
			self.__excFileSuffixesRegSpec = None
			return
		
		self.__excFileSuffixesRegSpec = '^(.)*('
		for i in range(count):
			self.__excFileSuffixesRegSpec = self.__excFileSuffixesRegSpec + self.__excFileSuffixes[i]
			if i != count - 1:
				self.__excFileSuffixesRegSpec = self.__excFileSuffixesRegSpec + '|'
		self.__excFileSuffixesRegSpec = self.__excFileSuffixesRegSpec + ')$'

	def shouldSkipFolder(self, name, path):
		if os.path.exists(path) == False or os.path.isdir(path) == False:
			return True
		if self.excFolderNames != None and (name in self.excFolderNames):
			return True
		if self.__excFolderPrefixesRegSpec != None and re.match(self.__excFolderPrefixesRegSpec, name, re.S) != None:
			return True
		if self.__excFolderSuffixesRegSpec != None and re.match(self.__excFolderSuffixesRegSpec, name, re.S) != None:
			return True
		return False
	
	def shouldSkipFile(self, name, path):
		if os.path.exists(path) == False or os.path.isdir(path) == True:
			return True
		if self.excFileNames != None and (name in self.excFileNames):
			return True
		if re.match('^(.)+\\.(h|m|mm|pch)$', name, re.S) == None:
			return True
		if self.__excFilePrefixesRegSpec != None and re.match(self.__excFilePrefixesRegSpec, name, re.S) != None:
			return True
		if self.__excFileSuffixesRegSpec != None and re.match(self.__excFileSuffixesRegSpec, name, re.S) != None:
			return True
		return False
	
	def shouldSkipContent(self, content):
		if content == None or len(content) == 0:
			return True
		if self.__excCharsRegSpec != None and re.match(self.__excCharsRegSpec, content, re.S) != None:
			return True
		return False