#ifndef STD_TYPES_H
#define STD_TYPES_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

typedef uint8_t uint8;
typedef uint16_t uint16;
typedef uint32_t uint32;
typedef int8_t sint8;
typedef int16_t sint16;
typedef int32_t sint32;

typedef uint8 Std_ReturnType;

#ifndef TRUE
#define TRUE 1u
#endif

#ifndef FALSE
#define FALSE 0u
#endif

#ifndef NULL_PTR
#define NULL_PTR ((void *)0)
#endif

#ifndef E_OK
#define E_OK ((Std_ReturnType)0u)
#endif

#ifndef E_NOT_OK
#define E_NOT_OK ((Std_ReturnType)1u)
#endif

#define STD_HIGH 1u
#define STD_LOW 0u
#define STD_ACTIVE 1u
#define STD_IDLE 0u
#define STD_ON 1u
#define STD_OFF 0u

#endif /* STD_TYPES_H */
