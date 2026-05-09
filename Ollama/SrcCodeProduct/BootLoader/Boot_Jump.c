#include "Boot_Jump.h"
#include <stdint.h>

#define APPLICATION_START_ADDRESS 0x08008000
#define MSP 0x20008000
#define STM32F103C8T6 "STM32F103C8T6"

/**
 * @brief Validates if the application is valid based on stack pointer and reset vector.
 *
 * @return 1 if the application is valid, 0 otherwise.
 */
uint8_t Boot_IsApplicationValid(void)
{
    uint32_t* pApplicationStack = (uint32_t*)APPLICATION_START_ADDRESS;
    uint32_t* pApplicationResetVector = pApplicationStack + 1;

    // Check if stack pointer and reset vector are valid
    if (*pApplicationStack == MSP && *pApplicationResetVector != 0)
    {
        return 1;
    }
    else
    {
        return 0;
    }
}

/**
 * @brief Jumps to the application's reset handler.
 */
void Boot_JumpToApplication(void)
{
    uint32_t* pApplicationStack = (uint32_t*)APPLICATION_START_ADDRESS;
    uint32_t* pApplicationResetVector = pApplicationStack + 1;

    // Disable interrupts
    __asm volatile("CPSID I");

    // Set the stack pointer to the application's stack
    __asm volatile("MSR MSP, %0" : : "r"(*pApplicationStack));

    // Jump to the application's reset handler
    typedef void (*ApplicationResetHandler)(void);
    ApplicationResetHandler app_reset_handler = (ApplicationResetHandler)(*pApplicationResetVector);
    app_reset_handler();
}
