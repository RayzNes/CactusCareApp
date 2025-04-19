import json
import os

class SpeciesDatabase:
    def __init__(self, species_file="cactus_species.json"):
        self.species_file = species_file
        self.species_data = self.load_species()

    def load_species(self):
        """Load cactus species data from JSON file"""
        default_species = {
            "Echinocactus grusonii": {
                "common_name": "Золотой бочонок",
                "watering_frequency": 14,
                "light_requirements": "Яркий прямой свет",
                "temperature_range": "15-30°C",
                "soil_type": "Песчаная, хорошо дренированная",
                "fertilizer_recommendation": "Удобрение для кактусов с низким содержанием азота (NPK 5-10-10), 1 раз в месяц весной и летом",
                "seasonal_care": {
                    "winter": "Редкий полив (1 раз в 3-4 недели), температура 10-15°C, избегать сквозняков",
                    "spring": "Умеренный полив (1 раз в 10-14 дней), начинать подкормки",
                    "summer": "Регулярный полив (1 раз в 7-10 дней), яркий свет",
                    "autumn": "Уменьшать полив (1 раз в 14-20 дней), подготовка к покою"
                }
            },
            "Opuntia microdasys": {
                "common_name": "Банни кактус",
                "watering_frequency": 10,
                "light_requirements": "Яркий рассеянный свет",
                "temperature_range": "18-28°C",
                "soil_type": "Смесь песка и перлита",
                "fertilizer_recommendation": "Жидкое удобрение для суккулентов (NPK 10-10-10), 1 раз в 3 недели летом",
                "seasonal_care": {
                    "winter": "Минимальный полив (1 раз в месяц), температура 12-18°C",
                    "spring": "Умеренный полив (1 раз в 7-10 дней), подкормки каждые 3 недели",
                    "summer": "Частый полив (1 раз в 5-7 дней), защита от прямых лучей",
                    "autumn": "Снижение полива (1 раз в 10-14 дней), без подкормок"
                }
            },
            "Mammillaria elongata": {
                "common_name": "Золотистая маммиллярия",
                "watering_frequency": 12,
                "light_requirements": "Яркий свет, полутень",
                "temperature_range": "15-25°C",
                "soil_type": "Рыхлая, дренированная",
                "fertilizer_recommendation": "Удобрение для кактусов (NPK 5-10-10), 1 раз в месяц весной",
                "seasonal_care": {
                    "winter": "Очень редкий полив (1 раз в 4 недели), температура 10-15°C",
                    "spring": "Полив 1 раз в 10 дней, начинать подкормки",
                    "summer": "Полив 1 раз в 7-10 дней, яркий рассеянный свет",
                    "autumn": "Полив 1 раз в 14 дней, прекратить подкормки"
                }
            }
        }

        if os.path.exists(self.species_file):
            try:
                with open(self.species_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                pass

        # Save default species if file doesn't exist or is invalid
        with open(self.species_file, 'w', encoding='utf-8') as f:
            json.dump(default_species, f, ensure_ascii=False, indent=4)
        return default_species

    def get_species_list(self):
        """Return list of species names"""
        return list(self.species_data.keys())

    def get_species_data(self, species_name):
        """Return data for a specific species"""
        return self.species_data.get(species_name, {})