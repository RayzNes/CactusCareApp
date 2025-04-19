import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class VisualizationManager:
    def __init__(self, app):
        self.app = app
        self.data_manager = app.data_manager

    def animate_cactus(self, cactus_name, canvas):
        """Animate cactus growth"""
        cactus_data = self.data_manager.data["cactuses"][cactus_name]
        canvas.delete("all")

        # Determine cactus height
        max_height = max([g["height"] for g in cactus_data["growth"]]) if cactus_data["growth"] else 5

        # Determine color based on health
        color = self.get_cactus_color(cactus_data)

        # Scale height for Canvas
        cactus_height = min(max_height * 10, 250)  # 1 cm = 10 pixels, max 250
        base_y = 300  # Bottom of Canvas

        # Draw pot
        canvas.create_rectangle(80, base_y - 50, 120, base_y, fill="brown", outline="black")

        # Initial cactus position
        current_height = 50

        def grow(step=0):
            if step <= 20:  # 20 animation steps
                canvas.delete("cactus")
                height = current_height + (cactus_height - current_height) * step / 20
                canvas.create_rectangle(90, base_y - height, 110, base_y - 50,
                                        fill=color, outline="black", tags="cactus")
                # Add spines
                for y in range(int(base_y - height), int(base_y - 50), 20):
                    canvas.create_line(90, y, 85, y, fill="black")
                    canvas.create_line(110, y, 115, y, fill="black")
                self.app.root.after(50, grow, step + 1)

        grow()

    def get_cactus_color(self, cactus_data):
        """Determine cactus color based on watering status"""
        if cactus_data["watering"]:
            last_watering = datetime.strptime(cactus_data["watering"][-1]["date"], "%Y-%m-%d %H:%M")
            days_since_watering = (datetime.now() - last_watering).days
            freq = cactus_data["watering_frequency"]
            if days_since_watering < freq:
                return "green"
            elif freq <= days_since_watering <= freq + 1:
                return "yellow"
            else:
                return "red"
        return "red"

    def update_health_indicator(self, cactus_name, health_indicator):
        """Update health indicator"""
        cactus_data = self.data_manager.data["cactuses"][cactus_name]
        health_indicator.delete("all")
        color = self.get_cactus_color(cactus_data)
        health_indicator.create_oval(2, 2, 18, 18, fill=color, outline="black")

    def show_graphs(self, cactus_name):
        """Display growth and watering graphs"""
        cactus_data = self.data_manager.data["cactuses"][cactus_name]

        window = tk.Toplevel(self.app.root)
        window.title(f"Графики для {cactus_name}")
        window.geometry("800x600")

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6))

        if cactus_data["growth"]:
            dates = [datetime.strptime(g["date"], "%Y-%m-%d %H:%M") for g in cactus_data["growth"]]
            heights = [g["height"] for g in cactus_data["growth"]]
            ax1.plot(dates, heights, marker="o", color="green", label="Рост (см)")
            ax1.set_title("Динамика роста")
            ax1.set_xlabel("Дата")
            ax1.set_ylabel("Высота (см)")
            ax1.legend()
            ax1.grid(True)
            plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
        else:
            ax1.text(0.5, 0.5, "Нет данных о росте", horizontalalignment="center", verticalalignment="center")
            ax1.set_title("Динамика роста")

        if cactus_data["watering"]:
            dates = [datetime.strptime(w["date"], "%Y-%m-%d %H:%M") for w in cactus_data["watering"]]
            watering_counts = [1] * len(dates)
            ax2.bar(dates, watering_counts, color="blue", label="Поливы")
            ax2.set_title("Частота полива")
            ax2.set_xlabel("Дата")
            ax2.set_ylabel("Количество поливов")
            ax2.legend()
            ax2.grid(True)
            plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
        else:
            ax2.text(0.5, 0.5, "Нет данных о поливах", horizontalalignment="center", verticalalignment="center")
            ax2.set_title("Частота полива")

        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        ttk.Button(window, text="Сохранить график", command=lambda: self.save_graph(fig, cactus_name)).pack(pady=10)

    def save_graph(self, fig, cactus_name):
        """Save graph as image"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png")],
            initialfile=f"{cactus_name}_graphs.png"
        )
        if file_path:
            fig.savefig(file_path, dpi=100, bbox_inches="tight")
            messagebox.showinfo("Успех", "График сохранен!")

