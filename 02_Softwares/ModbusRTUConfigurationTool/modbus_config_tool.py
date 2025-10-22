# -*- coding: utf-8 -*-
"""
modbus_config_tool.py - Enhanced Main Logic
Run this file to start the enhanced application
"""

import sys
import json
import re
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from ui_modbus_config import Ui_MainWindow


class RegisterRange:
    def __init__(self, start_addr, count, reg_type):
        self.start_addr = start_addr
        self.count = count
        self.reg_type = reg_type


class ModbusConfigTool(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        self.config = {
            'slave_id': 1,
            'is_master': False,
            'target_slaves': [],
            'slave_registers': {},
            'registers': [],
            'settings': self.get_default_settings()
        }
        self.current_selected_slave = None
        
        self.connect_signals()
        self.update_slave_config_display()
        self.update_mapped_address()
        self.update_register_management_state()
        self.update_operation_mode_visibility()
        self.statusbar.showMessage('Ready - Enhanced Modbus RTU Configuration Tool v2.0')
        
    def get_default_settings(self):
        return {
            'common': [
                {'var_name': 'MODBUS_BAUDRATE', 'value': '9600', 'description': 'UART baudrate'},
                {'var_name': 'MODBUS_DATA_BITS', 'value': '8', 'description': 'Data bits: 7 or 8'},
                {'var_name': 'MODBUS_PARITY', 'value': '0', 'description': 'Parity: 0=None, 1=Even, 2=Odd'},
                {'var_name': 'MODBUS_STOP_BITS', 'value': '1', 'description': 'Stop bits: 1 or 2'},
            ],
            'master': [
                {'var_name': 'MODBUS_TIMEOUT_MS', 'value': '1000', 'description': 'Response timeout (ms)'},
                {'var_name': 'MODBUS_FRAME_INTERVAL_MS', 'value': '10', 'description': 'Time between frames in one cycle (ms)'},
                {'var_name': 'MODBUS_CYCLE_INTERVAL_MS', 'value': '100', 'description': 'Time between complete cycles (ms)'},
                {'var_name': 'MODBUS_MAX_RETRIES', 'value': '3', 'description': 'Maximum retry attempts'},
            ],
            'slave': [
                {'var_name': 'MODBUS_SLAVE_ID', 'value': '1', 'description': 'Modbus slave address (1-247)'},
                {'var_name': 'MODBUS_RESPONSE_DELAY_MS', 'value': '0', 'description': 'Response delay (ms)'},
            ]
        }
    
    def connect_signals(self):
        self.action_new.triggered.connect(self.new_config)
        self.action_open.triggered.connect(self.open_config)
        self.action_save.triggered.connect(self.save_config)
        self.action_export.triggered.connect(self.export_library)
        self.action_import.triggered.connect(self.import_library)
        
        self.device_type.currentTextChanged.connect(self.on_device_type_changed)
        self.add_target_btn.clicked.connect(self.add_target_slave)
        self.delete_target_btn.clicked.connect(self.delete_selected_slave)
        self.target_slaves_list.itemClicked.connect(self.on_slave_selected)
        
        self.settings_btn.clicked.connect(self.open_settings_dialog)
        
        self.reg_tag_name.textChanged.connect(self.validate_tag_name)
        self.reg_address.valueChanged.connect(self.on_address_changed)
        self.reg_type.currentIndexChanged.connect(self.on_type_changed)
        self.reg_operation.currentTextChanged.connect(self.on_operation_changed)  # NEW
        self.add_reg_btn.clicked.connect(self.add_register)
        self.quick_add_5_btn.clicked.connect(lambda: self.quick_add_consecutive_registers(5))
        self.quick_add_10_btn.clicked.connect(lambda: self.quick_add_consecutive_registers(10))
        self.remove_all_btn.clicked.connect(self.remove_all_registers)
    
    def validate_tag_name(self, text):
        if text:
            valid = re.match(r'^[A-Z0-9_]*$', text) is not None
            if valid:
                self.reg_tag_name.setStyleSheet("")
            else:
                self.reg_tag_name.setStyleSheet("border: 2px solid red;")
        else:
            self.reg_tag_name.setStyleSheet("")
    
    def generate_default_tag_name(self, internal_addr, reg_type):
        """Generate default tag name based on register type and address"""
        type_prefix = ['COIL', 'DI', 'IR', 'HR'][reg_type]
        return f'{type_prefix}_{internal_addr:04d}'
    
    def open_settings_dialog(self):
        dialog = SettingsDialog(self.config, self)
        if dialog.exec_() == QDialog.Accepted:
            self.config['settings'] = dialog.get_settings()
            self.statusbar.showMessage('Configuration settings updated')
    
    def on_device_type_changed(self, text):
        self.config['is_master'] = (text == 'Master')
        self.current_selected_slave = None
        self.update_slave_config_display()
        self.update_register_management_state()
        self.update_operation_mode_visibility()
    
    def update_operation_mode_visibility(self):
        """Show/hide Operation and Mode fields based on device type"""
        is_master = self.config['is_master']
        
        # Show operation and mode controls only for Master
        self.operation_label.setVisible(is_master)
        self.reg_operation.setVisible(is_master)
        self.mode_label.setVisible(is_master)
        self.reg_mode.setVisible(is_master)
        
        # Enable/disable mode based on operation selection
        if is_master:
            self.on_operation_changed()
    
    def on_operation_changed(self):
        """Enable/disable mode combo based on operation selection"""
        is_write = self.reg_operation.currentText() == 'Write'
        self.reg_mode.setEnabled(is_write)
        if not is_write:
            self.reg_mode.setCurrentIndex(0)  # Reset to One-time
    
    def update_slave_config_display(self):
        if self.config['is_master']:
            self.slave_id_widget.hide()
            self.target_slaves_widget.show()
        else:
            self.slave_id_widget.hide()
            self.target_slaves_widget.hide()
    
    def update_register_management_state(self):
        if self.config['is_master']:
            if self.current_selected_slave is not None:
                self.register_status_label.setText(f'Master Mode: Managing registers for Slave {self.current_selected_slave}')
                self.register_status_label.setStyleSheet("font-weight: bold; color: blue; padding: 5px;")
                enable = True
            else:
                self.register_status_label.setText('Master Mode: Select a slave to manage its registers')
                self.register_status_label.setStyleSheet("font-weight: bold; color: orange; padding: 5px;")
                enable = False
            
            self.add_reg_btn.setEnabled(enable)
            self.reg_address.setEnabled(enable)
            self.reg_type.setEnabled(enable)
            self.reg_tag_name.setEnabled(enable)
            self.reg_operation.setEnabled(enable)
            self.reg_mode.setEnabled(enable and self.reg_operation.currentText() == 'Write')
            self.quick_add_5_btn.setEnabled(enable)
            self.quick_add_10_btn.setEnabled(enable)
            self.remove_all_btn.setEnabled(enable)
        else:
            self.register_status_label.setText('Slave Mode: Managing local registers')
            self.register_status_label.setStyleSheet("font-weight: bold; color: green; padding: 5px;")
            self.add_reg_btn.setEnabled(True)
            self.reg_address.setEnabled(True)
            self.reg_type.setEnabled(True)
            self.reg_tag_name.setEnabled(True)
            self.reg_operation.setEnabled(False)  # N/A for slave
            self.reg_mode.setEnabled(False)       # N/A for slave
            self.quick_add_5_btn.setEnabled(True)
            self.quick_add_10_btn.setEnabled(True)
            self.remove_all_btn.setEnabled(True)
        
        self.update_register_table()
        self.optimize_ranges()
    
    def add_target_slave(self):
        slave_id = self.target_slave_input.value()
        
        if slave_id in self.config['target_slaves']:
            QMessageBox.warning(self, 'Warning', f'Slave ID {slave_id} already exists!')
            return
        
        self.target_slaves_list.addItem(f'Slave {slave_id}')
        self.config['target_slaves'].append(slave_id)
        
        if 'slave_registers' not in self.config:
            self.config['slave_registers'] = {}
        self.config['slave_registers'][slave_id] = []
        
        self.target_slave_input.setValue(slave_id + 1)
        self.statusbar.showMessage(f'Added target slave {slave_id}')
        
        self.target_slaves_list.setCurrentRow(self.target_slaves_list.count() - 1)
        self.current_selected_slave = slave_id
        self.update_register_management_state()
    
    def delete_selected_slave(self):
        current_item = self.target_slaves_list.currentItem()
        if current_item is None:
            QMessageBox.warning(self, 'Warning', 'Please select a slave to delete!')
            return
        
        try:
            item_text = current_item.text()
            if 'Slave ' in item_text:
                slave_id = int(item_text.replace('Slave ', ''))
                
                if slave_id in self.config['target_slaves']:
                    self.config['target_slaves'].remove(slave_id)
                if 'slave_registers' in self.config and slave_id in self.config['slave_registers']:
                    del self.config['slave_registers'][slave_id]
                
                self.target_slaves_list.takeItem(self.target_slaves_list.row(current_item))
                
                if self.current_selected_slave == slave_id:
                    self.current_selected_slave = None
                    self.update_register_management_state()
                
                self.statusbar.showMessage(f'Deleted slave {slave_id}')
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Failed to delete slave: {str(e)}')
    
    def on_slave_selected(self, item):
        try:
            item_text = item.text()
            if 'Slave ' in item_text:
                slave_id = int(item_text.replace('Slave ', ''))
                self.current_selected_slave = slave_id
                self.update_register_management_state()
                self.statusbar.showMessage(f'Selected slave {slave_id} for register management')
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Failed to select slave: {str(e)}')
    
    def on_address_changed(self):
        self.update_mapped_address()
    
    def on_type_changed(self):
        self.update_mapped_address()
    
    def update_mapped_address(self):
        internal_addr = self.reg_address.value()
        reg_type = self.reg_type.currentIndex()
        
        if reg_type == 0:
            mapped_addr = internal_addr + 1
            self.mapped_address_label.setText(f'{mapped_addr} (Coil)')
        elif reg_type == 1:
            mapped_addr = 10000 + internal_addr + 1
            self.mapped_address_label.setText(f'{mapped_addr} (DI)')
        elif reg_type == 2:
            mapped_addr = 30000 + internal_addr + 1
            self.mapped_address_label.setText(f'{mapped_addr} (IR)')
        elif reg_type == 3:
            mapped_addr = 40000 + internal_addr + 1
            self.mapped_address_label.setText(f'{mapped_addr} (HR)')
        else:
            self.mapped_address_label.setText('-')
    
    def add_register(self):
        tag_name = self.reg_tag_name.text().strip().upper()
        internal_addr = self.reg_address.value()
        reg_type = self.reg_type.currentIndex()
        
        # Auto-generate tag name if empty
        if not tag_name:
            tag_name = self.generate_default_tag_name(internal_addr, reg_type)
        else:
            # Validate custom tag name
            if not re.match(r'^[A-Z0-9_]+$', tag_name):
                QMessageBox.warning(self, 'Error', 'Tag name must be uppercase with numbers and underscores only!')
                return
        
        if reg_type == 0:
            mapped_addr = internal_addr + 1
        elif reg_type == 1:
            mapped_addr = 10000 + internal_addr + 1
        elif reg_type == 2:
            mapped_addr = 30000 + internal_addr + 1
        elif reg_type == 3:
            mapped_addr = 40000 + internal_addr + 1
        else:
            QMessageBox.warning(self, 'Error', f'Invalid register type!')
            return
        
        current_registers = self.get_current_register_list()
        
        for reg in current_registers:
            if reg.get('tag_name', '') == tag_name:
                QMessageBox.warning(self, 'Warning', f'Tag name "{tag_name}" already exists!')
                return
        
        for reg in current_registers:
            if reg['internal_address'] == internal_addr and reg['type'] == reg_type:
                QMessageBox.warning(self, 'Warning', f'Register {mapped_addr} already exists!')
                return
        
        register = {
            'tag_name': tag_name,
            'internal_address': internal_addr,
            'mapped_address': mapped_addr,
            'type': reg_type,
            'modbus_type': [0, 1, 3, 4][reg_type],
            'type_name': self.reg_type.currentText()
        }
        
        # Add operation and mode for Master mode
        if self.config['is_master']:
            register['operation'] = self.reg_operation.currentText()
            register['mode'] = self.reg_mode.currentText() if self.reg_operation.currentText() == 'Write' else 'N/A'
        else:
            register['operation'] = 'N/A'  # Slave doesn't have operation concept
            register['mode'] = 'N/A'
        
        if self.config['is_master'] and self.current_selected_slave is not None:
            if 'slave_registers' not in self.config:
                self.config['slave_registers'] = {}
            if self.current_selected_slave not in self.config['slave_registers']:
                self.config['slave_registers'][self.current_selected_slave] = []
            self.config['slave_registers'][self.current_selected_slave].append(register)
        else:
            self.config['registers'].append(register)
        
        self.update_register_table()
        self.optimize_ranges()
        
        self.reg_address.setValue(internal_addr + 1)
        self.reg_tag_name.clear()
        self.update_mapped_address()
        
        self.statusbar.showMessage(f'Added register {tag_name} ({mapped_addr})')
    
    def get_current_register_list(self):
        if self.config['is_master'] and self.current_selected_slave is not None:
            if 'slave_registers' not in self.config:
                self.config['slave_registers'] = {}
            if self.current_selected_slave not in self.config['slave_registers']:
                self.config['slave_registers'][self.current_selected_slave] = []
            return self.config['slave_registers'][self.current_selected_slave]
        else:
            return self.config['registers']
    
    def update_register_table(self):
        current_registers = self.get_current_register_list()
        self.register_table.setRowCount(len(current_registers))
        
        # Hide/Show Operation and Mode columns based on device type
        if self.config['is_master']:
            self.register_table.setColumnHidden(4, False)  # Show Operation
            self.register_table.setColumnHidden(5, False)  # Show Mode
        else:
            self.register_table.setColumnHidden(4, True)   # Hide Operation
            self.register_table.setColumnHidden(5, True)   # Hide Mode
        
        for i, reg in enumerate(current_registers):
            self.register_table.setItem(i, 0, QTableWidgetItem(reg.get('tag_name', 'N/A')))
            self.register_table.setItem(i, 1, QTableWidgetItem(str(reg['internal_address'])))
            self.register_table.setItem(i, 2, QTableWidgetItem(str(reg['mapped_address'])))
            self.register_table.setItem(i, 3, QTableWidgetItem(reg['type_name']))
            
            # Operation column - dropdown for Master mode
            if self.config['is_master']:
                operation_combo = QComboBox()
                operation_combo.addItems(['Read', 'Write'])
                operation_combo.setCurrentText(reg.get('operation', 'Read'))
                operation_combo.currentTextChanged.connect(lambda text, row=i: self.on_table_operation_changed(row, text))
                self.register_table.setCellWidget(i, 4, operation_combo)
            else:
                self.register_table.setItem(i, 4, QTableWidgetItem('N/A'))
            
            # Mode column - dropdown for Master mode, only enabled for Write
            if self.config['is_master']:
                mode_combo = QComboBox()
                mode_combo.addItems(['One-time', 'Cyclic'])
                current_mode = reg.get('mode', 'One-time')
                if current_mode != 'N/A':
                    mode_combo.setCurrentText(current_mode)
                mode_combo.setEnabled(reg.get('operation', 'Read') == 'Write')
                mode_combo.currentTextChanged.connect(lambda text, row=i: self.on_table_mode_changed(row, text))
                self.register_table.setCellWidget(i, 5, mode_combo)
            else:
                self.register_table.setItem(i, 5, QTableWidgetItem('N/A'))
            
            remove_btn = QPushButton('Remove')
            remove_btn.clicked.connect(lambda checked, idx=i: self.remove_register(idx))
            self.register_table.setCellWidget(i, 6, remove_btn)
    
    def on_table_operation_changed(self, row, operation):
        """Handle operation change in table"""
        current_registers = self.get_current_register_list()
        if 0 <= row < len(current_registers):
            current_registers[row]['operation'] = operation
            
            # Update mode based on operation
            if operation == 'Read':
                current_registers[row]['mode'] = 'N/A'
                # Disable mode combo for this row
                mode_combo = self.register_table.cellWidget(row, 5)
                if isinstance(mode_combo, QComboBox):
                    mode_combo.setEnabled(False)
                    mode_combo.setCurrentText('One-time')  # Reset to default
            else:  # Write
                if current_registers[row]['mode'] == 'N/A':
                    current_registers[row]['mode'] = 'One-time'
                # Enable mode combo for this row
                mode_combo = self.register_table.cellWidget(row, 5)
                if isinstance(mode_combo, QComboBox):
                    mode_combo.setEnabled(True)
            
            self.statusbar.showMessage(f'Updated {current_registers[row]["tag_name"]} operation to {operation}')
    
    def on_table_mode_changed(self, row, mode):
        """Handle mode change in table"""
        current_registers = self.get_current_register_list()
        if 0 <= row < len(current_registers):
            current_registers[row]['mode'] = mode
            self.statusbar.showMessage(f'Updated {current_registers[row]["tag_name"]} mode to {mode}')
    
    def remove_register(self, index):
        current_registers = self.get_current_register_list()
        if 0 <= index < len(current_registers):
            removed_reg = current_registers.pop(index)
            self.update_register_table()
            self.optimize_ranges()
            self.statusbar.showMessage(f'Removed register {removed_reg.get("tag_name", "N/A")}')
    
    def remove_all_registers(self):
        current_registers = self.get_current_register_list()
        if not current_registers:
            QMessageBox.information(self, 'Info', 'No registers to remove!')
            return
        
        reply = QMessageBox.question(self, 'Confirm', 
                                   f'Are you sure you want to remove all {len(current_registers)} registers?',
                                   QMessageBox.Yes | QMessageBox.No, 
                                   QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            current_registers.clear()
            self.update_register_table()
            self.optimize_ranges()
            self.statusbar.showMessage('Removed all registers')
    
    def quick_add_consecutive_registers(self, count):
        start_addr = self.reg_address.value()
        reg_type = self.reg_type.currentIndex()
        
        added_count = 0
        
        for i in range(count):
            internal_addr = start_addr + i
            
            if reg_type == 0:
                mapped_addr = internal_addr + 1
            elif reg_type == 1:
                mapped_addr = 10000 + internal_addr + 1
            elif reg_type == 2:
                mapped_addr = 30000 + internal_addr + 1
            elif reg_type == 3:
                mapped_addr = 40000 + internal_addr + 1
            else:
                continue
            
            current_registers = self.get_current_register_list()
            
            exists = any(reg['internal_address'] == internal_addr and reg['type'] == reg_type 
                        for reg in current_registers)
            
            if not exists:
                tag_name = self.generate_default_tag_name(internal_addr, reg_type)
                
                register = {
                    'tag_name': tag_name,
                    'internal_address': internal_addr,
                    'mapped_address': mapped_addr,
                    'type': reg_type,
                    'modbus_type': [0, 1, 3, 4][reg_type],
                    'type_name': self.reg_type.currentText()
                }
                
                # Add operation and mode for Master mode
                if self.config['is_master']:
                    register['operation'] = self.reg_operation.currentText()
                    register['mode'] = self.reg_mode.currentText() if self.reg_operation.currentText() == 'Write' else 'N/A'
                else:
                    register['operation'] = 'N/A'
                    register['mode'] = 'N/A'
                
                if self.config['is_master'] and self.current_selected_slave is not None:
                    if 'slave_registers' not in self.config:
                        self.config['slave_registers'] = {}
                    if self.current_selected_slave not in self.config['slave_registers']:
                        self.config['slave_registers'][self.current_selected_slave] = []
                    self.config['slave_registers'][self.current_selected_slave].append(register)
                else:
                    self.config['registers'].append(register)
                
                added_count += 1
        
        self.update_register_table()
        self.optimize_ranges()
        
        self.reg_address.setValue(start_addr + count)
        self.update_mapped_address()
        
        self.statusbar.showMessage(f'Added {added_count} registers')
    
    def optimize_ranges(self):
        self.ranges_table.setRowCount(0)
        
        current_registers = self.get_current_register_list()
        if not current_registers:
            self.update_ranges_table([])
            return
        
        optimized_ranges = self.get_optimized_ranges_for_registers(current_registers)
        self.update_ranges_table(optimized_ranges)
    
    def get_optimized_ranges_for_registers(self, registers):
        if not registers:
            return []
        
        type_groups = {}
        for reg in registers:
            modbus_type = reg.get('modbus_type', [0, 1, 3, 4][reg['type']])
            
            if modbus_type not in type_groups:
                type_groups[modbus_type] = []
            type_groups[modbus_type].append(reg['internal_address'])
        
        optimized_ranges = []
        for modbus_type, addresses in type_groups.items():
            addresses.sort()
            ranges = self.create_ranges(addresses, modbus_type)
            optimized_ranges.extend(ranges)
        
        return optimized_ranges
    
    def create_ranges(self, addresses, reg_type):
        if not addresses:
            return []
        
        ranges = []
        start = addresses[0]
        count = 1
        
        for i in range(1, len(addresses)):
            if addresses[i] == addresses[i-1] + 1:
                count += 1
            else:
                ranges.append(RegisterRange(start, count, reg_type))
                start = addresses[i]
                count = 1
        
        ranges.append(RegisterRange(start, count, reg_type))
        
        return ranges
    
    def update_ranges_table(self, ranges):
        self.ranges_table.setRowCount(len(ranges))
        
        type_names = {0: 'Coil', 1: 'Discrete Input', 3: 'Input Register', 4: 'Holding Register'}
        
        for i, rng in enumerate(ranges):
            self.ranges_table.setItem(i, 0, QTableWidgetItem(str(rng.start_addr)))
            self.ranges_table.setItem(i, 1, QTableWidgetItem(str(rng.count)))
            self.ranges_table.setItem(i, 2, QTableWidgetItem(type_names.get(rng.reg_type, 'Unknown')))
            self.ranges_table.setItem(i, 3, QTableWidgetItem(f"{rng.count} regs/1 req"))
        
        current_registers = self.get_current_register_list()
        if len(current_registers) > 0:
            efficiency = ((len(current_registers) - len(ranges)) / len(current_registers) * 100)
            self.stats_label.setText(f'Statistics: {len(current_registers)} registers, {len(ranges)} ranges ({efficiency:.1f}% reduction)')
        else:
            self.stats_label.setText('Statistics: 0 registers, 0 ranges')
    
    def new_config(self):
        self.config = {
            'slave_id': 1,
            'is_master': False,
            'target_slaves': [],
            'slave_registers': {},
            'registers': [],
            'settings': self.get_default_settings()
        }
        self.current_selected_slave = None
        self.update_ui_from_config()
    
    def update_ui_from_config(self):
        self.device_type.setCurrentText('Master' if self.config['is_master'] else 'Slave')
        
        self.target_slaves_list.clear()
        if 'target_slaves' in self.config:
            for slave_id in self.config['target_slaves']:
                self.target_slaves_list.addItem(f'Slave {slave_id}')
        
        if 'settings' not in self.config:
            self.config['settings'] = self.get_default_settings()
        
        self.update_slave_config_display()
        self.update_operation_mode_visibility()
        self.update_register_table()
        self.optimize_ranges()
    
    def update_config_from_ui(self):
        self.config['is_master'] = self.device_type.currentText() == 'Master'
        
        self.config['target_slaves'] = []
        for i in range(self.target_slaves_list.count()):
            item_text = self.target_slaves_list.item(i).text()
            if 'Slave ' in item_text:
                slave_id = int(item_text.replace('Slave ', ''))
                self.config['target_slaves'].append(slave_id)
    
    def open_config(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Open Config', '', 'JSON Files (*.json)')
        if filename:
            try:
                with open(filename, 'r') as f:
                    self.config = json.load(f)
                if 'settings' not in self.config:
                    self.config['settings'] = self.get_default_settings()
                self.update_ui_from_config()
                self.statusbar.showMessage(f'Loaded config from {filename}')
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Failed to load config: {str(e)}')
    
    def save_config(self):
        self.update_config_from_ui()
        filename, _ = QFileDialog.getSaveFileName(self, 'Save Config', '', 'JSON Files (*.json)')
        if filename:
            try:
                with open(filename, 'w') as f:
                    json.dump(self.config, f, indent=2)
                self.statusbar.showMessage(f'Saved config to {filename}')
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Failed to save config: {str(e)}')
    
    def export_library(self):
        self.update_config_from_ui()
        
        output_dir = QFileDialog.getExistingDirectory(self, 'Select Output Directory')
        if not output_dir:
            return
        
        try:
            from modbus_code_generator import ModbusCodeGenerator
            generator = ModbusCodeGenerator(self.config)
            generator.generate_files(output_dir)
            self.statusbar.showMessage(f'Exported to {output_dir}')
            QMessageBox.information(self, 'Success', f'Files generated:\n- modbus_registers.h\n- modbus_registers.c')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to export: {str(e)}')
    
    def import_library(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Import Header', '', 'Header Files (*.h)')
        if filename:
            try:
                from modbus_code_generator import ModbusCodeGenerator
                generator = ModbusCodeGenerator(self.config)
                self.config = generator.parse_header(filename)
                self.update_ui_from_config()
                self.statusbar.showMessage(f'Imported from {filename}')
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Failed to import: {str(e)}')


class SettingsDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.settings = config.get('settings', {})
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle('Enhanced Modbus Configuration Settings v2.0')
        self.setMinimumSize(700, 500)
        
        layout = QVBoxLayout(self)
        
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # Common settings tab
        common_tab = QWidget()
        common_layout = QVBoxLayout(common_tab)
        
        common_label = QLabel('Common Settings:')
        common_label.setStyleSheet("font-weight: bold; margin: 5px;")
        common_layout.addWidget(common_label)
        
        self.common_table = self.create_settings_table(self.settings.get('common', []))
        common_layout.addWidget(self.common_table)
        
        tabs.addTab(common_tab, "Common")
        
        # Master settings tab
        master_tab = QWidget()
        master_layout = QVBoxLayout(master_tab)
        
        master_label = QLabel('Master Settings (Enhanced with Frame/Cycle timing):')
        master_label.setStyleSheet("font-weight: bold; margin: 5px;")
        master_layout.addWidget(master_label)
        
        timing_info = QLabel('â€¢ Frame Interval: Time between individual frames in one polling cycle\nâ€¢ Cycle Interval: Time between complete polling cycles')
        timing_info.setStyleSheet("color: blue; font-style: italic; margin: 5px;")
        master_layout.addWidget(timing_info)
        
        self.master_table = self.create_settings_table(self.settings.get('master', []))
        master_layout.addWidget(self.master_table)
        
        tabs.addTab(master_tab, "Master")
        
        # Slave settings tab
        slave_tab = QWidget()
        slave_layout = QVBoxLayout(slave_tab)
        
        slave_label = QLabel('Slave Settings:')
        slave_label.setStyleSheet("font-weight: bold; margin: 5px;")
        slave_layout.addWidget(slave_label)
        
        self.slave_table = self.create_settings_table(self.settings.get('slave', []))
        slave_layout.addWidget(self.slave_table)
        
        tabs.addTab(slave_tab, "Slave")
        
        button_layout = QHBoxLayout()
        
        ok_btn = QPushButton('OK')
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)
        
        cancel_btn = QPushButton('Cancel')
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def create_settings_table(self, settings):
        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(['Variable Name', 'Value', 'Description'])
        
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Interactive)
        header.setSectionResizeMode(1, QHeaderView.Interactive)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        
        table.setColumnWidth(0, 200)
        table.setColumnWidth(1, 120)
        
        table.setRowCount(len(settings))
        
        for i, setting in enumerate(settings):
            table.setItem(i, 0, QTableWidgetItem(setting['var_name']))
            
            # Create appropriate widget based on variable name
            value_widget = self.create_value_widget(setting['var_name'], setting['value'])
            if value_widget:
                table.setCellWidget(i, 1, value_widget)
            else:
                table.setItem(i, 1, QTableWidgetItem(setting['value']))
            
            table.setItem(i, 2, QTableWidgetItem(setting['description']))
        
        return table
    
    def create_value_widget(self, var_name, current_value):
        """Create appropriate widget for each setting"""
        if 'BAUDRATE' in var_name:
            combo = QComboBox()
            baudrates = ['1200', '2400', '4800', '9600', '19200', '38400', '57600', '115200']
            combo.addItems(baudrates)
            combo.setCurrentText(current_value)
            return combo
            
        elif 'DATA_BITS' in var_name:
            combo = QComboBox()
            combo.addItems(['7', '8'])
            combo.setCurrentText(current_value)
            return combo
            
        elif 'PARITY' in var_name:
            combo = QComboBox()
            combo.addItems(['0', '1', '2'])  # 0=None, 1=Even, 2=Odd
            combo.setCurrentText(current_value)
            return combo
            
        elif 'STOP_BITS' in var_name:
            combo = QComboBox()
            combo.addItems(['1', '2'])
            combo.setCurrentText(current_value)
            return combo
            
        elif 'SLAVE_ID' in var_name:
            spinbox = QSpinBox()
            spinbox.setRange(1, 247)
            spinbox.setValue(int(current_value))
            return spinbox
            
        elif var_name in ['MODBUS_TIMEOUT_MS', 'MODBUS_FRAME_INTERVAL_MS', 'MODBUS_CYCLE_INTERVAL_MS', 'MODBUS_RESPONSE_DELAY_MS']:
            spinbox = QSpinBox()
            spinbox.setRange(0, 60000)  # 0 to 60 seconds
            spinbox.setValue(int(current_value))
            spinbox.setSuffix(' ms')
            return spinbox
            
        elif 'RETRIES' in var_name:
            spinbox = QSpinBox()
            spinbox.setRange(1, 10)
            spinbox.setValue(int(current_value))
            return spinbox
        
        # Return None for text input (fallback)
        return None
    
    def get_settings(self):
        self.settings['common'] = []
        for row in range(self.common_table.rowCount()):
            var_name = self.common_table.item(row, 0).text()
            
            # Get value from widget or item
            widget = self.common_table.cellWidget(row, 1)
            if isinstance(widget, QComboBox):
                value = widget.currentText()
            elif isinstance(widget, QSpinBox):
                value = str(widget.value())
            else:
                value = self.common_table.item(row, 1).text()
            
            description = self.common_table.item(row, 2).text()
            
            self.settings['common'].append({
                'var_name': var_name,
                'value': value,
                'description': description
            })
        
        self.settings['master'] = []
        for row in range(self.master_table.rowCount()):
            var_name = self.master_table.item(row, 0).text()
            
            # Get value from widget or item
            widget = self.master_table.cellWidget(row, 1)
            if isinstance(widget, QComboBox):
                value = widget.currentText()
            elif isinstance(widget, QSpinBox):
                value = str(widget.value())
            else:
                value = self.master_table.item(row, 1).text()
            
            description = self.master_table.item(row, 2).text()
            
            self.settings['master'].append({
                'var_name': var_name,
                'value': value,
                'description': description
            })
        
        self.settings['slave'] = []
        for row in range(self.slave_table.rowCount()):
            var_name = self.slave_table.item(row, 0).text()
            
            # Get value from widget or item
            widget = self.slave_table.cellWidget(row, 1)
            if isinstance(widget, QComboBox):
                value = widget.currentText()
            elif isinstance(widget, QSpinBox):
                value = str(widget.value())
            else:
                value = self.slave_table.item(row, 1).text()
            
            description = self.slave_table.item(row, 2).text()
            
            self.settings['slave'].append({
                'var_name': var_name,
                'value': value,
                'description': description
            })
        
        return self.settings


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ModbusConfigTool()
    window.show()
    sys.exit(app.exec_())