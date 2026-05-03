#include "PduR.h"
#include "CanIf.h" // Assuming CanIf is available for STM32F4
#include <stdint.h>
#include <stdbool.h>

// Static routing table for COM <-> CanIf
typedef struct {
    uint8  (*TransmitFunc)(uint8* payload, uint16 length);
    void   (*RxIndicationFunc)(const PduInfoType* PduInfoPtr);
} PduR_RoutingEntry;

static PduR_RoutingEntry routingTable[MAX_PDUS] = {0};

// Initialize the PDU Router
void PduR_Init(void) {
    // Example routing table setup
    routingTable[PDU1_ID].TransmitFunc = CanIf_Transmit;
    routingTable[PDU2_ID].TransmitFunc = CanIf_Transmit;
    routingTable[PDU3_ID].TransmitFunc = CanIf_Transmit;
    routingTable[PDU4_ID].TransmitFunc = CanIf_Transmit;

    routingTable[PDU1_ID].RxIndicationFunc = CanIf_RxIndication;
    routingTable[PDU2_ID].RxIndicationFunc = CanIf_RxIndication;
    routingTable[PDU3_ID].RxIndicationFunc = CanIf_RxIndication;
    routingTable[PDU4_ID].RxIndicationFunc = CanIf_RxIndication;
}

// Transmit a PDU down
Std_ReturnType PduR_Transmit(PduIdType PduId, const PduInfoType* PduInfoPtr) {
    if (PduId >= MAX_PDUS || routingTable[PduId].TransmitFunc == NULL) {
        return E_NOT_OK;
    }

    // Call the transmit function from the routing table
    return routingTable[PduId].TransmitFunc(PduInfoPtr->payload, PduInfoPtr->length);
}

// Indicate PDU reception
Std_ReturnType PduR_RxIndication(PduIdType PduId, const PduInfoType* PduInfoPtr) {
    if (PduId >= MAX_PDUS || routingTable[PduId].RxIndicationFunc == NULL) {
        return E_NOT_OK;
    }

    // Call the receive indication function from the routing table
    routingTable[PduId].RxIndicationFunc(PduInfoPtr);
    return E_OK;
}

// Confirm transmission
Std_ReturnType PduR_TxConfirmation(PduIdType PduId) {
    if (PduId >= MAX_PDUS || routingTable[PduId].TransmitFunc == NULL) {
        return E_NOT_OK;
    }

    // Assuming CanIf_Transmit returns a boolean indicating success or failure
    Std_ReturnType result = CanIf_TransmitConfirmation();
    if (result != E_OK) {
        return result; // Propagate any errors
    }
    return E_OK;
}
