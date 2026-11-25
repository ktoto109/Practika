
import os
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djangoproject.settings")

import django

django.setup()

from django.contrib.auth.models import User
from django.utils import timezone

from SVO_I_Tochka.models import Asteroid, Composition, Order, SpectralClass


def seed_demo():
    if not Asteroid.objects.exists():
        seed_asteroids()
    else:
        print("Астероиды уже есть, пропускаю их создание.")

    seed_orders()


def seed_asteroids():
    classes = {}
    for name in ("M-Type", "C-Type", "S-Type", "R-Type"):
        classes[name], _ = SpectralClass.objects.get_or_create(name=name)

    compositions = {}
    for name in (
        "руда",
        "железо",
        "никель",
        "вода",
        "углерод",
        "кремний",
        "платина",
        "иридий",
        "золото",
        "медь",
        "титан",
        "кобальт",
        "магний",
        "олово",
        "цинк",
    ):
        compositions[name], _ = Composition.objects.get_or_create(name=name)

    lots = [
        {
            "title": "Глимер",
            "description": "Металлический астероид из Главного пояса. Спектральный анализ подтвердил высокое содержание никеля, железа и редкоземельных элементов. Поверхность стабильна, есть удобные площадки для буксировочных модулей. Доставка на опорную орбиту Земли займёт 14 стандартных циклов.",
            "price": 2_000_000,
            "distance": 1_450_000,
            "spectral": "M-Type",
            "tags": ("руда", "железо", "никель"),
            "sold": False,
        },
        {
            "title": "Коч",
            "description": "Углеродный объект с плотной корой и большими запасами летучих соединений. Подходит для станции длительного базирования и добычи воды. Орбита сближающаяся, окно для захвата открывается каждый третий цикл.",
            "price": 1_400_000,
            "distance": 980_000,
            "spectral": "C-Type",
            "tags": ("углерод", "вода"),
            "sold": True,
        },
        {
            "title": "Голда",
            "description": "Каменный астероид с вкраплениями тяжёлых металлов. Прошёл полный спектральный анализ, подтверждены платина, иридий и редкие минералы. Рекомендуется для промышленной разработки на орбите Луны.",
            "price": 3_200_000,
            "distance": 2_100_000,
            "spectral": "S-Type",
            "tags": ("руда", "платина"),
            "sold": False,
        },
        {
            "title": "Шары",
            "description": "Редкий объект R-класса с неоднородной структурой. Подходит для научной станции или частной коллекции. Требует аккуратной буксировки и предварительной установки стабилизаторов.",
            "price": 2_600_000,
            "distance": 1_760_000,
            "spectral": "R-Type",
            "tags": ("кремний", "иридий"),
            "sold": False,
        },
        {
            "title": "Веста",
            "description": "Крупный каменный астероид с устойчивой орбитой и богатым минеральным составом. Запасы кремния и металлов позволяют окупить доставку за несколько циклов. Есть свободные площадки для швартовки.",
            "price": 4_800_000,
            "distance": 3_250_000,
            "spectral": "S-Type",
            "tags": ("руда", "кремний"),
            "sold": False,
        },
        {
            "title": "Церера",
            "description": "Ледяной гигант Главного пояса. Запасы воды и углерода делают его стратегическим объектом для колоний. Требуется мощный буксир и разрешение на изменение орбиты.",
            "price": 6_000_000,
            "distance": 4_100_000,
            "spectral": "C-Type",
            "tags": ("вода", "углерод"),
            "sold": False,
        },
        {
            "title": "Паллада",
            "description": "Металлическое тело с неоднородной структурой и высоким содержанием никеля. Требует буксировки на опорную орбиту и дополнительной разведки. Подходит для добывающей станции среднего класса.",
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


def seed_orders():
    admin = User.objects.filter(username="admin").first()
    if admin is None:
        print("Пользователь admin не найден, демо-заказы не создаю.")
        return

    if Order.objects.filter(user=admin).exists():
        print("У admin уже есть заказы, пропускаю.")
        return

    glimer = Asteroid.objects.filter(title="Глимер").first()
    koch = Asteroid.objects.filter(title="Коч").first()
    if glimer is None or koch is None:
        print("Не нашёл астероиды для демо-заказов.")
        return

    first = Order.objects.create(
        user=admin,
        asteroid=glimer,
        code="#SO-0482",
        status="in_transit",
    )
    second = Order.objects.create(
        user=admin,
        asteroid=koch,
        code="#SO-0361",
        status="completed",
    )

    Order.objects.filter(pk=first.pk).update(
        created_at=timezone.make_aware(datetime(2026, 6, 18, 12, 0))
    )
    Order.objects.filter(pk=second.pk).update(
        created_at=timezone.make_aware(datetime(2026, 5, 2, 12, 0))
    )
    print("Добавлено демо-заказов: 2")


if __name__ == "__main__":
    seed_demo()
