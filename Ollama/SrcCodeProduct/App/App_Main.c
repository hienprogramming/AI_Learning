#include "App_Main.h"
#include "Boot_Safety.h"
#include "Boot_Jump.h"
#include "Com.h"
#include "CanIf.h"

// Initialize all app subsystems
void App_Init(void) {
    Boot_Safety_Initialize();
    Boot_Jump_Initialize();
    Com_Initialize();
    CanIf_Initialize();

    if (!Boot_Safety_CheckIntegrity()) {
        App_HandleError(0xFFFFFFFF);
    }

    if (!Boot_Jump_IsValidApp()) {
        App_HandleError(0xFFFFFFFE);
    }
}

// Main application loop
Std_ReturnType App_Run(void) {
    while (1) {
        App_ProcessCommands();

        // Perform necessary tasks here
    }

    return E_NOT_OK; // Should never reach here
}

// Process incoming commands
void App_ProcessCommands(void) {
    if (Com_HasNewCommand()) {
        uint8_t command = Com_GetNextCommand();
        switch (command) {
            case COMMAND_LOCK:
                Key_Manager_Lock();
                break;
            case COMMAND_UNLOCK:
                Key_Manager_Unlock();
                break;
            default:
                App_HandleError(0xFFFFFFFD);
                break;
        }
    }

    if (CanIf_HasNewCommand()) {
        uint8_t command = CanIf_GetNextCommand();
        switch (command) {
            case COMMAND_LOCK:
                Key_Manager_Lock();
                break;
            case COMMAND_UNLOCK:
                Key_Manager_Unlock();
                break;
            default:
                App_HandleError(0xFFFFFFFC);
                break;
        }
    }
}

// Error handling and recovery
void App_HandleError(uint32_t error_code) {
    while (1) {
        // Loop or reset
    }
}
