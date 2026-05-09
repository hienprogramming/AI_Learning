#ifndef RTE_TYPE_H
#define RTE_TYPE_H

#include "../Common/Std_Types.h"

typedef uint16 Rte_SignalIdType;
typedef uint16 Rte_LengthType;

typedef enum {
    RTE_E_OK = 0u,
    RTE_E_INVALID = 1u,
    RTE_E_LIMIT = 2u,
    RTE_E_NO_DATA = 3u
} Rte_StatusType;

typedef enum {
    RTE_MODE_STARTUP = 0u,
    RTE_MODE_RUN = 1u,
    RTE_MODE_SHUTDOWN = 2u
} Rte_ModeType;

typedef struct {
    Rte_SignalIdType signalId;
    void *data;
    Rte_LengthType length;
} Rte_SignalBufferType;

#endif /* RTE_TYPE_H */
