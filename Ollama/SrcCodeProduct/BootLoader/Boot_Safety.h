#ifndef BOOT_SAFETY_H
#define BOOT_SAFETY_H

#include <stdint.h>
#include <stdbool.h>

/**
 * Verify the metadata and CRC of a firmware image in a specific bank.
 *
 * @param bank 'A' or 'B'
 * @return true if the image is valid, false otherwise
 */
bool Boot_Safety_VerifyImage(uint8_t bank);

/**
 * Mark a firmware image as valid.
 *
 * @param bank 'A' or 'B'
 * @param version Version of the firmware
 * @param size Size of the firmware image
 * @param start_address Start address of the firmware image
 * @param data Pointer to the firmware image data
 */
void Boot_Safety_MarkImageValid(uint8_t bank, uint32_t version, uint32_t size, uint32_t start_address, const uint8_t *data);

/**
 * Request a rollback if an update fails.
 *
 * @param bank 'A' or 'B'
 */
void Boot_Safety_RequestRollback(uint8_t bank);

#endif // BOOT_SAFETY_H
