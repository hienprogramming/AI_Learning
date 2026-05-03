#ifndef COMSTACK_TYPES_H
#define COMSTACK_TYPES_H

#include "Std_Types.h"

/* Signal types */
typedef uint8_t SignalType_uint8;
typedef uint16_t SignalType_uint16;
typedef uint32_t SignalType_uint32;

/* PDU configuration structures */
typedef struct {
    uint16_t length;
    uint8_t* data;
} PduInfoType;

/* Signal configuration structures */
typedef struct {
    uint16_t startIndex;
    uint16_t length;
    SignalType_uint32* values;
} SignalGroupConfigType;

/* Com_SignalType enum */
typedef enum {
    COM_SIGNAL_TYPE_UINT8,
    COM_SIGNAL_TYPE_UINT16,
    COM_SIGNAL_TYPE_UINT32
} Com_SignalType;

/* PduR_PduIdType definition */
typedef uint16_t PduR_PduIdType;

/* CanIf_HrhType definition */
typedef uint8_t CanIf_HrhType;

/* Maximum limits */
#define MAX_SIGNALS 8
#define MAX_PDUS 4

/* Status and return codes */
#define E_OK (Std_ReturnType)0
#define E_NOT_OK (Std_ReturnType)1

#endif /* COMSTACK_TYPES_H */
