#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys, os, base64
from Crypto.Cipher import AES

class BACommonEncryptUtil(object):
	def __init__(self):
		super(BACommonEncryptUtil, self).__init__()

	@classmethod
	def __bytePad(cls, text, byteAlignLen):
		count = len(text)
		mod_num = count % byteAlignLen
		if mod_num == 0:
			return text
		add_num = ((count // byteAlignLen) + 1) * byteAlignLen - count
		return bytes(text.decode('utf-8') + chr(add_num) * add_num, 'utf-8')
	
	@classmethod
	def __byteUnpad(cls, text, byteAlignLen):
		textTmp = text.decode('utf-8')
		lastChar = textTmp[-1]
		lastLen = ord(lastChar)
		lastChunk = textTmp[-lastLen:]
		if lastChunk == chr(lastLen)*lastLen:
			return bytes(textTmp[:-lastLen], 'utf-8')
		return bytes(textTmp, 'utf-8')

	@classmethod
	def AESEncrypt(cls, source, key, iv):
		if source == None:
			return "⚠️ ERROR: Content null!"
		if key == None or iv == None:
			return "⚠️ ERROR: Key and iv can't be null!"
		if len(key) % 16 != 0 or len(iv) % 16 != 0:
			return '⚠️ ERROR: Length of key and iv must be a multiple of 16!'
		cryptor = AES.new(bytes(key, 'utf-8'), AES.MODE_CBC, bytes(iv, 'utf-8'))
		ciphertext = cryptor.encrypt(cls.__bytePad(bytes(source, 'utf-8'), 16))
		result = base64.b64encode(ciphertext).decode('utf-8')
		return result

	@classmethod
	def AESDecrypt(cls, source, key, iv):
		if source == None:
			return "⚠️ ERROR: Content null!"
		if key == None or iv == None:
			return "⚠️ ERROR: Key and iv can't be null!"
		if len(key) % 16 != 0 or len(iv) % 16 != 0:
			return '⚠️ ERROR: Length of key and iv must be a multiple of 16!'
		encrData = base64.b64decode(bytes(source, 'utf-8'))
		cipher = AES.new(bytes(key, 'utf-8'), AES.MODE_CBC, bytes(iv, 'utf-8'))
		decrData = cipher.decrypt(encrData)
		decrData = cls.__byteUnpad(decrData, 16)
		result = decrData.decode('utf-8')
		return result