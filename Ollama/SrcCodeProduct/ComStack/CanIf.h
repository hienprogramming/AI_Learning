#ifndef CANIF_H_
#define CANIF_H_

#include "ComStack_Types.h"

// Define PDU IDs and corresponding CAN IDs
typedef enum {
    CAN_TX_PDU_1 = 0,
    CAN_TX_PDU_2,
    CAN_TX_PDU_3,
    CAN_TX_PDU_4,
    NUM_CAN_TX_PDUS
} CanTxPduIdType;

#define CAN_ID_1 0x100
#define CAN_ID_2 0x200
#define CAN_ID_3 0x300
#define CAN_ID_4 0x400

// Function prototypes
Std_ReturnType CanIf_Init(void);
Std_ReturnType CanIf_Transmit(CanTxPduIdType TxPduId, PduInfoType* PduInfoPtr);
void CanIf_RxIndication(uint32 HrhId, uint16 CanId, const uint8* DataPtr);
void CanIf_TxConfirmation(CanTxPduIdType TxPduId);

#endif /* CANIF_H_ */
