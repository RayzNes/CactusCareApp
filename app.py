import tkinter as tk
from tkinter import ttk
from data_manager import DataManager
from ui_components import UIManager
from visualization import VisualizationManager
from health_diagnosis import HealthDiagnosis

class CactusCareApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Уход за кактусами")
        self.root.geometry("900x700")

        # Initialize managers in correct order
        self.data_manager = DataManager("cactus_data.json")
        self.visualization_manager = VisualizationManager(self)
        self.ui_manager = UIManager(self)

        # Create main interface
        self.ui_manager.create_main_window()

        # Initial profile display
        if self.data_manager.data["cactuses"]:
            self.ui_manager.show_cactus_profile(None)