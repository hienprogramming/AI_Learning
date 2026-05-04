#include "stm32f10x.h"
#include "Boot_Mcu.h"

#define FLASH_PAGE_SIZE 2048 // 2KB

// Function prototypes
void Boot_Flash_Erase(uint32_t address, uint32_t length);
void Boot_Flash_Write(uint32_t address, const uint8_t* data, uint32_t length);
void Boot_Flash_Read(uint32_t address, uint8_t* data, uint32_t length);

// Static buffer for flash operations
uint8_t FlashBuffer[FLASH_PAGE_SIZE];

void Boot_Mcu_Init(void) {
    // Enable the FLASH control clock
    RCC_APB1PeriphClockCmd(RCC_APB1Periph_PWR | RCC_APB1Periph_BKP, ENABLE);
    PWR_BackupAccessCmd(ENABLE);

    // Unlock the FLASH Program Erase Controller
    FLASH_Unlock();
}

void Boot_Mcu_DeInit(void) {
    // Lock the FLASH Program Erase Controller
    FLASH_Lock();

    // Disable the FLASH control clock
    RCC_APB1PeriphClockCmd(RCC_APB1Periph_PWR | RCC_APB1Periph_BKP, DISABLE);
    PWR_BackupAccessCmd(DISABLE);
}

void Boot_Mcu_DisableInterrupts(void) {
    __disable_irq();
}

void Boot_Flash_Erase(uint32_t address, uint32_t length) {
    // Calculate the number of pages to erase
    uint16_t num_pages = (length + FLASH_PAGE_SIZE - 1) / FLASH_PAGE_SIZE;

    for (uint16_t i = 0; i < num_pages; i++) {
        // Erase a page
        FLASH_EraseInitTypeDef EraseInitStruct;
        EraseInitStruct.TypeErase = FLASH_TypeErase_Page;
        EraseInitStruct.PageAddress = address + i * FLASH_PAGE_SIZE;
        EraseInitStruct.NbPages = 1;

        if (FLASH_Erase(&EraseInitStruct, NULL) != FLASH_ProgramError) {
            // Wait for the erase operation to complete
            while (FLASH_GetFlagStatus(FLASH_FLAG_BSY) != RESET);
        }
    }
}

void Boot_Flash_Write(uint32_t address, const uint8_t* data, uint32_t length) {
    // Calculate the number of bytes to write
    uint16_t num_bytes = (length + 3) / 4;

    for (uint16_t i = 0; i < num_bytes; i++) {
        // Copy data into buffer
        FlashBuffer[i * 4] = data[i * 4];
        if (i * 4 + 1 < length) FlashBuffer[i * 4 + 1] = data[i * 4 + 1];
        else FlashBuffer[i * 4 + 1] = 0xFF;
        if (i * 4 + 2 < length) FlashBuffer[i * 4 + 2] = data[i * 4 + 2];
        else FlashBuffer[i * 4 + 2] = 0xFF;
        if (i * 4 + 3 < length) FlashBuffer[i * 4 + 3] = data[i * 4 + 3];
        else FlashBuffer[i * 4 + 3] = 0xFF;

        // Program the buffer
        if (FLASH_Program(FLASH_ProgramWord, address + i * 4, *(uint32_t*)FlashBuffer) != FLASH_ProgramError) {
            // Wait for the program operation to complete
            while (FLASH_GetFlagStatus(FLASH_FLAG_BSY) != RESET);
        }
    }
}

void Boot_Flash_Read(uint32_t address, uint8_t* data, uint32_t length) {
    memcpy(data, (uint8_t*)address, length);
}
