/**
 * @file    modbus_port.c
 * @brief   Modbus RTU porting layer cho STM32F103 (HAL)
 */

#include "modbus_port.h"
#include "modbus_rtu.h"
#include "stm32f1xx_hal.h"
#include "main.h"

/* External handles */
extern UART_HandleTypeDef huart1;
extern modbus_rtu_ctx_t g_modbus_ctx;

/* Local timer handle */
static TIM_HandleTypeDef htim_modbus;

/* RX buffer cho HAL_UART_Receive_IT */
static uint8_t uart_rx_byte = 0;

/**
 * @brief   Initialize UART for Modbus RTU
 */
void
modbus_port_uart_init(uint32_t baudrate, uint8_t parity, uint8_t stop_bits) {
    /* Deinitialize UART */
    HAL_UART_DeInit(&huart1);

    /* Configure UART1 */
    huart1.Instance = USART1;
    huart1.Init.BaudRate = baudrate;
    huart1.Init.WordLength = (parity == 0) ? UART_WORDLENGTH_8B : UART_WORDLENGTH_9B;
    huart1.Init.StopBits = (stop_bits == 1) ? UART_STOPBITS_1 : UART_STOPBITS_2;

    if (parity == 0) {
        huart1.Init.Parity = UART_PARITY_NONE;
    } else if (parity == 1) {
        huart1.Init.Parity = UART_PARITY_ODD;
    } else {
        huart1.Init.Parity = UART_PARITY_EVEN;
    }

    huart1.Init.Mode = UART_MODE_TX_RX;
    huart1.Init.HwFlowCtl = UART_HWCONTROL_NONE;
    huart1.Init.OverSampling = UART_OVERSAMPLING_16;

    if (HAL_UART_Init(&huart1) != HAL_OK) {
        Error_Handler();
    }

    /* QUAN TRỌNG: Khởi tạo buffer trước khi gọi Receive_IT */
    uart_rx_byte = 0;

    /* Bắt đầu nhận UART với interrupt mode - 1 byte mỗi lần */
    if (HAL_UART_Receive_IT(&huart1, &uart_rx_byte, 1) != HAL_OK) {
        Error_Handler();
    }
}

/**
 * @brief   Send data via UART (blocking)
 */
void
modbus_port_send(const uint8_t *data, uint16_t length) {
    /* Send all bytes */
    HAL_UART_Transmit(&huart1, (uint8_t*)data, length, 100);
}

/**
 * @brief   Get time in milliseconds
 */
uint32_t
modbus_port_get_time_ms(void) {
    return HAL_GetTick();
}

/**
 * @brief   Get time in microseconds (dùng SysTick)
 */
uint32_t
modbus_port_get_time_us(void) {
    uint32_t ms = HAL_GetTick();
    uint32_t ticks = SysTick->VAL;
    uint32_t reload = SysTick->LOAD;

    /* SysTick đếm xuống, tính microseconds */
    return (ms * 1000) + ((reload - ticks) * 1000) / reload;
}

/**
 * @brief   Delay microseconds
 */
void
modbus_port_delay_us(uint32_t us) {
    uint32_t start = modbus_port_get_time_us();
    while ((modbus_port_get_time_us() - start) < us) {
        __NOP();
    }
}

/**
 * @brief   Enable/disable interrupts
 */
void
modbus_port_set_interrupts(bool enable) {
    if (enable) {
        __enable_irq();
    } else {
        __disable_irq();
    }
}

/**
 * @brief   Initialize timer for T3.5 detection
 * @param   period_us: T3.5 period in microseconds
 */
void
modbus_port_timer_init(uint32_t period_us) {
    TIM_ClockConfigTypeDef sClockSourceConfig = {0};
    TIM_MasterConfigTypeDef sMasterConfig = {0};

    /* Enable TIM2 clock */
    __HAL_RCC_TIM2_CLK_ENABLE();

    /* STM32F103: APB1 timer clock = 72MHz (với APB1 prescaler = 2)
     * Prescaler = 71 -> timer frequency = 72MHz / 72 = 1MHz = 1us per tick
     */
    htim_modbus.Instance = TIM2;
    htim_modbus.Init.Prescaler = 71;
    htim_modbus.Init.CounterMode = TIM_COUNTERMODE_UP;
    htim_modbus.Init.Period = period_us - 1;
    htim_modbus.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
    htim_modbus.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_DISABLE;

    if (HAL_TIM_Base_Init(&htim_modbus) != HAL_OK) {
        Error_Handler();
    }

    sClockSourceConfig.ClockSource = TIM_CLOCKSOURCE_INTERNAL;
    if (HAL_TIM_ConfigClockSource(&htim_modbus, &sClockSourceConfig) != HAL_OK) {
        Error_Handler();
    }

    sMasterConfig.MasterOutputTrigger = TIM_TRGO_RESET;
    sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
    if (HAL_TIMEx_MasterConfigSynchronization(&htim_modbus, &sMasterConfig) != HAL_OK) {
        Error_Handler();
    }

    /* Enable TIM2 interrupt */
    HAL_NVIC_SetPriority(TIM2_IRQn, 1, 0);
    HAL_NVIC_EnableIRQ(TIM2_IRQn);
}

/**
 * @brief   Enable/disable timer
 */
void
modbus_port_timer_enable(bool enable) {
    if (enable) {
        __HAL_TIM_SET_COUNTER(&htim_modbus, 0);
        HAL_TIM_Base_Start_IT(&htim_modbus);
    } else {
        HAL_TIM_Base_Stop_IT(&htim_modbus);
    }
}

/**
 * @brief   Get timer handle (để sử dụng trong interrupt)
 * @return  Pointer to TIM_HandleTypeDef (cast to void*)
 */
void* modbus_port_get_timer_handle(void) {
    return (void*)&htim_modbus;
}

/**
 * @brief   RS485 transmit enable (cho Simple API)
 */
void modbus_port_rs485_tx_enable(void) {
    /* Nếu có RS485 DE pin, uncomment dòng dưới */
    HAL_GPIO_WritePin(RS485_TXEN_GPIO_Port, RS485_TXEN_Pin, GPIO_PIN_SET);

    /* Delay nhỏ */
    for(volatile int i = 0; i < 10; i++);
}

/**
 * @brief   RS485 receive enable (cho Simple API)
 */
void modbus_port_rs485_rx_enable(void) {
    /* Delay nhỏ */
    for(volatile int i = 0; i < 10; i++);

    /* Nếu có RS485 DE pin, uncomment dòng dưới */
    HAL_GPIO_WritePin(RS485_TXEN_GPIO_Port, RS485_TXEN_Pin, GPIO_PIN_RESET);
}

/**
 * @brief   HAL UART Receive Complete Callback - gọi từ main.c
 */
uint8_t modbus_port_get_rx_byte(void) {
    return uart_rx_byte;
}

/**
 * @brief   Start next UART receive
 */
void modbus_port_uart_receive_next(void) {
    HAL_UART_Receive_IT(&huart1, &uart_rx_byte, 1);
}

