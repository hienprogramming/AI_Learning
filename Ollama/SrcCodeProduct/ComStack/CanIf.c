#include "CanIf.h"
#include "stm32f4xx_can.h"

// Static buffers for received data
#define MAX_RX_DATA_SIZE 8
static uint8_t RxData[MAX_RX_DATA_SIZE];
static CanRxMsgTypeDef RxMessage;

// Callback functions pointers
typedef struct {
    CanTxPduIdType TxPduId;
    CanIf_TxConfirmationCallbackType Callback;
} TxConfirmationCallbackEntry;

typedef struct {
    uint16_t RxHrhId;
    CanIf_RxIndicationCallbackType Callback;
} RxIndicationCallbackEntry;

static TxConfirmationCallbackEntry TxConfirmationCallbacks[MAX_TX_PDUS] = {0};
static RxIndicationCallbackEntry RxIndicationCallbacks[MAX_RX_HRHs] = {0};

// PDU ID to CAN ID mapping
typedef struct {
    CanTxPduIdType PduId;
    uint32_t CanId;
} PduToCanIdMappingType;

static const PduToCanIdMappingType PduToCanIdMap[] = {
    {CAN_TX_PDU_1, 0x100},
    {CAN_TX_PDU_2, 0x200},
    {CAN_TX_PDU_3, 0x300},
    {CAN_TX_PDU_4, 0x400}
};

// CAN handle
static Can_TypeDef* hCan = CAN1;

void CanIf_Init(void) {
    // Initialize CAN peripheral (example configuration)
    RCC_APB1PeriphClockCmd(RCC_APB1Periph_CAN1, ENABLE);
    CAN_InitTypeDef CAN_InitStructure;
    CAN_InitStructure.CAN_Mode = CAN_Mode_Normal;
    CAN_InitStructure.CAN_SJW = CAN_SJW_1tq;
    CAN_InitStructure.CAN_BS1 = CAN_BS1_13tq;
    CAN_InitStructure.CAN_BS2 = CAN_BS2_2tq;
    CAN_InitStructure.CAN_Prescaler = 16; // Example prescaler
    CAN_Init(hCan, &CAN_InitStructure);

    // Enable CAN RX FIFO0 interrupts
    CAN_ITConfig(hCan, CAN_IT_FMP0, ENABLE);
    NVIC_EnableIRQ(CAN1_RX0_IRQn);
}

Std_ReturnType CanIf_Transmit(CanTxPduIdType TxPduId, const PduInfoType* PduInfoPtr) {
    for (uint8_t i = 0; i < sizeof(PduToCanIdMap) / sizeof(PduToCanIdMappingType); i++) {
        if (PduToCanIdMap[i].PduId == TxPduId) {
            CAN_TxMsgTypeDef TxMessage;
            TxMessage.StdId = PduToCanIdMap[i].CanId;
            TxMessage.ExtId = 0;
            TxMessage.RTR = CAN_RTR_Data;
            TxMessage.IDE = CAN_ID_STD;
            TxMessage.DLC = PduInfoPtr->SduLength;
            memcpy(TxMessage.Data, PduInfoPtr->SduDataPtr, TxMessage.DLC);

            CAN_Transmit(hCan, &TxMessage);
            return E_OK;
        }
    }

    return E_NOT_OK;
}

Std_ReturnType CanIf_SetTxConfirmationCallback(CanTxPduIdType TxPduId, CanIf_TxConfirmationCallbackType Callback) {
    for (uint8_t i = 0; i < MAX_TX_PDUS; i++) {
        if (TxConfirmationCallbacks[i].TxPduId == TxPduId) {
            TxConfirmationCallbacks[i].Callback = Callback;
            return E_OK;
        }
    }

    return E_NOT_OK;
}

Std_ReturnType CanIf_SetRxIndicationCallback(uint16_t RxHrhId, CanIf_RxIndicationCallbackType Callback) {
    for (uint8_t i = 0; i < MAX_RX_HRHs; i++) {
        if (RxIndicationCallbacks[i].RxHrhId == RxHrhId) {
            RxIndicationCallbacks[i].Callback = Callback;
            return E_OK;
        }
    }

    return E_NOT_OK;
}

void CAN1_RX0_IRQHandler(void) {
    if (CAN_GetITStatus(CAN1, CAN_IT_FMP0) != RESET) {
        uint8_t messageCount = CAN_MessagePending(CAN1, CAN_FIFO0);
        for (uint8_t i = 0; i < messageCount; i++) {
            CAN_Receive(hCan, CAN_FIFO0, &RxMessage);

            if (RxIndicationCallbacks[RxMessage.StdId / 4].Callback != NULL) {
                RxIndicationCallbacks[RxMessage.StdId / 4].Callback(RxHrhId, RxMessage.StdId, RxMessage.Data);
            }
        }

        // Clear the FIFO0 message pending bit
        CAN_ClearITPendingBit(CAN1, CAN_IT_FMP0);
    }
}

void CanIf_TxConfirmation(CanTxPduIdType TxPduId) {
    for (uint8_t i = 0; i < MAX_TX_PDUS; i++) {
        if (TxConfirmationCallbacks[i].TxPduId == TxPduId) {
            if (TxConfirmationCallbacks[i].Callback != NULL) {
                TxConfirmationCallbacks[i].Callback(TxPduId);
            }
            break;
        }
    }
}
