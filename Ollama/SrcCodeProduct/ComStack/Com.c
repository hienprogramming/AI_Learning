#include "Com.h"

// Static buffer for signal data
static Com_SignalDataType signalBuffer[COM_MAX_SIGNALS];

// Flag to indicate if the main function is currently running
static boolean txMainFunctionRunning = FALSE;
static boolean rxMainFunctionRunning = FALSE;

// Initialize COM module
Std_ReturnType Com_Init(void) {
    // Initialize all signals as not received
    for (uint8_t i = 0; i < COM_MAX_SIGNALS; i++) {
        signalBuffer[i].isReceived = FALSE;
    }

    return E_OK;
}

// Send signal
Std_ReturnType Com_SendSignal(Com_SignalIdType SignalId, const Com_SignalDataType* SignalDataPtr) {
    if (SignalId >= COM_MAX_SIGNALS) {
        return E_NOT_OK;
    }

    // Check if the main function is already running
    if (txMainFunctionRunning) {
        return E_BUSY;
    }

    // Copy the data to the buffer
    memcpy(&signalBuffer[SignalId], SignalDataPtr, sizeof(Com_SignalDataType));
    signalBuffer[SignalId].isReceived = FALSE;  // Reset received flag

    // Trigger the transmission main function
    txMainFunctionRunning = TRUE;

    return E_OK;
}

// Receive signal
Std_ReturnType Com_ReceiveSignal(Com_SignalIdType SignalId, Com_SignalDataType* SignalDataPtr) {
    if (SignalId >= COM_MAX_SIGNALS) {
        return E_NOT_OK;
    }

    // Check if the main function is already running
    if (rxMainFunctionRunning) {
        return E_BUSY;
    }

    // Check if the signal has been received
    if (!signalBuffer[SignalId].isReceived) {
        return E_NOT_OK;
    }

    // Copy the data from the buffer
    memcpy(SignalDataPtr, &signalBuffer[SignalId], sizeof(Com_SignalDataType));
    signalBuffer[SignalId].isReceived = FALSE;  // Reset received flag

    return E_OK;
}

// Main function for transmission (10ms)
void Com_MainFunctionTx(void) {
    if (!txMainFunctionRunning) {
        return;
    }

    txMainFunctionRunning = FALSE;

    // Implement signal filtering and triggering logic here
    // For example, you can trigger the transmission based on certain conditions

    // Example: Trigger transmission for Signal_ID_0
    if (signalBuffer[SIGNAL_ID_0].isReceived) {
        // Transmit Signal_ID_0 data
        // (Implementation depends on your hardware)
    }
}

// Main function for reception (10ms)
void Com_MainFunctionRx(void) {
    if (!rxMainFunctionRunning) {
        return;
    }

    rxMainFunctionRunning = FALSE;

    // Implement signal filtering and triggering logic here
    // For example, you can trigger the reception based on certain conditions

    // Example: Trigger reception for Signal_ID_0
    if (/* Some condition */) {
        // Receive data for Signal_ID_0
        Com_SignalDataType receivedData;
        // Populate receivedData with received signal data
        Com_SendSignal(SIGNAL_ID_0, &receivedData);
    }
}
