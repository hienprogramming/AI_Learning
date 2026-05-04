#include "App_ComInterface.h"
#include "CanIf.h"
#include "Com.h"

// Static buffer for key data received via CAN
static uint8_t keyDataBuffer[256];
static uint16_t keyDataLength;

// Flag to indicate if a key request is pending
static volatile bool keyRequestPending = false;
static KeyRequestType currentKeyRequest;

void App_ComInterface_Init(void) {
    // Initialize the Com module for message handling
    Com_Init();

    // Initialize the CanIf module for CAN frame transmission
    CanIf_Init();
}

void App_ComInterface_SendKeyRequest(KeyRequestType request) {
    // Set the key request type and flag
    currentKeyRequest = request;
    keyRequestPending = true;

    // Create a CAN message to send the key request
    CanIf_MtMsgType canMsg;
    canMsg.SduInfo = &keyDataBuffer[0];
    canMsg.SduLength = sizeof(KeyRequestType);
    canMsg.Identifier = KEY_REQUEST_IDENTIFIER; // Define your CAN identifier for key requests

    // Copy the key request type into the buffer
    memcpy(canMsg.SduInfo, &request, canMsg.SduLength);

    // Transmit the CAN message using CanIf
    CanIf_Transmit(&canMsg);
}

Std_ReturnType App_ComInterface_ReceiveKeyData(uint8_t *buffer, uint16_t length) {
    if (keyDataLength > 0 && buffer != NULL && length >= keyDataLength) {
        memcpy(buffer, keyDataBuffer, keyDataLength);
        keyDataLength = 0;
        return E_OK;
    } else if (length <= 0 || buffer == NULL) {
        return E_NOT_OK; // Invalid buffer or length
    }
    return E_NOT_OK; // No data available to read
}

void App_ComInterface_HandleMessage(const CanIf_MtMsgType *msg) {
    if (msg->Identifier == KEY_RESPONSE_IDENTIFIER) { // Define your CAN identifier for key responses
        if (keyRequestPending) {
            // Copy the received key data into the buffer
            memcpy(keyDataBuffer, msg->SduInfo, msg->SduLength);
            keyDataLength = msg->SduLength;

            // Reset the pending flag
            keyRequestPending = false;
        }
    }

    // Pass the message to the Com module for further processing
    Com_ProcessMessage(msg);
}
