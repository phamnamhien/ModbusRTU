#ifndef MODBUS_RTU_H
#define MODBUS_RTU_H

#include <stdint.h>
#include <stdbool.h>
#include "modbus_registers.h"

/**
 * @file    modbus_rtu.h
 * @brief   Modbus RTU Protocol Implementation
 * @note    Platform independent, requires porting layer
 */

/* Modbus Function Codes */
#define MODBUS_FC_READ_COILS                    (0x01)
#define MODBUS_FC_READ_DISCRETE_INPUTS          (0x02)
#define MODBUS_FC_READ_HOLDING_REGISTERS        (0x03)
#define MODBUS_FC_READ_INPUT_REGISTERS          (0x04)
#define MODBUS_FC_WRITE_SINGLE_COIL             (0x05)
#define MODBUS_FC_WRITE_SINGLE_REGISTER         (0x06)
#define MODBUS_FC_WRITE_MULTIPLE_COILS          (0x0F)
#define MODBUS_FC_WRITE_MULTIPLE_REGISTERS      (0x10)

/* Modbus Exception Codes */
#define MODBUS_EX_ILLEGAL_FUNCTION              (0x01)
#define MODBUS_EX_ILLEGAL_DATA_ADDRESS          (0x02)
#define MODBUS_EX_ILLEGAL_DATA_VALUE            (0x03)
#define MODBUS_EX_SLAVE_DEVICE_FAILURE          (0x04)

/* Protocol Limits */
#define MODBUS_MAX_PDU_LENGTH                   (253)
#define MODBUS_MAX_ADU_LENGTH                   (256)
#define MODBUS_RTU_FRAME_MIN_SIZE               (4)

/* Timing Constants */
#define MODBUS_RTU_T15_US(baudrate)             ((15000000UL) / (baudrate))
#define MODBUS_RTU_T35_US(baudrate)             ((35000000UL) / (baudrate))

/* Modbus RTU State Machine */
typedef enum {
    MODBUS_STATE_IDLE = 0,
    MODBUS_STATE_RECEIVING,
    MODBUS_STATE_PROCESSING,
    MODBUS_STATE_TRANSMITTING,
    MODBUS_STATE_WAITING,
    MODBUS_STATE_ERROR
} modbus_state_t;

/* Modbus Request/Response Structure */
typedef struct {
    uint8_t  slave_id;
    uint8_t  function_code;
    uint16_t start_addr;
    uint16_t count;
    uint8_t  *data;
    uint16_t data_len;
    uint8_t  exception_code;
} modbus_frame_t;

/* Modbus Context Structure */
typedef struct {
    uint8_t  slave_id;
    bool     is_master;
    uint32_t baudrate;
    uint32_t t15_us;
    uint32_t t35_us;

    modbus_state_t state;
    uint32_t       timeout_ms;

    uint8_t  rx_buffer[MODBUS_MAX_ADU_LENGTH];
    uint16_t rx_length;
    uint32_t rx_timestamp;

    uint8_t  tx_buffer[MODBUS_MAX_ADU_LENGTH];
    uint16_t tx_length;

    modbus_frame_t current_frame;

    void (*tx_start_cb)(void);
    void (*tx_end_cb)(void);

} modbus_rtu_ctx_t;

/* ========================================================================
 * SIMPLE API - CHỈ CẦN 2 HÀM NÀY!
 * ======================================================================== */

/**
 * @brief   Easy init - Tự động cấu hình mọi thứ
 * @param   slave_id: Slave ID (1-247)
 * @param   baudrate: Baudrate (9600, 19200, 38400, 57600, 115200)
 * @note    Tự động init UART, Timer, RS485, và set initial values
 */
void modbus_easy_init(uint8_t slave_id, uint32_t baudrate);

/**
 * @brief   Easy poll - Gọi trong main loop
 * @note    Tự động xử lý tất cả: slave process, update registers, etc.
 */
void modbus_easy_poll(void);

/**
 * @brief   Get easy context (cho advanced users)
 * @return  Pointer to global modbus context
 */
modbus_rtu_ctx_t* modbus_easy_get_context(void);

/* ========================================================================
 * ADVANCED API - Cho người dùng nâng cao
 * ======================================================================== */

/* Initialization */
void modbus_rtu_init(modbus_rtu_ctx_t *ctx, uint8_t slave_id, bool is_master, uint32_t baudrate);
void modbus_rtu_set_callbacks(modbus_rtu_ctx_t *ctx, void (*tx_start)(void), void (*tx_end)(void));

/* Slave Functions */
void modbus_rtu_slave_process(modbus_rtu_ctx_t *ctx);

/* Master Functions */
bool modbus_rtu_master_read_coils(modbus_rtu_ctx_t *ctx, uint8_t slave_id, uint16_t addr, uint16_t count, uint8_t *dest);
bool modbus_rtu_master_read_discrete_inputs(modbus_rtu_ctx_t *ctx, uint8_t slave_id, uint16_t addr, uint16_t count, uint8_t *dest);
bool modbus_rtu_master_read_holding_registers(modbus_rtu_ctx_t *ctx, uint8_t slave_id, uint16_t addr, uint16_t count, uint16_t *dest);
bool modbus_rtu_master_read_input_registers(modbus_rtu_ctx_t *ctx, uint8_t slave_id, uint16_t addr, uint16_t count, uint16_t *dest);
bool modbus_rtu_master_write_single_coil(modbus_rtu_ctx_t *ctx, uint8_t slave_id, uint16_t addr, bool value);
bool modbus_rtu_master_write_single_register(modbus_rtu_ctx_t *ctx, uint8_t slave_id, uint16_t addr, uint16_t value);
bool modbus_rtu_master_write_multiple_coils(modbus_rtu_ctx_t *ctx, uint8_t slave_id, uint16_t addr, uint16_t count, const uint8_t *values);
bool modbus_rtu_master_write_multiple_registers(modbus_rtu_ctx_t *ctx, uint8_t slave_id, uint16_t addr, uint16_t count, const uint16_t *values);

/* Data Access */
bool modbus_rtu_get_coil(uint16_t addr, bool *value);
bool modbus_rtu_set_coil(uint16_t addr, bool value);
bool modbus_rtu_get_discrete_input(uint16_t addr, bool *value);
bool modbus_rtu_set_discrete_input(uint16_t addr, bool value);
bool modbus_rtu_get_holding_register(uint16_t addr, uint16_t *value);
bool modbus_rtu_set_holding_register(uint16_t addr, uint16_t value);
bool modbus_rtu_get_input_register(uint16_t addr, uint16_t *value);
bool modbus_rtu_set_input_register(uint16_t addr, uint16_t value);

/* Direct array access */
uint16_t* modbus_rtu_get_holding_register_array(void);
uint16_t* modbus_rtu_get_input_register_array(void);
uint8_t* modbus_rtu_get_coil_array(void);
uint8_t* modbus_rtu_get_discrete_input_array(void);

/* Utilities */
uint16_t modbus_rtu_calc_crc(const uint8_t *buffer, uint16_t length);
bool modbus_rtu_check_crc(const uint8_t *buffer, uint16_t length);

/* Internal - Called by porting layer */
void modbus_rtu_rx_byte(modbus_rtu_ctx_t *ctx, uint8_t byte);
void modbus_rtu_timer_callback(modbus_rtu_ctx_t *ctx);

#endif /* MODBUS_RTU_H */

