#include "Boot_Safety.h"
#include "crc.h"

#define METADATA_SIZE 512 // Adjust this based on your requirements

typedef struct {
    uint32_t version;
    uint32_t size;
    uint32_t start_address;
    uint32_t crc32;
    uint8_t state; // 0: Invalid, 1: Valid
} FirmwareMetadata;

#define BANK_A_METADATA_ADDR (0x0807E000)
#define BANK_B_METADATA_ADDR (0x080FC000)

static FirmwareMetadata metadata_bank_a __attribute__((section(".data.metadata_bank_a"))) = {0};
static FirmwareMetadata metadata_bank_b __attribute__((section(".data.metadata_bank_b"))) = {0};

/**
 * Calculate the CRC32 of a firmware image.
 *
 * @param data Pointer to the data
 * @param length Length of the data
 * @return Calculated CRC32 value
 */
uint32_t calculate_crc32(const uint8_t *data, size_t length) {
    uint32_t crc = 0xFFFFFFFF;
    for (size_t i = 0; i < length; ++i) {
        crc ^= (uint32_t)data[i] << 24;
        for (int j = 0; j < 8; ++j) {
            if (crc & 0x80000000) {
                crc = (crc << 1) ^ 0x04C11DB7;
            } else {
                crc <<= 1;
            }
        }
    }
    return crc ^ 0xFFFFFFFF;
}

/**
 * Verify the metadata and CRC of a firmware image.
 *
 * @param bank 'A' or 'B'
 * @return true if the image is valid, false otherwise
 */
bool Boot_Safety_VerifyImage(uint8_t bank) {
    FirmwareMetadata *metadata = (bank == 'A') ? &metadata_bank_a : &metadata_bank_b;
    
    if (metadata->state != 1) {
        return false; // Image is not valid
    }

    uint32_t calculated_crc = calculate_crc32((uint8_t *)metadata->start_address, metadata->size);
    if (calculated_crc != metadata->crc32) {
        return false; // CRC mismatch
    }

    return true;
}

/**
 * Mark a firmware image as valid.
 *
 * @param bank 'A' or 'B'
 * @param version Version of the firmware
 * @param size Size of the firmware image
 * @param start_address Start address of the firmware image
 * @param data Pointer to the firmware image data
 */
void Boot_Safety_MarkImageValid(uint8_t bank, uint32_t version, uint32_t size, uint32_t start_address, const uint8_t *data) {
    FirmwareMetadata *metadata = (bank == 'A') ? &metadata_bank_a : &metadata_bank_b;
    
    metadata->version = version;
    metadata->size = size;
    metadata->start_address = start_address;
    metadata->crc32 = calculate_crc32(data, size);
    metadata->state = 1; // Valid
}

/**
 * Request a rollback if an update fails.
 *
 * @param bank 'A' or 'B'
 */
void Boot_Safety_RequestRollback(uint8_t bank) {
    FirmwareMetadata *metadata = (bank == 'A') ? &metadata_bank_a : &metadata_bank_b;
    
    metadata->state = 0; // Invalid
}
