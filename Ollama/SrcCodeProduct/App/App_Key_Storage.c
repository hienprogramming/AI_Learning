#include "App_Key_Storage.h"
#include "Boot_Safety.h"

#define KEY_ENTRY_SIZE (KEY_ID_SIZE + KEY_DATA_SIZE + CRC_SIZE)

KeyEntry key_storage[MAX_KEYS] = {0};
uint8_t key_storage_buffer[KEY_STORAGE_SIZE];
static uint16_t used_slots = 0;

void App_Key_Init(void) {
    // Copy the existing key storage from flash to RAM
    for (int i = 0; i < MAX_KEYS; i++) {
        KeyEntry *entry = (KeyEntry *)(KEY_STORAGE_START_ADDRESS + i * KEY_ENTRY_SIZE);
        uint32_t crc_calculated = Boot_Safety_CalculateCRC((uint8_t *)entry, sizeof(KeyEntry) - CRC_SIZE);
        if (crc_calculated == entry->crc) {
            key_storage[i] = *entry;
            used_slots++;
        }
    }
}

App_Key_Status App_Key_Store(const uint8_t *key_id, const uint8_t *key_data, size_t key_size) {
    for (int i = 0; i < MAX_KEYS; i++) {
        if (memcmp(key_storage[i].id, key_id, KEY_ID_SIZE) == 0) {
            // Key already exists, update it
            memcpy(key_storage[i].data, key_data, key_size);
            uint32_t crc_calculated = Boot_Safety_CalculateCRC((uint8_t *)&key_storage[i], sizeof(KeyEntry) - CRC_SIZE);
            key_storage[i].crc = crc_calculated;
            return APP_KEY_STATUS_SUCCESS;
        }
    }

    // Find a free slot to store the new key
    for (int i = 0; i < MAX_KEYS; i++) {
        if (memcmp(key_storage[i].id, "\0\0\0\0\0\0\0\0", KEY_ID_SIZE) == 0) {
            memcpy(key_storage[i].id, key_id, KEY_ID_SIZE);
            memcpy(key_storage[i].data, key_data, key_size);
            uint32_t crc_calculated = Boot_Safety_CalculateCRC((uint8_t *)&key_storage[i], sizeof(KeyEntry) - CRC_SIZE);
            key_storage[i].crc = crc_calculated;
            used_slots++;
            return APP_KEY_STATUS_SUCCESS;
        }
    }

    return APP_KEY_STATUS_FULL; // No free slot found
}

App_Key_Status App_Key_Retrieve(const uint8_t *key_id, uint8_t *key_data, size_t *key_size) {
    for (int i = 0; i < MAX_KEYS; i++) {
        if (memcmp(key_storage[i].id, key_id, KEY_ID_SIZE) == 0) {
            memcpy(key_data, key_storage[i].data, sizeof(KeyEntry) - CRC_SIZE);
            *key_size = sizeof(KeyEntry) - CRC_SIZE;
            return APP_KEY_STATUS_SUCCESS;
        }
    }

    return APP_KEY_STATUS_NOT_FOUND; // Key not found
}

uint32_t App_Key_Exists(const uint8_t *key_id) {
    for (int i = 0; i < MAX_KEYS; i++) {
        if (memcmp(key_storage[i].id, key_id, KEY_ID_SIZE) == 0) {
            return 1;
        }
    }

    return 0;
}
