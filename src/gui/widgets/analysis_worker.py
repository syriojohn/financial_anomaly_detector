from PySide6.QtCore import QThread, Signal
from src.core.advanced_analyzer import AdvancedAnomalyAnalyzer

class AnalysisWorker(QThread):
    analysis_complete = Signal(object)
    error_occurred = Signal(str)
    progress_update = Signal(str)
    
    def __init__(self, data, feature_options, contamination=0.1):
        super().__init__()
        self.data = data
        self.feature_options = feature_options
        self.contamination = contamination
        
    def run(self):
        try:
            self.progress_update.emit("Initializing analysis...")
            analyzer = AdvancedAnomalyAnalyzer(contamination=self.contamination)
            
            self.progress_update.emit("Processing features...")
            analyzer.prepare_features(self.data, self.feature_options)
            
            self.progress_update.emit("Running anomaly detection...")
            result = analyzer.analyze()
            
            self.progress_update.emit("Generating visualizations...")
            analyzer.generate_plots(result)
            
            self.analysis_complete.emit(result)
            
        except Exception as e:
            self.error_occurred.emit(str(e))
