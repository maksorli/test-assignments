from django.db import models
from django.utils import timezone
from django.http import StreamingHttpResponse
from typing import Generator

class Player(models.Model):
    """
    Модель, представляющая игрока в системе.
    """
    player_id: str = models.CharField(max_length=100)
    
    def __str__(self) -> str:
        """
        Возвращает строковое представление объекта Player.

        :return: Идентификатор игрока.
        """
        return self.player_id


class Level(models.Model):
    """
    Модель, представляющая уровень в игре.
    """
    title: str = models.CharField(max_length=100)
    order: int = models.IntegerField(default=0)

    def __str__(self) -> str:
        """
        Возвращает строковое представление объекта Level.

        :return: Название уровня.
        """
        return self.title


class Prize(models.Model):
    """
    Модель, представляющая приз за уровень.
    """
    title: str = models.CharField(max_length=100)

    def __str__(self) -> str:
        """
        Возвращает строковое представление объекта Prize.

        :return: Название приза.
        """
        return self.title


class PlayerLevel(models.Model):
    """
    Модель, представляющая связь игрока с уровнем и его прогресс.
    """
    player: Player = models.ForeignKey(Player, on_delete=models.CASCADE)
    level: Level = models.ForeignKey(Level, on_delete=models.CASCADE)
    completed: str = models.DateField()
    is_completed: bool = models.BooleanField(default=False)
    score: int = models.PositiveIntegerField(default=0)

    def assign_prize(self) -> str:
        """
        Присваивает приз игроку за завершенный уровень, если он еще не был присвоен.

        :return: Сообщение о статусе присвоения приза.
        """
        if self.is_completed:
            level_prize = LevelPrize.objects.filter(level=self.level).first()

            if level_prize and not level_prize.received:
                level_prize.received = timezone.now()
                level_prize.save()
                return f"Приз '{level_prize.prize.title}' присвоен игроку {self.player.player_id} за уровень {self.level.title}."
            elif level_prize and level_prize.received:
                return "Приз уже был присвоен ранее."
            else:
                return f"Для уровня {self.level.title} не найдено приза."
        else:
            return f"Уровень {self.level.title} еще не завершен."

    @staticmethod
    def export_to_csv() -> StreamingHttpResponse:
        """
        Экспорт данных PlayerLevel в CSV с использованием стриминга для обработки больших объемов данных.

        :return: HTTP-ответ, содержащий CSV-файл.
        """
        # Генератор для стриминга данных
        def csv_generator() -> Generator[str, None, None]:
            """
            Генератор строк CSV-файла, возвращающий строки по мере обработки данных.

            :yield: Строка с данными для CSV.
            """
            # Заголовок CSV
            yield 'Player ID,Level Title,Is Completed,Prize\n'
            
            # Извлекаем данные по частям
            player_levels = PlayerLevel.objects.all().select_related('player', 'level').iterator(chunk_size=2000)
            
            # Генерация строк CSV по частям
            for player_level in player_levels:
                # Получаем приз для уровня
                level_prize = LevelPrize.objects.filter(level=player_level.level).first()
                prize_title = level_prize.prize.title if level_prize else "No prize"

                # Генерация строки данных
                yield f'{player_level.player.player_id},{player_level.level.title},{"Yes" if player_level.is_completed else "No"},{prize_title}\n'

        # Возвращаем стриминговый HTTP-ответ
        response = StreamingHttpResponse(csv_generator(), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="player_levels.csv"'
        return response

    def __str__(self) -> str:
        """
        Возвращает строковое представление объекта PlayerLevel.

        :return: Строка, представляющая связь игрока и уровня.
        """
        return f"{self.player.player_id} - {self.level.title}"


class LevelPrize(models.Model):
    """
    Модель, представляющая приз, присвоенный за конкретный уровень.
    """
    level: Level = models.ForeignKey(Level, on_delete=models.CASCADE)
    prize: Prize = models.ForeignKey(Prize, on_delete=models.CASCADE)
    received: str = models.DateField()

    def __str__(self) -> str:
        """
        Возвращает строковое представление объекта LevelPrize.

        :return: Строка, представляющая уровень и присвоенный приз.
        """
        return f"{self.prize.title} для уровня {self.level.title}"
