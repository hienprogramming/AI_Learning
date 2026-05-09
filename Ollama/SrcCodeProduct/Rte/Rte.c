#include "Rte.h"

#include "../App/App_Main.h"
#include "../ComStack/Com.h"

void App_KeyManager_Init(void);
void App_Security_Init(void);

static Rte_ModeType Rte_Mode = RTE_MODE_STARTUP;
static uint32 Rte_AppStatus = 0u;

void Rte_Init(void)
{
    Rte_Mode = RTE_MODE_STARTUP;
    Rte_AppStatus = 0u;
}

void Rte_Start(void)
{
    Rte_Mode = RTE_MODE_RUN;
}

void Rte_Stop(void)
{
    Rte_Mode = RTE_MODE_SHUTDOWN;
}

Rte_ModeType Rte_GetMode(void)
{
    return Rte_Mode;
}

Std_ReturnType Rte_Write_KeyRequest(const uint8 *data, Rte_LengthType length)
{
    if ((data == NULL_PTR) || (length == 0u)) {
        return E_NOT_OK;
    }

    return Com_SendSignal(RTE_SIGNAL_KEY_REQUEST, data, length);
}

Std_ReturnType Rte_Read_KeyResponse(uint8 *data, Rte_LengthType *length)
{
    if ((data == NULL_PTR) || (length == NULL_PTR)) {
        return E_NOT_OK;
    }

    return Com_ReceiveSignal(RTE_SIGNAL_KEY_RESPONSE, data, length);
}

Std_ReturnType Rte_Write_AppStatus(uint32 status)
{
    Rte_AppStatus = status;
    return Com_SendSignal(RTE_SIGNAL_APP_STATUS, &Rte_AppStatus, (Rte_LengthType)sizeof(Rte_AppStatus));
}

Std_ReturnType Rte_Read_AppStatus(uint32 *status)
{
    if (status == NULL_PTR) {
        return E_NOT_OK;
    }

    *status = Rte_AppStatus;
    return E_OK;
}

void Rte_Runnable_App_Init(void)
{
    Rte_Init();
    App_Init();
    App_KeyManager_Init();
    App_Security_Init();
    Rte_Start();
}

void Rte_Runnable_App_10ms(void)
{
    if (Rte_Mode != RTE_MODE_RUN) {
        return;
    }

    Com_MainFunctionRx();
    App_ProcessCommands();
    Com_MainFunctionTx();
}

void Rte_Runnable_App_100ms(void)
{
    if (Rte_Mode != RTE_MODE_RUN) {
        return;
    }

    (void)Rte_Write_AppStatus(0xA5000001u);
}

void Rte_Runnable_Background(void)
{
    if (Rte_Mode == RTE_MODE_SHUTDOWN) {
        return;
    }
}
