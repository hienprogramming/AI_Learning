#ifndef BOOT_UPDATE_H
#define BOOT_UPDATE_H

#include "stm32f1xx_hal.h"

#define APPLICATION_ADDRESS 0x08008000
#define MAX_PACKET_SIZE 256

typedef enum {
    CMD_ERASE,
    CMD_WRITE,
    CMD_VERIFY,
    CMD_JUMP
} BootCommand;

typedef struct {
    uint32_t address;
    uint16_t length;
    uint8_t data[MAX_PACKET_SIZE];
} Packet;

static Packet currentPacket;
static uint8_t buffer[MAX_PACKET_SIZE];

void Boot_Update_Init(void);
void Boot_Update_ProcessPacket(const uint8_t* data, size_t length);

#endif // BOOT_UPDATE_H
