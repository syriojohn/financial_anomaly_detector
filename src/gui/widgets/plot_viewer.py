import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QPushButton, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

class PlotViewer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        
        # Create scroll area for plots
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Container for plots
        self.plot_container = QWidget()
        self.plot_layout = QVBoxLayout(self.plot_container)
        
        self.scroll.setWidget(self.plot_container)
        self.layout.addWidget(self.scroll)
        
        # Refresh button
        self.refresh_btn = QPushButton("Refresh Plots")
        self.refresh_btn.clicked.connect(self.load_plots)
        self.layout.addWidget(self.refresh_btn)
        
        self.plots_dir = None
        
    def set_plots_directory(self, directory):
        """Set the directory containing plot images"""
        self.plots_dir = directory
        self.load_plots()
        
    def load_plots(self):
        """Load and display all plot images from the plots directory"""
        # Clear existing plots
        for i in reversed(range(self.plot_layout.count())):
            widget = self.plot_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        if not self.plots_dir or not os.path.exists(self.plots_dir):
            return
            
        # Load each PNG file
        for filename in sorted(os.listdir(self.plots_dir)):
            if filename.endswith('.png'):
                # Create label for plot title
                title = filename.replace('.png', '').replace('_', ' ').title()
                title_label = QLabel(title)
                title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.plot_layout.addWidget(title_label)
                
                # Create label for plot image
                plot_label = QLabel()
                pixmap = QPixmap(os.path.join(self.plots_dir, filename))
                scaled_pixmap = pixmap.scaled(800, 600, Qt.AspectRatioMode.KeepAspectRatio)
                plot_label.setPixmap(scaled_pixmap)
                plot_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.plot_layout.addWidget(plot_label)
                
                # Add spacing between plots
                self.plot_layout.addSpacing(20)
