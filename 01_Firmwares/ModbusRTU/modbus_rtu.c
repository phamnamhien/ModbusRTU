#include "modbus_rtu.h"
#include "modbus_port.h"
#include <string.h>

/* Sử dụng mapping mode từ modbus_registers.h nếu có define */
#ifdef MODBUS_USE_REGISTER_MAPPING
    /* Mapping mode: register data được define trong modbus_registers.c */
    extern uint16_t g_modbus_holding_registers[];
    extern uint16_t g_modbus_input_registers[];
    extern uint8_t  g_modbus_coils[];
    extern uint8_t  g_modbus_discrete_inputs[];

    #define g_holding_registers     g_modbus_holding_registers
    #define g_input_registers       g_modbus_input_registers
    #define g_coils                 g_modbus_coils
    #define g_discrete_inputs       g_modbus_discrete_inputs
#else
    /* Fixed array mode: cấp phát array cố định */
    #ifndef MODBUS_MAX_COILS
    #define MODBUS_MAX_COILS            256
    #endif

    #ifndef MODBUS_MAX_DISCRETE_INPUTS
    #define MODBUS_MAX_DISCRETE_INPUTS  256
    #endif

    #ifndef MODBUS_MAX_HOLDING_REGISTERS
    #define MODBUS_MAX_HOLDING_REGISTERS 256
    #endif

    #ifndef MODBUS_MAX_INPUT_REGISTERS
    #define MODBUS_MAX_INPUT_REGISTERS   256
    #endif

    /* Data Storage Arrays */
    static uint8_t  g_coils[MODBUS_MAX_COILS / 8];
    static uint8_t  g_discrete_inputs[MODBUS_MAX_DISCRETE_INPUTS / 8];
    static uint16_t g_holding_registers[MODBUS_MAX_HOLDING_REGISTERS];
    static uint16_t g_input_registers[MODBUS_MAX_INPUT_REGISTERS];
#endif

/* CRC-16 Lookup Table */
static const uint16_t crc16_table[256] = {
    0x0000, 0xC0C1, 0xC181, 0x0140, 0xC301, 0x03C0, 0x0280, 0xC241,
    0xC601, 0x06C0, 0x0780, 0xC741, 0x0500, 0xC5C1, 0xC481, 0x0440,
    0xCC01, 0x0CC0, 0x0D80, 0xCD41, 0x0F00, 0xCFC1, 0xCE81, 0x0E40,
    0x0A00, 0xCAC1, 0xCB81, 0x0B40, 0xC901, 0x09C0, 0x0880, 0xC841,
    0xD801, 0x18C0, 0x1980, 0xD941, 0x1B00, 0xDBC1, 0xDA81, 0x1A40,
    0x1E00, 0xDEC1, 0xDF81, 0x1F40, 0xDD01, 0x1DC0, 0x1C80, 0xDC41,
    0x1400, 0xD4C1, 0xD581, 0x1540, 0xD701, 0x17C0, 0x1680, 0xD641,
    0xD201, 0x12C0, 0x1380, 0xD341, 0x1100, 0xD1C1, 0xD081, 0x1040,
    0xF001, 0x30C0, 0x3180, 0xF141, 0x3300, 0xF3C1, 0xF281, 0x3240,
    0x3600, 0xF6C1, 0xF781, 0x3740, 0xF501, 0x35C0, 0x3480, 0xF441,
    0x3C00, 0xFCC1, 0xFD81, 0x3D40, 0xFF01, 0x3FC0, 0x3E80, 0xFE41,
    0xFA01, 0x3AC0, 0x3B80, 0xFB41, 0x3900, 0xF9C1, 0xF881, 0x3840,
    0x2800, 0xE8C1, 0xE981, 0x2940, 0xEB01, 0x2BC0, 0x2A80, 0xEA41,
    0xEE01, 0x2EC0, 0x2F80, 0xEF41, 0x2D00, 0xEDC1, 0xEC81, 0x2C40,
    0xE401, 0x24C0, 0x2580, 0xE541, 0x2700, 0xE7C1, 0xE681, 0x2640,
    0x2200, 0xE2C1, 0xE381, 0x2340, 0xE101, 0x21C0, 0x2080, 0xE041,
    0xA001, 0x60C0, 0x6180, 0xA141, 0x6300, 0xA3C1, 0xA281, 0x6240,
    0x6600, 0xA6C1, 0xA781, 0x6740, 0xA501, 0x65C0, 0x6480, 0xA441,
    0x6C00, 0xACC1, 0xAD81, 0x6D40, 0xAF01, 0x6FC0, 0x6E80, 0xAE41,
    0xAA01, 0x6AC0, 0x6B80, 0xAB41, 0x6900, 0xA9C1, 0xA881, 0x6840,
    0x7800, 0xB8C1, 0xB981, 0x7940, 0xBB01, 0x7BC0, 0x7A80, 0xBA41,
    0xBE01, 0x7EC0, 0x7F80, 0xBF41, 0x7D00, 0xBDC1, 0xBC81, 0x7C40,
    0xB401, 0x74C0, 0x7580, 0xB541, 0x7700, 0xB7C1, 0xB681, 0x7640,
    0x7200, 0xB2C1, 0xB381, 0x7340, 0xB101, 0x71C0, 0x7080, 0xB041,
    0x5000, 0x90C1, 0x9181, 0x5140, 0x9301, 0x53C0, 0x5280, 0x9241,
    0x9601, 0x56C0, 0x5780, 0x9741, 0x5500, 0x95C1, 0x9481, 0x5440,
    0x9C01, 0x5CC0, 0x5D80, 0x9D41, 0x5F00, 0x9FC1, 0x9E81, 0x5E40,
    0x5A00, 0x9AC1, 0x9B81, 0x5B40, 0x9901, 0x59C0, 0x5880, 0x9841,
    0x8801, 0x48C0, 0x4980, 0x8941, 0x4B00, 0x8BC1, 0x8A81, 0x4A40,
    0x4E00, 0x8EC1, 0x8F81, 0x4F40, 0x8D01, 0x4DC0, 0x4C80, 0x8C41,
    0x4400, 0x84C1, 0x8581, 0x4540, 0x8701, 0x47C0, 0x4680, 0x8641,
    0x8201, 0x42C0, 0x4380, 0x8341, 0x4100, 0x81C1, 0x8081, 0x4040
};

