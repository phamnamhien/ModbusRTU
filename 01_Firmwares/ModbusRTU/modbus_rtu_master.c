#include "modbus_rtu.h"
#include "modbus_port.h"
#include <string.h>

/**
 * @file    modbus_rtu_master.c
 * @brief   Modbus RTU Master mode implementation
 */

/* Helper function to send request and wait for response */
static bool
master_send_request(modbus_rtu_ctx_t *ctx, uint8_t slave_id, uint8_t function_code,
                   uint16_t addr, uint16_t count, const uint8_t *extra_data, uint16_t extra_len) {
    /* Build request */
    ctx->tx_buffer[0] = slave_id;
    ctx->tx_buffer[1] = function_code;
    ctx->tx_buffer[2] = addr >> 8;
    ctx->tx_buffer[3] = addr & 0xFF;
    ctx->tx_buffer[4] = count >> 8;
    ctx->tx_buffer[5] = count & 0xFF;
    ctx->tx_length = 6;

    /* Add extra data if provided */
    if (extra_data && extra_len > 0) {
        memcpy(&ctx->tx_buffer[ctx->tx_length], extra_data, extra_len);
        ctx->tx_length += extra_len;
    }

    /* Add CRC */
    uint16_t crc = modbus_rtu_calc_crc(ctx->tx_buffer, ctx->tx_length);
    ctx->tx_buffer[ctx->tx_length++] = crc & 0xFF;
    ctx->tx_buffer[ctx->tx_length++] = crc >> 8;

    /* Clear RX buffer */
    ctx->rx_length = 0;
    ctx->state = MODBUS_STATE_TRANSMITTING;

    /* Switch to TX mode */
    if (ctx->tx_start_cb)
        ctx->tx_start_cb();

    /* Send request */
    modbus_port_send(ctx->tx_buffer, ctx->tx_length);

    /* Switch to RX mode */
    if (ctx->tx_end_cb)
        ctx->tx_end_cb();

    /* Wait for response */
    ctx->state = MODBUS_STATE_WAITING;
    uint32_t start_time = modbus_port_get_time_ms();

    while (ctx->state == MODBUS_STATE_WAITING || ctx->state == MODBUS_STATE_RECEIVING) {
        /* Check timeout */
        if (modbus_port_get_time_ms() - start_time > ctx->timeout_ms) {
            ctx->state = MODBUS_STATE_IDLE;
            return false;
        }

        /* Check if frame received (T3.5 timeout) */
        if (ctx->state == MODBUS_STATE_RECEIVING) {
            uint32_t elapsed_us = modbus_port_get_time_us() - ctx->rx_timestamp;
            if (elapsed_us >= ctx->t35_us) {
                ctx->state = MODBUS_STATE_PROCESSING;
                break;
            }
        }

        /* Small delay to prevent busy waiting */
        modbus_port_delay_us(100);
    }

    /* Validate response */
    if (ctx->rx_length < 5)
        return false;

    if (!modbus_rtu_check_crc(ctx->rx_buffer, ctx->rx_length))
        return false;

    if (ctx->rx_buffer[0] != slave_id)
        return false;

    /* Check for exception */
    if (ctx->rx_buffer[1] & 0x80) {
        ctx->current_frame.exception_code = ctx->rx_buffer[2];
        return false;
    }

    if (ctx->rx_buffer[1] != function_code)
        return false;

    return true;
}

/**
 * @brief   Master: Read Coils (FC 0x01)
 */
bool
modbus_rtu_master_read_coils(modbus_rtu_ctx_t *ctx, uint8_t slave_id,
                            uint16_t addr, uint16_t count, uint8_t *dest) {
    if (!ctx->is_master || count == 0 || count > 2000 || !dest)
        return false;

    if (!master_send_request(ctx, slave_id, MODBUS_FC_READ_COILS, addr, count, NULL, 0))
        return false;

    /* Parse response */
    uint8_t byte_count = ctx->rx_buffer[2];
    if (byte_count != (count + 7) / 8)
        return false;

    memcpy(dest, &ctx->rx_buffer[3], byte_count);

    ctx->state = MODBUS_STATE_IDLE;
    return true;
}

/**
 * @brief   Master: Read Discrete Inputs (FC 0x02)
 */
bool
modbus_rtu_master_read_discrete_inputs(modbus_rtu_ctx_t *ctx, uint8_t slave_id,
                                      uint16_t addr, uint16_t count, uint8_t *dest) {
    if (!ctx->is_master || count == 0 || count > 2000 || !dest)
        return false;

    if (!master_send_request(ctx, slave_id, MODBUS_FC_READ_DISCRETE_INPUTS, addr, count, NULL, 0))
        return false;

    /* Parse response */
    uint8_t byte_count = ctx->rx_buffer[2];
    if (byte_count != (count + 7) / 8)
        return false;

    memcpy(dest, &ctx->rx_buffer[3], byte_count);

    ctx->state = MODBUS_STATE_IDLE;
    return true;
}

/**
 * @brief   Master: Read Holding Registers (FC 0x03)
 */
