from game_functions import *

def main():
    #Проверка на кадры
    frames = get_hangman_frames()
    if not frames:
        display_message("Ошибка: не найдены файлы с кадрами виселицы в папке hangman_frames/")
        return

    words_list = load_words_from_file('words.txt')

    if not words_list:
        display_message("❌ Нет доступных слов! Добавьте слова через админ-панель.")
        password = get_user_input("Введите пароль администратора для добавления слов: ")
        if is_admin_password(password):
            words_list = admin_panel(words_list)
        else:
            display_message("Неверный пароль! Игра завершена.")
            return

    used_words = []  # список использованных слов (строк)
    saved_state = load_game_state()

    if saved_state and continue_game():
        word = saved_state['word']
        word_display = saved_state['word_display']
        lives = saved_state['lives']
        used_words = saved_state['used_words']
        #описание для загруженного слова
        description = None
        for w, desc in words_list:
            if w == word:
                description = desc
                break
        if description is None:
            #Если слово не найдено в текущем списке, начинаем новую игру
            display_message("Загруженное слово отсутствует в текущем списке. Начинаем новую игру.")
            delete_save()
            #Выбираем новое слово из тех что не использованы
            available = [(w, d) for w, d in words_list if w not in used_words]
            word, description = get_random_word(available)
            if not word:
                display_message("🎉 Поздравляем! Вы отгадали все слова!")
                return
            word_display = create_hidden_word(word)
            lives = len(frames) - 1
            used_words.append(word)
        else:
            delete_save()
    else:
        delete_save()
        #Выбираем слово которое еще не использовалось
        available = [(w, d) for w, d in words_list if w not in used_words]
        word, description = get_random_word(available)

        if not word:
            display_message("🎉 Поздравляем! Вы отгадали все слова!")
            return

        word_display = create_hidden_word(word)
        lives = len(frames) - 1
        used_words.append(word)

    while is_game_alive(lives) and not is_word_guessed(word_display):
        clear_screen()
        display_message(display_hangman(frames, lives))
        display_message(display_info(word_display, lives, description))

        answer = get_user_input(
            "Назовите букву или слово целиком (или 'save' для сохранения, 'admin' для админ-панели): ").strip()

        if answer.lower() == 'save':
            save_game_state(word, word_display, lives, used_words)
            display_message("Игра сохранена! До скорой встречи!")
            break

        elif answer.lower() == 'admin':
            password = get_user_input("Введите пароль администратора: ")
            if is_admin_password(password):
                admin_panel(words_list)
                words_list = load_words_from_file('words.txt')
                # Обновляем описание текущего слова
                for w, desc in words_list:
                    if w == word:
                        description = desc
                        break
            else:
                display_message("❌ Неверный пароль!")
            continue

        elif len(answer) == 1:
            success, word_display = check_letter(word, word_display, answer)
            if success:
                display_message("✅ Верно!")
            else:
                lives -= 1
                display_message(f"❌ Неправильно! Вы теряете жизнь. Осталось: {lives}")

        elif len(answer) > 1:
            if check_full_word(word, answer):
                word_display = [c.upper() for c in word]
                break
            else:
                lives -= 1
                display_message(f"❌ Неправильно! Вы теряете жизнь. Осталось: {lives}")

        get_user_input("\nНажмите Enter для продолжения...")

    clear_screen()
    display_message(display_hangman(frames, lives))

    if is_word_guessed(word_display):
        display_message(f"\n{display_word_table(word_display)}")
        show_victory_message(word)
    elif not is_game_alive(lives):
        show_defeat_message(word)

    if play_again() and words_list:
        main()
    else:
        display_message("\nСпасибо за игру! До свидания!")

main()