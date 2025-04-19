import tkinter as tk
from tkinter import ttk
from datetime import datetime

class AchievementsManager:
    def __init__(self, app):
        self.app = app
        self.data_manager = app.data_manager

    def show_achievements(self):
        """Display achievements"""
        window = tk.Toplevel(self.app.root)
        window.title("Достижения")
        window.geometry("400x300")

        frame = ttk.Frame(window)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        achievements = self.data_manager.data["achievements"]

        ttk.Label(frame, text="Стабильный садовник: 30 дней без пропусков полива").pack(pady=2)
        stable_status = "Достигнуто" if achievements["stable_watering"]["completed"] else \
                        f"Прогресс: {achievements['stable_watering']['days']}/30 дней"
        ttk.Label(frame, text=stable_status,
                  foreground="green" if achievements["stable_watering"]["completed"] else "black").pack(pady=2)

        ttk.Label(frame, text="Фотограф кактусов: Добавить 10 фото").pack(pady=2)
        photo_status = "Достигнуто" if achievements["photo_collector"]["completed"] else \
                       f"Прогресс: {achievements['photo_collector']['photos']}/10 фото"
        ttk.Label(frame, text=photo_status,
                  foreground="green" if achievements["photo_collector"]["completed"] else "black").pack(pady=2)

        ttk.Label(frame, text="Мастер пересадки: Пересадить 3 кактуса").pack(pady=2)
        repot_status = "Достигнуто" if achievements["repotting_master"]["completed"] else \
                       f"Прогресс: {achievements['repotting_master']['repottings']}/3 пересадок"
        ttk.Label(frame, text=repot_status,
                  foreground="green" if achievements["repotting_master"]["completed"] else "black").pack(pady=2)

        ttk.Label(frame, text="Рост мастер: 5 измерений роста для одного кактуса").pack(pady=2)
        growth_status = "Достигнуто" if achievements["growth_master"]["completed"] else "Прогресс: см. профиль кактуса"
        ttk.Label(frame, text=growth_status,
                  foreground="green" if achievements["growth_master"]["completed"] else "black").pack(pady=2)

    def check_achievements(self):
        """Check and update achievements"""
        achievements = self.data_manager.data["achievements"]

        # Stable watering achievement
        all_watered_on_time = True
        for cactus_data in self.data_manager.data["cactuses"].values():
            if cactus_data["watering"]:
                last_watering = datetime.strptime(cactus_data["watering"][-1]["date"], "%Y-%m-%d %H:%M")
                days_since = (datetime.now() - last_watering).days
                if days_since > cactus_data["watering_frequency"] + 1:
                    all_watered_on_time = False
                    achievements["stable_watering"]["days"] = 0
                    break
        if all_watered_on_time and not achievements["stable_watering"]["completed"]:
            achievements["stable_watering"]["days"] += 1
            if achievements["stable_watering"]["days"] >= 30:
                achievements["stable_watering"]["completed"] = True

        self.data_manager.save_data()