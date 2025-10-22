# -*- coding: utf-8 -*-
"""
ui_modbus_config.py
Enhanced UI with Operation and Mode selection
"""

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1400, 950)  # Increased height for new fields
        
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        self.main_layout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.main_layout.setObjectName("main_layout")
        
        self.main_splitter = QtWidgets.QSplitter(self.centralwidget)
        self.main_splitter.setOrientation(QtCore.Qt.Horizontal)
        self.main_splitter.setObjectName("main_splitter")
        
        # LEFT PANEL
        self.left_container = QtWidgets.QWidget()
        self.left_container.setObjectName("left_container")
        self.left_container_layout = QtWidgets.QVBoxLayout(self.left_container)
        self.left_container_layout.setObjectName("left_container_layout")
        
        # Config Group
        self.config_group = QtWidgets.QGroupBox(self.left_container)
        self.config_group.setObjectName("config_group")
        self.config_layout = QtWidgets.QVBoxLayout(self.config_group)
        self.config_layout.setObjectName("config_layout")
        
        # Settings Button
        self.settings_btn = QtWidgets.QPushButton(self.config_group)
        self.settings_btn.setText("⚙ Configuration Settings")
        self.settings_btn.setObjectName("settings_btn")
        self.config_layout.addWidget(self.settings_btn)
        
        # Device Type row
        device_type_layout = QtWidgets.QHBoxLayout()
        self.device_type_label = QtWidgets.QLabel(self.config_group)
        self.device_type_label.setText("Device Type:")
        self.device_type = QtWidgets.QComboBox(self.config_group)
        self.device_type.addItem("Slave")
        self.device_type.addItem("Master")
        self.device_type.setObjectName("device_type")
        
        device_type_layout.addWidget(self.device_type_label)
        device_type_layout.addWidget(self.device_type)
        device_type_layout.addStretch()
        self.config_layout.addLayout(device_type_layout)
        
        # Slave/Master Config Container
        self.slave_config_container = QtWidgets.QWidget(self.config_group)
        self.slave_config_container.setObjectName("slave_config_container")
        self.slave_config_layout = QtWidgets.QVBoxLayout(self.slave_config_container)
        self.slave_config_layout.setContentsMargins(0, 0, 0, 0)
        
        # Slave ID Widget (hidden, moved to settings)
        self.slave_id_widget = QtWidgets.QWidget()
        self.slave_id_widget.setObjectName("slave_id_widget")
        self.slave_id_layout = QtWidgets.QHBoxLayout(self.slave_id_widget)
        self.slave_id_layout.setContentsMargins(0, 0, 0, 0)
        
        self.slave_id_label = QtWidgets.QLabel(self.slave_id_widget)
        self.slave_id_label.setText("Slave ID:")
        self.slave_id_layout.addWidget(self.slave_id_label)
        
        self.slave_id = QtWidgets.QSpinBox(self.slave_id_widget)
        self.slave_id.setRange(1, 247)
        self.slave_id.setValue(1)
        self.slave_id.setObjectName("slave_id")
        self.slave_id_layout.addWidget(self.slave_id)
        self.slave_id_layout.addStretch()
        
        # Target Slaves Widget
        self.target_slaves_widget = QtWidgets.QWidget()
        self.target_slaves_widget.setObjectName("target_slaves_widget")
        self.target_layout = QtWidgets.QVBoxLayout(self.target_slaves_widget)
        self.target_layout.setContentsMargins(0, 0, 0, 0)
        self.target_layout.setSpacing(5)
        
        self.target_label = QtWidgets.QLabel(self.target_slaves_widget)
        self.target_label.setText("Target Slave IDs:")
        self.target_layout.addWidget(self.target_label)
        
        self.target_input_layout = QtWidgets.QHBoxLayout()
        self.target_slave_input = QtWidgets.QSpinBox(self.target_slaves_widget)
        self.target_slave_input.setRange(1, 247)
        self.target_slave_input.setValue(1)
        self.target_slave_input.setObjectName("target_slave_input")
        self.target_input_layout.addWidget(self.target_slave_input)
        
        self.add_target_btn = QtWidgets.QPushButton(self.target_slaves_widget)
        self.add_target_btn.setText("Add Slave")
        self.add_target_btn.setObjectName("add_target_btn")
        self.target_input_layout.addWidget(self.add_target_btn)
        
        self.delete_target_btn = QtWidgets.QPushButton(self.target_slaves_widget)
        self.delete_target_btn.setText("Delete Slave")
        self.delete_target_btn.setObjectName("delete_target_btn")
        self.target_input_layout.addWidget(self.delete_target_btn)
        self.target_input_layout.addStretch()
        self.target_layout.addLayout(self.target_input_layout)
        
        self.target_slaves_list = QtWidgets.QListWidget(self.target_slaves_widget)
        self.target_slaves_list.setMinimumHeight(60)
        self.target_slaves_list.setObjectName("target_slaves_list")
        self.target_layout.addWidget(self.target_slaves_list, 1)
        
        self.slave_config_layout.addWidget(self.slave_id_widget)
        self.slave_config_layout.addWidget(self.target_slaves_widget, 1)
        self.config_layout.addWidget(self.slave_config_container, 1)
        
        self.config_group.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        self.left_container_layout.addWidget(self.config_group)
        
        # Register Group
        self.reg_group = QtWidgets.QGroupBox(self.left_container)
        self.reg_group.setObjectName("reg_group")
        self.reg_layout = QtWidgets.QVBoxLayout(self.reg_group)
        self.reg_layout.setObjectName("reg_layout")
        
        self.reg_group.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        
        self.register_status_label = QtWidgets.QLabel(self.reg_group)
        self.register_status_label.setText("Slave Mode: Managing local registers")
        self.register_status_label.setStyleSheet("font-weight: bold; color: green; padding: 5px;")
        self.register_status_label.setObjectName("register_status_label")
        self.reg_layout.addWidget(self.register_status_label)
        
        # Add Register Form - Enhanced
        self.add_form_layout = QtWidgets.QGridLayout()
        
        self.tag_name_label = QtWidgets.QLabel(self.reg_group)
        self.tag_name_label.setText("Tag Name:")
        self.add_form_layout.addWidget(self.tag_name_label, 0, 0)
        
        self.reg_tag_name = QtWidgets.QLineEdit(self.reg_group)
        self.reg_tag_name.setPlaceholderText("e.g. TEMPERATURE")
        self.reg_tag_name.setObjectName("reg_tag_name")
        self.add_form_layout.addWidget(self.reg_tag_name, 0, 1)
        
        self.address_label = QtWidgets.QLabel(self.reg_group)
        self.address_label.setText("Internal Address:")
        self.add_form_layout.addWidget(self.address_label, 1, 0)
        
        self.reg_address = QtWidgets.QSpinBox(self.reg_group)
        self.reg_address.setRange(0, 65535)
        self.reg_address.setValue(0)
        self.reg_address.setObjectName("reg_address")
        self.add_form_layout.addWidget(self.reg_address, 1, 1)
        
        self.type_label = QtWidgets.QLabel(self.reg_group)
        self.type_label.setText("Register Type:")
        self.add_form_layout.addWidget(self.type_label, 2, 0)
        
        self.reg_type = QtWidgets.QComboBox(self.reg_group)
        self.reg_type.addItem("Coil (0x)")
        self.reg_type.addItem("Discrete Input (1x)")
        self.reg_type.addItem("Input Register (3x)")
        self.reg_type.addItem("Holding Register (4x)")
        self.reg_type.setCurrentIndex(3)
        self.reg_type.setObjectName("reg_type")
        self.add_form_layout.addWidget(self.reg_type, 2, 1)
        
        self.mapped_label = QtWidgets.QLabel(self.reg_group)
        self.mapped_label.setText("Mapped Address:")
        self.add_form_layout.addWidget(self.mapped_label, 3, 0)
        
        self.mapped_address_label = QtWidgets.QLabel(self.reg_group)
        self.mapped_address_label.setText("40001 (HR)")
        self.mapped_address_label.setStyleSheet("font-weight: bold; color: blue;")
        self.mapped_address_label.setObjectName("mapped_address_label")
        self.add_form_layout.addWidget(self.mapped_address_label, 3, 1)
        
        # NEW: Operation (Read/Write) - only for Master mode
        self.operation_label = QtWidgets.QLabel(self.reg_group)
        self.operation_label.setText("Operation:")
        self.add_form_layout.addWidget(self.operation_label, 4, 0)
        
        self.reg_operation = QtWidgets.QComboBox(self.reg_group)
        self.reg_operation.addItem("Read")
        self.reg_operation.addItem("Write")
        self.reg_operation.setObjectName("reg_operation")
        self.add_form_layout.addWidget(self.reg_operation, 4, 1)
        
        # NEW: Mode (One-time/Cyclic) - only for Write operations
        self.mode_label = QtWidgets.QLabel(self.reg_group)
        self.mode_label.setText("Write Mode:")
        self.add_form_layout.addWidget(self.mode_label, 5, 0)
        
        self.reg_mode = QtWidgets.QComboBox(self.reg_group)
        self.reg_mode.addItem("One-time")
        self.reg_mode.addItem("Cyclic")
        self.reg_mode.setEnabled(False)  # Initially disabled
        self.reg_mode.setObjectName("reg_mode")
        self.add_form_layout.addWidget(self.reg_mode, 5, 1)
        
        self.add_reg_btn = QtWidgets.QPushButton(self.reg_group)
        self.add_reg_btn.setText("Add Register")
        self.add_reg_btn.setObjectName("add_reg_btn")
        self.add_form_layout.addWidget(self.add_reg_btn, 6, 0, 1, 2)  # Moved to row 6
        
        self.reg_layout.addLayout(self.add_form_layout)
        
        # Quick Add Buttons with Remove All
        self.quick_add_layout = QtWidgets.QHBoxLayout()
        self.quick_add_5_btn = QtWidgets.QPushButton(self.reg_group)
        self.quick_add_5_btn.setText("+5 Registers")
        self.quick_add_5_btn.setObjectName("quick_add_5_btn")
        self.quick_add_layout.addWidget(self.quick_add_5_btn)
        
        self.quick_add_10_btn = QtWidgets.QPushButton(self.reg_group)
        self.quick_add_10_btn.setText("+10 Registers")
        self.quick_add_10_btn.setObjectName("quick_add_10_btn")
        self.quick_add_layout.addWidget(self.quick_add_10_btn)
        
        self.quick_add_layout.addStretch()
        
        self.remove_all_btn = QtWidgets.QPushButton(self.reg_group)
        self.remove_all_btn.setText("Remove All")
        self.remove_all_btn.setObjectName("remove_all_btn")
        self.quick_add_layout.addWidget(self.remove_all_btn)
        
        self.reg_layout.addLayout(self.quick_add_layout)
        
        # Register Table with enhanced columns
        self.register_table = QtWidgets.QTableWidget(self.reg_group)
        self.register_table.setColumnCount(7)  # Increased from 5 to 7
        self.register_table.setHorizontalHeaderLabels(['Tag Name', 'Internal', 'Mapped', 'Type', 'Operation', 'Mode', 'Actions'])
        self.register_table.setObjectName("register_table")
        
        header = self.register_table.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)     # Tag Name
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)     # Internal
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)     # Mapped
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)     # Type
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.Stretch)     # Operation
        header.setSectionResizeMode(5, QtWidgets.QHeaderView.Stretch)     # Mode
        header.setSectionResizeMode(6, QtWidgets.QHeaderView.Stretch)     # Actions
        
        header.setStretchLastSection(True)
        
        # Set proportional widths
        header.resizeSection(0, 150)  # Tag Name
        header.resizeSection(1, 80)   # Internal
        header.resizeSection(2, 80)   # Mapped
        header.resizeSection(3, 120)  # Type
        header.resizeSection(4, 80)   # Operation
        header.resizeSection(5, 80)   # Mode
        header.resizeSection(6, 80)   # Actions
        
        header.setMinimumSectionSize(60)
        self.register_table.setMinimumWidth(600)
        
        self.reg_layout.addWidget(self.register_table)
        self.left_container_layout.addWidget(self.reg_group, 1)
        self.main_splitter.addWidget(self.left_container)
        
        # RIGHT PANEL
        self.ranges_group = QtWidgets.QGroupBox()
        self.ranges_group.setObjectName("ranges_group")
        self.ranges_layout = QtWidgets.QVBoxLayout(self.ranges_group)
        self.ranges_layout.setObjectName("ranges_layout")
        
        # Ranges Table
        self.ranges_table = QtWidgets.QTableWidget(self.ranges_group)
        self.ranges_table.setColumnCount(4)
        self.ranges_table.setHorizontalHeaderLabels(['Start', 'Count', 'Type', 'Efficiency'])
        self.ranges_table.setObjectName("ranges_table")
        
        ranges_header = self.ranges_table.horizontalHeader()
        ranges_header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        ranges_header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        ranges_header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        ranges_header.setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
        
        ranges_header.setStretchLastSection(True)
        
        ranges_header.resizeSection(0, 80)
        ranges_header.resizeSection(1, 80)
        ranges_header.resizeSection(2, 160)
        ranges_header.resizeSection(3, 120)
        
        ranges_header.setMinimumSectionSize(70)
        self.ranges_table.setMinimumWidth(400)
        
        self.ranges_layout.addWidget(self.ranges_table)
        
        self.stats_label = QtWidgets.QLabel(self.ranges_group)
        self.stats_label.setText("Statistics: 0 registers, 0 ranges")
        self.stats_label.setWordWrap(True)
        self.stats_label.setObjectName("stats_label")
        self.ranges_layout.addWidget(self.stats_label)
        
        self.main_splitter.addWidget(self.ranges_group)
        self.main_splitter.setSizes([800, 600])
        
        self.main_layout.addWidget(self.main_splitter)
        MainWindow.setCentralWidget(self.centralwidget)
        
        # Menu Bar
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1400, 21))
        self.menubar.setObjectName("menubar")
        
        self.menu_file = QtWidgets.QMenu(self.menubar)
        self.menu_file.setObjectName("menu_file")
        MainWindow.setMenuBar(self.menubar)
        
        # Status Bar
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        
        # Actions
        self.action_new = QtWidgets.QAction(MainWindow)
        self.action_new.setObjectName("action_new")
        self.action_new.setShortcut("Ctrl+N")
        
        self.action_open = QtWidgets.QAction(MainWindow)
        self.action_open.setObjectName("action_open")
        self.action_open.setShortcut("Ctrl+O")
        
        self.action_save = QtWidgets.QAction(MainWindow)
        self.action_save.setObjectName("action_save")
        self.action_save.setShortcut("Ctrl+S")
        
        self.action_export = QtWidgets.QAction(MainWindow)
        self.action_export.setObjectName("action_export")
        self.action_export.setShortcut("Ctrl+E")
        
        self.action_import = QtWidgets.QAction(MainWindow)
        self.action_import.setObjectName("action_import")
        
        self.menu_file.addAction(self.action_new)
        self.menu_file.addAction(self.action_open)
        self.menu_file.addAction(self.action_save)
        self.menu_file.addSeparator()
        self.menu_file.addAction(self.action_export)
        self.menu_file.addAction(self.action_import)
        self.menubar.addAction(self.menu_file.menuAction())
        
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Modbus RTU Configuration Tool - Enhanced v2.0"))
        self.config_group.setTitle(_translate("MainWindow", "Modbus Configuration"))
        self.reg_group.setTitle(_translate("MainWindow", "Register Management"))
        self.ranges_group.setTitle(_translate("MainWindow", "Optimized Register Ranges"))
        self.menu_file.setTitle(_translate("MainWindow", "File"))
        self.action_new.setText(_translate("MainWindow", "New"))
        self.action_open.setText(_translate("MainWindow", "Open Config"))
        self.action_save.setText(_translate("MainWindow", "Save Config"))
        self.action_export.setText(_translate("MainWindow", "Export Library (.c/.h)"))
        self.action_import.setText(_translate("MainWindow", "Import Library (.h)"))