from shutil import move
from typing import Union, Dict
import os
from requests import get
from zipfile import ZipFile
import PySimpleGUI as sg
from logging import basicConfig, getLogger, DEBUG
from traceback import format_exc


log = getLogger()
FORMAT = "%(levelname)-8s [%(asctime)s] %(message)s"
datefmt = '%d.%m.%y %H:%M:%S'
basicConfig(filename='log.log', format=FORMAT, datefmt=datefmt, level=DEBUG, encoding='utf-8')


def gui() -> None:
    """
    Графический интерфейс
    :return: None
    """
    key = False

    dict_files = {
        "base2020": 11,
        "base2022": 1,
        "base2017": 6,
        "bib_smetcica": 13,
        "grand_smeta12_3_3": 5,
        "lic": 1
    }

    download_score_max = sum(dict_files.values())

    # Окно авторизации
    field_one = [
        [sg.Text('Код активации:'), sg.InputText(password_char="*")],
        [sg.Submit(button_text='Ввести'), sg.CloseButton(button_text='Закрыть')]
    ]
    window = sg.Window(title='Менеджер загрузок', layout=field_one, icon='icon.ico', margins=(10, 1), size=(250, 50))
    log.debug('Открыто окно авторизации')

    # password задается пароль
    password = ''

    while True:
        event, values1 = window.read()

        if values1.get(0) == password:
            log.debug('Пароль верный')
            key = True
            window.close()
            log.debug('Закрыто окно авторизации')
            break

        elif event in (None, 'Exit', 'Закрыть'):
            log.debug('Выход')
            return

        log.error("Неверный пароль")

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/50.0.2661.102 Safari/537.36'}

    field_two = [
        [
            sg.Checkbox(text='ГЭСН-ФЭР 2020', default=False, key='bd2020'),
            sg.Checkbox(text='ГЭСН-ФЭР 2017', default=False, key='bd2017'),
            sg.Checkbox(text='ФСНБ-2022', default=False, key='bd2022'),
            sg.Checkbox(text='Библиотека сметчика', default=False, key='bib_smet')
        ],
        [sg.Text('Путь для баз:'), sg.InputText(), sg.FolderBrowse(button_text='Выбрать', key='path_save_base')],
        [sg.Checkbox(text='Гранд смета 2022.3.3', default=False, key='grand_smeta12_3_3')],
        [sg.Checkbox(text='Lic', default=False, key='lic')],
        [sg.Text('Путь для лицензий:'), sg.InputText(), sg.FolderBrowse(button_text='Выбрать',
                                                                        key='path_save_lic')],
        [
            sg.Text('Загрузка:'),
            sg.ProgressBar(max_value=download_score_max, orientation='h', size=(20, 20), key='progress_1',
                           style='winnative', border_width=1, visible=True)
         ],
        [sg.Output(size=(88, 5))],
        [sg.Submit(button_text='Загрузить'), sg.CloseButton(button_text='Закрыть')],
    ]

    window = sg.Window('Менеджер загрузок', field_two, icon='icon.ico', finalize=True)
    log.debug('Открыто окно менеджера загрузок')

    while key:
        downloader = 0
        event, values = window.read()

        if event in (None, 'Exit', 'Cancel'):
            log.debug('Выход')
            return

        if not os.path.exists('Download'):
            os.mkdir('Download')

        # 2020
        count = dict_files["base2020"]
        if values.get('bd2020'):

            for number in range(count):
                print(f'Загрузка файла NB1080{number}.zip')
                log.debug(f'Загрузка файла NB1080{number}.zip')
                window.refresh()
                try:
                    base2020(number=number, headers=headers, path=values.get('path_save_base'))
                except Exception:
                    log.error(f"Не удалось загрузить NB1080{number} {format_exc()}")
                    downloader += 1
                    continue

                downloader += 1
                window['progress_1'].update(downloader)

        else:
            downloader += count
            window['progress_1'].update(downloader)

        # 2017
        count = dict_files["base2017"]
        if values.get('bd2017'):

            for number in range(count):
                print(f"Загрузка файла NB10700{number}.zip")
                log.debug(f"Загрузка файла NB10700{number}.zip")
                window.refresh()
                try:
                    base2017(number=number, headers=headers, path=values.get('path_save_base'))
                except Exception:
                    log.error(f"Не удалось загрузить NB10700{number} {format_exc()}")
                    downloader += 1
                    continue
                downloader += 1
                window['progress_1'].update(downloader)

        else:
            downloader += count
            window['progress_1'].update(downloader)

        # 2022
        count = dict_files["base2022"]
        if values.get('bd2022'):

            for number in range(3, 4):
                print(f'Загрузка файла NB12100{number}')
                log.debug(f'Загрузка файла NB12100{number}')
                window.refresh()
                try:
                    base2022(number=number, headers=headers, path=values.get('path_save_base'))
                except Exception:
                    log.error(f"Не удалось загрузить NB12100{number} {format_exc()}")
                    downloader += 1
                    continue
                downloader += 1
                window['progress_1'].update(downloader)
        else:
            downloader += count
            window['progress_1'].update(downloader)

        # Библиотека сметчика
        count = dict_files["bib_smetcica"]
        if values.get('bib_smet'):

            all_number = ['01', '10', '11', '15', '16',
                          '20', '30', '40', '60', '61',
                          '65', '70', '80']

            for number in all_number:
                print(f'Загрузка файла NB1120{number}.zip')
                log.debug(f'Загрузка файла NB1120{number}.zip')
                window.refresh()
                try:
                    bib_smetcica(number=number, headers=headers, path=values.get('path_save_base'))
                except Exception:
                    log.error(f"Не удалось загрузить NB1120{number} {format_exc()}")
                    downloader += 1
                    continue
                downloader += 1
                window['progress_1'].update(downloader)

        else:
            downloader += count
            window['progress_1'].update(downloader)

        # Lic
        count = dict_files["lic"]
        if values.get('lic'):
            print('Загрузка лицензий')
            log.debug('Загрузка лицензий')
            window.refresh()
            try:
                lic(path=values.get('path_save_lic'))
            except Exception:
                log.error(f"Не удалось переместить лицензии {format_exc()}")

        downloader += count
        window['progress_1'].update(downloader)

        # Гранд Смета 2022.3.3
        count = dict_files["grand_smeta12_3_3"]
        if values.get('grand_smeta12_3_3'):
            print('Загрузка дистрибутива Гранд Смета 2022.3.3')
            log.debug('Загрузка дистрибутива Гранд Смета 2022.3.3')
            window.refresh()
            try:
                grand_smeta12_3_3(headers=headers)
            except Exception:
                log.error(f"Не удалось загрузить дистрибутив Гранд Смета 2022.3.3 {format_exc()}")

        downloader += count
        window['progress_1'].update(downloader)

        print("Готово")
        log.debug("Готово")


