#include "Boot_Safety.h"
#include <stdint.h>
#include <stddef.h>

// CRC32 lookup table
static const uint32_t crc32_table[256] = {
    0x00000000, 0x77073096, 0xee0e612c, 0x990951ba, 0x076dc419, 0x706af48f, 0xe963a535, 0x9e6495a3,
    0x0edb8832, 0x79dcb8a4, 0xe0d5e91e, 0x97d2d988, 0x09b64c2b, 0x7eb17cbd, 0xe7b82d07, 0x90bf1d91,
    0x1db71064, 0x6ab020f2, 0xf3b97148, 0x84be41de, 0x1adad47d, 0x6ddde4eb, 0xf4d4b551, 0x83d385c7,
    0x136c9856, 0x646ba8c0, 0xfd62f97a, 0x8a65c9ec, 0x14015c4f, 0x63066cd9, 0xfa0f3d63, 0x8d080de5,
    0x3b6e20ce, 0x4c69105a, 0xd56041e0, 0xa2677176, 0x3c03e4df, 0x4b04d449, 0xd20d85f3, 0xa50ab565,
    0x35b5a8fa, 0x42b2986c, 0xdbbbc9d6, 0xacbcf940, 0x32d86ce3, 0x45df5c75, 0xdcd60dcf, 0xabd13d59,
    0x26d930ac, 0x51de003a, 0xc8d75180, 0xbfd06116, 0x21b4f4b5, 0x56b3c423, 0xcfba9599, 0xb8bda50f,
    0x2802b89e, 0x5f058808, 0xc60cd9b2, 0xb10be924, 0x2f6f7c87, 0x58684c11, 0xcb611dab, 0xbc662d3d,
    0x2b6914d2, 0x5c6e2444, 0xc56775fe, 0xb2604568, 0x2c04b26b, 0x5b0382fe, 0xc20af344, 0xb50da3d2,
    0x2a0ad079, 0x5d0dd0ef, 0xc4048155, 0xb303b1c3, 0x2e636464, 0x596454f2, 0xc06d0548, 0xb76a35de,
    0x29ebe0ab, 0x5ecb903d, 0xc7c2c187, 0xb0c5f111, 0x2e98e4b2, 0x599fe424, 0xc096b59a, 0xb791850c,
    0x273cb26c, 0x503fc2fa, 0xc9369344, 0xbe31a3d2, 0x2ee6b241, 0x5be182d7, 0xc2beb36d, 0xb5bda3fb,
    0x2e1f74ad, 0x591c443b, 0xc0151581, 0xb7122517, 0x89ad78a4, 0xfecae832, 0x67c3d988, 0x10c4e91e,
    0x8ddde4b3, 0xfbdaf425, 0x6cd3e59f, 0x1bd4d509, 0x86d098a0, 0xf1d7a836, 0x68dee98c, 0x1fd9d91a,
    0x81beeffb, 0xf6b9dedd, 0x6fb08e57, 0x18b7bee1, 0x882cbfa3, 0xff2faff5, 0xc6c69ff5, 0xb1c1a063,
    0x2a6c416c, 0x5d6b71fe, 0xc4622044, 0xb36510dd, 0x2aad5b7e, 0x5daa6bce, 0xc4cf3a76, 0xb3c80af0,
    0x2d6f590b, 0x5a68699d, 0xcb613827, 0xbc6608b1, 0x226ba24c, 0x556cb2dd, 0xcce5d367, 0xbbcb03f1,
    0x2acc50e2, 0x5dc96074, 0xc6cf11cd, 0xb1c8215b, 0x2ebe145a, 0x59b924cb, 0xc0bb7531, 0xbbbc45af,
    0x2ac57864, 0x5dc248f2, 0xcbc91948, 0xbcc829d6, 0x256ff8a5, 0x5268ef33, 0xcb61be89, 0xbc668e1f,
    0x2b69b7bf, 0x5c6eb72d, 0xc567e697, 0xb260d601, 0x2c69aeab, 0x5b6ecedc, 0xcb67be66, 0xbc608ee0,
    0x2b69f7bf, 0x5c6eb72d, 0xc567e697, 0xb260d601, 0x2c69aeab, 0x5b6ecedc, 0xcb67be66, 0xbc608ee0
};

// Function to calculate CRC32
static uint32_t Boot_Safety_CalculateCRC32(const uint8_t *data, size_t length) {
    uint32_t crc = 0xFFFFFFFF;
    for (size_t i = 0; i < length; ++i) {
        crc = crc32_table[(crc ^ data[i]) & 0xFF] ^ (crc >> 8);
    }
    return crc ^ 0xFFFFFFFF;
}

// Function to verify image metadata and CRC
void Boot_Safety_VerifyImage(uint32_t metadata_address) {
    Boot_Safety_ImageMetadata *metadata = (Boot_Safety_ImageMetadata *)metadata_address;

    // Read the image data from the specified start address
    uint8_t *image_data = (uint8_t *)(metadata->start_address);
    size_t image_size = metadata->size;

    // Calculate the CRC of the image data
    uint32_t calculated_crc = Boot_Safety_CalculateCRC32(image_data, image_size);

    // Verify the CRC and state
    if (calculated_crc == metadata->crc && metadata->state != 0) {
        // Image is valid
        return;
    } else {
        // Image is invalid or rollback requested
        Boot_Safety_RequestRollback(metadata_address);
    }
}

// Function to mark an image as valid
void Boot_Safety_MarkImageValid(uint32_t metadata_address) {
    Boot_Safety_ImageMetadata *metadata = (Boot_Safety_ImageMetadata *)metadata_address;
    metadata->state = 1; // Mark the image as valid
}

// Function to request rollback
void Boot_Safety_RequestRollback(uint32_t metadata_address) {
    Boot_Safety_ImageMetadata *metadata = (Boot_Safety_ImageMetadata *)metadata_address;
    metadata->state = 2; // Request rollback
}
