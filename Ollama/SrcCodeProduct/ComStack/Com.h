#ifndef COM_H
#define COM_H

#include "ComStack_Types.h"

// Number of signals supported
#define MAX_SIGNALS 8

typedef struct {
    uint16_t SignalId;
    void* SignalDataPtr;
} ComSignal;

void Com_Init(void);
Std_ReturnType Com_SendSignal(uint16_t SignalId, const void* SignalDataPtr, uint16_t SignalSize);
Std_ReturnType Com_ReceiveSignal(uint16_t SignalId, void* SignalDataPtr, uint16_t* ReceivedSize);
void Com_MainFunctionTx(void);
void Com_MainFunctionRx(void);

#endif // COM_H
