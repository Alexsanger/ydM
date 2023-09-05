from cProfile import label
import os, pygame
import requests, io
import sys
import webbrowser
import speech_recognition as sr
from yandex_music import Client

# Инициализация Pygame
pygame.init()
pygame.mixer.init()
music_player = pygame.mixer.music

# Получение токена
if os.path.exists("token.txt"):
    with open("token.txt", "r") as file:
        token = file.read().strip()
else:
    token = input("Enter Yandex Music Token: ")
    with open("token.txt", "w") as file:
        file.write(token)

client = Client(token).init()

# Получение понравившихся треков
tracks = client.users_likes_tracks()

# Функция, позволяющая проговаривать слова
# Принимает параметр "Слова" и проговаривает их
def talk(words):
    print(words)  # Дополнительно выводим на экран
    os.system("say " + words)  # Проговариваем слова

# Функция command() служит для отслеживания микрофона.
# Вызывая функцию мы будем слушать, что скажет пользователь,
# при этом для прослушивания будет использован микрофон.
# Полученные данные будут сконвертированы в строку и далее
# будет происходить их проверка.
def command():
    # Создаем объект на основе библиотеки speech_recognition и вызываем метод для определения данных
    r = sr.Recognizer()

    # Начинаем прослушивать микрофон и записываем данные в source
    with sr.Microphone() as source:
        # Просто вывод, чтобы мы знали, когда говорить
        print("Говорите")
        # Устанавливаем паузу, чтобы прослушивание
        # началось лишь по прошествии 1 секунды
        r.pause_threshold = 1
        # Используем adjust_for_ambient_noise для удаления
        # посторонних шумов из аудио дорожки
        r.adjust_for_ambient_noise(source, duration=1)
        # Полученные данные записываем в переменную audio
        # пока мы получили лишь mp3 звук
        audio = r.listen(source)

    try:  # Обрабатываем все при помощи исключений
        """
        Распознаем данные из mp3 дорожки.
        Указываем, что отслеживаемый язык русский.
        Благодаря lower() приводим все в нижний регистр.
        Теперь мы получили данные в формате строки,
        которые спокойно можем проверить в условиях
        """
        zadanie = r.recognize_google(audio, language="ru-RU").lower()
        # Просто отображаем текст, что сказал пользователь
        print("Вы сказали: " + zadanie)
        # Если не смогли распознать текст, то будет вызвана эта ошибка
    except sr.UnknownValueError:
        # Здесь просто проговариваем слова "Я вас не поняла"
        # и вызываем снова функцию command() для
        # получения текста от пользователя
        talk("Я вас не поняла")
        zadanie = ""
    # В конце функции возвращаем текст задания
    # или же повторный вызов функции
    return zadanie

# Функция воспроизведения трека
def play_track(index):
    global current_track_index
    current_track_index = index

    # Получение информации о треке
    track = tracks[current_track_index].fetch_track()
    download_info = track.get_download_info(get_direct_links=True)
    direct_link = download_info[0].direct_link
    track_name = track.title

   # Загрузка и воспроизведение трека
    response = requests.get(direct_link)
    audio_content = response.content
    with open("temp.mp3", "wb") as file:
        file.write(audio_content)
    music_player.load("temp.mp3")
    music_player.play()

    # Вывод названия трека
    global playing
    playing = True

# Данная функция служит для проверки текста,
# что сказал пользователь (zadanie - текст от пользователя)
def makeSomething(zadanie):
    # Попросту проверяем текст на соответствие
    # Если в тексте, что сказал пользователь есть слова
    # "включи песни", то выполняем команду
    if 'включи песни' in zadanie:
        # Проговариваем текст
        talk("Включаю песни")

        # Воспроизведение понравившихся треков
        for i in range(len(tracks)):
            play_track(i)
            while pygame.mixer.music.get_busy():
                continue

    # если было сказано "стоп", то останавливаем прогу
    elif 'стоп' in zadanie:
        # Проговариваем текст
        talk("Да, конечно, без проблем")
        # Выходим из программы
        sys.exit()

    # Аналогично
    elif 'имя' in zadanie:
        talk("Меня зовут Сири")

# Вызов функции для проверки текста будет
# осуществляться постоянно, поэтому здесь
# прописан бесконечный цикл while
while True:
    makeSomething(command())