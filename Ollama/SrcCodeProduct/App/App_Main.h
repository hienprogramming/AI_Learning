#ifndef APP_MAIN_H_
#define APP_MAIN_H_

// Include project-specific headers
#include "ProjectConfig.h"
#include "Boot_Safety.h"

// Define subsystem pointers (static allocation)
typedef struct {
    KeyManager *KeyMgr;
    Security *SecurityMgr;
    ComInterface *ComIntf;
} AppSubsystem;

// Function prototypes
void App_Init(AppSubsystem *subsys);
void App_Run(AppSubsystem *subsys);
void App_ProcessCommands(AppSubsystem *subsys);
void App_HandleError(uint32_t error_code);

#endif // APP_MAIN_H_
