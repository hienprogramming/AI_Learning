#ifndef PDU_R_H
#define PDU_R_H

#include "ComStack_Types.h"

// Define maximum number of PDUs
#define MAX_PDUS 4

typedef enum {
    COM_PDU,
    CANIF_PDU
} PduType;

typedef struct {
    uint8* data;
    uint16 length;
    uint32 id;
} PduInfoType;

// Function prototypes
void PduR_Init(void);
Std_ReturnType PduR_Transmit(PduIdType PduId, const PduInfoType* PduInfoPtr);
Std_ReturnType PduR_RxIndication(PduIdType PduId, const PduInfoType* PduInfoPtr);
Std_ReturnType PduR_TxConfirmation(PduIdType PduId);

#endif // PDU_R_H
