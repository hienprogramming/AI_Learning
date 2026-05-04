#ifndef BOOT_PROTOCOL_H
#define BOOT_PROTOCOL_H

// Command IDs
#define CMD_ERASE     0x01
#define CMD_WRITE     0x02
#define CMD_VERIFY    0x03
#define CMD_JUMP      0x04

// Response codes
#define ACK           0x55
#define NACK          0xAA

// Packet format: [COMMAND][ADDRESS(4 bytes)][LENGTH(1 byte)][PAYLOAD(LENGTH bytes)][CRC(2 bytes)]
typedef struct {
    uint8_t command;
    uint32_t address;
    uint8_t length;
    uint8_t payload[256]; // Assuming max packet size of 256 bytes
} Packet;

// Function declarations
uint8_t Boot_Protocol_ParsePacket(const uint8_t *buffer, size_t length, Packet *packet);
void Boot_Protocol_BuildResponse(uint8_t command, uint8_t status, uint32_t address, uint8_t *response, size_t *response_length);

#endif // BOOT_PROTOCOL_H
