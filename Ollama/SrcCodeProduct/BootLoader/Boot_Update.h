#ifndef BOOT_UPDATE_H
#define BOOT_UPDATE_H

#include <stdint.h>

// Command codes
#define CMD_ERASE 0x52454153
#define CMD_WRITE 0x57484552
#define CMD_VERIFY 0x56455259
#define CMD_JUMP 0x4A504D4F

// Boot Update Status
typedef enum {
    BOOT_UPDATE_OK,
    BOOT_UPDATE_ERROR,
    BOOT_UPDATE_ERASE_FAILED,
    BOOT_UPDATE_WRITE_FAILED,
    BOOT_UPDATE_VERIFY_FAILED,
    BOOT_UPDATE_CMD_UNKNOWN,
} Boot_Update_Status;

void Boot_Update_Init(void);
Boot_Update_Status Boot_Update_ProcessPacket(const uint8_t *data, size_t length);

#endif // BOOT_UPDATE_H
