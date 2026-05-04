#include "Boot_Update.h"
#include "stm32f1xx_hal.h"

// Static buffers for commands and data
#define MAX_PACKET_SIZE 256
static uint8_t packet_buffer[MAX_PACKET_SIZE];
static uint16_t packet_index = 0;

// Application address where the firmware will be written
#define APPLICATION_ADDRESS 0x08008000

// Function prototypes
void Handle_Erase(void);
void Handle_Write(uint16_t length);
void Handle_Verify(uint32_t address, uint16_t length);
void Handle_Jump(void);

void Boot_Update_Init(void) {
    // Initialize UART (this is a placeholder for your actual UART initialization)
    HAL_UART_Receive(&huart1, packet_buffer, 1, HAL_MAX_DELAY); // Receive the command
}

int Boot_Update_ProcessPacket(uint8_t *data, uint16_t length) {
    if (length == 0) {
        return -1; // Invalid data length
    }

    uint8_t cmd = data[0];
    uint16_t packet_length = length;

    switch (cmd) {
        case CMD_ERASE:
            Handle_Erase();
            break;
        case CMD_WRITE:
            Handle_Write(packet_length);
            break;
        case CMD_VERIFY:
            if (packet_length < 4) {
                return -1; // Invalid verify data
            }
            uint32_t address = (data[1] << 24) | (data[2] << 16) | (data[3] << 8);
            Handle_Verify(address, packet_length - 4);
            break;
        case CMD_JUMP:
            Handle_Jump();
            break;
        default:
            return -1; // Unknown command
    }

    return 0;
}

void Handle_Erase(void) {
    uint32_t page_address = APPLICATION_ADDRESS;
    uint16_t pages_to_erase = (PAGE_SIZE / FLASH_PAGE_SIZE); // Assuming PAGE_SIZE is defined

    for (uint16_t i = 0; i < pages_to_erase; i++) {
        if (HAL_FLASHEx_Erase(FLASH_TYPEERASE_PAGES, page_address, pages_to_erase) != HAL_OK) {
            return; // Erase failed
        }
        page_address += FLASH_PAGE_SIZE;
    }
}

void Handle_Write(uint16_t length) {
    uint32_t address = APPLICATION_ADDRESS + packet_index;
    uint16_t bytes_to_write = (length < 4 ? length : length - 4);

    if ((address % 4 != 0) || (bytes_to_write % 4 != 0)) {
        return; // Invalid write address or length
    }

    for (uint16_t i = 0; i < bytes_to_write; i += 4) {
        uint32_t data = (packet_buffer[packet_index + i] << 24) |
                       (packet_buffer[packet_index + i + 1] << 16) |
                       (packet_buffer[packet_index + i + 2] << 8) |
                       packet_buffer[packet_index + i + 3];

        if (HAL_FLASH_Program(FLASH_TYPEPROGRAM_WORD, address + i, data) != HAL_OK) {
            return; // Write failed
        }
    }

    packet_index += bytes_to_write;
}

void Handle_Verify(uint32_t address, uint16_t length) {
    for (uint16_t i = 0; i < length; i += 4) {
        uint32_t data_from_flash = *(uint32_t *)(address + i);
        uint32_t data_to_verify = (packet_buffer[packet_index + i] << 24) |
                                  (packet_buffer[packet_index + i + 1] << 16) |
                                  (packet_buffer[packet_index + i + 2] << 8) |
                                  packet_buffer[packet_index + i + 3];

        if (data_from_flash != data_to_verify) {
            return; // Verification failed
        }
    }

    // CRC verification
    uint32_t crc = CalculateCRC(address, length);
    uint32_t received_crc = (packet_buffer[packet_index] << 24) |
                            (packet_buffer[packet_index + 1] << 16) |
                            (packet_buffer[packet_index + 2] << 8) |
                            packet_buffer[packet_index + 3];

    if (crc != received_crc) {
        return; // CRC verification failed
    }

    // If all checks pass, set a flag indicating successful update
    // You can use a global variable or a specific memory location for this
}

void Handle_Jump(void) {
    // Jump to the application
    uint32_t jump_address = APPLICATION_ADDRESS;
    typedef void (*ApplicationJump)(void);
    ApplicationJump jump_to_app = (ApplicationJump)jump_address;
    jump_to_app();
}

// CRC calculation function
uint32_t CalculateCRC(uint32_t address, uint16_t length) {
    // Implement your CRC calculation logic here
    return 0; // Placeholder
}
