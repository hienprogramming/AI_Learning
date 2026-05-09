#ifndef BOOT_PROTOCOL_H
#define BOOT_PROTOCOL_H

#include <stdint.h>

// Command IDs
#define CMD_ERASE   0x01
#define CMD_WRITE   0x02
#define CMD_VERIFY  0x03
#define CMD_JUMP    0x04

// ACK/NACK Response Codes
#define ACK         0x55
#define NAK         0xAA

// CRC Calculation Constants
#define XOR 0xFF

// Packet Format
typedef struct {
    uint8_t command;
    uint32_t address;
    uint16_t length;
    uint8_t payload[256]; // Adjust size as needed
    uint8_t crc;
} Boot_Packet;

// Function Prototypes
void Boot_Protocol_ParsePacket(const uint8_t *buffer, uint16_t buffer_size, Boot_Packet *packet);
uint8_t Boot_Protocol_BuildResponse(uint8_t command, uint32_t address, uint16_t length);

#endif // BOOT_PROTOCOL_H
