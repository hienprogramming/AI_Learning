#include "Boot_Protocol.h"
#include <string.h>
#include <stdint.h>

// Function to calculate CRC16 for a buffer
uint16_t CalculateCRC16(const uint8_t *buffer, size_t length) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < length; ++i) {
        crc ^= (uint16_t)buffer[i] << 8;
        for (int j = 0; j < 8; ++j) {
            if (crc & 0x8000)
                crc = (crc << 1) ^ 0x1021;
            else
                crc <<= 1;
        }
    }
    return crc;
}

// Function to parse a received packet and decode it
uint8_t Boot_Protocol_ParsePacket(Boot_Packet *packet, const uint8_t *buffer, size_t buffer_size) {
    if (buffer_size < sizeof(Boot_Packet))
        return NACK;

    // Extract the packet fields
    packet->command = buffer[0];
    memcpy(&packet->address, &buffer[1], 4);
    packet->length = buffer[5];

    // Check payload length and CRC
    if (packet->length > sizeof(packet->payload) || buffer_size < 7 + packet->length)
        return NACK;

    memcpy(packet->payload, &buffer[6], packet->length);

    // Calculate the expected CRC
    uint16_t calculated_crc = CalculateCRC16(buffer, 5 + packet->length);
    if (calculated_crc != *(uint16_t *)&buffer[6 + packet->length])
        return NACK;

    return ACK;
}

// Function to build an ACK/NACK response packet
void Boot_Protocol_BuildResponse(uint8_t *response_buffer, uint8_t command, uint8_t status) {
    response_buffer[0] = command;
    response_buffer[1] = status;
    CalculateCRC16(response_buffer, 2);
    memcpy(&response_buffer[2], &response_buffer[0], 2);
}