/* Forward Declarations */
static void process_received_frame(modbus_rtu_ctx_t *ctx);
static void build_exception_response(modbus_rtu_ctx_t *ctx, uint8_t exception_code);
static void send_response(modbus_rtu_ctx_t *ctx);
static bool validate_frame(modbus_rtu_ctx_t *ctx);

/* Helper Functions */
static inline void set_bit(uint8_t *array, uint16_t bit_pos, bool value) {
    if (value)
        array[bit_pos >> 3] |= (1 << (bit_pos & 0x07));
    else
        array[bit_pos >> 3] &= ~(1 << (bit_pos & 0x07));
}

static inline bool get_bit(const uint8_t *array, uint16_t bit_pos) {
    return (array[bit_pos >> 3] & (1 << (bit_pos & 0x07))) != 0;
}

#ifdef MODBUS_USE_REGISTER_MAPPING
/**
 * @brief   Get array index from internal address using mapping
 */
static int16_t get_register_index(uint16_t addr, uint8_t reg_type) {
    extern const modbus_register_map_t g_modbus_holding_register_map[];
    extern const modbus_register_map_t g_modbus_input_register_map[];
    extern const modbus_register_map_t g_modbus_coil_map[];
    extern const modbus_register_map_t g_modbus_discrete_input_map[];

    const modbus_register_map_t *map;
    int count;

    switch(reg_type) {
        case 0:
            map = g_modbus_coil_map;
            count = MODBUS_COIL_COUNT;
            break;
        case 1:
            map = g_modbus_discrete_input_map;
            count = MODBUS_DISCRETE_INPUT_COUNT;
            break;
        case 3:
            map = g_modbus_input_register_map;
            count = MODBUS_INPUT_REGISTER_COUNT;
            break;
        case 4:
            map = g_modbus_holding_register_map;
            count = MODBUS_HOLDING_REGISTER_COUNT;
            break;
        default:
            return -1;
    }

    /* Binary search */
    int left = 0, right = count - 1;
    while (left <= right) {
        int mid = (left + right) / 2;
        if (map[mid].internal_addr == addr) {
            return map[mid].array_index;
        } else if (map[mid].internal_addr < addr) {
            left = mid + 1;
        } else {
            right = mid - 1;
        }
    }

    return -1;
}
#endif

/**
 * @brief   Initialize Modbus RTU context
 */
