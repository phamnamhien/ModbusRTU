# -*- coding: utf-8 -*-
"""
ui_modbus_config.py
Generated UI file (Qt Designer style)
"""

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1400, 900)
        
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
        self.config_layout = QtWidgets.QFormLayout(self.config_group)
        self.config_layout.setObjectName("config_layout")
        
        self.device_type_label = QtWidgets.QLabel(self.config_group)
        self.device_type_label.setText("Device Type:")
        self.device_type = QtWidgets.QComboBox(self.config_group)
        self.device_type.addItem("Slave")
        self.device_type.addItem("Master")
        self.device_type.setObjectName("device_type")
        self.config_layout.addRow(self.device_type_label, self.device_type)
        
        # Slave/Master Config Container
        self.slave_config_container = QtWidgets.QWidget(self.config_group)
        self.slave_config_container.setObjectName("slave_config_container")
        self.slave_config_layout = QtWidgets.QVBoxLayout(self.slave_config_container)
        self.slave_config_layout.setContentsMargins(0, 0, 0, 0)
        
        # Slave ID Widget
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
        self.target_slaves_list.setMaximumHeight(80)
        self.target_slaves_list.setObjectName("target_slaves_list")
        self.target_layout.addWidget(self.target_slaves_list)
        
        self.slave_config_layout.addWidget(self.slave_id_widget)
        self.slave_config_layout.addWidget(self.target_slaves_widget)
        self.config_layout.addRow(self.slave_config_container)
        
        # Settings Button
        self.settings_btn = QtWidgets.QPushButton(self.config_group)
        self.settings_btn.setText("⚙ Configuration Settings")
        self.settings_btn.setObjectName("settings_btn")
        self.config_layout.addRow(self.settings_btn)
        
        # Note Label
        self.note_label = QtWidgets.QLabel(self.config_group)
        self.note_label.setText("Note: Additional UART/Modbus settings can be configured via Settings button")
        self.note_label.setWordWrap(True)
        self.note_label.setStyleSheet("color: gray; font-style: italic; font-size: 10px;")
        self.config_layout.addRow(self.note_label)
        
        self.left_container_layout.addWidget(self.config_group)
        
        # Register Group
        self.reg_group = QtWidgets.QGroupBox(self.left_container)
        self.reg_group.setObjectName("reg_group")
        self.reg_layout = QtWidgets.QVBoxLayout(self.reg_group)
        self.reg_layout.setObjectName("reg_layout")
        
        self.register_status_label = QtWidgets.QLabel(self.reg_group)
        self.register_status_label.setText("Slave Mode: Managing local registers")
        self.register_status_label.setStyleSheet("font-weight: bold; color: green; padding: 5px;")
        self.register_status_label.setObjectName("register_status_label")
        self.reg_layout.addWidget(self.register_status_label)
        
        # Add Register Form
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
        
        self.add_reg_btn = QtWidgets.QPushButton(self.reg_group)
        self.add_reg_btn.setText("Add Register")
        self.add_reg_btn.setObjectName("add_reg_btn")
        self.add_form_layout.addWidget(self.add_reg_btn, 4, 0, 1, 2)
        
        self.reg_layout.addLayout(self.add_form_layout)
        
        # Quick Add Buttons
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
        self.reg_layout.addLayout(self.quick_add_layout)
        
        # Register Table
        self.register_table = QtWidgets.QTableWidget(self.reg_group)
        self.register_table.setColumnCount(5)
        self.register_table.setHorizontalHeaderLabels(['Tag Name', 'Internal', 'Mapped', 'Type', 'Actions'])
        self.register_table.setObjectName("register_table")
        
        header = self.register_table.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Interactive)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Interactive)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.Interactive)
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
        header.setMinimumSectionSize(60)
        self.register_table.setColumnWidth(1, 80)
        self.register_table.setColumnWidth(2, 80)
        self.register_table.setColumnWidth(3, 120)
        
        self.reg_layout.addWidget(self.register_table)
        self.left_container_layout.addWidget(self.reg_group)
        self.main_splitter.addWidget(self.left_container)
        
        # RIGHT PANEL
        self.ranges_group = QtWidgets.QGroupBox()
        self.ranges_group.setObjectName("ranges_group")
        self.ranges_layout = QtWidgets.QVBoxLayout(self.ranges_group)
        self.ranges_layout.setObjectName("ranges_layout")
        
        self.optimize_btn = QtWidgets.QPushButton(self.ranges_group)
        self.optimize_btn.setText("Manual Optimize Ranges")
        self.optimize_btn.setObjectName("optimize_btn")
        self.ranges_layout.addWidget(self.optimize_btn)
        
        # Ranges Table
        self.ranges_table = QtWidgets.QTableWidget(self.ranges_group)
        self.ranges_table.setColumnCount(4)
        self.ranges_table.setHorizontalHeaderLabels(['Start', 'Count', 'Type', 'Efficiency'])
        self.ranges_table.setObjectName("ranges_table")
        
        ranges_header = self.ranges_table.horizontalHeader()
        ranges_header.setSectionResizeMode(0, QtWidgets.QHeaderView.Interactive)
        ranges_header.setSectionResizeMode(1, QtWidgets.QHeaderView.Interactive)
        ranges_header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        ranges_header.setSectionResizeMode(3, QtWidgets.QHeaderView.Interactive)
        ranges_header.setMinimumSectionSize(50)
        self.ranges_table.setColumnWidth(0, 80)
        self.ranges_table.setColumnWidth(1, 60)
        self.ranges_table.setColumnWidth(3, 120)
        
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
        MainWindow.setWindowTitle(_translate("MainWindow", "Modbus RTU Configuration Tool - Enhanced"))
        self.config_group.setTitle(_translate("MainWindow", "Modbus Configuration"))
        self.reg_group.setTitle(_translate("MainWindow", "Register Management"))
        self.ranges_group.setTitle(_translate("MainWindow", "Optimized Register Ranges"))
        self.menu_file.setTitle(_translate("MainWindow", "File"))
        self.action_new.setText(_translate("MainWindow", "New"))
        self.action_open.setText(_translate("MainWindow", "Open Config"))
        self.action_save.setText(_translate("MainWindow", "Save Config"))
        self.action_export.setText(_translate("MainWindow", "Export Library (.c/.h)"))
        self.action_import.setText(_translate("MainWindow", "Import Library (.h)"))

        