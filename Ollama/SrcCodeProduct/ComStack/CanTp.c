#include "CanTp.h"
#include "ComStack_Types.h"

#define CAN_TP_MAX_SEGMENTS 10
#define CAN_TP_BUFFER_SIZE 1024

typedef enum {
    CAN_TP_STATE_IDLE,
    CAN_TP_STATE_WAITING_FOR_CTS,
    CAN_TP_STATE_RECEIVING_DATA
} CanTpState;

typedef struct {
    uint8_t buffer[CAN_TP_BUFFER_SIZE];
    uint32_t bufferSize;
    uint32_t readIndex;
} CanTpBuffer;

static CanTpState state = CAN_TP_STATE_IDLE;
static CanTpBuffer transmitBuffer;
static CanTpBuffer receiveBuffer;
static uint16_t nextFrameId = 0;
static CanTp_SendFrameFunc sendFrameFunc = NULL;
static CanTp_TxConfirmationFunc txConfirmationFunc = NULL;

void CanTp_Init(void) {
    // Initialize CAN TP
    state = CAN_TP_STATE_IDLE;
    transmitBuffer.bufferSize = 0;
    receiveBuffer.bufferSize = 0;
}

Std_ReturnType CanTp_Transmit(uint8_t TxPduId, PduInfoType *PduInfoPtr) {
    if (state != CAN_TP_STATE_IDLE) {
        return E_NOT_OK;
    }

    uint16_t dataSize = PduInfoPtr->SduDataLength;
    if (dataSize > CAN_TP_BUFFER_SIZE - 2) { // 2 bytes for header
        return E_NOT_OK; // Data too large to fit in buffer
    }

    transmitBuffer.bufferSize = 0;
    transmitBuffer.readIndex = 0;

    // Fill the transmit buffer with the header and data
    transmitBuffer.buffer[transmitBuffer.bufferSize++] = (dataSize >> 8) & 0xFF; // Length MSB
    transmitBuffer.buffer[transmitBuffer.bufferSize++] = dataSize & 0xFF;        // Length LSB

    for (uint16_t i = 0; i < dataSize; i++) {
        transmitBuffer.buffer[transmitBuffer.bufferSize++] = PduInfoPtr->SduDataPtr[i];
    }

    state = CAN_TP_STATE_WAITING_FOR_CTS;

    // Simulate sending the header frame
    CanTp_SendFrame(nextFrameId++, &transmitBuffer, 2);

    return E_OK;
}

void CanTp_RxIndication(uint8_t RxPduId, PduInfoType *PduInfoPtr) {
    uint16_t dataSize = (PduInfoPtr->SduDataPtr[0] << 8) | PduInfoPtr->SduDataPtr[1];
    if (dataSize > CAN_TP_BUFFER_SIZE - 2) { // 2 bytes for header
        return; // Invalid data size
    }

    uint16_t segmentId = nextFrameId++;

    switch (PduInfoPtr->SduDataPtr[0]) {
        case 0x13: // FF (First Frame)
            state = CAN_TP_STATE_RECEIVING_DATA;
            receiveBuffer.bufferSize = dataSize;
            receiveBuffer.readIndex = 2; // Start reading after header
            for (uint16_t i = 2; i < PduInfoPtr->SduDataLength; i++) {
                receiveBuffer.buffer[receiveBuffer.readIndex++] = PduInfoPtr->SduDataPtr[i];
            }
            break;
        case 0x15: // CF (Consecutive Frame)
            if (segmentId != nextFrameId - 1) {
                return; // Out of order
            }
            for (uint16_t i = 2; i < PduInfoPtr->SduDataLength; i++) {
                receiveBuffer.buffer[receiveBuffer.readIndex++] = PduInfoPtr->SduDataPtr[i];
            }
            break;
        case 0x17: // SF (Single Frame)
            state = CAN_TP_STATE_IDLE;
            for (uint16_t i = 2; i < PduInfoPtr->SduDataLength; i++) {
                receiveBuffer.buffer[receiveBuffer.readIndex++] = PduInfoPtr->SduDataPtr[i];
            }
            break;
        default:
            return; // Unknown frame type
    }

    if (state == CAN_TP_STATE_RECEIVING_DATA) {
        if (segmentId + 1 < dataSize / 7U) {
            CanTp_SendFrame(nextFrameId++, &receiveBuffer, PduInfoPtr->SduDataLength);
        } else {
            state = CAN_TP_STATE_IDLE;
            CanTp_TxConfirmation(RxPduId, E_OK);
        }
    }
}

void CanTp_MainFunction(void) {
    // Periodic task for managing flow control and timeouts
    static uint32_t tickCounter = 0;

    if (++tickCounter >= 10) { // Assuming 10ms interval
        tickCounter = 0;
        switch (state) {
            case CAN_TP_STATE_WAITING_FOR_CTS:
                CanTp_SendFrame(nextFrameId++, &transmitBuffer, transmitBuffer.bufferSize);
                break;
            default:
                break;
        }
    }
}

void CanTp_SetSendFrameCallback(CanTp_SendFrameFunc func) {
    sendFrameFunc = func;
}

void CanTp_SetTxConfirmationCallback(CanTp_TxConfirmationFunc func) {
    txConfirmationFunc = func;
}

void CanTp_SendFrame(uint16_t frameId, CanTpBuffer *buffer, uint16_t length) {
    if (sendFrameFunc != NULL) {
        sendFrameFunc(frameId, buffer->buffer, length);
    } else {
        // Handle the case where no callback is set
    }
}

void CanTp_TxConfirmation(uint8_t TxPduId, Std_ReturnType Result) {
    if (txConfirmationFunc != NULL) {
        txConfirmationFunc(TxPduId, Result);
    } else {
        // Handle the case where no callback is set
    }
}
