#include "Boot_Safety.h"
#include <stdint.h>
#include <string.h>

// Define the metadata structures for dual-bank A and B
static ImageMetadata metadata_a = {0};
static ImageMetadata metadata_b = {0};

#define MAX_VERSION 0xFFFFFFFF

// Function to calculate CRC32 of a buffer
uint32_t CalculateCRC32(const uint8_t *data, size_t length) {
    uint32_t crc = 0xFFFFFFFF;
    for (size_t i = 0; i < length; i++) {
        crc ^= ((uint32_t)data[i]) << 24;
        for (int j = 0; j < 8; j++) {
            if (crc & 0x80000000) {
                crc = (crc << 1) ^ 0x04C11DB7;
            } else {
                crc <<= 1;
            }
        }
    }
    return crc;
}

// Function to verify the image metadata and CRC
void Boot_Safety_VerifyImage(uint32_t metadata_address) {
    ImageMetadata *metadata = (ImageMetadata *)metadata_address;

    if (metadata->version > MAX_VERSION || metadata->state != 1) {
        Boot_Safety_RequestRollback();
    }

    uint32_t calculated_crc = CalculateCRC32((uint8_t *)(metadata->start_address), metadata->size);
    if (calculated_crc != metadata->crc) {
        Boot_Safety_RequestRollback();
    }
}

// Function to mark an image as valid
void Boot_Safety_MarkImageValid(uint32_t metadata_address) {
    ImageMetadata *metadata = (ImageMetadata *)metadata_address;
    metadata->state = 1;
}

// Function to request a rollback
void Boot_Safety_RequestRollback(void) {
    // Set the rollback flag or perform any other necessary actions
    // For simplicity, we'll just clear the valid state of both banks
    metadata_a.state = 0;
    metadata_b.state = 0;
}