def base2020(number: int, headers: Dict, path: Union[str] = None) -> None:
    """
    Загрузка архива нормативной базы 2020 с распаковкой в указанную директорию path
    :param number: Номер базы
    :param headers: Заголовок get-запроса
    :param path: Путь распаковки
    :return: None
    """
    listdir = os.listdir('Download')
    name = f'NB10800{number}' if number < 10 else f'NB1080{number}'
    if f'{name}.zip' in listdir:
        with ZipFile(rf'Download\{name}.zip') as zipp:
            zipp.extractall(path=path)

    else:
        url = f'https://ftp.grandsmeta.ru/grandsmeta/data/2020/{name}.zip'

        res = get(url=url, headers=headers)
        path_arh = os.path.join('Download', f"{name}.zip")
        with open(path_arh, 'wb') as file:
            file.write(res.content)

        with ZipFile(path_arh) as zipp:
            zipp.extractall(path)

    print(f'Файл {name}.zip установлен')


def base2022(number: int, headers: Dict, path: str) -> None:
    """
    Загрузка архива нормативной базы 2022 с распаковкой в указанную директорию path
    :param number: Номер базы
    :param headers: Заголовок get-запроса
    :param path: Путь распаковки
    :return: None
    """
    listdir = os.listdir('Download')

    name = f'NB12100{number}'
    if f'{name}.zip' in listdir:
        with ZipFile(rf'Download\{name}.zip') as zipp:
            zipp.extractall(path)
    else:
        url = f'https://cdn.grandsmeta.ru/ftp/grandsmeta/data/2022/{name}.zip'

        res = get(url=url, headers=headers)
        path_arh = os.path.join('Download', f"{name}.zip")
        with open(path_arh, 'wb') as file:
            file.write(res.content)

        with ZipFile(path_arh) as zipp:
            zipp.extractall(path)

    print(f'')


