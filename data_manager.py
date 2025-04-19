import json
import os
import csv
import shutil
from datetime import datetime
from tkinter import filedialog, messagebox
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet

class DataManager:
    def __init__(self, data_file):
        self.data_file = data_file
        self.data = {}
        self.load_data()

    def load_data(self):
        """Load data from JSON file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
                if "cactuses" not in self.data:
                    self.data["cactuses"] = {}
                if "achievements" not in self.data:
                    self.data["achievements"] = {
                        "stable_watering": {"completed": False, "days": 0},
                        "photo_collector": {"completed": False, "photos": 0},
                        "repotting_master": {"completed": False, "repottings": 0},
                        "growth_master": {"completed": False, "growths": {}}
                    }
                for cactus in self.data["cactuses"].values():
                    if "notes" not in cactus:
                        cactus["notes"] = ""
                    if "next_repotting" not in cactus:
                        cactus["next_repotting"] = None
            except json.JSONDecodeError:
                self.initialize_default_data()
        else:
            self.initialize_default_data()
        self.save_data()

    def initialize_default_data(self):
        """Initialize default data structure"""
        self.data = {
            "cactuses": {},
            "achievements": {
                "stable_watering": {"completed": False, "days": 0},
                "photo_collector": {"completed": False, "photos": 0},
                "repotting_master": {"completed": False, "repottings": 0},
                "growth_master": {"completed": False, "growths": {}}
            }
        }

    def save_data(self):
        """Save data to JSON file"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)

    def export_data(self, parent):
        """Export data to CSV or PDF"""
        formats = [("CSV файл (*.csv)", "*.csv"), ("PDF файл (*.pdf)", "*.pdf")]
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=formats,
            initialfile="cactus_data_export"
        )
        if not file_path:
            return

        if file_path.endswith(".csv"):
            self.export_to_csv(file_path)
        elif file_path.endswith(".pdf"):
            self.export_to_pdf(file_path)

        messagebox.showinfo("Успех", f"Данные экспортированы в {file_path}")

    def export_to_csv(self, file_path):
        """Export data to CSV"""
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Имя кактуса", "Частота полива (дней)", "Последний полив", "Рост (см)", "Фото", "Заметки",
                             "Следующая пересадка"])

            for cactus_name, cactus_data in self.data["cactuses"].items():
                last_watering = cactus_data["watering"][-1]["date"] if cactus_data["watering"] else "Нет данных"
                growth = "; ".join([f"{g['date']} - {g['height']} см" for g in cactus_data["growth"]]) or "Нет данных"
                photos = "; ".join([p["date"] + " - " + p["path"] for p in cactus_data["photos"]]) or "Нет данных"
                next_repotting = cactus_data["next_repotting"] or "Не установлено"
                writer.writerow([cactus_name, cactus_data["watering_frequency"], last_watering, growth, photos,
                                 cactus_data["notes"], next_repotting])

    def export_to_pdf(self, file_path):
        """Export data to PDF"""
        doc = SimpleDocTemplate(file_path, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []

        elements.append(Paragraph("Данные о кактусах", styles["Title"]))
        elements.append(Spacer(1, 12))

        for cactus_name, cactus_data in self.data["cactuses"].items():
            elements.append(Paragraph(f"Кактус: {cactus_name}", styles["Heading2"]))
            elements.append(Spacer(1, 6))

            elements.append(Paragraph(f"Частота полива: {cactus_data['watering_frequency']} дней", styles["BodyText"]))
            last_watering = cactus_data["watering"][-1]["date"] if cactus_data["watering"] else "Нет данных"
            elements.append(Paragraph(f"Последний полив: {last_watering}", styles["BodyText"]))

            growth_data = [["Дата", "Высота (см)"]] + [[g["date"], g["height"]] for g in cactus_data["growth"]]
            if len(growth_data) > 1:
                growth_table = Table(growth_data)
                growth_table.setStyle([("GRID", (0, 0), (-1, -1), 1, "black")])
                elements.append(Paragraph("Рост:", styles["BodyText"]))
                elements.append(growth_table)
            else:
                elements.append(Paragraph("Рост: Нет данных", styles["BodyText"]))

            photos = "; ".join([f"{p['date']} - {p['path']}" for p in cactus_data["photos"]]) or "Нет данных"
            elements.append(Paragraph(f"Фото: {photos}", styles["BodyText"]))

            elements.append(Paragraph(f"Заметки: {cactus_data['notes'] or 'Нет заметок'}", styles["BodyText"]))
            next_repotting = cactus_data["next_repotting"] or "Не установлено"
            elements.append(Paragraph(f"Следующая пересадка: {next_repotting}", styles["BodyText"]))
            elements.append(Spacer(1, 12))

        doc.build(elements)

    def backup_data(self):
        """Create a backup of the data file"""
        backup_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON файл (*.json)", "*.json")],
            initialfile=f"cactus_data_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        if backup_path:
            try:
                shutil.copy(self.data_file, backup_path)
                messagebox.showinfo("Успех", f"Резервная копия сохранена в {backup_path}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось создать резервную копию: {str(e)}")

    def restore_data(self):
        """Restore data from a backup file"""
        backup_path = filedialog.askopenfilename(
            filetypes=[("JSON файл (*.json)", "*.json")],
            title="Выберите файл резервной копии"
        )
        if backup_path:
            try:
                # Validate the backup file
                with open(backup_path, 'r', encoding='utf-8') as f:
                    json.load(f)  # Ensure it's valid JSON
                shutil.copy(backup_path, self.data_file)
                self.load_data()  # Reload data
                messagebox.showinfo("Успех", "Данные восстановлены из резервной копии")
                return True
            except json.JSONDecodeError:
                messagebox.showerror("Ошибка", "Недопустимый файл резервной копии")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось восстановить данные: {str(e)}")
        return False