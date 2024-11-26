import sys
import os
import json
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QFileDialog, 
                            QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox,
                            QScrollArea, QFrame, QListWidget, QLineEdit,
                            QTabWidget, QCheckBox, QGroupBox)
from PySide6.QtCore import Qt, QThread, Signal, QMutex
from PySide6.QtGui import QPixmap
import pandas as pd
import numpy as np
from pathlib import Path
from ..core.advanced_analyzer import AdvancedAnomalyAnalyzer
import logging
import matplotlib
matplotlib.use('Agg')  # Use Agg backend for thread safety
import matplotlib.pyplot as plt
import seaborn as sns
from queue import Queue
import traceback
from datetime import datetime

from .widgets.feature_options import FeatureOptionsWidget
from .widgets.plot_viewer import PlotViewer
from .workers.analysis_worker import AnalysisWorker
from ..utils.logging_config import QTextEditLogger, setup_logging

class AnomalyDetectorGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Financial Anomaly Detector")
        self.setMinimumSize(1200, 800)  # Increased window size
        
        # Load config if exists
        self.config = self.load_config()
        
        # Create main widget with tab widget
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.main_layout = QVBoxLayout(self.main_widget)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)
        
        # Create and add tabs
        self.setup_analysis_tab()
        self.setup_results_tab()
        self.setup_logs_tab()
        
        # Initialize analysis worker
        self.analysis_thread = None
        
        # Store current data and results
        self.current_data = None
        self.current_result = None
        self.output_dir = None
        
        print("Creating main window...")
        
    def setup_analysis_tab(self):
        """Set up the analysis tab with data loading and parameter controls"""
        analysis_tab = QWidget()
        layout = QVBoxLayout(analysis_tab)
        
        # File selection group
        file_group = QGroupBox("Data Selection")
        file_layout = QVBoxLayout()
        
        # Input file selection
        input_layout = QHBoxLayout()
        self.input_file_label = QLabel("No file selected")
        load_button = QPushButton("Load Data")
        load_button.clicked.connect(self.load_data)
        input_layout.addWidget(self.input_file_label)
        input_layout.addWidget(load_button)
        file_layout.addLayout(input_layout)
        
        # Output directory selection
        output_layout = QHBoxLayout()
        self.output_dir_label = QLabel("No output directory selected")
        output_button = QPushButton("Select Output Directory")
        output_button.clicked.connect(self.select_output_directory)
        output_layout.addWidget(self.output_dir_label)
        output_layout.addWidget(output_button)
        file_layout.addLayout(output_layout)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # Feature selection group
        feature_group = QGroupBox("Feature Selection")
        feature_layout = QVBoxLayout()
        
        # Target feature selection
        target_layout = QHBoxLayout()
        target_layout.addWidget(QLabel("Target Feature:"))
        self.target_feature_combo = QComboBox()
        target_layout.addWidget(self.target_feature_combo)
        feature_layout.addLayout(target_layout)
        
        # Analysis features selection
        self.feature_list = QListWidget()
        self.feature_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        feature_layout.addWidget(QLabel("Analysis Features:"))
        feature_layout.addWidget(self.feature_list)
        
        # Feature options container
        self.feature_options_container = QWidget()
        self.feature_options_layout = QVBoxLayout(self.feature_options_container)
        
        # Create scroll area for feature options
        feature_options_scroll = QScrollArea()
        feature_options_scroll.setWidget(self.feature_options_container)
        feature_options_scroll.setWidgetResizable(True)
        feature_layout.addWidget(QLabel("Feature Options:"))
        feature_layout.addWidget(feature_options_scroll)
        
        feature_group.setLayout(feature_layout)
        layout.addWidget(feature_group)
        
        # Analysis parameters group
        params_group = QGroupBox("Analysis Parameters")
        params_layout = QVBoxLayout()
        
        # Contamination parameter
        contamination_layout = QHBoxLayout()
        contamination_layout.addWidget(QLabel("Contamination:"))
        self.contamination_spin = QDoubleSpinBox()
        self.contamination_spin.setRange(0.01, 0.5)
        self.contamination_spin.setSingleStep(0.01)
        self.contamination_spin.setValue(0.1)
        contamination_layout.addWidget(self.contamination_spin)
        params_layout.addLayout(contamination_layout)
        
        params_group.setLayout(params_layout)
        layout.addWidget(params_group)
        
        # Run analysis button
        self.run_button = QPushButton("Run Analysis")
        self.run_button.clicked.connect(self.run_analysis)
        self.run_button.setEnabled(False)
        layout.addWidget(self.run_button)
        
        # Add tab
        self.tab_widget.addTab(analysis_tab, "Analysis")
        
    def setup_results_tab(self):
        """Set up the results tab with plot viewer"""
        results_tab = QWidget()
        layout = QVBoxLayout(results_tab)
        
        # Add plot viewer
        self.plot_viewer = PlotViewer()
        layout.addWidget(self.plot_viewer)
        
        self.tab_widget.addTab(results_tab, "Results")
        
    def setup_logs_tab(self):
        """Set up the logs tab with log viewer"""
        logs_tab = QWidget()
        layout = QVBoxLayout(logs_tab)
        
        # Add log viewer
        self.log_text = QTextEdit()
        layout.addWidget(self.log_text)
        
        # Set up logging to text widget
        log_handler = QTextEditLogger(self.log_text)
        logging.getLogger().addHandler(log_handler)
        
        self.tab_widget.addTab(logs_tab, "Logs")
        
    def load_data(self):
        """Load data from CSV file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Data File",
            "",
            "CSV Files (*.csv);;All Files (*.*)"
        )
        
        if file_path:
            try:
                # Load data
                self.current_data = pd.read_csv(file_path)
                self.input_file_label.setText(os.path.basename(file_path))
                
                # Update feature selection
                self.update_feature_selection()
                
                # Enable run button if output directory is selected
                self.run_button.setEnabled(bool(self.output_dir))
                
                logging.info(f"Loaded data from {file_path}")
                
            except Exception as e:
                logging.error(f"Error loading data: {str(e)}")
                
    def select_output_directory(self):
        """Select output directory for results"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Output Directory",
            ""
        )
        
        if directory:
            self.output_dir = directory
            self.output_dir_label.setText(os.path.basename(directory))
            
            # Enable run button if data is loaded
            self.run_button.setEnabled(bool(self.current_data is not None))
            
            logging.info(f"Selected output directory: {directory}")
            
    def update_feature_selection(self):
        """Update feature selection widgets based on loaded data"""
        if self.current_data is not None:
            # Clear existing items
            self.target_feature_combo.clear()
            self.feature_list.clear()
            
            # Get numeric columns
            numeric_cols = self.current_data.select_dtypes(include=[np.number]).columns
            
            # Update target feature combo box
            self.target_feature_combo.addItems(numeric_cols)
            
            # Update analysis features list
            self.feature_list.addItems(numeric_cols)
            
            # Update feature options
            self.update_feature_options()
            
    def update_feature_options(self):
        """Update feature options based on selected features"""
        # Clear existing options
        for i in reversed(range(self.feature_options_layout.count())):
            widget = self.feature_options_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # Add options for each numeric feature
        numeric_cols = self.current_data.select_dtypes(include=[np.number]).columns
        for feature in numeric_cols:
            option_widget = FeatureOptionsWidget(feature)
            self.feature_options_layout.addWidget(option_widget)
            
    def get_feature_options(self):
        """Get current feature options"""
        options = {}
        for i in range(self.feature_options_layout.count()):
            widget = self.feature_options_layout.itemAt(i).widget()
            if isinstance(widget, FeatureOptionsWidget):
                options[widget.feature_name] = widget.get_options()
        return options
        
    def run_analysis(self):
        """Run the anomaly detection analysis"""
        if not self.current_data is not None or not self.output_dir:
            return
            
        # Get selected features
        selected_features = [item.text() for item in self.feature_list.selectedItems()]
        if not selected_features:
            logging.warning("No features selected for analysis")
            return
            
        # Get target feature
        target_feature = self.target_feature_combo.currentText()
        if not target_feature:
            logging.warning("No target feature selected")
            return
            
        # Get feature options
        feature_options = self.get_feature_options()
        
        # Create and start analysis thread
        self.analysis_thread = AnalysisWorker(
            input_file=self.input_file_label.text(),
            output_dir=self.output_dir,
            target_feature=target_feature,
            analysis_features=selected_features,
            contamination=self.contamination_spin.value(),
            feature_options=feature_options
        )
        
        # Connect signals
        self.analysis_thread.progress.connect(lambda msg: logging.info(msg))
        self.analysis_thread.error.connect(lambda msg: logging.error(msg))
        self.analysis_thread.finished.connect(self.analysis_completed)
        
        # Disable run button during analysis
        self.run_button.setEnabled(False)
        
        # Start analysis
        self.analysis_thread.start()
        logging.info("Started analysis")
        
    def analysis_completed(self, result):
        """Handle completed analysis"""
        self.current_result = result
        
        # Update plot viewer
        if self.output_dir:
            self.plot_viewer.set_plots_directory(self.output_dir)
        
        # Re-enable run button
        self.run_button.setEnabled(True)
        
        # Switch to results tab
        self.tab_widget.setCurrentIndex(1)
        
        logging.info("Analysis completed")
        
    def load_config(self):
        """Load configuration from file"""
        config_path = Path("config.json")
        if config_path.exists():
            try:
                with open(config_path) as f:
                    return json.load(f)
            except Exception as e:
                logging.error(f"Error loading config: {str(e)}")
        return {}
