import random
import pickle
import os
from pathlib import Path
from games.base_game import BaseGame
from config.settings import settings


class RomanFriendGame(BaseGame):
    """Игра 'Письма римскому другу' по мотивам стихотворения Бродского"""

    name = "Письма римскому другу"
    poem = "Письма римскому другу"
    description = "Напиши письма другу в Рим, выбирая строки Бродского, и создай свою судьбу в изгнании"

    def __init__(self, user_id: int):
        super().__init__(user_id)

        # Основные параметры игры
        self.wisdom = 0  # Мудрость (-100 до 100)
        self.rome_reputation = 0  # Репутация в Риме (-100 до 100)
        self.balance = 0  # Душевное равновесие (-100 до 100)
        self.creative_force = 0  # Творческая сила (-100 до 100)
        self.adaptation = 0  # Адаптация к провинции (-100 до 100)

        # Игровые параметры
        self.season = "весна"  # Текущий сезон (весна, лето, осень, зима)
        self.year = 1  # Год в изгнании
        self.day = 1  # День в изгнании
        self.letters_sent = 0  # Количество отправленных писем
        self.season_letters = 0  # Количество писем в текущем сезоне

        # Состояние игры
        self.state = "normal"  # Состояние (normal, special_state, game_over)

        # Инициализация фрагментов стихотворения
        self.init_fragments()

    def init_fragments(self):
        """Инициализация фрагментов стихотворения 'Письма римскому другу'"""
        self.fragments = {
            # Фрагмент 1
            "fragment_1": {
                "text": "Нынче ветрено и волны с перехлестом.\nСкоро осень, все изменится в округе.\nНе забудь поставить сетку на окне,\nчтоб цикада не будила по ночам.",
                "effects": {
                    "wisdom": 10,
                    "balance": 5,
                    "rome_reputation": -5,
                    "adaptation": 5,
                },
                "seasons": {"осень": {"wisdom": 5}},
            },
            # Фрагмент 2
            "fragment_2": {
                "text": "Посылаю тебе, Постум, эти книги.\nЧто в столице? Мягко стелют? Спать не жестко?\nКак там Цезарь? Чем он занят? Все интриги?\nВсе интриги, вероятно, да обжорство.",
                "effects": {"rome_reputation": 5, "balance": -5, "creative_force": 5},
                "seasons": {"зима": {"creative_force": 5}},
            },
            # Фрагмент 3
            "fragment_3": {
                "text": "Я сижу в своем саду, горит светильник.\nНи подруги, ни прислуги, ни знакомых.\nВместо слабых мира этого и сильных —\nлишь согласное гуденье насекомых.",
                "effects": {
                    "adaptation": 10,
                    "creative_force": 10,
                    "rome_reputation": -5,
                    "balance": 5,
                },
                "seasons": {"лето": {"creative_force": 5, "adaptation": 5}},
            },
            # Фрагмент 4
            "fragment_4": {
                "text": "Здесь лежит купец из Азии. Толковым\nбыл купцом он — деловит, но незаметен.\nУмер быстро: лихорадка. По торговым\nон делам сюда приплыл, а не за этим.",
                "effects": {"wisdom": 15, "balance": -5, "creative_force": 5},
                "seasons": {"лето": {"balance": 5}},
            },
            # Фрагмент 5
            "fragment_5": {
                "text": "Пусть и вправду, Постум, курица не птица,\nно с куриными мозгами хватишь горя.\nЕсли выпало в Империи родиться,\nлучше жить в глухой провинции у моря.",
                "effects": {"adaptation": 15, "balance": 10, "rome_reputation": -10},
                "seasons": {"зима": {"adaptation": 5}},
            },
            # Фрагмент 6
            "fragment_6": {
                "text": "Зелень лавра, доходящая до дрожи.\nДверь распахнутая, пыльное оконце.\nСтул покинутый, оставленное ложе.\nТкань, впитавшая полуденное солнце.",
                "effects": {"wisdom": 10, "balance": 10, "rome_reputation": -5},
                "seasons": {},
            },
            # Фрагмент 7
            "fragment_7": {
                "text": "Был в горах. Сейчас вожусь с большим букетом.\nРазыщу большой кувшин, воды налью им...\nКак там в Ливии, мой Постум, — или где там?\nНеужели до сих пор еще воюем?",
                "effects": {"adaptation": 10, "balance": 5, "rome_reputation": 5},
                "seasons": {"весна": {"adaptation": 5}},
            },
            # Фрагмент 8
            "fragment_8": {
                "text": "Помнишь, Постум, у наместника сестрица?\nХудощавая, но с полными ногами.\nТы с ней спал еще… Недавно стала жрица.\nЖрица, Постум, и общается с богами.",
                "effects": {"rome_reputation": 5, "adaptation": -5, "balance": -5},
                "seasons": {},
            },
            # Фрагмент 9
            "fragment_9": {"text": "Приезжай, попьем вина, закусим хлебом.\nИли сливами. Расскажешь мне известья.\nПостелю тебе в саду под чистым небом\nи скажу, как называются созвездья.",
                "effects": {
                    "wisdom": 15,
                    "balance": 5,
                    "rome_reputation": -10,
                    "creative_force": 5,
                },
                "seasons": {"осень": {"wisdom": 5}},
            },
            # Фрагмент 10
            "fragment_10": {
                "text": "Вот и прожили мы больше половины.\nКак сказал мне старый раб перед таверной:\n«Мы, оглядываясь, видим лишь руины».\nВзгляд, конечно, очень варварский, но верный.",
                "effects": {"wisdom": 15, "balance": -5, "creative_force": 5},
                "seasons": {"осень": {"wisdom": 5}},
            },
            # Фрагмент 11
            "fragment_11": {
                "text": "Скоро, Постум, друг твой, любящий сложенье,\nдолг свой давний вычитанию заплатит.\nЗабери из-под подушки сбереженья,\nтам немного, но на похороны хватит.",
                "effects": {"adaptation": 10, "creative_force": 10, "balance": 5},
                "seasons": {"лето": {"creative_force": 5}},
            },
            # Фрагмент 12
            "fragment_12": {
                "text": "Понт шумит за черной изгородью пиний.\nЧье-то судно с ветром борется у мыса.\nНа рассохшейся скамейке — Старший Плиний.\nДрозд щебечет в шевелюре кипариса.",
                "effects": {"adaptation": 15, "balance": 5, "wisdom": 5},
                "seasons": {"весна": {"adaptation": 5}},
            },
        }

            # Порядок появления фрагментов по сезонам (номера фрагментов)
        self.seasonal_fragments = {
            "весна": ["fragment_7", "fragment_12", "fragment_2", "fragment_5"],
            "лето": ["fragment_3", "fragment_4", "fragment_11", "fragment_8"],
            "осень": ["fragment_1", "fragment_10", "fragment_9", "fragment_6"],
            "зима": ["fragment_5", "fragment_2", "fragment_6", "fragment_10"],
        }

    def save_game_state(self) -> str:
        """Create a compact string representation of game state"""
        state_parts = [
            "roman",
            str(self.wisdom),
            str(self.rome_reputation),
            str(self.balance),
            str(self.creative_force),
            str(self.adaptation),
            self.season,
            str(self.year),
            str(self.day),
            str(self.letters_sent),
            str(self.season_letters),
            self.state,
        ]

        return ":".join(state_parts)

    @classmethod
    def load_from_state_string(
        cls, user_id: int, state_string: str
    ) -> "RomanFriendGame":
        """Recreate game state from compact string"""
        game = cls(user_id)

        if not state_string or not state_string.startswith("roman:"):
            return game

        parts = state_string.split(":")
        if len(parts) >= 12:
            game.wisdom = int(parts[1])
            game.rome_reputation = int(parts[2])
            game.balance = int(parts[3])
            game.creative_force = int(parts[4])
            game.adaptation = int(parts[5])
            game.season = parts[6]
            game.year = int(parts[7])
            game.day = int(parts[8])
            game.letters_sent = int(parts[9])
            game.season_letters = int(parts[10])
            game.state = parts[11]

        return game

    def get_help(self) -> str:
        """Получить справку по игре"""
        help_text = """
📜 Доступные команды:

Основные команды:
- письмо - написать новое письмо римскому другу
- прогресс - проверить свой прогресс и параметры
- помощь - показать эту справку

🎮 Цель игры: Наберите 100 в одном из параметров для положительной концовки.
Будьте осторожны: -100 в любом параметре приведет к негативной концовке.

Выбирайте фрагменты для своих писем с умом,
учитывайте сезоны и их влияние на эффекты.
"""
        return help_text

    def get_intro(self) -> str:
        """Получить вступление к игре"""
        intro = """
╔=================╗
║::::::::::ПИСЬМА:::::::::::║
║:::РИМСКОМУ ДРУГУ::║
║————————————║
║.....игра по мотивам....║
║::::::стихотворения::::::║
║::::::::::Бродского:::::::::║
║————————————║
║:::автор @pudan416::::║
╚=================╝

"Нынче ветрено и волны с перехлестом.
Скоро осень, всё изменится в округе..."

Ты – поэт в изгнании, живущий в провинции у моря. 
Твой единственный контакт с прежней жизнью – письма другу Постуму в Рим.

В этой игре ты будешь составлять письма, выбирая строки из стихотворения Бродского.
Твои выборы повлияют на пять ключевых параметров и определят твою судьбу.

Введи 'письмо', чтобы начать писать, или 'помощь' для списка команд.
"""
        return intro

    def process_command(self, command: str) -> str:
        """Обработка команды игрока"""
        command = command.lower().strip()

        # Если игра завершена
        if self.state == "game_over":
            return "Игра завершена. Введи /start для начала новой игры."

        # Если в процессе создания письма
        if self.state.startswith("letter_"):
            parts = self.state.split("_")
            step = parts[1]

            if step == "selecting":
                # Обработка выбора фрагментов
                try:
                    choices = [c.strip() for c in command.split(",")]
                    if len(choices) != 2:
                        return "Выбери ровно 2 фрагмента (например: 1, 3)"

                    # Преобразование цифр в индексы (1=0, 2=1, 3=2, 4=3)
                    indices = []
                    for choice in choices:
                        if choice == "1":
                            indices.append(0)
                        elif choice == "2":
                            indices.append(1)
                        elif choice == "3":
                            indices.append(2)
                        elif choice == "4":
                            indices.append(3)
                        else:
                            return f"Некорректный выбор: {choice}. Используй цифры 1, 2, 3 или 4."

                    return self.complete_letter(indices)
                except Exception as e:
                    self.state = "normal"
                    return f"Произошла ошибка при выборе фрагментов. Пожалуйста, попробуй еще раз: {str(e)}"

        # Основные команды
        if command == "письмо" or command == "написать письмо":
            return self.start_letter()
        elif command == "прогресс" or command == "статус":
            return self.show_progress()
        elif command == "помощь":
            return self.get_help()
        else:
            return (
                "Я не понимаю эту команду. Введи 'помощь' для списка доступных команд."
            )

    def start_letter(self) -> str:
        """Начать составление письма"""
        # Проверка, не превышено ли количество писем в сезоне
        if self.season_letters >= 2:
            # Переход к следующему сезону
            self.advance_season()
            return f"Сезон {self.season} начался. Теперь ты можешь написать новое письмо.\nВведи 'письмо', чтобы начать."

        # Выбор фрагментов для текущего сезона
        available_fragments = self.seasonal_fragments[self.season]

        # Формируем текст для выбора
        message = f"""
=== ПИСЬМО РИМСКОМУ ДРУГУ ===
Сезон: {self.season.capitalize()} ({self.season_letters + 1}-е письмо сезона)
Год в изгнании: {self.year}, День: {self.day}

Твои параметры:
- Мудрость: {self.wisdom}
- Репутация в Риме: {self.rome_reputation}
- Душевное равновесие: {self.balance}
- Творческая сила: {self.creative_force}
- Адаптация к провинции: {self.adaptation}

Выбери 2 фрагмента для письма из 4 доступных (напиши цифры через запятую, например: 1, 3):

1. "{self.fragments[available_fragments[0]]['text']}"

2. "{self.fragments[available_fragments[1]]['text']}"

3. "{self.fragments[available_fragments[2]]['text']}"

4. "{self.fragments[available_fragments[3]]['text']}"
"""

        # Переходим в состояние выбора фрагментов
        self.state = "letter_selecting"

        return message

    def complete_letter(self, indices: list) -> str:
        """Завершить создание письма и применить эффекты"""
        # Получаем доступные фрагменты для текущего сезона
        available_fragments = self.seasonal_fragments[self.season]

        # Выбранные фрагменты
        selected_fragments = [available_fragments[i] for i in indices]

        # Составляем письмо
        letter_text = "Дорогой Постум!\n\n"

        # Добавляем выбранные фрагменты
        for fragment_id in selected_fragments:
            letter_text += self.fragments[fragment_id]["text"] + "\n\n"

        letter_text += "Твой друг в изгнании"

        # Применяем эффекты от фрагментов
        effects_text = "Изменение параметров:\n"

        for fragment_id in selected_fragments:
            fragment = self.fragments[fragment_id]

            # Базовые эффекты
            for param, value in fragment["effects"].items():
                # Проверяем сезонные бонусы
                bonus = 0
                if (
                    self.season in fragment["seasons"]
                    and param in fragment["seasons"][self.season]
                ):
                    bonus = fragment["seasons"][self.season][param]

                # Применяем эффект с бонусом
                total_effect = value + bonus

                # Обновляем параметр
                if param == "wisdom":
                    self.wisdom = max(-100, min(100, self.wisdom + total_effect))
                    effects_text += (
                        f"- Мудрость: {'+' if total_effect > 0 else ''}{total_effect}"
                    )
                    if bonus > 0:
                        effects_text += f" (сезонный бонус {self.season}!)"
                    effects_text += f" → {self.wisdom}\n"
                elif param == "rome_reputation":
                    self.rome_reputation = max(
                        -100, min(100, self.rome_reputation + total_effect)
                    )
                    effects_text += f"- Репутация в Риме: {'+' if total_effect > 0 else ''}{total_effect}"
                    if bonus > 0:
                        effects_text += f" (сезонный бонус {self.season}!)"
                    effects_text += f" → {self.rome_reputation}\n"
                elif param == "balance":
                    self.balance = max(-100, min(100, self.balance + total_effect))
                    effects_text += f"- Душевное равновесие: {'+' if total_effect > 0 else ''}{total_effect}"
                    if bonus > 0:
                        effects_text += f" (сезонный бонус {self.season}!)"
                    effects_text += f" → {self.balance}\n"
                elif param == "creative_force":
                    self.creative_force = max(
                        -100, min(100, self.creative_force + total_effect)
                    )
                    effects_text += f"- Творческая сила: {'+' if total_effect > 0 else ''}{total_effect}"
                    if bonus > 0:
                        effects_text += f" (сезонный бонус {self.season}!)"
                    effects_text += f" → {self.creative_force}\n"
                elif param == "adaptation":
                    self.adaptation = max(
                        -100, min(100, self.adaptation + total_effect)
                    )
                    effects_text += f"- Адаптация к провинции: {'+' if total_effect > 0 else ''}{total_effect}"
                    if bonus > 0:
                        effects_text += f" (сезонный бонус {self.season}!)"
                    effects_text += f" → {self.adaptation}\n"

        # Обновляем игровые счетчики
        self.letters_sent += 1
        self.season_letters += 1
        self.day += 30  # Каждое письмо занимает примерно месяц

        # Возвращаем к нормальному состоянию
        self.state = "normal"

        # Проверяем, не достигли ли мы какой-либо концовки
        if self.check_special_ending() or self.check_time_ending():
            return f"{letter_text}\n\n{effects_text}\n\n{self.get_ending_message()}"

        # Формируем интересный факт о стихотворении
        facts = [
            "Стихотворение «Письма римскому другу» было написано Бродским в 1972 году.",
            "Постум, адресат писем, является вымышленным другом поэта в Древнем Риме.",
            "В стихотворении Бродский проводит параллели между Римской империей и Советским Союзом.",
            "Тема изгнания в стихотворении перекликается с личным опытом Бродского, который был выслан из СССР в 1972 году.",
            "«Если выпало в Империи родиться, лучше жить в глухой провинции у моря» — один из самых известных афоризмов Бродского.",
        ]

        # Возвращаем результат
        result = f"{letter_text}\n\n{effects_text}\n\nИнтересный факт: {random.choice(facts)}\n\nНапишите, что хотите делать дальше:\n- письмо - написать новое письмо римскому другу\n- прогресс - проверить свой прогресс и параметры\n- помощь - показать эту справку"

        return result

    def advance_season(self) -> None:
        """Переход к следующему сезону"""
        if self.season == "весна":
            self.season = "лето"
        elif self.season == "лето":
            self.season = "осень"
        elif self.season == "осень":
            self.season = "зима"
        elif self.season == "зима":
            self.season = "весна"
            self.year += 1

        # Сбрасываем счетчик писем в сезоне
        self.season_letters = 0

        # Добавляем дни
        self.day += 10  # Небольшой промежуток между сезонами

    def show_progress(self) -> str:
        """Показать прогресс и параметры игрока"""
        progress = f"""
=== ТВОЙ ПРОГРЕСС ===
Год в изгнании: {self.year}
Сезон: {self.season}
День: {self.day}
Отправлено писем: {self.letters_sent}

Параметры:
- Мудрость: {self.wisdom} / 100
- Репутация в Риме: {self.rome_reputation} / 100
- Душевное равновесие: {self.balance} / 100
- Творческая сила: {self.creative_force} / 100
- Адаптация к провинции: {self.adaptation} / 100

"""

        # Добавляем подсказки в зависимости от текущих параметров
        if (
            max(
                abs(self.wisdom),
                abs(self.rome_reputation),
                abs(self.balance),
                abs(self.creative_force),
                abs(self.adaptation),
            )
            >= 75
        ):
            progress += "Ты приближаешься к одной из концовок.\n"

        if self.season_letters >= 2:
            progress += "Ты написал максимальное количество писем в этом сезоне. Напиши 'письмо', чтобы начать новый сезон.\n"
        else:
            progress += f"Ты можешь написать еще {2 - self.season_letters} письма в этом сезоне.\n"

        # Возвращаем статус
        return progress

    def check_special_ending(self) -> bool:
        """Проверить условие для особой концовки"""
        # Проверяем, достиг ли игрок +100 в каком-либо параметре (положительная концовка)
        if (
            self.wisdom >= 100
            or self.rome_reputation >= 100
            or self.balance >= 100
            or self.creative_force >= 100
            or self.adaptation >= 100
        ):
            self.state = "game_over"
            return True

        # Проверяем, достиг ли игрок -100 в каком-либо параметре (отрицательная концовка)
        if (
            self.wisdom <= -100
            or self.rome_reputation <= -100
            or self.balance <= -100
            or self.creative_force <= -100
            or self.adaptation <= -100
        ):
            self.state = "game_over"
            return True

        return False

    def check_time_ending(self) -> bool:
        """Проверить условие для концовки по времени"""
        # Концовка по времени не используется в этой игре
        return False

    def get_ending_message(self) -> str:
        """Получить сообщение о концовке"""
        # Определяем, какая концовка достигнута

        # Положительные концовки
        if self.wisdom >= 100:
            return self.get_wisdom_positive_ending()
        elif self.rome_reputation >= 100:
            return self.get_reputation_positive_ending()
        elif self.balance >= 100:
            return self.get_balance_positive_ending()
        elif self.creative_force >= 100:
            return self.get_creative_positive_ending()
        elif self.adaptation >= 100:
            return self.get_adaptation_positive_ending()

        # Отрицательные концовки
        elif self.wisdom <= -100:
            return self.get_wisdom_negative_ending()
        elif self.rome_reputation <= -100:
            return self.get_reputation_negative_ending()
        elif self.balance <= -100:
            return self.get_balance_negative_ending()
        elif self.creative_force <= -100:
            return self.get_creative_negative_ending()
        elif self.adaptation <= -100:
            return self.get_adaptation_negative_ending()

        # Если по какой-то причине не определена концовка
        return "Твое путешествие в изгнании подошло к концу.\n\nВведи /start, чтобы начать новую игру."

    def get_wisdom_positive_ending(self) -> str:
        """Положительная концовка по Мудрости"""
        return """
╔════════════════════════════════════════════════════════════╗
║             ФИЛОСОФСКОЕ ПРОСВЕТЛЕНИЕ                       ║
╚════════════════════════════════════════════════════════════╝

Твои размышления о жизни, смерти и временности всего сущего привлекают внимание. 
К тебе начинают приезжать ученики со всей империи. Твоя хижина у моря становится 
академией, где простота быта соседствует с глубиной мысли. Местные власти 
уважительно обходят тебя стороной, а молодые поэты записывают каждое твое слово.

Годы изгнания превратились в годы обретения истинной свободы мысли. 
Рим больше не кажется центром мира — он лишь еще одна точка на карте вечности,
которую ты научился читать.

ПОЗДРАВЛЯЕМ!
Ты достиг высшей мудрости и обрел внутреннюю свободу.

Введи /start, чтобы начать новую игру.
"""

    def get_reputation_positive_ending(self) -> str:
        """Положительная концовка по Репутации в Риме"""
        return """
╔=================╗
║     ВОЗВРАЩЕНИЕ      ║
║      ИЗ ИЗГНАНИЯ       ║
╚=================╝

Постум добился своего. На рассвете к твоему дому подходит официальный 
посланник с императорской печатью. Твое изгнание окончено. В Риме тебя 
ждет дом, восстановленное положение и, возможно, место при дворе.

Собирая немногочисленные вещи, ты бросаешь последний взгляд на море, навсегда запоминая его шум и запах.

ПОЗДРАВЛЯЕМ!
Ты вернул себе утраченное положение в Риме, и можешь вернуться к прежней жизни.

Введи /start, чтобы начать новую игру."""

    def get_balance_positive_ending(self) -> str:
        """Положительная концовка по Душевному равновесию"""
        return """
╔=================╗
║      АТАРАКСИЯ      ║
╚=================╝

Ты достиг внутренней безмятежности, которой позавидовали бы древние стоики.
Жизнь в провинции, размеренная и простая, оказалась именно тем, что нужно твоей душе. 
Перемены империй, интриги Рима — все это теперь кажется незначительным.

Твоя хижина, сад и море стали целым миром, вместившим в себя все, что действительно важно.
Ты больше не чувствуешь себя изгнанником — ты просто человек, нашедший свое место.

ПОЗДРАВЛЯЕМ!
Ты обрел внутренний покой и равновесие, недоступное даже императорам.

Введи /start, чтобы начать новую игру.
"""

    def get_creative_positive_ending(self) -> str:
        """Положительная концовка по Творческой силе"""
        return """
╔=================╗
║     ПОЭТИЧЕСКОЕ     ║
║     БЕССМЕРТИЕ      ║
╚=================╝

Твои стихи, которые ты отправлял Постуму, начали тайно распространяться по Риму. 
Их переписывают, передают из рук в руки, читают на закрытых вечерах. Даже не 
присутствуя в столице физически, ты стал самым влиятельным поэтом своего времени.

Когда-нибудь твои строки будут высечены в мраморе, и потомки будут изучать их, 
пытаясь понять, как в изгнании можно было создать нечто столь совершенное.

ПОЗДРАВЛЯЕМ!
Ты создал поэзию, которая переживет и тебя, и Рим.

Введи /start, чтобы начать новую игру.
"""

    def get_adaptation_positive_ending(self) -> str:
        """Положительная концовка по Адаптации"""
        return """
╔=================╗
║    НОВАЯ РОДИНА     ║
╚=================╝

Местные жители перестали считать тебя чужаком. Ты женился на дочери рыбака, 
выучил местный диалект, освоил ремесла этого края. Когда из Рима приходят 
известия о возможном возвращении, ты понимаешь, что уже не хочешь уезжать.

Эта простая жизнь у моря, эти люди, этот воздух — все это стало твоим настоящим 
домом, в отличие от мраморного Рима, который теперь кажется музеем призраков.

ПОЗДРАВЛЯЕМ!
Ты нашел свой настоящий дом и принял свою новую жизнь.

Введи /start, чтобы начать новую игру.
"""

    def get_wisdom_negative_ending(self) -> str:
        """Отрицательная концовка по Мудрости"""
        return """
╔=================╗
║      ДУХОВНОЕ       ║
║     ОПУСТОШЕНИЕ     ║
╚=================╝

Изоляция и отсутствие интеллектуального общения сделали свое дело. Твои мысли 
мельчают, письма становятся пустыми и бессодержательными. Ты больше не можешь 
сформулировать ничего глубокого, ничего достойного записи.

Дни сливаются в бесконечную серую полосу, а вопросы, которые раньше волновали 
тебя, теперь кажутся бессмысленными. Ум, некогда острый как меч, заржавел и 
притупился от безделья и одиночества.

КОНЕЦ ИГРЫ.
Твой разум не выдержал испытания изгнанием.

Введи /start, чтобы начать новую игру.
"""

    def get_balance_negative_ending(self) -> str:
        """Отрицательная концовка по Душевному равновесию"""
        return """
╔=================╗
║     МЕЛАНХОЛИЯ      ║
╚=================╝

Тоска по Риму становится невыносимой. Ты не спишь по ночам, вслушиваясь в шум 
моря, который теперь кажется насмешкой. Еда теряет вкус, вино не приносит радости.

Ты перестаешь писать, выходить из дома, говорить с людьми. Каждый день похож на 
предыдущий — серый, пустой, бессмысленный. Твоя душа словно покинула тело и 
улетела в далекий Рим.

КОНЕЦ ИГРЫ.
Твой дух сломлен тяжестью изгнания.

Введи /start, чтобы начать новую игру.
"""

    def get_creative_negative_ending(self) -> str:
        """Отрицательная концовка по Творческой силе"""
        return """
╔=================╗
║    ТВОРЧЕСКИЙ       ║
║       КРИЗИС        ║
╚=================╝

Муза покидает тебя. Сначала ты не можешь подобрать нужные слова, потом перестаешь 
слышать ритм, наконец, исчезает сама потребность писать. Ты смотришь на чистые 
свитки с ужасом. Перо в твоей руке кажется бесполезным орудием.

Мысли есть, но они не облекаются в стихи. Молчание становится твоим новым языком.
Поэт умер, остался только изгнанник.

КОНЕЦ ИГРЫ.
Творческий огонь в тебе погас.

Введи /start, чтобы начать новую игру.
"""

    def get_adaptation_negative_ending(self) -> str:
        """Отрицательная концовка по Адаптации"""
        return """
╔=================╗
║    ВЕЧНЫЙ ЧУЖАК     ║
╚=================╝

Местные жители так и не приняли тебя. Они шепчутся за твоей спиной, отводят 
детей, когда ты проходишь мимо, перестают продавать тебе свежую рыбу и фрукты.

Твой латинский акцент, твои римские привычки, твоя образованность — все это 
стена между тобой и этими людьми. Ты построил себе хижину вдали от деревни, 
став отшельником не по своей воле.

КОНЕЦ ИГРЫ.
Ты не смог стать своим ни здесь, ни там.

Введи /start, чтобы начать новую игру.
"""

    def get_reputation_negative_ending(self) -> str:
        """Отрицательная концовка по Репутации в Риме"""
        return """
╔=================╗
║   ПОЛНОЕ ЗАБВЕНИЕ   ║
╚=================╝

Письма от Постума приходят все реже, а затем прекращаются совсем. Ты узнаешь 
от проезжающего купца, что твое имя вычеркнуто из всех официальных записей, 
твои книги сожжены, а дом передан новому владельцу.

В Риме ты больше не существуешь. Ни друзья, ни враги не упоминают тебя — 
словно ты никогда не жил. Ты стал призраком при жизни, человеком без прошлого.

КОНЕЦ ИГРЫ.
Рим забыл тебя, как бесполезный сон.

Введи /start, чтобы начать новую игру.
"""

    def get_special_ending(self) -> str:
        """Получить текст особой концовки"""
        return self.get_ending_message()

    def get_time_ending(self) -> str:
        """Получить текст концовки по времени"""
        # Концовка по времени не используется в этой игре
        return "В этой игре нет концовки по времени."