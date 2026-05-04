#ifndef APP_MAIN_H
#define APP_MAIN_H

#include "Std_Types.h"

void App_Init(void);
Std_ReturnType App_Run(void);
void App_ProcessCommands(void);
void App_HandleError(uint32_t error_code);

#endif // APP_MAIN_H
