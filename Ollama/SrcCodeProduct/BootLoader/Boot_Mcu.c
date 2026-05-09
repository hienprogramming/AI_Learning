#include "Boot_Mcu.h"

#define FLASH_PAGE_SIZE 0x1000 // 4KB per page on STM32F103C8T6

static uint32_t flash_base_address = FLASH_BASE_ADDRESS; // Start of user Flash memory
static uint32_t application_entry_point = APPLICATION_ENTRY_POINT; // Typically, the first page after bootloader

void Boot_Mcu_Init(void) {
    // Initialize the system clock and peripherals if needed
    HAL_Init();
    SystemClock_Config();

    // Enable the Flash Control Register access
    FLASH->CR &= ~(FLASH_CR_LOCK);
}

void Boot_Mcu_DeInit(void) {
    // Disable the Flash Control Register access
    FLASH->CR |= FLASH_CR_LOCK;

    // Clear any pending interrupts
    __NVIC_ClearPendingIRQ(FLASH_IRQn);
}

void Boot_Mcu_DisableInterrupts(void) {
    // Disable all interrupts globally
    __disable_irq();
}

void Boot_Flash_Erase(uint32_t address, uint32_t length) {
    uint32_t page_size = FLASH_PAGE_SIZE;
    uint32_t num_pages = (length + page_size - 1) / page_size;

    for (uint32_t i = 0; i < num_pages; i++) {
        uint32_t page_address = address + i * page_size;

        // Clear the busy flag
        while ((FLASH->SR & FLASH_SR_BSY) != 0);

        // Set the address and start the page erase operation
        FLASH->AR = page_address;
        FLASH->CR |= (FLASH_CR_STRT | FLASH_CR_PER);
        while ((FLASH->SR & FLASH_SR_EOP) == 0);
        FLASH->SR |= FLASH_SR_EOP; // Clear EOP flag

        if ((FLASH->SR & FLASH_SR_PGERR) != 0) {
            // Page error occurred
            return;
        }
    }

    // Unlock the Flash to enable the flash control register access
    FLASH->CR &= ~(FLASH_CR_LOCK);
}

void Boot_Flash_Write(uint32_t address, const uint8_t* data, uint32_t length) {
    uint32_t page_size = FLASH_PAGE_SIZE;
    uint32_t num_pages = (length + page_size - 1) / page_size;

    for (uint32_t i = 0; i < num_pages; i++) {
        uint32_t page_address = address + i * page_size;
        const uint8_t* page_data = data + i * page_size;

        // Clear the busy flag
        while ((FLASH->SR & FLASH_SR_BSY) != 0);

        // Set the address and start the page erase operation
        FLASH->AR = page_address;
        FLASH->CR |= (FLASH_CR_STRT | FLASH_CR_PER);
        while ((FLASH->SR & FLASH_SR_EOP) == 0);
        FLASH->SR |= FLASH_SR_EOP; // Clear EOP flag

        if ((FLASH->SR & FLASH_SR_PGERR) != 0) {
            // Page error occurred
            return;
        }

        // Write the data to the page
        for (uint32_t j = 0; j < page_size; j++) {
            if (j < length - i * page_size) {
                uint32_t word_address = page_address + j * 4;
                *(volatile uint32_t*)word_address = *((uint32_t*)(page_data + j * 4));
            }
        }

        // Clear the busy flag
        while ((FLASH->SR & FLASH_SR_BSY) != 0);

        // Set the address and start the page program operation
        FLASH->AR = page_address;
        FLASH->CR |= (FLASH_CR_STRT | FLASH_CR_PG);
        while ((FLASH->SR & FLASH_SR_EOP) == 0);
        FLASH->SR |= FLASH_SR_EOP; // Clear EOP flag

        if ((FLASH->SR & FLASH_SR_PGERR) != 0) {
            // Programming error occurred
            return;
        }
    }

    // Unlock the Flash to enable the flash control register access
    FLASH->CR &= ~(FLASH_CR_LOCK);
}

void Boot_Flash_Read(uint32_t address, uint8_t* data, uint32_t length) {
    for (uint32_t i = 0; i < length; i++) {
        data[i] = *(volatile uint8_t*)(address + i);
    }
}
