#ifndef BOOT_MCU_H
#define BOOT_MCU_H

#include "stm32f1xx_hal.h"

// Define missing symbols
#define FLASH_BASE_ADDRESS 0x08000000
#define APPLICATION_ENTRY_POINT (FLASH_BASE_ADDRESS + (FLASH_PAGE_SIZE * 4))
#define FLASH_CR_LOCK 0x00000001
#define FLASH_CR_PER 0x00000002
#define FLASH_CR_PG 0x00000004
#define FLASH_CR_STRT 0x00000040
#define FLASH_SR_BSY 0x00000001
#define FLASH_SR_EOP 0x00000020
#define FLASH_SR_PGERR 0x00000080

// Function prototypes
void Boot_Mcu_Init(void);
void Boot_Mcu_DeInit(void);
void Boot_Mcu_DisableInterrupts(void);
void Boot_Flash_Erase(uint32_t address, uint32_t length);
void Boot_Flash_Write(uint32_t address, const uint8_t* data, uint32_t length);
void Boot_Flash_Read(uint32_t address, uint8_t* data, uint32_t length);

#endif // BOOT_MCU_H
