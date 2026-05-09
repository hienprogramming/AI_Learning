#include "App_ComInterface.h"
#include "ComStack_Types.h"  // Include ComStack types if needed
#include "CanIf.h"

// Static buffer for sending key request
static uint8_t keyRequestBuffer[2];

// Initialize communication layer
void App_ComInterface_Init(void) {
    // Initialize CAN interface (Assuming CanIf is already initialized elsewhere)
    CanIf_Init();
}

// Send key request via CAN
void App_ComInterface_SendKeyRequest(uint8_t request) {
    // Fill the buffer with the key request
    keyRequestBuffer[0] = 0x5A;  // Example ID for key request message
    keyRequestBuffer[1] = request;

    // Send the CAN frame using CanIf
    CanIf_Transmit(CAN_TX_ID_KEY_REQUEST, keyRequestBuffer, sizeof(keyRequestBuffer));
}

// Receive key data
uint8_t App_ComInterface_ReceiveKeyData(uint8_t *buffer, uint16_t length) {
    if (length > sizeof(keyRequestBuffer)) {
        return 0;  // Error: Buffer too small
    }
    memcpy(buffer, keyRequestBuffer, length);
    return length;
}

// Process incoming CAN messages
void App_ComInterface_HandleMessage(const CAN_RxHeaderTypeDef *RxHeader, const uint8_t *RxData) {
    if (RxHeader->ID == CAN_RX_ID_KEY_REQUEST) {
        // Handle the received key request message
        uint8_t receivedRequest = RxData[1];
        // Process the received request (e.g., store it in a buffer or trigger an event)
    }
}
