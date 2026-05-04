#ifndef APP_COM_INTERFACE_H
#define APP_COM_INTERFACE_H

#include "CanIf.h"
#include "Com.h"

typedef enum {
    KEY_REQUEST_TYPE_1,
    KEY_REQUEST_TYPE_2,
    // Add more types as needed
} KeyRequestType;

void App_ComInterface_Init(void);
void App_ComInterface_SendKeyRequest(KeyRequestType request);
Std_ReturnType App_ComInterface_ReceiveKeyData(uint8_t *buffer, uint16_t length);
void App_ComInterface_HandleMessage(const CanIf_MtMsgType *msg);

#endif /* APP_COM_INTERFACE_H */