void
modbus_rtu_init(modbus_rtu_ctx_t *ctx, uint8_t slave_id, bool is_master, uint32_t baudrate) {
    memset(ctx, 0, sizeof(modbus_rtu_ctx_t));

    ctx->slave_id = slave_id;
    ctx->is_master = is_master;
    ctx->baudrate = baudrate;
    ctx->t15_us = MODBUS_RTU_T15_US(baudrate);
    ctx->t35_us = MODBUS_RTU_T35_US(baudrate);
    ctx->state = MODBUS_STATE_IDLE;
    ctx->timeout_ms = 1000;

    modbus_registers_init();
}

/**
 * @brief   Set TX start/end callbacks
 */
void
modbus_rtu_set_callbacks(modbus_rtu_ctx_t *ctx, void (*tx_start)(void), void (*tx_end)(void)) {
    ctx->tx_start_cb = tx_start;
    ctx->tx_end_cb = tx_end;
}

/**
 * @brief   Calculate CRC-16 (Modbus)
 */
uint16_t
modbus_rtu_calc_crc(const uint8_t *buffer, uint16_t length) {
    uint16_t crc = 0xFFFF;

    for (uint16_t i = 0; i < length; i++) {
        crc = (crc >> 8) ^ crc16_table[(crc ^ buffer[i]) & 0xFF];
    }

    return crc;
}

/**
 * @brief   Check CRC-16
 */
bool
modbus_rtu_check_crc(const uint8_t *buffer, uint16_t length) {
    if (length < 4) return false;

    uint16_t calc_crc = modbus_rtu_calc_crc(buffer, length - 2);
    uint16_t recv_crc = buffer[length - 2] | (buffer[length - 1] << 8);

    return (calc_crc == recv_crc);
}

/**
 * @brief   Receive byte callback (called from ISR)
 */
void
modbus_rtu_rx_byte(modbus_rtu_ctx_t *ctx, uint8_t byte) {
    if (ctx->rx_length < MODBUS_MAX_ADU_LENGTH) {
        ctx->rx_buffer[ctx->rx_length++] = byte;
        ctx->rx_timestamp = modbus_port_get_time_us();
        ctx->state = MODBUS_STATE_RECEIVING;
    }
}

/**
 * @brief   Timer callback for T3.5 timeout (called from timer ISR)
 */
void
modbus_rtu_timer_callback(modbus_rtu_ctx_t *ctx) {
    uint32_t elapsed = modbus_port_get_time_us() - ctx->rx_timestamp;

    if (ctx->state == MODBUS_STATE_RECEIVING && elapsed >= ctx->t35_us) {
        ctx->state = MODBUS_STATE_PROCESSING;
    }
}

/**
 * @brief   Process received frame (Slave mode)
 */
void
modbus_rtu_slave_process(modbus_rtu_ctx_t *ctx) {
    if (ctx->state != MODBUS_STATE_PROCESSING)
        return;

    if (!validate_frame(ctx)) {
        ctx->state = MODBUS_STATE_IDLE;
        ctx->rx_length = 0;
        return;
    }

    if (ctx->rx_buffer[0] != ctx->slave_id && ctx->rx_buffer[0] != 0) {
        ctx->state = MODBUS_STATE_IDLE;
        ctx->rx_length = 0;
        return;
    }

    ctx->current_frame.slave_id = ctx->rx_buffer[0];
    ctx->current_frame.function_code = ctx->rx_buffer[1];
    ctx->current_frame.start_addr = (ctx->rx_buffer[2] << 8) | ctx->rx_buffer[3];
    ctx->current_frame.count = (ctx->rx_buffer[4] << 8) | ctx->rx_buffer[5];

    process_received_frame(ctx);
    send_response(ctx);

    ctx->state = MODBUS_STATE_IDLE;
    ctx->rx_length = 0;
}

/**
 * @brief   Validate received frame
 */
static bool
validate_frame(modbus_rtu_ctx_t *ctx) {
    if (ctx->rx_length < MODBUS_RTU_FRAME_MIN_SIZE)
        return false;

    return modbus_rtu_check_crc(ctx->rx_buffer, ctx->rx_length);
}

/**
 * @brief   Process received frame based on function code
 */
