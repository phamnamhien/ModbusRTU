################################################################################
# Automatically-generated file. Do not edit!
# Toolchain: GNU Tools for STM32 (13.3.rel1)
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
D:/Documents/WORKSPACE/ModbusRTU/01_Firmwares/ModbusRTU/modbus_port.c \
D:/Documents/WORKSPACE/ModbusRTU/01_Firmwares/ModbusRTU/modbus_registers.c \
D:/Documents/WORKSPACE/ModbusRTU/01_Firmwares/ModbusRTU/modbus_rtu.c \
D:/Documents/WORKSPACE/ModbusRTU/01_Firmwares/ModbusRTU/modbus_rtu_master.c 

OBJS += \
./ModbusRTU/modbus_port.o \
./ModbusRTU/modbus_registers.o \
./ModbusRTU/modbus_rtu.o \
./ModbusRTU/modbus_rtu_master.o 

C_DEPS += \
./ModbusRTU/modbus_port.d \
./ModbusRTU/modbus_registers.d \
./ModbusRTU/modbus_rtu.d \
./ModbusRTU/modbus_rtu_master.d 


# Each subdirectory must supply rules for building sources it contributes
ModbusRTU/modbus_port.o: D:/Documents/WORKSPACE/ModbusRTU/01_Firmwares/ModbusRTU/modbus_port.c ModbusRTU/subdir.mk
	arm-none-eabi-gcc "$<" -mcpu=cortex-m3 -std=gnu11 -g3 -DDEBUG -DUSE_HAL_DRIVER -DSTM32F103xB -c -I../Core/Inc -I../Drivers/STM32F1xx_HAL_Driver/Inc -I../Drivers/STM32F1xx_HAL_Driver/Inc/Legacy -I../Drivers/CMSIS/Device/ST/STM32F1xx/Include -I../Drivers/CMSIS/Include -I"D:/Documents/WORKSPACE/ModbusRTU/01_Firmwares/ModbusRTU" -O0 -ffunction-sections -fdata-sections -Wall -fstack-usage -fcyclomatic-complexity -MMD -MP -MF"$(@:%.o=%.d)" -MT"$@" --specs=nano.specs -mfloat-abi=soft -mthumb -o "$@"
ModbusRTU/modbus_registers.o: D:/Documents/WORKSPACE/ModbusRTU/01_Firmwares/ModbusRTU/modbus_registers.c ModbusRTU/subdir.mk
	arm-none-eabi-gcc "$<" -mcpu=cortex-m3 -std=gnu11 -g3 -DDEBUG -DUSE_HAL_DRIVER -DSTM32F103xB -c -I../Core/Inc -I../Drivers/STM32F1xx_HAL_Driver/Inc -I../Drivers/STM32F1xx_HAL_Driver/Inc/Legacy -I../Drivers/CMSIS/Device/ST/STM32F1xx/Include -I../Drivers/CMSIS/Include -I"D:/Documents/WORKSPACE/ModbusRTU/01_Firmwares/ModbusRTU" -O0 -ffunction-sections -fdata-sections -Wall -fstack-usage -fcyclomatic-complexity -MMD -MP -MF"$(@:%.o=%.d)" -MT"$@" --specs=nano.specs -mfloat-abi=soft -mthumb -o "$@"
ModbusRTU/modbus_rtu.o: D:/Documents/WORKSPACE/ModbusRTU/01_Firmwares/ModbusRTU/modbus_rtu.c ModbusRTU/subdir.mk
	arm-none-eabi-gcc "$<" -mcpu=cortex-m3 -std=gnu11 -g3 -DDEBUG -DUSE_HAL_DRIVER -DSTM32F103xB -c -I../Core/Inc -I../Drivers/STM32F1xx_HAL_Driver/Inc -I../Drivers/STM32F1xx_HAL_Driver/Inc/Legacy -I../Drivers/CMSIS/Device/ST/STM32F1xx/Include -I../Drivers/CMSIS/Include -I"D:/Documents/WORKSPACE/ModbusRTU/01_Firmwares/ModbusRTU" -O0 -ffunction-sections -fdata-sections -Wall -fstack-usage -fcyclomatic-complexity -MMD -MP -MF"$(@:%.o=%.d)" -MT"$@" --specs=nano.specs -mfloat-abi=soft -mthumb -o "$@"
ModbusRTU/modbus_rtu_master.o: D:/Documents/WORKSPACE/ModbusRTU/01_Firmwares/ModbusRTU/modbus_rtu_master.c ModbusRTU/subdir.mk
	arm-none-eabi-gcc "$<" -mcpu=cortex-m3 -std=gnu11 -g3 -DDEBUG -DUSE_HAL_DRIVER -DSTM32F103xB -c -I../Core/Inc -I../Drivers/STM32F1xx_HAL_Driver/Inc -I../Drivers/STM32F1xx_HAL_Driver/Inc/Legacy -I../Drivers/CMSIS/Device/ST/STM32F1xx/Include -I../Drivers/CMSIS/Include -I"D:/Documents/WORKSPACE/ModbusRTU/01_Firmwares/ModbusRTU" -O0 -ffunction-sections -fdata-sections -Wall -fstack-usage -fcyclomatic-complexity -MMD -MP -MF"$(@:%.o=%.d)" -MT"$@" --specs=nano.specs -mfloat-abi=soft -mthumb -o "$@"

clean: clean-ModbusRTU

clean-ModbusRTU:
	-$(RM) ./ModbusRTU/modbus_port.cyclo ./ModbusRTU/modbus_port.d ./ModbusRTU/modbus_port.o ./ModbusRTU/modbus_port.su ./ModbusRTU/modbus_registers.cyclo ./ModbusRTU/modbus_registers.d ./ModbusRTU/modbus_registers.o ./ModbusRTU/modbus_registers.su ./ModbusRTU/modbus_rtu.cyclo ./ModbusRTU/modbus_rtu.d ./ModbusRTU/modbus_rtu.o ./ModbusRTU/modbus_rtu.su ./ModbusRTU/modbus_rtu_master.cyclo ./ModbusRTU/modbus_rtu_master.d ./ModbusRTU/modbus_rtu_master.o ./ModbusRTU/modbus_rtu_master.su

.PHONY: clean-ModbusRTU

