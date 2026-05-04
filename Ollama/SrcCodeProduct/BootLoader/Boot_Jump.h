#ifndef BOOT_JUMP_H_
#define BOOT_JUMP_H_

#include "stm32f1xx.h"

/**
 * @brief Validate if the application at 0x08008000 is valid.
 *
 * This function checks if the stack pointer and reset vector of the application are set correctly.
 *
 * @return uint8_t 1 if the application is valid, 0 otherwise.
 */
uint8_t Boot_IsApplicationValid(void);

/**
 * @brief Jump to the application at 0x08008000.
 *
 * This function disables interrupts, sets the Main Stack Pointer (MSP), and jumps
 * to the application's reset handler.
 */
void Boot_JumpToApplication(void);

#endif /* BOOT_JUMP_H_ */