static void
process_received_frame(modbus_rtu_ctx_t *ctx) {
    uint8_t fc = ctx->current_frame.function_code;
    uint16_t addr = ctx->current_frame.start_addr;
    uint16_t count = ctx->current_frame.count;

    ctx->tx_buffer[0] = ctx->slave_id;
    ctx->tx_buffer[1] = fc;
    ctx->tx_length = 2;

    switch (fc) {
        case MODBUS_FC_READ_COILS:
        case MODBUS_FC_READ_DISCRETE_INPUTS: {
            uint8_t reg_type = (fc == MODBUS_FC_READ_COILS) ? 0 : 1;
            uint8_t byte_count = (count + 7) / 8;

            if (count == 0 || count > 2000) {
                build_exception_response(ctx, MODBUS_EX_ILLEGAL_DATA_VALUE);
                return;
            }

            for (uint16_t i = 0; i < count; i++) {
                if (!modbus_is_register_valid(addr + i, reg_type)) {
                    build_exception_response(ctx, MODBUS_EX_ILLEGAL_DATA_ADDRESS);
                    return;
                }
            }

            ctx->tx_buffer[2] = byte_count;
            ctx->tx_length = 3;

            for (uint16_t i = 0; i < count; i++) {
                bool value;
                if (fc == MODBUS_FC_READ_COILS)
                    modbus_rtu_get_coil(addr + i, &value);
                else
                    modbus_rtu_get_discrete_input(addr + i, &value);

                if (value)
                    ctx->tx_buffer[3 + (i >> 3)] |= (1 << (i & 0x07));
            }
            ctx->tx_length += byte_count;
            break;
        }

        case MODBUS_FC_READ_HOLDING_REGISTERS:
        case MODBUS_FC_READ_INPUT_REGISTERS: {
            uint8_t reg_type = (fc == MODBUS_FC_READ_HOLDING_REGISTERS) ? 4 : 3;

            if (count == 0 || count > 125) {
                build_exception_response(ctx, MODBUS_EX_ILLEGAL_DATA_VALUE);
                return;
            }

            for (uint16_t i = 0; i < count; i++) {
                if (!modbus_is_register_valid(addr + i, reg_type)) {
                    build_exception_response(ctx, MODBUS_EX_ILLEGAL_DATA_ADDRESS);
                    return;
                }
            }

            ctx->tx_buffer[2] = count * 2;
            ctx->tx_length = 3;

            for (uint16_t i = 0; i < count; i++) {
                uint16_t value;
                if (fc == MODBUS_FC_READ_HOLDING_REGISTERS)
                    modbus_rtu_get_holding_register(addr + i, &value);
                else
                    modbus_rtu_get_input_register(addr + i, &value);

                ctx->tx_buffer[ctx->tx_length++] = value >> 8;
                ctx->tx_buffer[ctx->tx_length++] = value & 0xFF;
            }
            break;
        }

        case MODBUS_FC_WRITE_SINGLE_COIL: {
            if (!modbus_is_register_valid(addr, 0)) {
                build_exception_response(ctx, MODBUS_EX_ILLEGAL_DATA_ADDRESS);
                return;
            }

            uint16_t value = (ctx->rx_buffer[4] << 8) | ctx->rx_buffer[5];
            if (value != 0x0000 && value != 0xFF00) {
                build_exception_response(ctx, MODBUS_EX_ILLEGAL_DATA_VALUE);
                return;
            }

            modbus_rtu_set_coil(addr, value == 0xFF00);

            memcpy(&ctx->tx_buffer[2], &ctx->rx_buffer[2], 4);
            ctx->tx_length = 6;
            break;
        }

        case MODBUS_FC_WRITE_SINGLE_REGISTER: {
            if (!modbus_is_register_valid(addr, 4)) {
                build_exception_response(ctx, MODBUS_EX_ILLEGAL_DATA_ADDRESS);
                return;
            }

            uint16_t value = (ctx->rx_buffer[4] << 8) | ctx->rx_buffer[5];
            modbus_rtu_set_holding_register(addr, value);

            memcpy(&ctx->tx_buffer[2], &ctx->rx_buffer[2], 4);
            ctx->tx_length = 6;
            break;
        }

        case MODBUS_FC_WRITE_MULTIPLE_COILS: {
            uint8_t byte_count = ctx->rx_buffer[6];

            if (count == 0 || count > 1968 || byte_count != (count + 7) / 8) {
                build_exception_response(ctx, MODBUS_EX_ILLEGAL_DATA_VALUE);
                return;
            }

            for (uint16_t i = 0; i < count; i++) {
                if (!modbus_is_register_valid(addr + i, 0)) {
                    build_exception_response(ctx, MODBUS_EX_ILLEGAL_DATA_ADDRESS);
                    return;
                }
            }

            for (uint16_t i = 0; i < count; i++) {
                bool value = (ctx->rx_buffer[7 + (i >> 3)] & (1 << (i & 0x07))) != 0;
                modbus_rtu_set_coil(addr + i, value);
            }

            memcpy(&ctx->tx_buffer[2], &ctx->rx_buffer[2], 4);
            ctx->tx_length = 6;
            break;
        }

        case MODBUS_FC_WRITE_MULTIPLE_REGISTERS: {
            uint8_t byte_count = ctx->rx_buffer[6];

            if (count == 0 || count > 123 || byte_count != count * 2) {
                build_exception_response(ctx, MODBUS_EX_ILLEGAL_DATA_VALUE);
                return;
            }

            for (uint16_t i = 0; i < count; i++) {
                if (!modbus_is_register_valid(addr + i, 4)) {
                    build_exception_response(ctx, MODBUS_EX_ILLEGAL_DATA_ADDRESS);
                    return;
                }
            }

            for (uint16_t i = 0; i < count; i++) {
                uint16_t value = (ctx->rx_buffer[7 + i * 2] << 8) | ctx->rx_buffer[8 + i * 2];
                modbus_rtu_set_holding_register(addr + i, value);
            }

            memcpy(&ctx->tx_buffer[2], &ctx->rx_buffer[2], 4);
            ctx->tx_length = 6;
            break;
        }

        default:
            build_exception_response(ctx, MODBUS_EX_ILLEGAL_FUNCTION);
            break;
    }
}

