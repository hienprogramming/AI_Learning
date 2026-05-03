#include "Com.h"
#include "ComStack_Types.h"

// Static buffers for signals
static uint8_t signalBuffers[MAX_SIGNALS][MAX_SIGNAL_SIZE];
static ComSignal signalList[MAX_SIGNALS];

// Initialize COM module
void Com_Init(void) {
    // Initialize all signals to invalid state
    for (uint8_t i = 0; i < MAX_SIGNALS; i++) {
        signalList[i].SignalId = INVALID_SIGNAL_ID;
        signalList[i].SignalDataPtr = NULL;
    }
}

// Send signal
Std_ReturnType Com_SendSignal(uint16_t SignalId, const void* SignalDataPtr, uint16_t SignalSize) {
    for (uint8_t i = 0; i < MAX_SIGNALS; i++) {
        if (signalList[i].SignalId == SignalId) {
            // Check if the signal size is within the buffer limits
            if (SignalSize > MAX_SIGNAL_SIZE) {
                return E_NOT_OK;
            }
            // Copy data to buffer
            memcpy(signalBuffers[i], SignalDataPtr, SignalSize);
            return E_OK;
        }
    }
    return E_NOT_OK;
}

// Receive signal
Std_ReturnType Com_ReceiveSignal(uint16_t SignalId, void* SignalDataPtr, uint16_t* ReceivedSize) {
    for (uint8_t i = 0; i < MAX_SIGNALS; i++) {
        if (signalList[i].SignalId == SignalId) {
            // Check if the signal size is within the buffer limits
            if (*ReceivedSize > MAX_SIGNAL_SIZE) {
                return E_NOT_OK;
            }
            // Copy data from buffer
            memcpy(SignalDataPtr, signalBuffers[i], *ReceivedSize);
            return E_OK;
        }
    }
    return E_NOT_OK;
}

// Main function for transmission (10ms)
void Com_MainFunctionTx(void) {
    // Implement periodic or event-driven transmission logic here
    // For example, send signals based on a timer or an event flag
}

// Main function for reception (10ms)
void Com_MainFunctionRx(void) {
    // Implement reception logic here
    // For example, receive data and update signal buffers
}
