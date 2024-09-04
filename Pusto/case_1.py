from django.db import models
from django.utils import timezone
from datetime import timedelta


class Player(models.Model):
    """
    Модель игрока, которая содержит информацию о пользователе, его баллах и времени входа.
    """

    player_id = models.CharField(max_length=100)
    username = models.CharField(max_length=255, unique=True)
    first_login = models.DateTimeField(auto_now_add=True)  # Дата первого входа
    last_login = models.DateTimeField(null=True, blank=True)
    points = models.PositiveIntegerField(default=0)

    def login(self, new_points: int) -> None:
        """
        Записывает вход и начисляет баллы только если входы были подряд.

        :param new_points: Количество баллов, которое нужно начислить за вход.
        """
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        # проверяем был ли вчера вход, чтобы начислить баллы
        if self.last_login.date() == yesterday:
            self.points += new_points
            self.last_login = timezone.now()
            self.save()
        # обрабатываем логику первого входа
        elif self.last_login is None:
            self.last_login = timezone.now()
            self.save()

    def add_boost(self, boost: Boost, quantity: int = 1) -> None:
        """
        Добавляет буст игроку или увеличивает количество, если такой буст уже есть.

        :param boost: Объект буста, который нужно добавить.
        :param quantity: Количество бустов для добавления (по умолчанию 1).
        """
        player_boost, created = PlayerBoost.objects.get_or_create(
            player=self, boost=boost
        )
        player_boost.quantity += quantity
        player_boost.save()

    def __str__(self) -> str:
        """Возвращает строковое представление имени пользователя."""
        return self.username


class Boost(models.Model):
    """
    Модель буста, которая содержит информацию о типе буста.
    """

    BOOST_TYPES = [
        ("type1", "Type 1"),
        ("type2", "Type 2"),
        ("type3", "Type 3"),
    ]

    name = models.CharField(max_length=255, unique=True)
    boost_type = models.CharField(max_length=20, choices=BOOST_TYPES)
    description = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        """Возвращает строковое представление буста."""
        return self.name


class PlayerBoost(models.Model):
    """
    Промежуточная модель, связывающая игроков и бусты с учетом количества.
    """

    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    boost = models.ForeignKey(Boost, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    boost_add_time = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        """Возвращает строковое представление буста игрока."""
        return f"{self.player.username} - {self.boost.name} (Quantity: {self.quantity})"
