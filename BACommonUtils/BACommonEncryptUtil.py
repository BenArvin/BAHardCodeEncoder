#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys, os, base64
from Crypto.Cipher import AES
reload(sys)
sys.setdefaultencoding("utf-8")

class BACommonEncryptUtil(object):
	def __init__(self):
		super(BACommonEncryptUtil, self).__init__()

	@classmethod
	def AESEncrypt(cls, source, key, iv):
		if source == None:
			return "⚠️ ERROR: Content null!"
		if key == None or iv == None:
			return "⚠️ ERROR: Key and iv can't be null!"
		if len(key) % 16 != 0 or len(iv) % 16 != 0:
			return '⚠️ ERROR: Length of key and iv must be a multiple of 16!'
		text = source
		cryptor = AES.new(key, AES.MODE_CBC, iv)
		length = 16
		count = len(text)
		if count % length != 0:
			add = (((count // length) + 1) * length - count)
			text += (chr(add) * add)
		ciphertext = cryptor.encrypt(text)
		return base64.b64encode(ciphertext)

	@classmethod
	def AESDecrypt(cls, source, key, iv):
		if source == None:
			return "⚠️ ERROR: Content null!"
		if key == None or iv == None:
			return "⚠️ ERROR: Key and iv can't be null!"
		if len(key) % 16 != 0 or len(iv) % 16 != 0:
			return '⚠️ ERROR: Length of key and iv must be a multiple of 16!'
		encrData = base64.b64decode(source)
		cipher = AES.new(key, AES.MODE_CBC, iv)
		decrData = cipher.decrypt(encrData)
		decrData = decrData[:-ord(decrData[len(decrData)-1:])]
		return decrData.decode('utf-8')
