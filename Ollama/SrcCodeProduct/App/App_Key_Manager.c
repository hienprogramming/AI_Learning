#include "App_Key_Manager.h"
#include "Boot_Safety.h"

#define MAX_KEYS 10

static KeyInfo keys[MAX_KEYS];
static uint8_t key_count = 0;

void App_KeyManager_Init(void) {
    // Initialize the key manager (e.g., read keys from flash)
    // This is a placeholder for actual initialization logic
}

bool App_KeyManager_ValidateKey(uint32_t key_id) {
    for (uint8_t i = 0; i < key_count; i++) {
        if (keys[i].key_id == key_id) {
            return Boot_Safety_IsKeyValid(keys[i]);
        }
    }
    return false;
}

bool App_KeyManager_IsKeyValid(uint32_t key_id, const char* key) {
    for (uint8_t i = 0; i < key_count; i++) {
        if (keys[i].key_id == key_id && strcmp(keys[i].key_version, key->version) == 0) {
            return Boot_Safety_IsKeyValid(keys[i]);
        }
    }
    return false;
}

void App_KeyManager_GetKeyInfo(uint32_t key_id, KeyInfo* info) {
    for (uint8_t i = 0; i < key_count; i++) {
        if (keys[i].key_id == key_id) {
            *info = keys[i];
            return;
        }
    }
    // Handle error or initialize with default values
}

void App_KeyManager_AddKey(uint32_t key_id, uint8_t version, uint32_t expiration_time) {
    if (key_count < MAX_KEYS) {
        keys[key_count].key_id = key_id;
        keys[key_count].key_version = version;
        keys[key_count].expiration_time = expiration_time;
        key_count++;
    }
}

// Example usage in main or bootloader
void InitializeKeyManager() {
    App_KeyManager_Init();
    // Add keys to the manager (e.g., from flash)
    App_KeyManager_AddKey(0x1234, 1, 1672502400); // Unix timestamp for 2023-01-01
}

#endif /* APP_KEY_MANAGER_C_ */
