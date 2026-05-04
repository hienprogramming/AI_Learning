#include "Boot_Mcu.h"
#include "stm32f10x.h"

// Constants for flash operations
#define FLASH_PAGE_SIZE 1024
#define FLASH_SECTOR_SIZE (FLASH_PAGE_SIZE * 8)
#define FLASH_START_ADDRESS 0x08000000

// Function to initialize MCU resources needed by the bootloader
void Boot_Mcu_Init(void) {
    // Enable clock for GPIO and AFIO
    RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOA | RCC_APB2Periph_AFIO, ENABLE);
    
    // Disable all interrupts to ensure a clean state
    __disable_irq();
}

// Function to deinitialize resources before jumping to application
void Boot_Mcu_DeInit(void) {
    // Enable clock for GPIO and AFIO
    RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOA | RCC_APB2Periph_AFIO, ENABLE);
    
    // Re-enable all interrupts after the bootloader has completed its task
    __enable_irq();
}

// Function to disable interrupts safely
void Boot_Mcu_DisableInterrupts(void) {
    __disable_irq();
}

// Function to erase flash pages/sectors
void Boot_Flash_Erase(uint32_t address, uint32_t length) {
    FLASH_Unlock();
    
    for (uint32_t page_address = address; page_address < address + length; page_address += FLASH_PAGE_SIZE) {
        FLASH_EraseInitTypeDef eraseInitStruct;
        eraseInitStruct.TypeErase = FLASH_TYPEERASE_PAGES;
        eraseInitStruct.PageAddress = page_address;
        eraseInitStruct.NbPages = 1;
        
        uint32_t sectorError = 0;
        if (FLASH_Erase(&eraseInitStruct, &sectorError) != FLASH_COMPLETE) {
            // Handle error
            while (1);
        }
    }
    
    FLASH_Lock();
}

// Function to write firmware bytes to flash
void Boot_Flash_Write(uint32_t address, const uint8_t* data, uint32_t length) {
    if ((address & 0x7) != 0) {
        // Address must be aligned to a word boundary (4 bytes)
        while ((length > 0) && ((address & 0x7) != 0)) {
            *(__IO uint8_t*) address = *data;
            address++;
            data++;
            length--;
        }
    }

    if (length >= 4) {
        uint32_t* word_ptr = (__IO uint32_t*) address;
        while (length >= 4) {
            *word_ptr++ = *((uint32_t*) data);
            data += 4;
            length -= 4;
        }
    }

    if ((length & 0x3) != 0) {
        // Handle remaining bytes
        uint32_t word = *(__IO uint32_t*) (address - 4);
        while (length > 0) {
            word >>= 8;
            *(__IO uint8_t*) address = *data;
            data++;
            length--;
            address++;
        }
        *word_ptr = word;
    }

    FLASH_Unlock();
    
    for (uint32_t write_address = address; write_address < address + length; write_address += 4) {
        __IO uint32_t* word_ptr = (__IO uint32_t*) write_address;
        while (*word_ptr != *((uint32_t*) data)) {
            *word_ptr = *((uint32_t*) data);
        }
    }
    
    FLASH_Lock();
}

// Function to read flash bytes
void Boot_Flash_Read(uint32_t address, uint8_t* data, uint32_t length) {
    while (length > 0) {
        *data++ = *(__IO uint8_t*) address++;
        length--;
    }
}