def bib_smetcica(number: int, headers: Dict, path: Union[str] = None) -> None:
    """
    Загрузка архива нормативной базы библиотеки сметчика с распаковкой в указанную директорию path
    :param number: Номер базы
    :param headers: Заголовок get-запроса
    :param path: Путь распаковки
    :return: None
    """
    listdir = os.listdir('Download')
    if f'NB1120{number}.zip' in listdir:
        with ZipFile(f'Download/NB1120{number}.zip') as zipp:
            zipp.extractall(path)
    else:
        url = f'https://ftp.grandsmeta.ru/grandsmeta/data/si/NB1120{number}.zip'

        res = get(url=url, headers=headers)
        path_arh = os.path.join('Download', f"NB1120{number}.zip")
        with open(path_arh, 'wb') as file:
            file.write(res.content)

        with ZipFile(path_arh) as zipp:
            zipp.extractall(path)

    print(f'Файл NB1120{number}.zip загружен')


def base2017(number: int, headers: Dict, path: str) -> None:
    """
    Загрузка архива нормативной базы 2017 с распаковкой в указанную директорию path
    :param number: Номер базы
    :param headers: Заголовок get-запроса
    :param path: Путь распаковки
    :return: None
    """
    listdir = os.listdir('Download')
    if f'NB10700{number}.zip' in listdir:
        with ZipFile(f'Download/NB10700{number}.zip') as zipp:
            zipp.extractall(path)

    else:
        url = f'https://ftp.grandsmeta.ru/grandsmeta/data/2017/nb10700{number}.zip'
        res = get(url=url, headers=headers)
        path_arh = os.path.join('Download', f"NB10700{number}.zip")
        with open(path_arh, 'wb') as file:
            file.write(res.content)

        with ZipFile(path_arh) as zipp:
            zipp.extractall(path)

    print(f"Файл NB10700{number}.zip установлен")


def grand_smeta12_3_3(headers: Dict) -> None:
    """
    Загружает и распаковыем дистрибутив программы Гранд Смета 2022.3.3 в директорию Download
    :param headers: Заголовок get-запроса
    :return: None
    """

    url = 'https://ftp.grandsmeta.ru/grandsmeta/distrib/smeta2022.3.3.zip'
    res = get(url=url, headers=headers)
    path_arh = os.path.join('Download', "smeta2022.3.3.zip")
    with open(path_arh, 'wb') as file:
        file.write(res.content)

    with ZipFile(path_arh) as zipp:
        zipp.extractall('Download')


def lic(path: str) -> None:
    """
    Перемещает все файлы в директории Lic с расширением .lic в указанный путь
    :param path: Путь перемещения
    :return: None
    """
    listdir = os.listdir('Lic')
    for file in listdir:
        if file.endswith('.lic'):
            move(os.path.join('Lic', file), path)


if __name__ == '__main__':
    gui()