/**
 * @brief   Build exception response
 */
static void
build_exception_response(modbus_rtu_ctx_t *ctx, uint8_t exception_code) {
    ctx->tx_buffer[0] = ctx->slave_id;
    ctx->tx_buffer[1] = ctx->current_frame.function_code | 0x80;
    ctx->tx_buffer[2] = exception_code;
    ctx->tx_length = 3;
}

/**
 * @brief   Send response frame
 */
static void
send_response(modbus_rtu_ctx_t *ctx) {
    uint16_t crc = modbus_rtu_calc_crc(ctx->tx_buffer, ctx->tx_length);
    ctx->tx_buffer[ctx->tx_length++] = crc & 0xFF;
    ctx->tx_buffer[ctx->tx_length++] = crc >> 8;

    if (ctx->tx_start_cb)
        ctx->tx_start_cb();

    modbus_port_send(ctx->tx_buffer, ctx->tx_length);

    if (ctx->tx_end_cb)
        ctx->tx_end_cb();
}

/* Data Access Functions */
bool modbus_rtu_get_coil(uint16_t addr, bool *value) {
    if (!modbus_is_register_valid(addr, 0)) return false;

#ifdef MODBUS_USE_REGISTER_MAPPING
    int16_t idx = get_register_index(addr, 0);
    if (idx < 0) return false;
    *value = get_bit(g_coils, idx);
#else
    if (addr >= MODBUS_MAX_COILS) return false;
    *value = get_bit(g_coils, addr);
#endif
    return true;
}

bool modbus_rtu_set_coil(uint16_t addr, bool value) {
    if (!modbus_is_register_valid(addr, 0)) return false;

#ifdef MODBUS_USE_REGISTER_MAPPING
    int16_t idx = get_register_index(addr, 0);
    if (idx < 0) return false;
    set_bit(g_coils, idx, value);
#else
    if (addr >= MODBUS_MAX_COILS) return false;
    set_bit(g_coils, addr, value);
#endif
    return true;
}

bool modbus_rtu_get_discrete_input(uint16_t addr, bool *value) {
    if (!modbus_is_register_valid(addr, 1)) return false;

#ifdef MODBUS_USE_REGISTER_MAPPING
    int16_t idx = get_register_index(addr, 1);
    if (idx < 0) return false;
    *value = get_bit(g_discrete_inputs, idx);
#else
    if (addr >= MODBUS_MAX_DISCRETE_INPUTS) return false;
    *value = get_bit(g_discrete_inputs, addr);
#endif
    return true;
}

bool modbus_rtu_set_discrete_input(uint16_t addr, bool value) {
    if (!modbus_is_register_valid(addr, 1)) return false;

#ifdef MODBUS_USE_REGISTER_MAPPING
    int16_t idx = get_register_index(addr, 1);
    if (idx < 0) return false;
    set_bit(g_discrete_inputs, idx, value);
#else
    if (addr >= MODBUS_MAX_DISCRETE_INPUTS) return false;
    set_bit(g_discrete_inputs, addr, value);
#endif
    return true;
}

