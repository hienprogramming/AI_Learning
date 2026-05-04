#include "Boot_Protocol.h"
#include <stdint.h>
#include <stddef.h>

// Helper function to calculate CRC16
uint16_t CalculateCRC(const uint8_t *buffer, size_t length) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < length; i++) {
        crc ^= buffer[i] << 8;
        for (int j = 0; j < 8; j++) {
            if (crc & 0x8000) {
                crc = (crc << 1) ^ 0x1021;
            } else {
                crc <<= 1;
            }
        }
    }
    return crc;
}

// Function to parse a received packet
uint8_t Boot_Protocol_ParsePacket(const uint8_t *buffer, size_t length, Packet *packet) {
    if (length < 7) { // Minimum length: COMMAND + ADDRESS(4 bytes) + LENGTH(1 byte)
        return NACK;
    }

    packet->command = buffer[0];
    packet->address = ((uint32_t)buffer[1] << 24) |
                      ((uint32_t)buffer[2] << 16) |
                      ((uint32_t)buffer[3] << 8) |
                      (uint32_t)buffer[4];
    packet->length = buffer[5];

    if (packet->length > sizeof(packet->payload)) {
        return NACK;
    }

    // Copy payload
    for (size_t i = 0; i < packet->length; i++) {
        packet->payload[i] = buffer[6 + i];
    }

    // Calculate and check CRC
    uint16_t received_crc = ((uint16_t)buffer[length - 2] << 8) | buffer[length - 1];
    uint16_t calculated_crc = CalculateCRC(buffer, length - 2);
    if (received_crc != calculated_crc) {
        return NACK;
    }

    return ACK;
}

// Function to build an ACK/NACK response packet
void Boot_Protocol_BuildResponse(uint8_t command, uint8_t status, uint32_t address, uint8_t *response, size_t *response_length) {
    response[0] = command; // COMMAND
    response[1] = (address >> 24) & 0xFF; // ADDRESS(4 bytes)
    response[2] = (address >> 16) & 0xFF;
    response[3] = (address >> 8) & 0xFF;
    response[4] = address & 0xFF;
    response[5] = status; // STATUS
    *response_length = 6;

    // Calculate and append CRC
    uint16_t crc = CalculateCRC(response, *response_length);
    response[*response_length] = (crc >> 8) & 0xFF;
    response[*response_length + 1] = crc & 0xFF;
    *response_length += 2;
}