bool
modbus_rtu_master_read_holding_registers(modbus_rtu_ctx_t *ctx, uint8_t slave_id,
                                        uint16_t addr, uint16_t count, uint16_t *dest) {
    if (!ctx->is_master || count == 0 || count > 125 || !dest)
        return false;

    if (!master_send_request(ctx, slave_id, MODBUS_FC_READ_HOLDING_REGISTERS, addr, count, NULL, 0))
        return false;

    /* Parse response */
    uint8_t byte_count = ctx->rx_buffer[2];
    if (byte_count != count * 2)
        return false;

    for (uint16_t i = 0; i < count; i++) {
        dest[i] = (ctx->rx_buffer[3 + i * 2] << 8) | ctx->rx_buffer[4 + i * 2];
    }

    ctx->state = MODBUS_STATE_IDLE;
    return true;
}

/**
 * @brief   Master: Read Input Registers (FC 0x04)
 */
bool
modbus_rtu_master_read_input_registers(modbus_rtu_ctx_t *ctx, uint8_t slave_id,
                                      uint16_t addr, uint16_t count, uint16_t *dest) {
    if (!ctx->is_master || count == 0 || count > 125 || !dest)
        return false;

    if (!master_send_request(ctx, slave_id, MODBUS_FC_READ_INPUT_REGISTERS, addr, count, NULL, 0))
        return false;

    /* Parse response */
    uint8_t byte_count = ctx->rx_buffer[2];
    if (byte_count != count * 2)
        return false;

    for (uint16_t i = 0; i < count; i++) {
        dest[i] = (ctx->rx_buffer[3 + i * 2] << 8) | ctx->rx_buffer[4 + i * 2];
    }

    ctx->state = MODBUS_STATE_IDLE;
    return true;
}

/**
 * @brief   Master: Write Single Coil (FC 0x05)
 */
bool
modbus_rtu_master_write_single_coil(modbus_rtu_ctx_t *ctx, uint8_t slave_id,
                                   uint16_t addr, bool value) {
    if (!ctx->is_master)
        return false;

    uint16_t coil_value = value ? 0xFF00 : 0x0000;

    if (!master_send_request(ctx, slave_id, MODBUS_FC_WRITE_SINGLE_COIL, addr, coil_value, NULL, 0))
        return false;

    /* Verify echo */
    uint16_t echo_addr = (ctx->rx_buffer[2] << 8) | ctx->rx_buffer[3];
    uint16_t echo_value = (ctx->rx_buffer[4] << 8) | ctx->rx_buffer[5];

    if (echo_addr != addr || echo_value != coil_value)
        return false;

    ctx->state = MODBUS_STATE_IDLE;
    return true;
}

/**
 * @brief   Master: Write Single Register (FC 0x06)
 */
bool
modbus_rtu_master_write_single_register(modbus_rtu_ctx_t *ctx, uint8_t slave_id,
                                       uint16_t addr, uint16_t value) {
    if (!ctx->is_master)
        return false;

    if (!master_send_request(ctx, slave_id, MODBUS_FC_WRITE_SINGLE_REGISTER, addr, value, NULL, 0))
        return false;

    /* Verify echo */
    uint16_t echo_addr = (ctx->rx_buffer[2] << 8) | ctx->rx_buffer[3];
    uint16_t echo_value = (ctx->rx_buffer[4] << 8) | ctx->rx_buffer[5];

    if (echo_addr != addr || echo_value != value)
        return false;

    ctx->state = MODBUS_STATE_IDLE;
    return true;
}

/**
 * @brief   Master: Write Multiple Coils (FC 0x0F)
 */
bool
modbus_rtu_master_write_multiple_coils(modbus_rtu_ctx_t *ctx, uint8_t slave_id,
                                      uint16_t addr, uint16_t count, const uint8_t *values) {
    if (!ctx->is_master || count == 0 || count > 1968 || !values)
        return false;

    uint8_t byte_count = (count + 7) / 8;
    uint8_t extra_data[256];
    extra_data[0] = byte_count;
    memcpy(&extra_data[1], values, byte_count);

    if (!master_send_request(ctx, slave_id, MODBUS_FC_WRITE_MULTIPLE_COILS, addr, count,
                           extra_data, byte_count + 1))
        return false;

    /* Verify echo */
    uint16_t echo_addr = (ctx->rx_buffer[2] << 8) | ctx->rx_buffer[3];
    uint16_t echo_count = (ctx->rx_buffer[4] << 8) | ctx->rx_buffer[5];

    if (echo_addr != addr || echo_count != count)
        return false;

    ctx->state = MODBUS_STATE_IDLE;
    return true;
}

/**
 * @brief   Master: Write Multiple Registers (FC 0x10)
 */
bool
modbus_rtu_master_write_multiple_registers(modbus_rtu_ctx_t *ctx, uint8_t slave_id,
                                          uint16_t addr, uint16_t count, const uint16_t *values) {
    if (!ctx->is_master || count == 0 || count > 123 || !values)
        return false;

    uint8_t byte_count = count * 2;
    uint8_t extra_data[256];
    extra_data[0] = byte_count;

    for (uint16_t i = 0; i < count; i++) {
        extra_data[1 + i * 2] = values[i] >> 8;
        extra_data[2 + i * 2] = values[i] & 0xFF;
    }

    if (!master_send_request(ctx, slave_id, MODBUS_FC_WRITE_MULTIPLE_REGISTERS, addr, count,
                           extra_data, byte_count + 1))
        return false;

    /* Verify echo */
    uint16_t echo_addr = (ctx->rx_buffer[2] << 8) | ctx->rx_buffer[3];
    uint16_t echo_count = (ctx->rx_buffer[4] << 8) | ctx->rx_buffer[5];

    if (echo_addr != addr || echo_count != count)
        return false;

    ctx->state = MODBUS_STATE_IDLE;
    return true;
}

