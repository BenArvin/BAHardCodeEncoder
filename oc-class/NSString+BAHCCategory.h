//
//  NSString+BAHCCategory.h
//  BAHardCodeEncoder
//
//  Created by BenArvin on 2018/11/2.
//  Copyright ©BenArvin. All rights reserved.
//

#import <Foundation/Foundation.h>

@interface NSString (BAHCCategory)

- (NSString *)BAHC_Encrypt;
- (NSString *)BAHC_Decrypt;

- (NSString *)BAHC_AESEncrypt:(NSString *)key IV:(NSString *)IV;
- (NSString *)BAHC_AESDecrypt:(NSString *)key IV:(NSString *)IV;

@end
