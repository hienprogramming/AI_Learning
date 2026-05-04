#include "Boot_Jump.h"
#include "stm32f10x.h"

#define APPLICATION_START_ADDRESS 0x08008000

// Function to validate the application
void Boot_IsApplicationValid(void) {
    uint32_t *appStackPointer = (uint32_t *)APPLICATION_START_ADDRESS;
    uint32_t *appResetVector = (uint32_t *)(APPLICATION_START_ADDRESS + 4);

    // Check if stack pointer and reset vector are valid
    if ((appStackPointer != NULL) && (appResetVector != NULL)) {
        __IO uint32_t spValue = appStackPointer[0]; // MSP value
        __IO uint32_t pcValue = appResetVector[1]; // Reset handler address

        // Check if the reset vector is a valid function pointer
        if ((pcValue >= APPLICATION_START_ADDRESS) && (pcValue < 0x10000000)) {
            // Valid application
        } else {
            // Invalid application, stay in bootloader
        }
    } else {
        // Invalid application, stay in bootloader
    }
}

// Function to jump to the application
void Boot_JumpToApplication(void) {
    uint32_t *appResetVector = (uint32_t *)(APPLICATION_START_ADDRESS + 4);
    __IO uint32_t pcValue = appResetVector[1]; // Reset handler address

    // Disable all interrupts
    __disable_irq();

    // Set the MSP stack pointer to the application's stack pointer
    __set_MSP(appResetVector[0]);

    // Jump to the application reset handler
    ((void (*)(void))pcValue)();
}
