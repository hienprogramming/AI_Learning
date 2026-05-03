#ifndef PDUR_H
#define PDUR_H

#include "ComStack_Types.h"

// Define the maximum number of PDUs
#define MAX_PDUS 4

// Define PDU IDs
typedef enum {
    PDU1_ID = 0,
    PDU2_ID = 1,
    PDU3_ID = 2,
    PDU4_ID = 3
} PduIdType;

// Define the PDU information structure
typedef struct {
    uint8* payload;
    uint16 length;
} PduInfoType;

// Initialize the PDU Router
void PduR_Init(void);

// Transmit a PDU down
Std_ReturnType PduR_Transmit(PduIdType PduId, const PduInfoType* PduInfoPtr);

// Indicate PDU reception
Std_ReturnType PduR_RxIndication(PduIdType PduId, const PduInfoType* PduInfoPtr);

// Confirm transmission
Std_ReturnType PduR_TxConfirmation(PduIdType PduId);

#endif /* PDUR_H */
