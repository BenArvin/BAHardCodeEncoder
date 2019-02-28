#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys, os

class BAFileUtil(object):
	def __init__(self):
		super(BAFileUtil, self).__init__()

	@classmethod
	def isPathExisted(cls, path, isDir):
		if path == None or isinstance(path, str) == False or len(path) == 0:
			return False
		if os.path.exists(path) == False:
			return False
		if os.path.isdir(path) != isDir:
			return False
		return True

	@classmethod
	def getFileNameByPath(cls, path):
		if cls.isPathExisted(path, False) == False:
			return None
		(filePath, fileName) = os.path.split(path)
		return fileName

	@classmethod
	def getDirPathByFilePath(cls, path):
		if cls.isPathExisted(path, False) == False:
			return None
		(filePath, fileName) = os.path.split(path)
		return filePath

	@classmethod
	def getDirNameByDirPath(cls, path):
		if cls.isPathExisted(path, True) == False:
			return None
		tmpPath = path
		lastChar = tmpPath[len(tmpPath) - 1 : len(tmpPath)]
		if lastChar == '/':
			tmpPath = tmpPath[0 : len(tmpPath)-1]
		location = tmpPath.rfind('/')
		result = None
		if location == -1:
			result = tmpPath
		else:
			result = tmpPath[location + 1 : len(tmpPath)]
		return result

	@classmethod
	def getFileSuffix(cls, fileName):
		if fileName == None or len(fileName) == 0:
			return None
		(realName, suffix) = os.path.splitext(fileName)
		return suffix

	@classmethod
	def getFileSuffixByPath(cls, path):
		if cls.isPathExisted(path, False) == False:
			return None
		(filePath, fileName) = os.path.split(path)
		(realName, suffix) = os.path.splitext(fileName)
		return suffix

	@classmethod
	def __ergodicToFind(cls, targetName, isDir, rootPath, resultArray):
		for itemName in os.listdir(rootPath):
			itemPath = os.path.join(rootPath, itemName)
			itemIsDir = os.path.isdir(itemPath)
			if targetName == itemName and itemIsDir == isDir:
				resultArray.append(itemPath)
			elif itemIsDir == True:
				cls.__ergodicToFind(targetName, isDir, itemPath, resultArray)

	@classmethod
	def findTargetPaths(cls, targetName, isDir, rootPath):
		if targetName == None or isinstance(targetName, str) == False or len(targetName) == 0:
			return None
		if cls.isPathExisted(rootPath, True) == False:
			return None
		resultArray = []
		if isDir == True:
			rootDirName = cls.getDirNameByDirPath(rootPath)
			if rootDirName == targetName:
				resultArray.append(rootPath)
		cls.__ergodicToFind(targetName, isDir, rootPath, resultArray)
		return resultArray

	@classmethod
	def getLinesSize(cls, filePath):
		if cls.isPathExisted(filePath, False) == False:
			return None
		fileHandler = open(filePath, 'r')
		lines = fileHandler.readlines()
		fileHandler.close()
		result = []
		for line in lines:
			result.append(len(line))
		return result

	@classmethod
	def convertToOffset(cls, linesSize, line, column):
		if linesSize == None:
			return -1
		if len(linesSize) == 0:
			return 0
		result = 0
		for i in range(0, len(linesSize), 1):
			if i == line:
				result = result + column
				break
			else:
				result = result + linesSize[i]
		return result