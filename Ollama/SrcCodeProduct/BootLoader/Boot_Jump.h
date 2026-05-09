#ifndef BOOT_JUMP_H
#define BOOT_JUMP_H

#include <stdint.h>

#define APPLICATION_START_ADDRESS 0x08008000
#define MSP 0x20008000
#define STM32F103C8T6 "STM32F103C8T6"

/**
 * @brief Validates if the application is valid based on stack pointer and reset vector.
 *
 * @return 1 if the application is valid, 0 otherwise.
 */
uint8_t Boot_IsApplicationValid(void);

/**
 * @brief Jumps to the application's reset handler.
 */
void Boot_JumpToApplication(void);

#endif /* BOOT_JUMP_H */
