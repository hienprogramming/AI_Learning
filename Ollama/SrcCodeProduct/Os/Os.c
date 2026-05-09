#include "Os.h"

#include "../Rte/Rte.h"

const Os_TaskConfigType Os_TaskConfig[OS_TASK_COUNT] = {
    {OS_TASK_INIT, "OsTask_Init", 1u, 0u, TRUE},
    {OS_TASK_APP_10MS, "OsTask_App_10ms", 3u, 10u, TRUE},
    {OS_TASK_APP_100MS, "OsTask_App_100ms", 5u, 100u, TRUE},
    {OS_TASK_BACKGROUND, "OsTask_Background", 10u, 0u, TRUE}
};

static Os_TaskStateType Os_TaskState[OS_TASK_COUNT];
static uint32 Os_TickCount;

static void Os_DispatchTask(Os_TaskIdType taskId)
{
    Os_TaskState[taskId] = OS_TASK_RUNNING;

    switch (taskId) {
    case OS_TASK_INIT:
        Rte_Runnable_App_Init();
        break;
    case OS_TASK_APP_10MS:
        Rte_Runnable_App_10ms();
        break;
    case OS_TASK_APP_100MS:
        Rte_Runnable_App_100ms();
        break;
    case OS_TASK_BACKGROUND:
        Rte_Runnable_Background();
        break;
    default:
        break;
    }

    Os_TaskState[taskId] = OS_TASK_SUSPENDED;
}

void Os_Init(void)
{
    uint8 taskIndex;

    Os_TickCount = 0u;
    for (taskIndex = 0u; taskIndex < (uint8)OS_TASK_COUNT; taskIndex++) {
        Os_TaskState[taskIndex] = OS_TASK_SUSPENDED;
    }
}

void Os_Start(void)
{
    if (Os_TaskConfig[OS_TASK_INIT].autostart == TRUE) {
        (void)Os_ActivateTask(OS_TASK_INIT);
    }
}

void Os_Tick(void)
{
    Os_TickCount++;

    if ((Os_TickCount % Os_TaskConfig[OS_TASK_APP_10MS].periodMs) == 0u) {
        (void)Os_ActivateTask(OS_TASK_APP_10MS);
    }

    if ((Os_TickCount % Os_TaskConfig[OS_TASK_APP_100MS].periodMs) == 0u) {
        (void)Os_ActivateTask(OS_TASK_APP_100MS);
    }
}

Std_ReturnType Os_ActivateTask(Os_TaskIdType taskId)
{
    if (taskId >= OS_TASK_COUNT) {
        return E_NOT_OK;
    }

    Os_TaskState[taskId] = OS_TASK_READY;
    Os_DispatchTask(taskId);
    return E_OK;
}

Os_TaskStateType Os_GetTaskState(Os_TaskIdType taskId)
{
    if (taskId >= OS_TASK_COUNT) {
        return OS_TASK_SUSPENDED;
    }

    return Os_TaskState[taskId];
}

uint32 Os_GetTickCount(void)
{
    return Os_TickCount;
}
