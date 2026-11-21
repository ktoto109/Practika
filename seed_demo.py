
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djangoproject.settings")

import django

django.setup()

from SVO_I_Tochka.models import Asteroid, Composition, SpectralClass


def seed_demo():
    if Asteroid.objects.exists():
        print("Демо-данные уже есть, пропускаю.")
        return

    classes = {}
    for name in ("M-Type", "C-Type", "S-Type", "R-Type"):
        classes[name], _ = SpectralClass.objects.get_or_create(name=name)

    compositions = {}
    for name in ("руда", "железо", "никель", "вода", "углерод", "кремний", "платина", "иридий"):
        compositions[name], _ = Composition.objects.get_or_create(name=name)

    lots = [
        {
            "title": "Глимер",
            "description": "Металлический астероид из Главного пояса. Анализ подтвердил высокое содержание никеля и железа.",
            "price": 2_000_000,
            "distance": 1_450_000,
            "spectral": "M-Type",
            "tags": ("руда", "железо", "никель"),
            "sold": False,
        },
        {
            "title": "Коч",
            "description": "Углеродный объект с плотной корой. Отличный кандидат для станции длительного базирования.",
            "price": 1_400_000,
            "distance": 980_000,
            "spectral": "C-Type",
            "tags": ("углерод", "вода"),
            "sold": True,
        },
        {
            "title": "Голда",
            "description": "Каменный астероид с вкраплениями тяжёлых металлов. Прошёл полный спектральный анализ.",
            "price": 3_200_000,
            "distance": 2_100_000,
            "spectral": "S-Type",
            "tags": ("руда", "платина"),
            "sold": False,
        },
        {
            "title": "Шары",
            "description": "Редкий объект R-класса. Подходит для научной станции или частной коллекции.",
            "price": 2_600_000,
            "distance": 1_760_000,
            "spectral": "R-Type",
            "tags": ("кремний", "иридий"),
            "sold": False,
        },
        {
            "title": "Веста",
            "description": "Крупный каменный астероид. Устойчивая орбита и богатый минеральный состав.",
            "price": 4_800_000,
            "distance": 3_250_000,
            "spectral": "S-Type",
            "tags": ("руда", "кремний"),
            "sold": False,
        },
        {
            "title": "Церера",
            "description": "Ледяной гигант Главного пояса. Запасы воды и углерода для колоний.",
            "price": 6_000_000,
            "distance": 4_100_000,
            "spectral": "C-Type",
            "tags": ("вода", "углерод"),
            "sold": False,
        },
        {
            "title": "Паллада",
            "description": "Металлическое тело с неоднородной структурой. Требует буксировки на опорную орбиту.",
            "price": 3_900_000,
            "distance": 2_780_000,
            "spectral": "M-Type",
            "tags": ("руда", "никель", "иридий"),
            "sold": False,
        },
    ]

    for lot in lots:
        asteroid = Asteroid.objects.create(
            title=lot["title"],
            description=lot["description"],
            price=lot["price"],
            distance=lot["distance"],
            spectral_class=classes[lot["spectral"]],
            is_sold=lot["sold"],
        )
        asteroid.compositions.set([compositions[tag] for tag in lot["tags"]])

    print(f"Добавлено астероидов: {len(lots)}")


if __name__ == "__main__":
    seed_demo()
