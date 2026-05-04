#ifndef __BOOT_MCU_H__
#define __BOOT_MCU_H__

#include "stm32f10x.h"

void Boot_Mcu_Init(void);
void Boot_Mcu_DeInit(void);
void Boot_Mcu_DisableInterrupts(void);

#endif /* __BOOT_MCU_H__ */
