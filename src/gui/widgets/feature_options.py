from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QCheckBox

class FeatureOptionsWidget(QWidget):
    def __init__(self, feature_name, parent=None):
        super().__init__(parent)
        self.feature_name = feature_name
        layout = QHBoxLayout(self)
        
        # Feature name label
        self.label = QLabel(feature_name)
        layout.addWidget(self.label)
        
        # Checkboxes for options
        self.use_raw = QCheckBox("Use Raw")
        self.use_raw.setChecked(True)  # Default to True
        self.use_ratio = QCheckBox("Use Ratio")
        self.use_ratio.setChecked(True)  # Default to True
        
        layout.addWidget(self.use_raw)
        layout.addWidget(self.use_ratio)
        
    def get_options(self):
        return {
            'use_raw': self.use_raw.isChecked(),
            'use_ratio': self.use_ratio.isChecked()
        }
