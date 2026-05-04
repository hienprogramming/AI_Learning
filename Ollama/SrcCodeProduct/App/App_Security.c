#ifndef APP_SECURITY_H
#define APP_SECURITY_H

#include <stdint.h>
#include <stddef.h>

// Constants
#define MAX_SIGNALS 8
#define MAX_PDUS 4

// Function prototypes
void App_Security_Init(void);
uint32_t App_Security_HashData(const uint8_t *data, size_t length);
int App_Security_VerifySignature(const uint8_t *data, const uint8_t *signature, size_t data_length);
int App_Security_EncryptKey(uint8_t *key, uint8_t *encrypted, size_t key_length);
int App_Security_DecryptKey(uint8_t *encrypted, uint8_t *key, size_t key_length);

#endif // APP_SECURITY_H
