#ifndef APP_COM_INTERFACE_H
#define APP_COM_INTERFACE_H

// Include necessary types for communication
#include "ComStack_Types.h"

// Define CAN IDs
#define CAN_RX_ID_KEY_REQUEST 0x100
#define CAN_TX_ID_KEY_REQUEST 0x101

// Function prototypes
void App_ComInterface_Init(void);
void App_ComInterface_SendKeyRequest(uint8_t request);
uint8_t App_ComInterface_ReceiveKeyData(uint8_t *buffer, uint16_t length);
void App_ComInterface_HandleMessage(const CAN_RxHeaderTypeDef *RxHeader, const uint8_t *RxData);

#endif // APP_COM_INTERFACE_H
