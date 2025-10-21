#ifndef MODBUS_PORT_H
#define MODBUS_PORT_H

#include <stdint.h>
#include <stdbool.h>

/**
 * @file    modbus_port.h
 * @brief   Platform-specific porting layer for Modbus RTU
 * @note    Implement these functions for your specific platform
 */

/**
 * @brief   Initialize UART hardware
 * @param   baudrate: Baud rate (e.g., 9600, 19200, 115200)
 * @param   parity: 0=None, 1=Odd, 2=Even
 * @param   stop_bits: 1 or 2
 * @note    Must enable RX interrupt and call modbus_rtu_rx_byte() in ISR
 */
void modbus_port_uart_init(uint32_t baudrate, uint8_t parity, uint8_t stop_bits);

/**
 * @brief   Send data via UART
 * @param   data: Data buffer to send
 * @param   length: Number of bytes to send
 * @note    Should block until all data is sent, or use TX complete interrupt
 */
void modbus_port_send(const uint8_t *data, uint16_t length);

/**
 * @brief   Get current time in milliseconds
 * @return  Current time in ms (32-bit, wraps around)
 * @note    Used for timeout detection
 */
uint32_t modbus_port_get_time_ms(void);

/**
 * @brief   Get current time in microseconds
 * @return  Current time in us (32-bit, wraps around)
 * @note    Used for T3.5 character timeout detection
 */
uint32_t modbus_port_get_time_us(void);

/**
 * @brief   Delay in microseconds
 * @param   us: Delay time in microseconds
 */
void modbus_port_delay_us(uint32_t us);

/**
 * @brief   Enable/disable interrupts (optional, for critical sections)
 * @param   enable: true to enable, false to disable
 */
void modbus_port_set_interrupts(bool enable);

/**
 * @brief   Initialize timer for T3.5 timeout detection
 * @param   period_us: Timer period in microseconds (T3.5 value)
 * @note    Timer ISR should call modbus_rtu_timer_callback()
 */
void modbus_port_timer_init(uint32_t period_us);

/**
 * @brief   Start/stop timer
 * @param   enable: true to start, false to stop
 */
void modbus_port_timer_enable(bool enable);

/**
 * @brief   Get timer handle (platform specific)
 * @return  Pointer to timer handle (for use in ISR)
 * @note    STM32: returns TIM_HandleTypeDef*, cast to void* for portability
 */
void* modbus_port_get_timer_handle(void);

/**
 * @brief   Get received byte from UART (for HAL callback mode)
 * @return  Last received byte
 */
uint8_t modbus_port_get_rx_byte(void);

/**
 * @brief   Start receiving next UART byte (for HAL callback mode)
 */
void modbus_port_uart_receive_next(void);

#endif /* MODBUS_PORT_H */

