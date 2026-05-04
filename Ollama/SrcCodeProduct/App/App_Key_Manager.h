#ifndef APP_KEY_MANAGER_H_
#define APP_KEY_MANAGER_H_

#include "Boot_Safety.h"

typedef struct {
    uint32_t key_id;
    uint8_t key_version;
    uint32_t expiration_time; // Unix timestamp in seconds
} KeyInfo;

#ifdef __cplusplus
extern "C" {
#endif

void App_KeyManager_Init(void);
bool App_KeyManager_ValidateKey(uint32_t key_id);
bool App_KeyManager_IsKeyValid(uint32_t key_id, const char* key);
void App_KeyManager_GetKeyInfo(uint32_t key_id, KeyInfo* info);

#ifdef __cplusplus
}
#endif

#endif /* APP_KEY_MANAGER_H_ */
