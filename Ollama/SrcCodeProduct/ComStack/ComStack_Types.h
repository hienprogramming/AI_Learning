#ifndef COMSTACK_TYPES_H
#define COMSTACK_TYPES_H

// Signal types
typedef uint8 Com_SignalType_Byte;
typedef uint16 Com_SignalType_Word;
typedef uint32 Com_SignalType_DWord;

// PDU configuration structures
typedef struct {
    uint16 id;           // PDU ID
    uint8 length;        // Length of the PDU in bytes
} PduR_PduIdType;

// Signal configuration structures
typedef struct {
    Com_SignalType_Byte* dataPtr;   // Pointer to signal data
    uint16 offset;                // Offset within the PDU buffer
    uint8 length;                  // Length of the signal in bytes
} Com_SignalConfigType;

// Com_SignalType enum
typedef enum {
    COM_SIGNAL_TYPE_BYTE,
    COM_SIGNAL_TYPE_WORD,
    COM_SIGNAL_TYPE_DWORD,
    COM_SIGNAL_TYPE_COUNT  // This value seems out of place and should be removed or corrected
} Com_SignalType;

// Maximum limits
#define MAX_SIGNALS 8
#define MAX_PDUS 4

// Status and return codes
typedef enum {
    E_OK,
    E_NOT_OK,
    E_BUSY,
    E_TIMEOUT,
    E_INVALID_PARAM
} Std_ReturnType;

#endif // COMSTACK_TYPES_H