bool modbus_rtu_get_holding_register(uint16_t addr, uint16_t *value) {
    if (!modbus_is_register_valid(addr, 4)) return false;

#ifdef MODBUS_USE_REGISTER_MAPPING
    int16_t idx = get_register_index(addr, 4);
    if (idx < 0) return false;
    *value = g_holding_registers[idx];
#else
    if (addr >= MODBUS_MAX_HOLDING_REGISTERS) return false;
    *value = g_holding_registers[addr];
#endif
    return true;
}

bool modbus_rtu_set_holding_register(uint16_t addr, uint16_t value) {
    if (!modbus_is_register_valid(addr, 4)) return false;

#ifdef MODBUS_USE_REGISTER_MAPPING
    int16_t idx = get_register_index(addr, 4);
    if (idx < 0) return false;
    g_holding_registers[idx] = value;
#else
    if (addr >= MODBUS_MAX_HOLDING_REGISTERS) return false;
    g_holding_registers[addr] = value;
#endif
    return true;
}

bool modbus_rtu_get_input_register(uint16_t addr, uint16_t *value) {
    if (!modbus_is_register_valid(addr, 3)) return false;

#ifdef MODBUS_USE_REGISTER_MAPPING
    int16_t idx = get_register_index(addr, 3);
    if (idx < 0) return false;
    *value = g_input_registers[idx];
#else
    if (addr >= MODBUS_MAX_INPUT_REGISTERS) return false;
    *value = g_input_registers[addr];
#endif
    return true;
}

bool modbus_rtu_set_input_register(uint16_t addr, uint16_t value) {
    if (!modbus_is_register_valid(addr, 3)) return false;

#ifdef MODBUS_USE_REGISTER_MAPPING
    int16_t idx = get_register_index(addr, 3);
    if (idx < 0) return false;
    g_input_registers[idx] = value;
#else
    if (addr >= MODBUS_MAX_INPUT_REGISTERS) return false;
    g_input_registers[addr] = value;
#endif
    return true;
}

/* Direct array access functions */
uint16_t* modbus_rtu_get_holding_register_array(void) {
    return g_holding_registers;
}

uint16_t* modbus_rtu_get_input_register_array(void) {
    return g_input_registers;
}

uint8_t* modbus_rtu_get_coil_array(void) {
    return g_coils;
}

uint8_t* modbus_rtu_get_discrete_input_array(void) {
    return g_discrete_inputs;
}

/* ========================================================================
 * SIMPLE API IMPLEMENTATION
 * ======================================================================== */

/* Global context - EXPORT để main.c dùng */
modbus_rtu_ctx_t g_modbus_ctx;

/* Local variables */
static bool g_easy_initialized = false;

/* RS485 control - sẽ được define trong modbus_port.c */
extern void modbus_port_rs485_tx_enable(void);
extern void modbus_port_rs485_rx_enable(void);

/**
 * @brief   Easy init - Chỉ 1 dòng code!
 */
void modbus_easy_init(uint8_t slave_id, uint32_t baudrate) {
    /* 1. Init Modbus context */
    modbus_rtu_init(&g_modbus_ctx, slave_id, false, baudrate);

    /* 2. Set RS485 callbacks */
    modbus_rtu_set_callbacks(&g_modbus_ctx,
                            modbus_port_rs485_tx_enable,
                            modbus_port_rs485_rx_enable);

    /* 3. Init UART với Even parity, 1 stop bit */
    modbus_port_uart_init(baudrate, 2, 1);

    /* 4. Init Timer T3.5 */
    modbus_port_timer_init(g_modbus_ctx.t35_us);

    /* 5. Start timer */
    modbus_port_timer_enable(true);

    /* 6. Set RX mode */
    modbus_port_rs485_rx_enable();

    g_easy_initialized = true;
}

void modbus_easy_poll(void) {
    // DEBUG: Kiểm tra context
    if (&g_modbus_ctx == NULL) {
        Error_Handler();  // Context NULL!
    }

    if (!g_easy_initialized) {
        return;
    }

    // DEBUG: Kiểm tra state hợp lệ
    if (g_modbus_ctx.state > MODBUS_STATE_ERROR) {
        Error_Handler();  // State không hợp lệ!
    }

    /* Process Modbus slave */
    modbus_rtu_slave_process(&g_modbus_ctx);
}

/**
 * @brief   Get easy context (cho advanced users)
 */
modbus_rtu_ctx_t* modbus_easy_get_context(void) {
    return &g_modbus_ctx;
}

