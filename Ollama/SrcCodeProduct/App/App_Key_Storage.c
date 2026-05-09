#ifndef APP_KEY_STORAGE_H
#define APP_KEY_STORAGE_H

#include <stdint.h>
#include "Boot_Safety.h"

// Maximum number of key entries
#define MAX_KEYS 10

// Size of each key entry in bytes (adjust according to your needs)
#define KEY_ENTRY_SIZE 64

// Key ID type
typedef uint8_t App_Key_ID;

// Function prototypes
void App_Key_Init(void);
int App_Key_Store(App_Key_ID key_id, const uint8_t *key_data, size_t key_size);
int App_Key_Retrieve(App_Key_ID key_id, uint8_t *key_data, size_t key_size);
int App_Key_Exists(App_Key_ID key_id);

#endif // APP_KEY_STORAGE_H
