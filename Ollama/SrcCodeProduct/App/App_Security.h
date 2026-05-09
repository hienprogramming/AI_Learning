#ifndef APP_SECURITY_H_
#define APP_SECURITY_H_

#include <stdint.h>
#include <stdbool.h>

// Define AES and CRC32 if they are not already defined
#ifdef __cplusplus
extern "C" {
#endif

void AES_Encrypt(const uint8_t *key, const uint8_t *plaintext, uint8_t *ciphertext);
uint32_t CRC32(const uint8_t *data, size_t length);

#ifdef __cplusplus
}
#endif

// Initialize security subsystem
void App_Security_Init(void);

// Compute hash using CRC32 or similar method
uint32_t App_Security_HashData(const uint8_t *data, size_t length);

// Verify digital signature
bool App_Security_VerifySignature(const uint8_t *data, size_t data_length,
                                  const uint8_t *signature, size_t signature_length);

// Basic encryption wrapper
void App_Security_EncryptKey(uint8_t *key, uint8_t *encrypted);

// Basic decryption wrapper
void App_Security_DecryptKey(const uint8_t *encrypted, uint8_t *key);

#endif // APP_SECURITY_H_
