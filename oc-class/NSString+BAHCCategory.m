//
//  NSString+BAHCCategory.m
//  BAHardCodeEncoder
//
//  Created by BenArvin on 2018/11/2.
//  Copyright ©BenArvin. All rights reserved.
//

#import "NSString+BAHCCategory.h"
#import <CommonCrypto/CommonDigest.h>
#import <CommonCrypto/CommonCryptor.h>
#import "GTMBase64.h"

#define BAHC_AES_KEY @"9Jvae2bFOYL$JoTt"
#define BAHC_AES_IV @"yg@t2lLZXmP8&J7r"

@implementation NSString (BAHCCategory)

#pragma mark - public methods
- (NSString *)BAHC_Encrypt
{
    return [self BAHC_AESEncrypt:BAHC_AES_KEY IV:BAHC_AES_IV];
}

- (NSString *)BAHC_Decrypt
{
    return [self BAHC_AESDecrypt:BAHC_AES_KEY IV:BAHC_AES_IV];
}

- (NSString *)BAHC_AESEncrypt:(NSString *)key IV:(NSString *)IV
{
    NSData *data = [self dataUsingEncoding:NSUTF8StringEncoding];
    NSData *AESData = [self AES128operation:kCCEncrypt
                                       data:data
                                        key:key
                                         iv:IV];
    NSString *baseStr_GTM = [self encodeBase64Data:AESData];
    return baseStr_GTM;
}

- (NSString *)BAHC_AESDecrypt:(NSString *)key IV:(NSString *)IV
{
    NSData *baseData = [[NSData alloc]initWithBase64EncodedString:self options:0];
    
    NSData *AESData = [self AES128operation:kCCDecrypt
                                       data:baseData
                                        key:key
                                         iv:IV];

    NSString *decStr = [[NSString alloc] initWithData:AESData encoding:NSUTF8StringEncoding];
    return decStr;
}

#pragma mark - private methods
/**
 *  AES加解密算法
 *
 *  @param operation kCCEncrypt（加密）kCCDecrypt（解密）
 *  @param data      待操作Data数据
 *  @param key       key
 *  @param iv        向量
 *
 *  @return
 */
- (NSData *)AES128operation:(CCOperation)operation data:(NSData *)data key:(NSString *)key iv:(NSString *)iv
{
    char keyPtr[kCCKeySizeAES128 + 1];
    bzero(keyPtr, sizeof(keyPtr));
    [key getCString:keyPtr maxLength:sizeof(keyPtr) encoding:NSUTF8StringEncoding];
    
    // IV
    char ivPtr[kCCBlockSizeAES128 + 1];
    bzero(ivPtr, sizeof(ivPtr));
    [iv getCString:ivPtr maxLength:sizeof(ivPtr) encoding:NSUTF8StringEncoding];
    
    size_t bufferSize = [data length] + kCCBlockSizeAES128;
    void *buffer = malloc(bufferSize);
    size_t numBytesEncrypted = 0;
    
    CCCryptorStatus cryptorStatus = CCCrypt(operation, kCCAlgorithmAES128, kCCOptionPKCS7Padding,
                                            keyPtr, kCCKeySizeAES128,
                                            ivPtr,
                                            [data bytes], [data length],
                                            buffer, bufferSize,
                                            &numBytesEncrypted);
    
    if(cryptorStatus == kCCSuccess) {
        return [NSData dataWithBytesNoCopy:buffer length:numBytesEncrypted];
    }
    
    free(buffer);
    return nil;
}

/**< GTMBase64编码 */
- (NSString*)encodeBase64Data:(NSData *)data
{
    data = [GTMBase64 encodeData:data];
    NSString *base64String = [[NSString alloc] initWithData:data encoding:NSUTF8StringEncoding];
    return base64String;
}

/**< GTMBase64解码 */
- (NSData*)decodeBase64Data:(NSData *)data
{
    data = [GTMBase64 decodeData:data];
    return data;
}

@end
