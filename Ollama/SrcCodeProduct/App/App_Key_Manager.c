#include "App_Key_Manager.h"
#include "Boot_Safety.h"

// Define the maximum number of keys
#define MAX_KEYS 10

// Define a structure to store key metadata
typedef struct {
    uint8_t version;
    uint32_t expiration_time; // Unix timestamp
    Boot_Safety_Status safety_status;
} KeyMetadata;

// Static array to store key metadata (static allocation only)
KeyMetadata keys[MAX_KEYS];

// Initialize the key manager
void App_KeyManager_Init(void) {
    // Clear all keys and their metadata
    for (uint8_t i = 0; i < MAX_KEYS; i++) {
        keys[i].version = 0;
        keys[i].expiration_time = 0;
        keys[i].safety_status = BOOT_SAFETY_STATUS_UNKNOWN;
    }
}

// Validate key integrity and expiration
KeyValidationStatus App_KeyManager_ValidateKey(uint8_t key_id) {
    if (key_id >= MAX_KEYS || keys[key_id].version == 0) {
        return KEY_INVALID;
    }

    Boot_Safety_Status safety_status = Boot_Safety_Check(keys[key_id].safety_status);

    if (safety_status != BOOT_SAFETY_STATUS_OK) {
        return KEY_INVALID;
    }

    uint32_t current_time = HAL_GetTick(); // Use a mock function for demonstration
    if (current_time > keys[key_id].expiration_time) {
        return KEY_EXPIRED;
    }

    return KEY_VALID;
}

// Check if key is valid
int8_t App_KeyManager_IsKeyValid(uint8_t key_id) {
    KeyValidationStatus status = App_KeyManager_ValidateKey(key_id);
    return (status == KEY_VALID);
}

// Retrieve key metadata
void App_KeyManager_GetKeyInfo(uint8_t key_id, KeyInfo *info) {
    if (key_id >= MAX_KEYS || keys[key_id].version == 0) {
        info->version = 0;
        info->expiration_time = 0;
        return;
    }

    info->version = keys[key_id].version;
    info->expiration_time = keys[key_id].expiration_time;
}
