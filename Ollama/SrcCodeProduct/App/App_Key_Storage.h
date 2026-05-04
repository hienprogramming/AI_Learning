#ifndef APP_KEY_STORAGE_H
#define APP_KEY_STORAGE_H

#include <stdint.h>

#define KEY_STORAGE_START_ADDRESS 0x08040000
#define KEY_STORAGE_SIZE 1024 // 1KB for key storage area
#define MAX_KEYS 32
#define KEY_ID_SIZE 8
#define KEY_DATA_SIZE 64
#define CRC_SIZE 4

typedef enum {
    APP_KEY_STATUS_SUCCESS,
    APP_KEY_STATUS_ERROR,
    APP_KEY_STATUS_FULL,
    APP_KEY_STATUS_NOT_FOUND
} App_Key_Status;

typedef struct {
    uint8_t id[KEY_ID_SIZE];
    uint8_t data[KEY_DATA_SIZE];
    uint32_t crc;
} KeyEntry;

void App_Key_Init(void);
App_Key_Status App_Key_Store(const uint8_t *key_id, const uint8_t *key_data, size_t key_size);
App_Key_Status App_Key_Retrieve(const uint8_t *key_id, uint8_t *key_data, size_t *key_size);
uint32_t App_Key_Exists(const uint8_t *key_id);

#endif // APP_KEY_STORAGE_H
