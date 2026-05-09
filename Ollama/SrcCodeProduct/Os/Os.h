#ifndef OS_H
#define OS_H

#include "Os_Cfg.h"

void Os_Init(void);
void Os_Start(void);
void Os_Tick(void);
Std_ReturnType Os_ActivateTask(Os_TaskIdType taskId);
Os_TaskStateType Os_GetTaskState(Os_TaskIdType taskId);
uint32 Os_GetTickCount(void);

#endif /* OS_H */
