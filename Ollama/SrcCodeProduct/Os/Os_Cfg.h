#ifndef OS_CFG_H
#define OS_CFG_H

#include "../Common/Std_Types.h"

#define OS_TICK_BASE_MS 1u

typedef enum {
    OS_TASK_INIT = 0u,
    OS_TASK_APP_10MS,
    OS_TASK_APP_100MS,
    OS_TASK_BACKGROUND,
    OS_TASK_COUNT
} Os_TaskIdType;

typedef enum {
    OS_TASK_SUSPENDED = 0u,
    OS_TASK_READY,
    OS_TASK_RUNNING
} Os_TaskStateType;

typedef struct {
    Os_TaskIdType id;
    const char *name;
    uint8 priority;
    uint16 periodMs;
    uint8 autostart;
} Os_TaskConfigType;

extern const Os_TaskConfigType Os_TaskConfig[OS_TASK_COUNT];

#endif /* OS_CFG_H */
