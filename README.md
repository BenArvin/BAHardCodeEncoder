# BAHardCodeEncoder

Encode all hard code string in objective-c project. Of course, you can decode the changes too.

## 1. Install and use

- (1) put files in /oc-class into your project
- (2) pipenv install
- (3) start encode/decode action by command:
    > python param1 --encode/--decode param2
    >
    > param1: path of this script
    > 
    > param2: root path of project
- (4) import `NSString+BAHCCategory.h` and `BAHCDefenitions.h` globally

Also, you can use option --encrypt/--decrypt to encrypt/decrypt individual content

## 2. Set rules of exception
You can set rules of exception by change these vlaues in `BAHardCodeEncoder.py`

- `Exception_File_Names`: file name
- `Exception_File_Prefix`: file name prefix
- `Exception_File_Suffix`: file name suffix
- `Exception_Folder_Names`: folder name
- `Exception_Folder_Prefix`: folder name prefix
- `Exception_Folder_Suffix`: folder name suffix
- `Exception_String_Format_Specifiers`: string format specifiers like `%@`. If string contain one of these, then shall skip it

**You must skip these files: `NSString+BAHCCategory.h`, `NSString+BAHCCategory.m`, `BAHCDefenitions.h`, `GTMBase64.h`, `GTMBase64.m`, `GTMDefines.h`**

## 3. Keep encoded content different
You should change `Key_salt` in `BAHardCodeEncoder.py` every time, to keep encoded content on code file alaways different

## 4. Self define encode logic
The default encode logic is AES, you can just change key and iv of it, or rewrite encode logic

### 4.1 Change key and iv of AES
Change `AES_key` and `AES_iv` in `BAHardCodeEncoder.py`

**Length of Key and iv for AES must be a multiple of 16**

### 4.2 Rewrite encode logic
You can make it by rewrite function `__encryptFunc` in `BAHardCodeEncoder.py`

GitHub Link: [https://github.com/BenArvin/BAHardCodeEncoder](https://github.com/BenArvin/BAHardCodeEncoder)