import os
import random


def load_words_from_file(filename):
    # Загрузка слов и описаний из файла
    words_with_desc = []
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if line and '|' in line:
                    word, description = line.split('|', 1)
                    words_with_desc.append((word.strip().lower(), description.strip()))
    except FileNotFoundError:
        return []
    return words_with_desc


def save_words_to_file(filename, words_with_desc):
    # Сохранение слов и описаний в файл
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            for word, desc in words_with_desc:
                file.write(f"{word}|{desc}\n")
        return True
    except:
        return False


def get_random_word(words_list):
    # Получение случайного слова из списка
    if not words_list:
        return None, None
    return random.choice(words_list)


def create_hidden_word(word):
    # Создание скрытого слова в виде списка символов
    return ['■' for _ in word]


def get_hangman_frames():
    # Загрузка всех фрагментов виселицы из файлов
    frames = []
    frame_number = 0
    while True:
        filename = f"hangman_frames/frame_{frame_number}.txt"
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                frames.append(file.read())
            frame_number += 1
        except FileNotFoundError:
            break
    return frames


def display_hangman(frames, lives):
    # Отображение текущего состояния виселицы
    if not frames:
        return "Виселица не загружена"
    max_lives = len(frames) - 1
    current_frame = max_lives - lives if lives <= max_lives else 0
    if current_frame < len(frames):
        return frames[current_frame]
    return frames[-1]


def display_word_table(word_display):
    # Отображение текущего состояния слова
    return ' '.join(word_display)


def display_info(word_display, lives, description):
    # Отображение всей информации об игре
    return f"\n{display_word_table(word_display)}\n\n📖 Подсказка: {description}\n\n❤️ Жизней осталось: {lives}\n"


def is_game_alive(lives):
    # Проверка жив ли
    return lives > 0


def is_word_guessed(word_display):
    # Проверка угадано слово
    return '■' not in word_display


def check_letter(word, word_display, letter):
    # Проверка буквы и обновление отображения
    letter = letter.lower()
    if letter in word:
        updated = False
        for i, char in enumerate(word):
            if char == letter:
                word_display[i] = letter.upper()
                updated = True
        return True, word_display
    return False, word_display


def check_full_word(word, guess):
    """Проверка полного слова"""
    return guess.lower() == word


def get_user_input(prompt_message):
    """Получение ввода от пользователя"""
    return input(prompt_message)


def display_message(message):
    """Вывод сообщения"""
    print(message)


def clear_screen():
    # Очистка экрана
    os.system('cls' if os.name == 'nt' else 'clear')


def save_game_state(word, word_display, lives, used_words):
    # Сохранение состояния игры в текстовый файл
    try:
        with open('savegame.txt', 'w', encoding='utf-8') as f:
            f.write(f"{word}\n")
            f.write(','.join(word_display) + "\n")
            f.write(str(lives) + "\n")
            f.write(','.join(used_words) + "\n")
        return True
    except:
        return False


def load_game_state():
    # Загрузка состояния игры из текстового файла
    try:
        with open('savegame.txt', 'r', encoding='utf-8') as f:
            word = f.readline().strip()
            word_display = f.readline().strip().split(',')
            lives = int(f.readline().strip())
            used_line = f.readline().strip()
            used_words = used_line.split(',') if used_line else []
        return {
            'word': word,
            'word_display': word_display,
            'lives': lives,
            'used_words': used_words
        }
    except (FileNotFoundError, ValueError, IndexError):
        return None


def delete_save():
    # Удаление сохранения
    try:
        os.remove('savegame.txt')
        return True
    except:
        return False


def is_admin_password(password):
    # Проверка пароля администратора
    try:
        with open('admin_password.txt', 'r', encoding='utf-8') as f:
            correct_password = f.read().strip()
        return password == correct_password
    except:
        return password == "Passw0rd"


def admin_panel(words_list):
    # Админ-панель для редактирования списка слов
    while True:
        display_message("\n" + "=" * 50)
        display_message("АДМИН-ПАНЕЛЬ")
        display_message("=" * 50)
        display_message("1. Показать все слова")
        display_message("2. Добавить слово")
        display_message("3. Удалить слово")
        display_message("4. Очистить весь список")
        display_message("5. Сохранить и выйти")
        display_message("6. Выйти без сохранения")

        choice = get_user_input("\nВыберите действие: ")

        if choice == '1':
            display_message("\nСписок слов:")
            for i, (word, desc) in enumerate(words_list, 1):
                display_message(f"{i}. {word} - {desc}")

        elif choice == '2':
            word = get_user_input("Введите слово: ").strip().lower()
            desc = get_user_input("Введите описание: ").strip()
            if word and desc:
                words_list.append((word, desc))
                display_message("✅ Слово добавлено!")
            else:
                display_message("❌ Ошибка: слово и описание не могут быть пустыми!")

        elif choice == '3':
            display_message("\nСписок слов:")
            for i, (word, desc) in enumerate(words_list, 1):
                display_message(f"{i}. {word} - {desc}")
            try:
                index = int(get_user_input("Введите номер слова для удаления: ")) - 1
                if 0 <= index < len(words_list):
                    removed = words_list.pop(index)
                    display_message(f"✅ Удалено слово: {removed[0]}")
                else:
                    display_message("❌ Неверный номер!")
            except ValueError:
                display_message("❌ Введите число!")

        elif choice == '4':
            confirm = get_user_input("Вы уверены? (да/нет): ").lower()
            if confirm == 'да':
                words_list.clear()
                display_message("✅ Список очищен!")

        elif choice == '5':
            if save_words_to_file('words.txt', words_list):
                display_message("✅ Изменения сохранены!")
            else:
                display_message("❌ Ошибка сохранения!")
            break

        elif choice == '6':
            display_message("Выход без сохранения...")
            break

        else:
            display_message("❌ Неверный выбор!")

    return words_list


def play_again():
    # Спросить хочет ли игрок сыграть ещё
    answer = get_user_input("\nХотите сыграть ещё? (да/нет): ").lower()
    return answer == 'да'


def continue_game():
    # Спросить, хочет ли игрок продолжить сохранённую игру
    answer = get_user_input("Найдено сохранение! Продолжить игру? (да/нет): ").lower()
    return answer == 'да'


def show_victory_message(word):
    # Показать сообщение о победе
    display_message(f"\n🎉 ПОБЕДА! 🎉")
    display_message(f"Загаданное слово: {word.upper()}")
    display_message("Вы выиграли! Приз в студию!")


def show_defeat_message(word):
    # Показать сообщение о поражении
    display_message(f"\n💀 ВАС ПОВЕСИЛИ! 💀")
    display_message(f"Загаданное слово было: {word.upper()}")
    display_message("Попробуйте в следующий раз!")