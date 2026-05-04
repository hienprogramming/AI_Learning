#include "Boot_Jump.h"

#define APPLICATION_ADDRESS 0x08008000

/**
 * @brief Validate if the application at 0x08008000 is valid.
 *
 * This function checks if the stack pointer and reset vector of the application are set correctly.
 *
 * @return uint8_t 1 if the application is valid, 0 otherwise.
 */
uint8_t Boot_IsApplicationValid(void)
{
    // Get the address of the reset handler from the application
    void (*app_reset_handler)(void) = (void (*)(void))*(volatile unsigned int *)(APPLICATION_ADDRESS + 4);

    // Check if the reset vector and stack pointer are valid
    return (app_reset_handler != NULL);
}

/**
 * @brief Jump to the application at 0x08008000.
 *
 * This function disables interrupts, sets the Main Stack Pointer (MSP), and jumps
 * to the application's reset handler.
 */
void Boot_JumpToApplication(void)
{
    // Get the address of the stack pointer from the application
    unsigned int app_stack_pointer = *(volatile unsigned int *)(APPLICATION_ADDRESS);

    // Disable interrupts
    __disable_irq();

    // Set the Main Stack Pointer (MSP) to the application's stack pointer
    __set_MSP(app_stack_pointer);

    // Get the address of the reset handler from the application
    void (*app_reset_handler)(void) = (void (*)(void))*(volatile unsigned int *)(APPLICATION_ADDRESS + 4);

    // Jump to the application's reset handler
    app_reset_handler();
}
