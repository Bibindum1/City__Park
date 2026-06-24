import random
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.text import slugify

from faker import Faker

from CityPark import settings
from catalog.models import Category, Dish, Order, OrderItem
from restaurant.models import RestaurantInfo, Booking, Table, Review


class Command(BaseCommand):
    help = "Заполнение базы данных тестовыми данными"

    def handle(self, *args, **kwargs):

        fake = Faker("ru_RU")
        User = get_user_model()

        self.stdout.write("Очистка базы...")

        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        Dish.objects.all().delete()
        Category.objects.all().delete()
        Booking.objects.all().delete()
        Table.objects.all().delete()
        Review.objects.all().delete()
        RestaurantInfo.objects.all().delete()
        if settings.DEBUG:
            User.objects.exclude(is_superuser=True).delete()

        self.stdout.write("База очищена")

        # ----------------------------
        # РЕСТОРАН
        # ----------------------------

        RestaurantInfo.objects.create(
            name="CityPark",
            slogan="Высокая кухня в центре города",
            description=fake.text(max_nb_chars=300),
            address="г. Москва, ул. Центральная, 15",
            phone="+7 (999) 123-45-67",
            email="info@citypark.ru",
            working_hours="10:00 - 23:00",
        )

        self.stdout.write("RestaurantInfo создан")

        # ----------------------------
        # КАТЕГОРИИ
        # ----------------------------

        categories = []

        for name in [
            "Закуски", "Салаты", "Супы", "Паста", "Пицца",
            "Горячие блюда", "Мясо", "Рыба", "Десерты",
            "Напитки", "Кофе", "Вино",
        ]:
            categories.append(Category.objects.create(name=name))

        self.stdout.write("Категории созданы")

        # ----------------------------
        # ПОЛЬЗОВАТЕЛИ (БЫСТРО + БЕЗ ЛАГОВ)
        # ----------------------------

        users = []

        for i in range(30):
            user = User(
                username=f"user{i+1}",
                full_name=fake.name(),
                phone=fake.phone_number()[:20],
                email=f"user{i+1}@mail.ru",
                address=fake.address(),
            )
            user.set_password("12345678")
            users.append(user)

        User.objects.bulk_create(users)

        users = list(User.objects.filter(username__startswith="user"))

        self.stdout.write("Пользователи созданы")

        # ----------------------------
        # ДАННЫЕ ДЛЯ БЛЮД
        # ----------------------------

        adjectives = [
            "Фирменный", "Домашний", "Нежный", "Сливочный",
            "Пряный", "Острый", "Запечённый", "Итальянский",
            "Французский", "Классический",
        ]

        products = [
            "бургер", "стейк", "салат", "суп", "ризотто",
            "лосось", "карбонара", "паста", "пицца",
            "тирамису", "чизкейк", "капучино", "латте",
            "лимонад", "утка", "курица", "говядина", "креветки",
        ]

        ingredients = [
            "говядина", "курица", "лосось", "сыр", "моцарелла",
            "томат", "сливки", "чеснок", "базилик", "грибы",
            "лук", "оливковое масло", "сливочное масло",
            "пармезан", "креветки", "рис", "картофель",
        ]

        dishes = []

        # ----------------------------
        # БЛЮДА (БЕЗ WHILE TRUE)
        # ----------------------------

        for _ in range(100):

            name = f"{random.choice(adjectives)} {random.choice(products)}"
            slug = slugify(name)

            # ЖЁСТКИЙ FALLBACK (НИКОГДА НЕ ЗАВИСНЕТ)
            if not slug:
                name = f"Блюдо {random.randint(1000, 9999)}"
                slug = f"dish-{random.randint(1000, 9999)}"

            dish = Dish.objects.create(
                name=name,
                description=fake.text(max_nb_chars=200),
                ingredients=", ".join(
                    random.sample(ingredients, random.randint(3, 6))
                ),
                price=Decimal(random.randint(250, 3000)),
                weight=random.randint(150, 700),
                calories=random.randint(150, 1200),
                prep_time=random.randint(5, 20),
                cooking_time=random.randint(10, 45),
                is_available=random.choice([True, True, True, False]),
                category=random.choice(categories),
            )

            dishes.append(dish)

        self.stdout.write("Блюда созданы")

        # ----------------------------
        # СТОЛИКИ
        # ----------------------------

        Table.objects.bulk_create([
            Table(
                number=i,
                seats=random.choice([2, 2, 4, 4, 6, 8]),
                is_active=True,
            )
            for i in range(1, 21)
        ])

        self.stdout.write("Столики созданы")

        # ----------------------------
        # БРОНИ
        # ----------------------------

        for _ in range(40):
            Booking.objects.create(
                full_name=fake.name(),
                phone=fake.phone_number()[:20],
                email=fake.email(),
                booking_date=fake.date_between("-10d", "+30d"),
                booking_time=fake.time_object(),
                guests=random.randint(1, 8),
                comment=fake.sentence(),
                status=random.choice(["new", "confirmed", "completed", "cancelled"]),
            )

        self.stdout.write("Бронирования созданы")

        # ----------------------------
        # ОТЗЫВЫ
        # ----------------------------

        Review.objects.bulk_create([
            Review(
                author=fake.name(),
                rating=random.randint(3, 5),
                text=fake.paragraph(),
                is_published=True,
            )
            for _ in range(60)
        ])

        self.stdout.write("Отзывы созданы")

        # ----------------------------
        # ЗАКАЗЫ
        # ----------------------------

        for _ in range(50):

            order = Order.objects.create(
                user=random.choice(users),
                status=random.choice([
                    "new", "accepted", "cooking",
                    "delivery", "completed"
                ]),
                total=0,
                comment=fake.sentence(),
            )

            total = Decimal("0")

            for dish in random.sample(dishes, random.randint(2, 5)):

                qty = random.randint(1, 3)

                OrderItem.objects.create(
                    order=order,
                    name=dish.name,
                    price=dish.price,
                    quantity=qty,
                )

                total += dish.price * qty

            order.total = total
            order.save()

        self.stdout.write("Заказы созданы")

        self.stdout.write("==============================")
        self.stdout.write("ГОТОВО — БЕЗ ЗАВИСАНИЙ")
        self.stdout.write("==============================")