import sys
import json
import struct
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class RegisterRange:
    def __init__(self, start_addr, count, reg_type):
        self.start_addr = start_addr
        self.count = count
        self.reg_type = reg_type

class ModbusConfigTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = {
            'slave_id': 1,
            'is_master': False,
            'target_slaves': [],  # For master mode
            'slave_registers': {},  # Master mode: {slave_id: [registers]}
            'registers': []  # Slave mode registers
        }
        self.current_selected_slave = None  # Track which slave is selected in master mode
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('Modbus RTU Configuration Tool')
        self.setGeometry(100, 100, 1200, 800)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main horizontal layout
        main_layout = QHBoxLayout(central_widget)
        
        # Create horizontal splitter
        main_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(main_splitter)
        
        # LEFT PANEL - Create container widget
        left_container = QWidget()
        left_container_layout = QVBoxLayout(left_container)
        
        # =================== MODBUS CONFIGURATION GROUP ===================
        config_group = QGroupBox("Modbus Configuration")
        config_layout = QFormLayout(config_group)
        
        # Device type
        self.device_type = QComboBox()
        self.device_type.addItems(['Slave', 'Master'])
        self.device_type.currentTextChanged.connect(self.on_device_type_changed)
        config_layout.addRow('Device Type:', self.device_type)
        
        # Slave configuration container
        self.slave_config_container = QWidget()
        slave_config_layout = QVBoxLayout(self.slave_config_container)
        
        # Slave mode widgets
        self.slave_id_widget = QWidget()
        slave_id_layout = QHBoxLayout(self.slave_id_widget)
        slave_id_layout.addWidget(QLabel('Slave ID:'))
        self.slave_id = QSpinBox()
        self.slave_id.setRange(1, 247)
        self.slave_id.setValue(1)
        slave_id_layout.addWidget(self.slave_id)
        slave_id_layout.addStretch()
        
        # Master mode widgets  
        self.target_slaves_widget = QWidget()
        target_layout = QVBoxLayout(self.target_slaves_widget)
        target_layout.addWidget(QLabel('Target Slave IDs:'))
        
        target_input_layout = QHBoxLayout()
        self.target_slave_input = QSpinBox()
        self.target_slave_input.setRange(1, 247)
        self.target_slave_input.setValue(1)
        target_input_layout.addWidget(self.target_slave_input)
        
        self.add_target_btn = QPushButton('Add Slave')
        self.add_target_btn.clicked.connect(self.add_target_slave)
        target_input_layout.addWidget(self.add_target_btn)
        
        self.delete_target_btn = QPushButton('Delete Slave')
        self.delete_target_btn.clicked.connect(self.delete_selected_slave)
        target_input_layout.addWidget(self.delete_target_btn)
        
        target_input_layout.addStretch()
        target_layout.addLayout(target_input_layout)
        
        self.target_slaves_list = QListWidget()
        self.target_slaves_list.setMaximumHeight(80)
        self.target_slaves_list.itemClicked.connect(self.on_slave_selected)  # Single click to select
        target_layout.addWidget(self.target_slaves_list)
        
        slave_config_layout.addWidget(self.slave_id_widget)
        slave_config_layout.addWidget(self.target_slaves_widget)
        config_layout.addRow(self.slave_config_container)
        
        # Note label
        note_label = QLabel('Note: UART settings are configured in platform-specific port files')
        note_label.setWordWrap(True)
        note_label.setStyleSheet("color: gray; font-style: italic; font-size: 10px;")
        config_layout.addRow(note_label)
        
        # Add config group to left container
        left_container_layout.addWidget(config_group)
        
        # =================== REGISTER MANAGEMENT GROUP ===================
        reg_group = QGroupBox("Register Management")
        reg_layout = QVBoxLayout(reg_group)
        
        # Status label to show which slave's registers are being edited
        self.register_status_label = QLabel('Slave Mode: Managing local registers')
        self.register_status_label.setStyleSheet("font-weight: bold; color: green; padding: 5px;")
        reg_layout.addWidget(self.register_status_label)
        
        # Add register form
        add_form_layout = QGridLayout()
        
        # Internal address
        add_form_layout.addWidget(QLabel('Internal Address:'), 0, 0)
        self.reg_address = QSpinBox()
        self.reg_address.setRange(0, 65535)
        self.reg_address.setValue(0)  # Start from 0
        self.reg_address.valueChanged.connect(self.on_address_changed)
        add_form_layout.addWidget(self.reg_address, 0, 1)
        
        # Register type
        add_form_layout.addWidget(QLabel('Register Type:'), 1, 0)
        self.reg_type = QComboBox()
        self.reg_type.addItems(['Coil (0x)', 'Discrete Input (1x)', 'Input Register (3x)', 'Holding Register (4x)'])
        self.reg_type.setCurrentIndex(3)
        self.reg_type.currentIndexChanged.connect(self.on_type_changed)
        add_form_layout.addWidget(self.reg_type, 1, 1)
        
        # Mapped address display
        add_form_layout.addWidget(QLabel('Mapped Address:'), 2, 0)
        self.mapped_address_label = QLabel('1 (Coil)')  # Updated for address 0, type 0
        self.mapped_address_label.setStyleSheet("font-weight: bold; color: blue;")
        add_form_layout.addWidget(self.mapped_address_label, 2, 1)
        
        # Add button (enabled only when slave is selected in master mode)
        self.add_reg_btn = QPushButton('Add Register')
        self.add_reg_btn.clicked.connect(self.add_register)
        add_form_layout.addWidget(self.add_reg_btn, 3, 0, 1, 2)
        
        reg_layout.addLayout(add_form_layout)
        
        # Register table
        self.register_table = QTableWidget()
        self.register_table.setColumnCount(4)
        self.register_table.setHorizontalHeaderLabels(['Internal', 'Mapped', 'Type', 'Actions'])
        
        # Set column resize modes for responsive behavior
        header = self.register_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Interactive)       # Internal - user resizable
        header.setSectionResizeMode(1, QHeaderView.Interactive)       # Mapped - user resizable  
        header.setSectionResizeMode(2, QHeaderView.Stretch)           # Type - stretch to fill
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Actions - fit content
        
        # Set minimum column widths
        header.setMinimumSectionSize(60)
        self.register_table.setColumnWidth(0, 80)   # Internal initial width
        self.register_table.setColumnWidth(1, 80)   # Mapped initial width
        
        reg_layout.addWidget(self.register_table)
        
        # Add register group to left container
        left_container_layout.addWidget(reg_group)
        
        # Add left container to splitter
        main_splitter.addWidget(left_container)
        
        # =================== RIGHT PANEL - OPTIMIZED RANGES ===================
        ranges_group = QGroupBox("Optimized Register Ranges")
        ranges_layout = QVBoxLayout(ranges_group)
        
        # Optimize button
        self.optimize_btn = QPushButton('Manual Optimize Ranges')
        self.optimize_btn.clicked.connect(self.optimize_ranges)
        ranges_layout.addWidget(self.optimize_btn)
        
        # Ranges table
        self.ranges_table = QTableWidget()
        self.ranges_table.setColumnCount(4)
        self.ranges_table.setHorizontalHeaderLabels(['Start', 'Count', 'Type', 'Efficiency'])
        
        # Set column resize modes for responsive behavior
        ranges_header = self.ranges_table.horizontalHeader()
        ranges_header.setSectionResizeMode(0, QHeaderView.Interactive)       # Start - user resizable
        ranges_header.setSectionResizeMode(1, QHeaderView.Interactive)       # Count - user resizable
        ranges_header.setSectionResizeMode(2, QHeaderView.Stretch)           # Type - stretch
        ranges_header.setSectionResizeMode(3, QHeaderView.Interactive)       # Efficiency - user resizable
        
        # Set minimum column widths and initial sizes
        ranges_header.setMinimumSectionSize(50)
        self.ranges_table.setColumnWidth(0, 80)   # Start initial width
        self.ranges_table.setColumnWidth(1, 60)   # Count initial width
        self.ranges_table.setColumnWidth(3, 120)  # Efficiency initial width
        
        ranges_layout.addWidget(self.ranges_table)
        
        # Statistics label
        self.stats_label = QLabel('Statistics: 0 registers, 0 ranges')
        self.stats_label.setWordWrap(True)
        ranges_layout.addWidget(self.stats_label)
        
        # Add ranges group to splitter
        main_splitter.addWidget(ranges_group)
        
        # Set splitter proportions
        main_splitter.setSizes([600, 400])
        
        # Initialize UI state
        self.update_slave_config_display()
        self.update_mapped_address()
        self.update_register_management_state()
        
        # Menu bar
        self.create_menu_bar()
        
        # Status bar
        self.statusBar().showMessage('Ready - Modbus RTU Configuration Tool')
        
    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        new_action = QAction('New', self)
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.new_config)
        file_menu.addAction(new_action)
        
        open_action = QAction('Open Config', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_config)
        file_menu.addAction(open_action)
        
        save_action = QAction('Save Config', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_config)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        export_action = QAction('Export Library (.c/.h)', self)
        export_action.setShortcut('Ctrl+E')
        export_action.triggered.connect(self.export_library)
        file_menu.addAction(export_action)
        
        import_action = QAction('Import Library (.h)', self)
        import_action.triggered.connect(self.import_library)
        file_menu.addAction(import_action)
        
    def on_device_type_changed(self, text):
        self.config['is_master'] = (text == 'Master')
        self.current_selected_slave = None  # Reset selection
        self.update_slave_config_display()
        self.update_register_management_state()
        
    def update_slave_config_display(self):
        """Update the slave configuration display based on device type"""
        if self.config['is_master']:
            self.slave_id_widget.hide()
            self.target_slaves_widget.show()
        else:
            self.slave_id_widget.show()
            self.target_slaves_widget.hide()
            
    def update_register_management_state(self):
        """Update register management UI based on current mode and selection"""
        if self.config['is_master']:
            if self.current_selected_slave is not None:
                self.register_status_label.setText(f'Master Mode: Managing registers for Slave {self.current_selected_slave}')
                self.register_status_label.setStyleSheet("font-weight: bold; color: blue; padding: 5px;")
                self.add_reg_btn.setEnabled(True)
                self.reg_address.setEnabled(True)
                self.reg_type.setEnabled(True)
            else:
                self.register_status_label.setText('Master Mode: Select a slave to manage its registers')
                self.register_status_label.setStyleSheet("font-weight: bold; color: orange; padding: 5px;")
                self.add_reg_btn.setEnabled(False)
                self.reg_address.setEnabled(False)
                self.reg_type.setEnabled(False)
        else:
            self.register_status_label.setText('Slave Mode: Managing local registers')
            self.register_status_label.setStyleSheet("font-weight: bold; color: green; padding: 5px;")
            self.add_reg_btn.setEnabled(True)
            self.reg_address.setEnabled(True)
            self.reg_type.setEnabled(True)
        
        self.update_register_table()
        self.optimize_ranges()
            
    def add_target_slave(self):
        """Add target slave ID for master mode"""
        slave_id = self.target_slave_input.value()
        
        # Check if already exists
        if slave_id in self.config['target_slaves']:
            QMessageBox.warning(self, 'Warning', f'Slave ID {slave_id} already exists!')
            return
        
        # Add to list and config
        self.target_slaves_list.addItem(f'Slave {slave_id}')
        self.config['target_slaves'].append(slave_id)
        
        # Initialize empty register list for this slave
        if 'slave_registers' not in self.config:
            self.config['slave_registers'] = {}
        self.config['slave_registers'][slave_id] = []
        
        self.statusBar().showMessage(f'Added target slave {slave_id}')
        
    def delete_selected_slave(self):
        """Delete currently selected slave"""
        current_item = self.target_slaves_list.currentItem()
        if current_item is None:
            QMessageBox.warning(self, 'Warning', 'Please select a slave to delete!')
            return
            
        try:
            item_text = current_item.text()
            if 'Slave ' in item_text:
                slave_id = int(item_text.replace('Slave ', ''))
                
                # Remove from config
                if slave_id in self.config['target_slaves']:
                    self.config['target_slaves'].remove(slave_id)
                if 'slave_registers' in self.config and slave_id in self.config['slave_registers']:
                    del self.config['slave_registers'][slave_id]
                
                # Remove from list
                self.target_slaves_list.takeItem(self.target_slaves_list.row(current_item))
                
                # Reset selection if deleted slave was selected
                if self.current_selected_slave == slave_id:
                    self.current_selected_slave = None
                    self.update_register_management_state()
                
                self.statusBar().showMessage(f'Deleted slave {slave_id}')
        except (ValueError, IndexError) as e:
            QMessageBox.warning(self, 'Error', f'Failed to delete slave: {str(e)}')
            
    def on_slave_selected(self, item):
        """Handle slave selection in master mode"""
        try:
            item_text = item.text()
            if 'Slave ' in item_text:
                slave_id = int(item_text.replace('Slave ', ''))
                self.current_selected_slave = slave_id
                self.update_register_management_state()
                self.statusBar().showMessage(f'Selected slave {slave_id} for register management')
        except (ValueError, IndexError) as e:
            QMessageBox.warning(self, 'Error', f'Failed to select slave: {str(e)}')
        
    def on_address_changed(self):
        self.update_mapped_address()
        
    def on_type_changed(self):
        self.update_mapped_address()
        
    def update_mapped_address(self):
        internal_addr = self.reg_address.value()
        reg_type = self.reg_type.currentIndex()
        
        # Modbus address mapping: type prefix + internal address + 1
        if reg_type == 0:  # Coils (0x)
            mapped_addr = internal_addr + 1
            self.mapped_address_label.setText(f'{mapped_addr} (Coil)')
        elif reg_type == 1:  # Discrete Input (1x)
            mapped_addr = 10000 + internal_addr + 1
            self.mapped_address_label.setText(f'{mapped_addr} (DI)')
        elif reg_type == 2:  # Input Register (3x) - index 2 in combobox
            mapped_addr = 30000 + internal_addr + 1
            self.mapped_address_label.setText(f'{mapped_addr} (IR)')
        elif reg_type == 3:  # Holding Register (4x) - index 3 in combobox
            mapped_addr = 40000 + internal_addr + 1
            self.mapped_address_label.setText(f'{mapped_addr} (HR)')
        else:
            self.mapped_address_label.setText('-')

    def add_register(self):
        internal_addr = self.reg_address.value()
        reg_type = self.reg_type.currentIndex()
        
        # Calculate mapped address
        if reg_type == 0:  # Coils
            mapped_addr = internal_addr + 1
        elif reg_type == 1:  # Discrete Input
            mapped_addr = 10000 + internal_addr + 1
        elif reg_type == 2:  # Input Register (index 2 in combobox)
            mapped_addr = 30000 + internal_addr + 1
        elif reg_type == 3:  # Holding Register (index 3 in combobox)
            mapped_addr = 40000 + internal_addr + 1
        else:
            QMessageBox.warning(self, 'Error', f'Invalid register type! Got index: {reg_type}')
            return
        
        # Get current register list
        current_registers = self.get_current_register_list()
        
        # Check if register already exists in current context
        for reg in current_registers:
            if reg['internal_address'] == internal_addr and reg['type'] == reg_type:
                context_info = f"Slave {self.current_selected_slave}" if (self.config['is_master'] and self.current_selected_slave) else "this device"
                QMessageBox.warning(self, 'Warning', f'Register {mapped_addr} already exists in {context_info}!')
                return
        
        # Create register object  
        register = {
            'internal_address': internal_addr,
            'mapped_address': mapped_addr, 
            'type': reg_type,  # Store combobox index (0,1,2,3)
            'modbus_type': [0, 1, 3, 4][reg_type],  # Store actual Modbus type (0,1,3,4)
            'type_name': self.reg_type.currentText()
        }
        
        # Add to appropriate register list
        if self.config['is_master'] and self.current_selected_slave is not None:
            # Master mode - add to selected slave's registers
            if 'slave_registers' not in self.config:
                self.config['slave_registers'] = {}
            if self.current_selected_slave not in self.config['slave_registers']:
                self.config['slave_registers'][self.current_selected_slave] = []
            self.config['slave_registers'][self.current_selected_slave].append(register)
            slave_info = f' for Slave {self.current_selected_slave}'
        else:
            # Slave mode - add to local registers
            self.config['registers'].append(register)
            slave_info = ''
        
        # Update UI
        self.update_register_table()
        self.optimize_ranges()
        self.statusBar().showMessage(f'Added register {mapped_addr}{slave_info}')
        
    def get_current_register_list(self):
        """Get the current register list based on mode and selection"""
        if self.config['is_master'] and self.current_selected_slave is not None:
            # Master mode - return selected slave's registers
            if 'slave_registers' not in self.config:
                self.config['slave_registers'] = {}
            if self.current_selected_slave not in self.config['slave_registers']:
                self.config['slave_registers'][self.current_selected_slave] = []
            return self.config['slave_registers'][self.current_selected_slave]
        else:
            # Slave mode - return local registers
            return self.config['registers']
        
    def update_register_table(self):
        current_registers = self.get_current_register_list()
        self.register_table.setRowCount(len(current_registers))
        
        for i, reg in enumerate(current_registers):
            self.register_table.setItem(i, 0, QTableWidgetItem(str(reg['internal_address'])))
            self.register_table.setItem(i, 1, QTableWidgetItem(str(reg['mapped_address'])))
            self.register_table.setItem(i, 2, QTableWidgetItem(reg['type_name']))
            
            # Remove button
            remove_btn = QPushButton('Remove')
            remove_btn.clicked.connect(lambda checked, idx=i: self.remove_register(idx))
            self.register_table.setCellWidget(i, 3, remove_btn)
            
    def remove_register(self, index):
        current_registers = self.get_current_register_list()
        if 0 <= index < len(current_registers):
            removed_reg = current_registers.pop(index)
            self.update_register_table()
            self.optimize_ranges()
            
            if self.config['is_master'] and self.current_selected_slave is not None:
                slave_info = f' from Slave {self.current_selected_slave}'
            else:
                slave_info = ''
            self.statusBar().showMessage(f'Removed register {removed_reg["mapped_address"]}{slave_info}')
            
    def optimize_ranges(self):
        """Group nearby registers into ranges for efficient access"""
        # Clear previous ranges
        self.ranges_table.setRowCount(0)
        
        current_registers = self.get_current_register_list()
        if not current_registers:
            self.update_ranges_table([])
            return
            
        # Get optimized ranges for current register list
        optimized_ranges = self.get_optimized_ranges_for_registers(current_registers)
        
        # Update ranges table
        self.update_ranges_table(optimized_ranges)

    def get_optimized_ranges(self):
        """Get optimized register ranges for current context"""
        current_registers = self.get_current_register_list()
        return self.get_optimized_ranges_for_registers(current_registers)
        
    def get_optimized_ranges_for_registers(self, registers):
        """Get optimized register ranges for given register list"""
        if not registers:
            return []
            
        # Group by type using modbus_type (not combobox index)
        type_groups = {}
        for reg in registers:
            # Use modbus_type if available, otherwise map from combobox index
            if 'modbus_type' in reg:
                modbus_type = reg['modbus_type']
            else:
                # Map combobox index to modbus type
                modbus_type = [0, 1, 3, 4][reg['type']]
                
            if modbus_type not in type_groups:
                type_groups[modbus_type] = []
            type_groups[modbus_type].append(reg['internal_address'])
        
        # Optimize each type
        optimized_ranges = []
        for modbus_type, addresses in type_groups.items():
            addresses.sort()
            ranges = self.create_ranges(addresses, modbus_type)
            optimized_ranges.extend(ranges)
        
        return optimized_ranges
        
    def create_ranges(self, addresses, reg_type):
        """Create optimized ranges from sorted internal addresses"""
        if not addresses:
            return []
            
        ranges = []
        start = addresses[0]
        count = 1
        
        for i in range(1, len(addresses)):
            if addresses[i] == addresses[i-1] + 1:
                count += 1
            else:
                # Gap found, create range
                ranges.append(RegisterRange(start, count, reg_type))
                start = addresses[i]
                count = 1
        
        # Add last range
        ranges.append(RegisterRange(start, count, reg_type))
        
        return ranges
        
    def update_ranges_table(self, ranges):
        self.ranges_table.setRowCount(len(ranges))
        
        # Correct type names mapping for Modbus types
        type_names = {
            0: 'Coil',
            1: 'Discrete Input', 
            3: 'Input Register',
            4: 'Holding Register'
        }
        
        total_requests = len(ranges)
        current_registers = self.get_current_register_list()
        original_requests = len(current_registers)
        
        for i, rng in enumerate(ranges):
            self.ranges_table.setItem(i, 0, QTableWidgetItem(str(rng.start_addr)))
            self.ranges_table.setItem(i, 1, QTableWidgetItem(str(rng.count)))
            
            # Use correct type name
            type_name = type_names.get(rng.reg_type, f'Unknown({rng.reg_type})')
            self.ranges_table.setItem(i, 2, QTableWidgetItem(type_name))
            
            efficiency = f"{rng.count} regs/1 req"
            self.ranges_table.setItem(i, 3, QTableWidgetItem(efficiency))
        
        # Update statistics
        if original_requests > 0:
            efficiency_pct = ((original_requests - total_requests) / original_requests * 100)
            if self.config['is_master'] and self.current_selected_slave is not None:
                slave_info = f' (Slave {self.current_selected_slave})'
            else:
                slave_info = ''
            self.stats_label.setText(f'Statistics{slave_info}: {original_requests} registers, {total_requests} ranges '
                                   f'({efficiency_pct:.1f}% reduction in requests)')
        else:
            self.stats_label.setText('Statistics: 0 registers, 0 ranges')
        
    def new_config(self):
        self.config = {
            'slave_id': 1,
            'is_master': False,
            'target_slaves': [],
            'slave_registers': {},
            'registers': []
        }
        self.current_selected_slave = None
        self.update_ui_from_config()
        
    def update_ui_from_config(self):
        self.device_type.setCurrentText('Master' if self.config['is_master'] else 'Slave')
        self.slave_id.setValue(self.config['slave_id'])
        
        # Update target slaves list
        self.target_slaves_list.clear()
        if 'target_slaves' in self.config:
            for slave_id in self.config['target_slaves']:
                self.target_slaves_list.addItem(f'Slave {slave_id}')
        
        self.update_slave_config_display()
        self.update_register_table()
        self.optimize_ranges()
        
    def update_config_from_ui(self):
        self.config['is_master'] = self.device_type.currentText() == 'Master'
        self.config['slave_id'] = self.slave_id.value()
        
        # Update target slaves from list
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
                self.update_ui_from_config()
                self.statusBar().showMessage(f'Loaded config from {filename}')
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Failed to load config: {str(e)}')
                
    def save_config(self):
        self.update_config_from_ui()
        filename, _ = QFileDialog.getSaveFileName(self, 'Save Config', '', 'JSON Files (*.json)')
        if filename:
            try:
                with open(filename, 'w') as f:
                    json.dump(self.config, f, indent=2)
                self.statusBar().showMessage(f'Saved config to {filename}')
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Failed to save config: {str(e)}')
                
    def export_library(self):
        self.update_config_from_ui()
        
        # Get output directory
        output_dir = QFileDialog.getExistingDirectory(self, 'Select Output Directory')
        if not output_dir:
            return
            
        try:
            self.generate_library_files(output_dir)
            self.statusBar().showMessage(f'Exported library files to {output_dir}')
            QMessageBox.information(self, 'Success', f'Library files generated:\n- modbus_registers.h\n- modbus_registers.c\n\nLocation: {output_dir}')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to export library: {str(e)}')
                
    def import_library(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Import Library Header', '', 'Header Files (*.h)')
        if filename:
            try:
                self.parse_library_header(filename)
                self.update_ui_from_config()
                self.statusBar().showMessage(f'Imported library from {filename}')
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Failed to import library: {str(e)}')
                
    def generate_library_files(self, output_dir):
        """Generate modbus_registers.h and modbus_registers.c files"""
        
        # Collect all registers from all slaves (for master) or local (for slave)
        all_registers = []
        
        if self.config['is_master']:
            # Master mode: collect registers from all slaves
            if 'slave_registers' in self.config:
                for slave_id, registers in self.config['slave_registers'].items():
                    for reg in registers:
                        # Add slave_id info to register
                        reg_with_slave = reg.copy()
                        reg_with_slave['slave_id'] = slave_id
                        all_registers.append(reg_with_slave)
        else:
            # Slave mode: use local registers
            all_registers = self.config['registers']
        
        # Generate optimized ranges for all registers
        optimized_ranges = self.get_optimized_ranges_for_registers(all_registers)
        
        # Generate header file content with proper C style
        header_content = self.generate_header_file_c_style(optimized_ranges, all_registers)
        with open(f'{output_dir}/modbus_registers.h', 'w') as f:
            f.write(header_content)
            
        # Generate source file with proper C style 
        source_content = self.generate_source_file_c_style(optimized_ranges, all_registers)
        with open(f'{output_dir}/modbus_registers.c', 'w') as f:
            f.write(source_content)

    def generate_header_file_c_style(self, optimized_ranges, all_registers):
        """Generate modbus_registers.h content with proper C coding style"""
        
        header = '''#ifndef MODBUS_REGISTERS_H
#define MODBUS_REGISTERS_H

#include <stdint.h>
#include <stdbool.h>

/**
 * @file    modbus_registers.h
 * @brief   Modbus register mapping definitions
 * @note    Generated by Modbus Configuration Tool
 */

/* Device Configuration */
'''
        
        if self.config['is_master']:
            header += "#define MODBUS_DEVICE_TYPE_MASTER           (1)\n"
            if self.config.get('target_slaves'):
                header += f"/* Target slave IDs: {', '.join(map(str, self.config['target_slaves']))} */\n"
        else:
            header += "#define MODBUS_DEVICE_TYPE_SLAVE            (1)\n"
            header += f"#define MODBUS_SLAVE_ID                     ({self.config['slave_id']})\n"
        
        header += "\n/* Register Address Definitions */\n"
        
        # Add individual register defines using internal addresses
        for reg in all_registers:
            reg_name = self.get_register_name_c_style(reg['internal_address'], reg.get('modbus_type', [0,1,3,4][reg['type']]))
            if self.config['is_master'] and 'slave_id' in reg:
                header += f"#define {reg_name}_SLAVE{reg['slave_id']:<25} ({reg['internal_address']})  /* Slave {reg['slave_id']} */\n"
            else:
                header += f"#define {reg_name:<35} ({reg['internal_address']})\n"
            
        header += f"\n/* Register Ranges Configuration */\n"
        header += f"#define MODBUS_REGISTER_RANGES_COUNT        ({len(optimized_ranges)})\n\n"
        
        header += '''/* Register range structure */
typedef struct {
    uint16_t start_addr;        /* Starting internal address */
    uint16_t count;             /* Number of consecutive registers */
    uint8_t  reg_type;          /* Register type (0=coil, 1=DI, 3=IR, 4=HR) */
} modbus_register_range_t;

/* External variable declarations */
extern const modbus_register_range_t g_modbus_register_ranges[];

/* Function prototypes */
bool modbus_is_register_valid(uint16_t addr, uint8_t reg_type);
int modbus_get_register_ranges(const modbus_register_range_t **ranges);
void modbus_registers_init(void);

#endif /* MODBUS_REGISTERS_H */
'''
        
        return header
        
    def generate_source_file_c_style(self, optimized_ranges, all_registers):
        """Generate modbus_registers.c content with proper C coding style"""
        
        source = '''#include "modbus_registers.h"

/**
 * @file    modbus_registers.c  
 * @brief   Modbus register mapping implementation
 * @note    Generated by Modbus Configuration Tool
 */

'''
            
        source += f"/* Optimized register ranges ({len(optimized_ranges)} ranges) */\n"
        source += f"const modbus_register_range_t g_modbus_register_ranges[{max(1, len(optimized_ranges))}] = {{\n"
        
        if optimized_ranges:
            for i, range_obj in enumerate(optimized_ranges):
                source += f"    {{{range_obj.start_addr:4}, {range_obj.count:2}, {range_obj.reg_type}}}"
                if i < len(optimized_ranges) - 1:
                    source += ","
                source += f"  /* {self.get_range_comment(range_obj)} */\n"
        else:
            source += "    {0, 0, 0}  /* No registers defined */\n"
            
        source += "};\n\n"
        
        # Add function implementations
        source += '''/**
 * @brief   Check if register address is valid for given type
 * @param   addr: Internal register address (0-based)
 * @param   reg_type: Register type (0=coil, 1=DI, 3=IR, 4=HR)
 * @return  true if register is valid, false otherwise
 */
bool
modbus_is_register_valid(uint16_t addr, uint8_t reg_type) {
    for (int i = 0; i < MODBUS_REGISTER_RANGES_COUNT; i++) {
        const modbus_register_range_t *range = &g_modbus_register_ranges[i];
        if (range->reg_type == reg_type && 
            addr >= range->start_addr && 
            addr < range->start_addr + range->count) {
            return true;
        }
    }
    return false;
}

/**
 * @brief   Get pointer to register ranges array
 * @param   ranges: Pointer to store ranges array pointer
 * @return  Number of ranges
 */
int
modbus_get_register_ranges(const modbus_register_range_t **ranges) {
    if (ranges != NULL) {
        *ranges = g_modbus_register_ranges;
    }
    return MODBUS_REGISTER_RANGES_COUNT;
}

/**
 * @brief   Initialize register values to default
 * @note    User can modify this function to set initial values
 */
void
modbus_registers_init(void) {
    /* Initialize register values if needed */
    /* User implementation goes here */
}
'''
        
        return source
        
    def get_register_name_c_style(self, internal_addr, modbus_type):
        """Generate register name for #define with proper C style"""
        type_prefix = ['COIL', 'DI', 'RESERVED', 'INPUT_REG', 'HOLDING_REG'][modbus_type]
        return f"MODBUS_{type_prefix}_{internal_addr:04d}"
        
    def get_range_comment(self, range_obj):
        """Generate comment for register range"""
        type_names = ['Coils', 'DI', 'Reserved', 'Input Regs', 'Holding Regs']
        if range_obj.count == 1:
            return f"{type_names[range_obj.reg_type]} {range_obj.start_addr}"
        else:
            end_addr = range_obj.start_addr + range_obj.count - 1
            return f"{type_names[range_obj.reg_type]} {range_obj.start_addr}-{end_addr}"
            
    def parse_library_header(self, filename):
        """Parse existing modbus_registers.h to import configuration"""
        with open(filename, 'r') as f:
            content = f.read()
            
        # Reset config
        self.config = {
            'slave_id': 1,
            'is_master': False,
            'target_slaves': [],
            'slave_registers': {},
            'registers': []
        }
        self.current_selected_slave = None
        
        # Parse device type
        if '#define MODBUS_DEVICE_TYPE_MASTER' in content:
            self.config['is_master'] = True
            
            # Parse target slaves from comments
            import re
            target_match = re.search(r'/\* Target slave IDs: ([0-9, ]+) \*/', content)
            if target_match:
                slave_ids = [int(x.strip()) for x in target_match.group(1).split(',')]
                self.config['target_slaves'] = slave_ids
                # Initialize empty register lists for each slave
                for slave_id in slave_ids:
                    self.config['slave_registers'][slave_id] = []
        
        # Parse slave ID
        slave_match = re.search(r'#define MODBUS_SLAVE_ID\s+\((\d+)\)', content)
        if slave_match:
            self.config['slave_id'] = int(slave_match.group(1))
            
        # Parse register defines
        type_map = {'COIL': 0, 'DI': 1, 'INPUT_REG': 3, 'HOLDING_REG': 4}
        
        for type_name, modbus_type in type_map.items():
            # Regular registers
            pattern = rf'#define MODBUS_{type_name}_(\d+)\s+\((\d+)\)'
            matches = re.findall(pattern, content)
            
            for match in matches:
                internal_addr = int(match[1])
                
                # Calculate mapped address and combobox index
                if modbus_type == 0:  # Coils
                    mapped_addr = internal_addr + 1
                    combo_index = 0
                elif modbus_type == 1:  # Discrete Input
                    mapped_addr = 10000 + internal_addr + 1
                    combo_index = 1
                elif modbus_type == 3:  # Input Register
                    mapped_addr = 30000 + internal_addr + 1
                    combo_index = 2
                elif modbus_type == 4:  # Holding Register
                    mapped_addr = 40000 + internal_addr + 1
                    combo_index = 3
                
                register = {
                    'internal_address': internal_addr,
                    'mapped_address': mapped_addr,
                    'type': combo_index,  # Combobox index
                    'modbus_type': modbus_type,  # Actual Modbus type
                    'type_name': ['Coil (0x)', 'Discrete Input (1x)', 'Input Register (3x)', 'Holding Register (4x)'][combo_index]
                }
                
                # Add to appropriate register list
                if self.config['is_master']:
                    # For master mode, add to first available slave (since we can't determine which slave from header)
                    if self.config['target_slaves']:
                        first_slave = self.config['target_slaves'][0]
                        self.config['slave_registers'][first_slave].append(register)
                else:
                    self.config['registers'].append(register)
            
            # Master mode with slave-specific registers
            if self.config['is_master']:
                slave_pattern = rf'#define MODBUS_{type_name}_(\d+)_SLAVE(\d+)\s+\((\d+)\)'
                slave_matches = re.findall(slave_pattern, content)
                
                for match in slave_matches:
                    internal_addr = int(match[2])
                    slave_id = int(match[1])
                    
                    # Calculate mapped address and combobox index
                    if modbus_type == 0:  # Coils
                        mapped_addr = internal_addr + 1
                        combo_index = 0
                    elif modbus_type == 1:  # Discrete Input
                        mapped_addr = 10000 + internal_addr + 1
                        combo_index = 1
                    elif modbus_type == 3:  # Input Register
                        mapped_addr = 30000 + internal_addr + 1
                        combo_index = 2
                    elif modbus_type == 4:  # Holding Register
                        mapped_addr = 40000 + internal_addr + 1
                        combo_index = 3
                    
                    register = {
                        'internal_address': internal_addr,
                        'mapped_address': mapped_addr,
                        'type': combo_index,
                        'modbus_type': modbus_type,
                        'type_name': ['Coil (0x)', 'Discrete Input (1x)', 'Input Register (3x)', 'Holding Register (4x)'][combo_index]
                    }
                    
                    # Ensure slave exists in config
                    if slave_id not in self.config['target_slaves']:
                        self.config['target_slaves'].append(slave_id)
                    if slave_id not in self.config['slave_registers']:
                        self.config['slave_registers'][slave_id] = []
                    
                    self.config['slave_registers'][slave_id].append(register)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ModbusConfigTool()
    window.show()
    sys.exit(app.exec_())