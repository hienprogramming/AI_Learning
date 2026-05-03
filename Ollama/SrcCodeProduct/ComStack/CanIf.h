#ifndef CANIF_H_
#define CANIF_H_

#include "ComStack_Types.h"

// PDU IDs for CAN frames
typedef enum {
    CAN_TX_PDU_1,
    CAN_TX_PDU_2,
    CAN_TX_PDU_3,
    CAN_TX_PDU_4,
} CanTxPduIdType;

// Callback function types
typedef void (*CanIf_TxConfirmationCallbackType)(CanTxPduIdType TxPduId);
typedef void (*CanIf_RxIndicationCallbackType)(uint16_t RxHrhId, uint32_t CanId, const uint8_t* DataPtr);

// Initialize CAN Interface
void CanIf_Init(void);

// Transmit a CAN frame
Std_ReturnType CanIf_Transmit(CanTxPduIdType TxPduId, const PduInfoType* PduInfoPtr);

// Set TX confirmation callback
Std_ReturnType CanIf_SetTxConfirmationCallback(CanTxPduIdType TxPduId, CanIf_TxConfirmationCallbackType Callback);

// Set RX indication callback
Std_ReturnType CanIf_SetRxIndicationCallback(uint16_t RxHrhId, CanIf_RxIndicationCallbackType Callback);

#endif /* CANIF_H_ */
