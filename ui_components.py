import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta, date
from PIL import Image, ImageTk
from achievements import AchievementsManager
from visualization import VisualizationManager
from species_database import SpeciesDatabase
from health_diagnosis import HealthDiagnosis
from utils import sort_cactuses


class UIManager:
    def __init__(self, app):
        self.app = app
        self.root = app.root
        self.data_manager = app.data_manager
        self.visualization_manager = app.visualization_manager
        self.achievements_manager = AchievementsManager(app)
        self.species_db = SpeciesDatabase()
        self.health_diagnosis = HealthDiagnosis()

    def create_main_window(self):
        """Create the main window"""
        self.root.configure(bg="#f0f0f0")

        title = tk.Label(self.root, text="Мои кактусы", font=("Arial", 20, "bold"), bg="#f0f0f0", fg="#2e7d32")
        title.pack(pady=10)

        self.cactus_frame = ttk.Frame(self.root)
        self.cactus_frame.pack(pady=10, fill="x", padx=20)

        ttk.Label(self.cactus_frame, text="Выберите кактус:").pack(side="left", padx=5)
        self.cactus_var = tk.StringVar()
        self.cactus_dropdown = ttk.Combobox(self.cactus_frame, textvariable=self.cactus_var)
        self.cactus_dropdown.pack(side="left", padx=5)
        self.cactus_dropdown.bind("<<ComboboxSelected>>", self.show_cactus_profile)

        ttk.Button(self.cactus_frame, text="Добавить кактус", command=self.add_cactus).pack(side="left", padx=5)

        ttk.Label(self.cactus_frame, text="Сортировать по:").pack(side="left", padx=5)
        self.sort_var = tk.StringVar(value="По имени")
        sort_options = [("По имени", "name"), ("По частоте полива", "frequency"),
                        ("По последнему поливу", "last_watering")]
        self.sort_dropdown = ttk.Combobox(self.cactus_frame, textvariable=self.sort_var,
                                          values=[opt[0] for opt in sort_options])
        self.sort_dropdown.pack(side="left", padx=5)
        self.sort_dropdown.bind("<<ComboboxSelected>>", lambda e: self.update_cactus_dropdown())

        ttk.Button(self.cactus_frame, text="Подсказки по уходу", command=self.show_care_tips).pack(side="left", padx=5)
        ttk.Button(self.cactus_frame, text="Экспорт данных",
                   command=lambda: self.data_manager.export_data(self.root)).pack(side="left", padx=5)
        ttk.Button(self.cactus_frame, text="Достижения", command=self.achievements_manager.show_achievements).pack(
            side="left", padx=5)
        ttk.Button(self.cactus_frame, text="Создать резервную копию", command=self.data_manager.backup_data).pack(
            side="left", padx=5)
        ttk.Button(self.cactus_frame, text="Восстановить данные", command=self.restore_data).pack(side="left", padx=5)
        ttk.Button(self.cactus_frame, text="Массовая обработка", command=self.bulk_processing).pack(side="left", padx=5)

        self.update_cactus_dropdown()

        self.content_frame = ttk.Frame(self.root)
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=10)

    def update_cactus_dropdown(self):
        """Update cactus dropdown with sorted list"""
        cactus_list = sort_cactuses(self.data_manager.data["cactuses"], self.sort_var.get())
        self.cactus_dropdown["values"] = cactus_list
        if cactus_list:
            self.cactus_var.set(cactus_list[0])
        else:
            self.cactus_var.set("")

    def show_cactus_profile(self, event):
        """Display selected cactus profile"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        cactus_name = self.cactus_var.get()
        if not cactus_name:
            ttk.Label(self.content_frame, text="Добавьте кактус, чтобы получить профиль").pack(pady=20)
            return

        cactus_data = self.data_manager.data["cactuses"][cactus_name]
        self.achievements_manager.check_achievements()

        profile_frame = ttk.Frame(self.content_frame)
        profile_frame.pack(fill="both", expand=True)

        # Visualization frame
        vis_frame = ttk.LabelFrame(profile_frame, text="Визуализация")
        vis_frame.pack(side="left", padx=10, pady=10, fill="y")
        self.cactus_canvas = tk.Canvas(vis_frame, width=200, height=300, bg="white")
        self.cactus_canvas.pack(pady=5)
        self.visualization_manager.animate_cactus(cactus_name, self.cactus_canvas)

        # Photo frame
        photo_frame = ttk.LabelFrame(profile_frame, text="Последнее фото")
        photo_frame.pack(side="left", padx=10, pady=10, fill="y")
        if cactus_data["photos"]:
            img_path = cactus_data["photos"][-1]["path"]
            try:
                img = Image.open(img_path).resize((200, 200), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                photo_label = ttk.Label(photo_frame, image=photo)
                photo_label.image = photo
                photo_label.pack(pady=5)
            except FileNotFoundError:
                ttk.Label(photo_frame, text="Фото не найдено").pack(pady=5)
        else:
            ttk.Label(photo_frame, text="Фото отсутствует").pack(pady=5)

        # Info frame
        info_frame = ttk.LabelFrame(profile_frame, text=f"Профиль: {cactus_name}")
        info_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Display species information
        species = cactus_data.get("species", "Не указан")
        species_info = self.species_db.get_species_data(species)
        species_text = f"Вид: {species}\nОбщее название: {species_info.get('common_name', 'Неизвестно')}"
        ttk.Label(info_frame, text=species_text).pack(pady=5)

        # Seasonal care recommendations
        current_month = date.today().month
        season = "winter" if current_month in [12, 1, 2] else "spring" if current_month in [3, 4, 5] else \
            "summer" if current_month in [6, 7, 8] else "autumn"
        seasonal_care = species_info.get("seasonal_care", {}).get(season, "Нет рекомендаций")
        ttk.Label(info_frame, text=f"Сезонные рекомендации ({season}): {seasonal_care}").pack(pady=5)

        # Fertilizer recommendation
        fertilizer_rec = species_info.get("fertilizer_recommendation", "Нет рекомендаций")
        ttk.Label(info_frame, text=f"Рекомендации по удобрениям: {fertilizer_rec}").pack(pady=5)

        health_frame = ttk.Frame(info_frame)
        health_frame.pack(pady=5)
        ttk.Label(health_frame, text="Здоровье:").pack(side="left")
        self.health_indicator = tk.Canvas(health_frame, width=20, height=20)
        self.health_indicator.pack(side="left", padx=5)
        self.visualization_manager.update_health_indicator(cactus_name, self.health_indicator)

        ttk.Button(info_frame, text="Добавить полив", command=lambda: self.add_watering(cactus_name)).pack(pady=5)
        ttk.Button(info_frame, text="Записать рост", command=lambda: self.add_growth(cactus_name)).pack(pady=5)
        ttk.Button(info_frame, text="Добавить фото", command=lambda: self.add_photo(cactus_name)).pack(pady=5)
        ttk.Button(info_frame, text="Добавить подкормку", command=lambda: self.add_fertilizer(cactus_name)).pack(pady=5)
        ttk.Button(info_frame, text="Диагностика здоровья", command=lambda: self.diagnose_health(cactus_name)).pack(
            pady=5)
        ttk.Button(info_frame, text="Показать графики",
                   command=lambda: self.visualization_manager.show_graphs(cactus_name)).pack(pady=5)
        ttk.Button(info_frame, text="Фотоальбом", command=lambda: self.show_photo_album(cactus_name)).pack(pady=5)
        ttk.Button(info_frame, text="Редактировать заметки", command=lambda: self.edit_notes(cactus_name)).pack(pady=5)
        ttk.Button(info_frame, text="Запланировать пересадку", command=lambda: self.plan_repotting(cactus_name)).pack(
            pady=5)

        ttk.Label(info_frame, text="Частота полива (дней):").pack()
        self.freq_entry = ttk.Entry(info_frame)
        seasonal_freq = self.data_manager.get_seasonal_watering_frequency(cactus_name, self.species_db)
        self.freq_entry.insert(0, str(seasonal_freq))
        self.freq_entry.pack()
        ttk.Button(info_frame, text="Сохранить частоту", command=lambda: self.save_frequency(cactus_name)).pack(pady=5)

        self.reminder_label = ttk.Label(info_frame, text="")
        self.reminder_label.pack(pady=5)
        self.update_reminder(cactus_name)

        self.repotting_label = ttk.Label(info_frame, text="")
        self.repotting_label.pack(pady=5)
        self.update_repotting_reminder(cactus_name)

        growth_count = len(cactus_data["growth"])
        ttk.Label(info_frame, text=f"Измерений роста: {growth_count}/5 (Рост мастер)").pack(pady=5)

        notes_frame = ttk.LabelFrame(info_frame, text="Заметки")
        notes_frame.pack(fill="x", pady=5)
        self.notes_text = tk.Text(notes_frame, height=5, width=40, wrap="word", font=("Arial", 10))
        self.notes_text.insert("1.0", cactus_data["notes"] or "Нет заметок")
        self.notes_text.config(state="disabled")
        self.notes_text.pack(pady=5)

        history_frame = ttk.LabelFrame(self.content_frame, text="История")
        history_frame.pack(fill="both", expand=True, pady=10)
        self.history_text = tk.Text(history_frame, height=10, width=80, bg="#ffffff", font=("Arial", 10))
        self.history_text.pack(pady=5)
        self.update_history(cactus_name)

    def add_cactus(self):
        """Add a new cactus with species selection"""
        window = tk.Toplevel(self.root)
        window.title("Новый кактус")
        window.geometry("300x250")

        ttk.Label(window, text="Имя кактуса:").pack(pady=5)
        name_entry = ttk.Entry(window)
        name_entry.pack(pady=5)

        ttk.Label(window, text="Выберите вид:").pack(pady=5)
        species_var = tk.StringVar()
        species_dropdown = ttk.Combobox(window, textvariable=species_var, values=self.species_db.get_species_list())
        species_dropdown.pack(pady=5)
        species_dropdown.set("")

        ttk.Label(window, text="Частота полива (дней):").pack(pady=5)
        freq_entry = ttk.Entry(window)
        freq_entry.pack(pady=5)

        def update_frequency(event):
            species = species_var.get()
            if species:
                species_data = self.species_db.get_species_data(species)
                freq_entry.delete(0, tk.END)
                freq_entry.insert(0, str(species_data.get("watering_frequency", 7)))

        species_dropdown.bind("<<ComboboxSelected>>", update_frequency)

        def save_cactus():
            name = name_entry.get().strip()
            species = species_var.get()
            try:
                freq = int(freq_entry.get()) if freq_entry.get() else 7
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректное число для частоты полива")
                return

            if name and name not in self.data_manager.data["cactuses"]:
                self.data_manager.data["cactuses"][name] = {
                    "watering": [],
                    "growth": [],
                    "photos": [],
                    "fertilizers": [],
                    "watering_frequency": freq,
                    "notes": "",
                    "next_repotting": None,
                    "species": species if species else "Не указан"
                }
                self.data_manager.save_data()
                self.update_cactus_dropdown()
                self.cactus_var.set(name)
                self.show_cactus_profile(None)
                window.destroy()
            elif not name:
                messagebox.showerror("Ошибка", "Введите имя кактуса")
            else:
                messagebox.showerror("Ошибка", "Кактус с таким именем уже существует")

        ttk.Button(window, text="Сохранить", command=save_cactus).pack(pady=10)

    def show_care_tips(self):
        """Show care tips"""
        tips_window = tk.Toplevel(self.root)
        tips_window.title("Подсказки по уходу за кактусами")
        tips_window.geometry("600x400")

        tips_frame = ttk.Frame(tips_window)
        tips_frame.pack(fill="both", expand=True, padx=10, pady=10)

        tips_text = tk.Text(tips_frame, wrap="word", height=20, width=70, font=("Arial", 12))
        tips_text.pack(fill="both", expand=True)

        care_tips = """
        **Советы по уходу за кактусами**

        1. **Полив:**
        - Большинство кактусов требуют редкого полива. Летом поливайте раз в 7-14 дней, зимой — раз в 3-4 недели.
        - Убедитесь, что почва полностью просохла перед следующим поливом.
        - Используйте воду комнатной температуры, избегайте переувлажнения.

        2. **Освещение:**
        - Кактусы любят яркий свет. Размещайте их на южных или восточных окнах.
        - Зимой может потребоваться дополнительное освещение (фитолампы).

        3. **Температура:**
        - Оптимальная температура летом: 20-30°C.
        - Зимой желательно снизить до 10-15°C для периода покоя.

        4. **Почва:**
        - Используйте хорошо дренированную смесь (песок, перлит, земля в равных частях).
        - Горшок должен иметь дренажные отверстия.

        5. **Удобрения:**
        - Подкармливайте раз в месяц весной и летом специальным удобрением для кактусов (с низким содержанием азота).

        6. **Пересадка:**
        - Пересаживайте раз в 1-2 года весной, если горшок стал тесным.

        Следите за состоянием вашего кактуса и корректируйте уход в зависимости от его вида и условий!
        """

        tips_text.insert("1.0", care_tips)
        tips_text.config(state="disabled")

        scrollbar = ttk.Scrollbar(tips_frame, orient="vertical", command=tips_text.yview)
        scrollbar.pack(side="right", fill="y")
        tips_text.config(yscrollcommand=scrollbar.set)

    def add_watering(self, cactus_name):
        """Add watering record"""
        window = tk.Toplevel(self.root)
        window.title("Добавить полив")
        window.geometry("300x200")

        ttk.Label(window, text="Комментарий:").pack()
        comment_entry = ttk.Entry(window, width=30)
        comment_entry.pack(pady=5)

        def save_watering():
            comment = comment_entry.get()
            watering = {
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "comment": comment
            }
            self.data_manager.data["cactuses"][cactus_name]["watering"].append(watering)
            self.data_manager.save_data()
            self.update_history(cactus_name)
            self.update_reminder(cactus_name)
            self.visualization_manager.update_health_indicator(cactus_name, self.health_indicator)
            self.achievements_manager.check_achievements()
            self.visualization_manager.animate_cactus(cactus_name, self.cactus_canvas)
            self.update_cactus_dropdown()
            window.destroy()

        ttk.Button(window, text="Сохранить", command=save_watering).pack(pady=10)

    def add_growth(self, cactus_name):
        """Add growth record"""
        window = tk.Toplevel(self.root)
        window.title("Записать рост")
        window.geometry("300x200")

        ttk.Label(window, text="Рост (см):").pack()
        height_entry = ttk.Entry(window)
        height_entry.pack(pady=5)

        ttk.Label(window, text="Комментарий:").pack()
        comment_entry = ttk.Entry(window, width=30)
        comment_entry.pack(pady=5)

        def save_growth():
            try:
                height = float(height_entry.get())
                comment = comment_entry.get()
                growth = {
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "height": height,
                    "comment": comment
                }
                self.data_manager.data["cactuses"][cactus_name]["growth"].append(growth)
                self.data_manager.save_data()
                self.update_history(cactus_name)
                self.data_manager.data["achievements"]["growth_master"]["growths"][cactus_name] = len(
                    self.data_manager.data["cactuses"][cactus_name]["growth"])
                if self.data_manager.data["achievements"]["growth_master"]["growths"][cactus_name] >= 5 and not \
                        self.data_manager.data["achievements"]["growth_master"]["completed"]:
                    self.data_manager.data["achievements"]["growth_master"]["completed"] = True
                self.data_manager.save_data()
                self.visualization_manager.animate_cactus(cactus_name, self.cactus_canvas)
                window.destroy()
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректное число для роста")

        ttk.Button(window, text="Сохранить", command=save_growth).pack(pady=10)

    def add_photo(self, cactus_name):
        """Add photo"""
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg")])
        if file_path:
            photo = {
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "path": file_path
            }
            self.data_manager.data["cactuses"][cactus_name]["photos"].append(photo)
            self.data_manager.save_data()
            self.data_manager.data["achievements"]["photo_collector"]["photos"] += 1
            if self.data_manager.data["achievements"]["photo_collector"]["photos"] >= 10:
                self.data_manager.data["achievements"]["photo_collector"]["completed"] = True
            self.data_manager.save_data()
            self.show_cactus_profile(None)
            messagebox.showinfo("Успех", "Фото добавлено!")

    def add_fertilizer(self, cactus_name):
        """Add fertilizer record"""
        window = tk.Toplevel(self.root)
        window.title("Добавить подкормку")
        window.geometry("300x300")

        ttk.Label(window, text="Тип удобрения:").pack(pady=5)
        type_entry = ttk.Entry(window)
        type_entry.pack(pady=5)

        ttk.Label(window, text="Дозировка (например, 5 мл/л):").pack(pady=5)
        dosage_entry = ttk.Entry(window)
        dosage_entry.pack(pady=5)

        ttk.Label(window, text="Комментарий:").pack(pady=5)
        comment_entry = ttk.Entry(window, width=30)
        comment_entry.pack(pady=5)

        def save_fertilizer():
            fertilizer_type = type_entry.get().strip()
            dosage = dosage_entry.get().strip()
            comment = comment_entry.get()
            if not fertilizer_type or not dosage:
                messagebox.showerror("Ошибка", "Укажите тип удобрения и дозировку")
                return
            fertilizer = {
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "type": fertilizer_type,
                "dosage": dosage,
                "comment": comment
            }
            self.data_manager.data["cactuses"][cactus_name]["fertilizers"].append(fertilizer)
            self.data_manager.save_data()
            self.update_history(cactus_name)
            self.show_cactus_profile(None)
            window.destroy()

        ttk.Button(window, text="Сохранить", command=save_fertilizer).pack(pady=10)

    def diagnose_health(self, cactus_name):
        """Show health diagnosis interface"""
        window = tk.Toplevel(self.root)
        window.title("Диагностика здоровья")
        window.geometry("400x400")

        ttk.Label(window, text="Выберите симптомы:").pack(pady=5)
        symptoms = self.health_diagnosis.get_symptoms()
        selected_symptoms = []

        for symptom in symptoms:
            var = tk.BooleanVar()
            ttk.Checkbutton(window, text=symptom, variable=var).pack(anchor="w", padx=10)
            selected_symptoms.append((symptom, var))

        def diagnose():
            chosen_symptoms = [symptom for symptom, var in selected_symptoms if var.get()]
            if not chosen_symptoms:
                messagebox.showwarning("Предупреждение", "Выберите хотя бы один симптом")
                return
            diagnosis = self.health_diagnosis.diagnose(chosen_symptoms)
            result_window = tk.Toplevel(window)
            result_window.title("Результат диагностики")
            result_window.geometry("400x300")
            result_text = tk.Text(result_window, wrap="word", height=15, width=50, font=("Arial", 12))
            result_text.pack(fill="both", expand=True, padx=10, pady=10)
            result_text.insert("1.0", diagnosis)
            result_text.config(state="disabled")

        ttk.Button(window, text="Диагностировать", command=diagnose).pack(pady=10)

    def save_frequency(self, cactus_name):
        """Save watering frequency"""
        try:
            freq = int(self.freq_entry.get())
            if freq > 0:
                self.data_manager.data["cactuses"][cactus_name]["watering_frequency"] = freq
                self.data_manager.save_data()
                self.update_reminder(cactus_name)
                self.visualization_manager.update_health_indicator(cactus_name, self.health_indicator)
                self.achievements_manager.check_achievements()
                self.visualization_manager.animate_cactus(cactus_name, self.cactus_canvas)
                self.update_cactus_dropdown()
            else:
                messagebox.showerror("Ошибка", "Частота должна быть положительной")
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное число")

    def update_reminder(self, cactus_name):
        """Update watering reminder"""
        cactus_data = self.data_manager.data["cactuses"][cactus_name]
        seasonal_freq = self.data_manager.get_seasonal_watering_frequency(cactus_name, self.species_db)
        if cactus_data["watering"]:
            last_watering = datetime.strptime(cactus_data["watering"][-1]["date"], "%Y-%m-%d %H:%M")
            next_watering = last_watering + timedelta(days=seasonal_freq)
            days_left = (next_watering - datetime.now()).days
            if days_left <= 0:
                self.reminder_label.config(text="Пора полить кактус!", foreground="red")
            else:
                self.reminder_label.config(text=f"Следующий полив через {days_left} дней", foreground="green")
        else:
            self.reminder_label.config(text="Добавьте первый полив", foreground="black")

    def update_repotting_reminder(self, cactus_name):
        """Update repotting reminder"""
        cactus_data = self.data_manager.data["cactuses"][cactus_name]
        if cactus_data["next_repotting"]:
            repotting_date = datetime.strptime(cactus_data["next_repotting"], "%Y-%m-%d")
            days_left = (repotting_date - datetime.now()).days
            if days_left < 0:
                self.repotting_label.config(text="Пора пересаживать кактус!", foreground="red")
            elif days_left <= 7:
                self.repotting_label.config(text=f"Пересадка через {days_left} дней", foreground="orange")
            else:
                self.repotting_label.config(text=f"Пересадка запланирована на {cactus_data['next_repotting']}",
                                            foreground="green")
        else:
            self.repotting_label.config(text="Дата пересадки не установлена", foreground="black")

    def update_history(self, cactus_name):
        """Update history display"""
        cactus_data = self.data_manager.data["cactuses"][cactus_name]
        self.history_text.delete(1.0, tk.END)
        self.history_text.insert(tk.END, "Поливы:\n")
        for w in cactus_data["watering"]:
            self.history_text.insert(tk.END, f"{w['date']} - {w['comment']}\n")

        self.history_text.insert(tk.END, "\nРост:\n")
        for g in cactus_data["growth"]:
            self.history_text.insert(tk.END, f"{g['date']} - {g['height']} см - {g['comment']}\n")

        self.history_text.insert(tk.END, "\nФото:\n")
        for p in cactus_data["photos"]:
            self.history_text.insert(tk.END, f"{p['date']} - {p['path']}\n")

        self.history_text.insert(tk.END, "\nПодкормки:\n")
        for f in cactus_data["fertilizers"]:
            self.history_text.insert(tk.END, f"{f['date']} - {f['type']} ({f['dosage']}) - {f['comment']}\n")

    def plan_repotting(self, cactus_name):
        """Plan repotting"""
        window = tk.Toplevel(self.root)
        window.title(f"Запланировать пересадку для {cactus_name}")
        window.geometry("300x200")

        ttk.Label(window, text="Дата пересадки (ГГГГ-ММ-ДД):").pack(pady=5)
        date_entry = ttk.Entry(window)
        date_entry.pack(pady=5)

        def save_repotting():
            date_str = date_entry.get().strip()
            try:
                repotting_date = datetime.strptime(date_str, "%Y-%m-%d")
                self.data_manager.data["cactuses"][cactus_name]["next_repotting"] = date_str
                self.data_manager.save_data()
                self.update_repotting_reminder(cactus_name)
                if repotting_date <= datetime.now():
                    self.data_manager.data["achievements"]["repotting_master"]["repottings"] += 1
                    if self.data_manager.data["achievements"]["repotting_master"]["repottings"] >= 3:
                        self.data_manager.data["achievements"]["repotting_master"]["completed"] = True
                self.data_manager.save_data()
                window.destroy()
            except ValueError:
                messagebox.showerror("Ошибка", "Введите дату в формате ГГГГ-ММ-ДД (например, 2025-03-15)")

        ttk.Button(window, text="Сохранить", command=save_repotting).pack(pady=10)

    def edit_notes(self, cactus_name):
        """Edit notes"""
        window = tk.Toplevel(self.root)
        window.title(f"Заметки для {cactus_name}")
        window.geometry("400x300")

        notes_frame = ttk.Frame(window)
        notes_frame.pack(fill="both", expand=True, padx=10, pady=10)

        notes_entry = tk.Text(notes_frame, wrap="word", height=15, width=50, font=("Arial", 12))
        notes_entry.insert("1.0", self.data_manager.data["cactuses"][cactus_name]["notes"])
        notes_entry.pack(fill="both", expand=True)

        def save_notes():
            new_notes = notes_entry.get("1.0", "end-1c")
            self.data_manager.data["cactuses"][cactus_name]["notes"] = new_notes
            self.data_manager.save_data()
            self.show_cactus_profile(None)
            window.destroy()

        ttk.Button(notes_frame, text="Сохранить", command=save_notes).pack(pady=10)

    def show_photo_album(self, cactus_name):
        """Show photo album"""
        cactus_data = self.data_manager.data["cactuses"][cactus_name]
        photos = cactus_data["photos"]

        album_window = tk.Toplevel(self.root)
        album_window.title(f"Фотоальбом: {cactus_name}")
        album_window.geometry("600x400")

        canvas = tk.Canvas(album_window)
        scrollbar = ttk.Scrollbar(album_window, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        if not photos:
            ttk.Label(scrollable_frame, text="Фото отсутствуют").pack(pady=20)
        else:
            for photo in photos:
                try:
                    img = Image.open(photo["path"]).resize((100, 100), Image.Resampling.LANCZOS)
                    photo_tk = ImageTk.PhotoImage(img)
                    photo_frame = ttk.Frame(scrollable_frame)
                    photo_frame.pack(pady=5, fill="x")

                    label = ttk.Label(photo_frame, image=photo_tk)
                    label.image = photo_tk
                    label.pack(side="left", padx=5)

                    ttk.Label(photo_frame, text=photo["date"]).pack(side="left", padx=5)

                    ttk.Button(photo_frame, text="Увеличить",
                               command=lambda p=photo["path"]: self.show_full_image(p)).pack(side="right", padx=5)
                except FileNotFoundError:
                    ttk.Label(scrollable_frame, text=f"Фото от {photo['date']} не найдено").pack(pady=5)

    def show_full_image(self, photo_path):
        """Show enlarged image"""
        try:
            img = Image.open(photo_path)
            img.thumbnail((800, 600), Image.Resampling.LANCZOS)
            photo_tk = ImageTk.PhotoImage(img)

            full_window = tk.Toplevel(self.root)
            full_window.title("Увеличенное фото")
            full_window.geometry(f"{img.width}x{img.height}")

            label = ttk.Label(full_window, image=photo_tk)
            label.image = photo_tk
            label.pack()
        except FileNotFoundError:
            messagebox.showerror("Ошибка", "Файл изображения не найден")

    def restore_data(self):
        """Restore data and refresh UI"""
        if self.data_manager.restore_data():
            self.update_cactus_dropdown()
            self.show_cactus_profile(None)

    def bulk_processing(self):
        """Interface for bulk watering or fertilizing"""
        window = tk.Toplevel(self.root)
        window.title("Массовая обработка")
        window.geometry("400x400")

        ttk.Label(window, text="Выберите кактусы:").pack(pady=5)
        cactus_list = list(self.data_manager.data["cactuses"].keys())
        selected_cactuses = []

        for cactus in cactus_list:
            var = tk.BooleanVar()
            ttk.Checkbutton(window, text=cactus, variable=var).pack(anchor="w", padx=10)
            selected_cactuses.append((cactus, var))

        ttk.Label(window, text="Действие:").pack(pady=5)
        action_var = tk.StringVar(value="Полив")
        ttk.Radiobutton(window, text="Полив", variable=action_var, value="Полив").pack(anchor="w", padx=10)
        ttk.Radiobutton(window, text="Подкормка", variable=action_var, value="Подкормка").pack(anchor="w", padx=10)

        ttk.Label(window, text="Комментарий (для полива):").pack(pady=5)
        comment_entry = ttk.Entry(window, width=30)
        comment_entry.pack(pady=5)

        ttk.Label(window, text="Тип удобрения (для подкормки):").pack(pady=5)
        type_entry = ttk.Entry(window)
        type_entry.pack(pady=5)

        ttk.Label(window, text="Дозировка (для подкормки):").pack(pady=5)
        dosage_entry = ttk.Entry(window)
        dosage_entry.pack(pady=5)

        def process():
            chosen_cactuses = [cactus for cactus, var in selected_cactuses if var.get()]
            if not chosen_cactuses:
                messagebox.showwarning("Предупреждение", "Выберите хотя бы один кактус")
                return
            action = action_var.get()
            comment = comment_entry.get()
            fertilizer_type = type_entry.get().strip()
            dosage = dosage_entry.get().strip()

            if action == "Полив":
                self.data_manager.bulk_add_watering(chosen_cactuses, comment)
                messagebox.showinfo("Успех", f"Полив добавлен для {len(chosen_cactuses)} кактусов")
            elif action == "Подкормка":
                if not fertilizer_type or not dosage:
                    messagebox.showerror("Ошибка", "Укажите тип удобрения и дозировку")
                    return
                self.data_manager.bulk_add_fertilizer(chosen_cactuses, fertilizer_type, dosage, comment)
                messagebox.showinfo("Успех", f"Подкормка добавлена для {len(chosen_cactuses)} кактусов")

            self.update_cactus_dropdown()
            self.show_cactus_profile(None)
            window.destroy()

        ttk.Button(window, text="Выполнить", command=process).pack(pady=10)