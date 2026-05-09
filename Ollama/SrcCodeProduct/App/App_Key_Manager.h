#ifndef APP_KEY_MANAGER_H
#define APP_KEY_MANAGER_H

#include <stdint.h>
#include "Boot_Safety.h"

typedef enum {
    KEY_VALID,
    KEY_INVALID,
    KEY_EXPIRED
} KeyValidationStatus;

typedef struct {
    uint8_t version;
    uint32_t expiration_time; // Unix timestamp
} KeyInfo;

// Define constants for key validation statuses
#define BOOT_SAFETY_STATUS_OK 0
#define BOOT_SAFETY_STATUS_UNKNOWN -1

// Function prototypes
void App_KeyManager_Init(void);
KeyValidationStatus App_KeyManager_ValidateKey(uint8_t key_id);
int8_t App_KeyManager_IsKeyValid(uint8_t key_id);
void App_KeyManager_GetKeyInfo(uint8_t key_id, KeyInfo *info);

#endif // APP_KEY_MANAGER_H
