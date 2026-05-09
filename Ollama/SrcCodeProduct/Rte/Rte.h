#ifndef RTE_H
#define RTE_H

#include "Rte_Cfg.h"

void Rte_Init(void);
void Rte_Start(void);
void Rte_Stop(void);
Rte_ModeType Rte_GetMode(void);

Std_ReturnType Rte_Write_KeyRequest(const uint8 *data, Rte_LengthType length);
Std_ReturnType Rte_Read_KeyResponse(uint8 *data, Rte_LengthType *length);
Std_ReturnType Rte_Write_AppStatus(uint32 status);
Std_ReturnType Rte_Read_AppStatus(uint32 *status);

void Rte_Runnable_App_Init(void);
void Rte_Runnable_App_10ms(void);
void Rte_Runnable_App_100ms(void);
void Rte_Runnable_Background(void);

#endif /* RTE_H */
