from time import time
from shutil import move
from typing import Union, Dict
import os
from requests import get
from zipfile import ZipFile
import PySimpleGUI as sg
from logging import config, getLogger, DEBUG
from traceback import format_exc
from yadisk import YaDisk
from yadisk.exceptions import UnavailableError


FORMAT = "%(levelname)-8s [%(asctime)s] %(message)s"
datefmt = '%d.%m.%y %H:%M:%S'

log_config = {
    'version': 1,
    'formatters': {
        'for_file': {
            'format': FORMAT,
            'datefmt': datefmt
        }
    },
    'handlers': {
        'for_file': {
            'class': 'logging.FileHandler',
            'filename': 'log.log',
            'encoding': 'utf-8',
            'formatter': 'for_file',
            'level': DEBUG
        }
    },
    'loggers': {
        '': {
            'handlers': ['for_file'],
            'level': DEBUG
        }
    }
}
config.dictConfig(log_config)
log = getLogger()

# basicConfig(filename='log.log', format=FORMAT, datefmt=datefmt,
#             level=DEBUG, encoding='utf-8')


def gui() -> None:
    """
    Графический интерфейс
    :return: None
    """

    dict_files_all = {
        "base2020": 11,
        "base2022": 3,
        "base2017": 6,
        "base2001_2009": 8,
        "base2001_2014": 4,
        "rt": 5,
        "bib_smetcica": 13,
        "grand_smeta12_3_3": 5,
        "grand_smeta13_1_0": 5,
        "grand_smeta13_1_1": 5,
        "grand_smeta13_1_2": 5,
        "grand_smeta13_1_3": 5,
        "grand_smeta13_2_0": 5,
        "grand_smeta13_2_1": 5,
        "grand_smeta13_2_2": 5,
        "grand_smeta13_2_3": 5,
        "grand_smeta13_2_4": 5,
        "grand_smeta13_3_0": 5,
        "lic": 1,
        "ucrup_norm": 1,
        "pir": 1,
        "ved_sbor": 1
    }

    # Окно авторизации
    field_one = [
        [sg.Text('Код активации:'), sg.InputText(password_char="*")],
        [sg.Submit(button_text='Ввести'), sg.CloseButton(button_text='Закрыть')]
    ]
    window = sg.Window(title='Менеджер загрузок', layout=field_one, icon='icon.ico', margins=(10, 1), size=(250, 50))
    log.debug('Открыто окно авторизации')

    # password задается пароль
    password = '253333'

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
            sg.Checkbox(text='ГЭСН-ФЭР 2001 в редакции 2009 года', default=False, key='base2001_2009'),
            sg.Checkbox(text='ГЭСН-ФЭР 2001 в редакции 2014 года', default=False, key='base2001_2014'),
        ],
        [
            sg.Checkbox(text='ГЭСН-ФЭР 2020', default=False, key='base2020'),
            sg.Checkbox(text='ГЭСН-ФЭР 2017', default=False, key='base2017'),
            sg.Checkbox(text='ФСНБ-2022', default=False, key='base2022'),
            sg.Checkbox(text='Библиотека сметчика', default=False, key='bib_smetcica')
        ],
        [
            sg.Checkbox(text='Укрупненные нормативы', default=False, key='ucrup_norm'),
            sg.Checkbox(text='Проектно-изыскательские работы', default=False, key='pir'),
            sg.Checkbox(text='Ведомcтвенные и прочие сборники', default=False, key='ved_sbor'),
            # sg.Checkbox(text='РТ', default=False, key='rt')
        ],
        [sg.Text('Путь для баз:'), sg.InputText(), sg.FolderBrowse(button_text='Выбрать', key='path_save_base')],

        [sg.Checkbox(text='Гранд смета 2022.3.3', default=False, key='grand_smeta12_3_3')],

        [sg.Checkbox(text='Гранд смета 2023.1.0', default=False, key="grand_smeta13_1_0"),
         sg.Checkbox(text='Гранд смета 2023.1.1', default=False, key="grand_smeta13_1_1"),
         sg.Checkbox(text='Гранд смета 2023.1.2', default=False, key="grand_smeta13_1_2"),
         sg.Checkbox(text='Гранд смета 2023.1.3', default=False, key="grand_smeta13_1_3")],

        [
         sg.Checkbox(text='Гранд смета 2023.2.0', default=False, key="grand_smeta13_2_0"),
         sg.Checkbox(text='Гранд смета 2023.2.1', default=False, key="grand_smeta13_2_1"),
         sg.Checkbox(text='Гранд смета 2023.2.2', default=False, key="grand_smeta13_2_2"),
         sg.Checkbox(text='Гранд смета 2023.2.3', default=False, key="grand_smeta13_2_3"),
         sg.Checkbox(text='Гранд смета 2023.2.4', default=False, key="grand_smeta13_2_4")],

        [sg.Checkbox(text='Гранд смета 2023.3.0', default=False, key='grand_smeta13_3_0')],

        # [sg.Checkbox(text='Яндекс Диск', default=False, key='yadisk')],
        [sg.Checkbox(text='Лицензии', default=False, key='lic')],
        [sg.Text('Путь для лицензий:'), sg.InputText(), sg.FolderBrowse(button_text='Выбрать',
                                                                        key='path_save_lic')],
        [
            sg.Text('Загрузка:'),
            sg.ProgressBar(max_value=100, orientation='h', size=(20, 20), key='progress_1',
                           style='winnative', border_width=1, visible=True)
         ],
        [sg.Output(size=(60, 2))],
        [sg.Submit(button_text='Загрузить'), sg.CloseButton(button_text='Закрыть')],
    ]

    window = sg.Window('Менеджер загрузок', field_two, icon='icon.ico', finalize=True)
    log.debug('Открыто окно менеджера загрузок')

    while key:
        downloader = 0
        event, values = window.read()
        window['progress_1'].update(downloader)
        if event in (None, 'Exit', 'Cancel'):
            log.debug('Выход')
            return

        if not os.path.exists('Download'):
            os.mkdir('Download')

        flag_yadisk = values.get('yadisk')
        if flag_yadisk:
            log.info('Загружается с яндекс диска')
            token = 'y0_AgAAAABaMOijAAlKtgAAAADetvbzbJVgeUqxQke0TgdLdkV4W5gD318'
            disk = YaDisk(token=token)
        else:
            log.info('Загружается с сайта www.grandsmeta.ru')

        dict_files = {app: value for app, value in dict_files_all.items() if values.get(app)}
        download_score_max = sum(dict_files.values())
        window['progress_1'].update(current_count=0, max=download_score_max)
        start = time()

        # Гранд Смета 2023.3.0
        if values.get('grand_smeta13_3_0'):
            count = dict_files["grand_smeta13_3_0"]
            print('Загрузка дистрибутива Гранд Смета 2023.3.0')
            log.debug('Загрузка дистрибутива Гранд Смета 2023.3.0')
            window.refresh()
            try:
                grand_smeta13_3_0(headers=headers)
                log.debug(f"Загружен дистрибутив Гранд Смета 2023.3.0")
            except (Exception, UnavailableError):
                log.error(f"Не удалось загрузить дистрибутив Гранд Смета 2023.3.0 {format_exc()}")
            finally:
                downloader += count
                window['progress_1'].update(downloader)

        # Гранд Смета 2023.2.4
        if values.get('grand_smeta13_2_4'):
            count = dict_files["grand_smeta13_2_4"]
            print('Загрузка дистрибутива Гранд Смета 2023.2.4')
            log.debug('Загрузка дистрибутива Гранд Смета 2023.2.4')
            window.refresh()
            try:
                if flag_yadisk:
                    grand_smeta13_2_4_yadisk(disk=disk)
                else:
                    grand_smeta13_2_4(headers=headers)
                log.debug(f"Загружен дистрибутив Гранд Смета 2023.2.4")
            except (Exception, UnavailableError):
                log.error(f"Не удалось загрузить дистрибутив Гранд Смета 2023.2.4 {format_exc()}")
            finally:
                downloader += count
                window['progress_1'].update(downloader)

        # Гранд Смета 2023.2.3
        if values.get('grand_smeta13_2_3'):
            count = dict_files["grand_smeta13_2_3"]
            print('Загрузка дистрибутива Гранд Смета 2023.2.3')
            log.debug('Загрузка дистрибутива Гранд Смета 2023.2.3')
            window.refresh()
            try:
                if flag_yadisk:
                    grand_smeta13_2_3_yadisk(disk=disk)
                else:
                    grand_smeta13_2_3(headers=headers)
                log.debug(f"Загружен дистрибутив Гранд Смета 2023.2.3")
            except (Exception, UnavailableError):
                log.error(f"Не удалось загрузить дистрибутив Гранд Смета 2023.2.3 {format_exc()}")
            finally:
                downloader += count
                window['progress_1'].update(downloader)

        # Гранд Смета 2023.2.2
        if values.get('grand_smeta13_2_2'):
            count = dict_files["grand_smeta13_2_2"]
            print('Загрузка дистрибутива Гранд Смета 2023.2.2')
            log.debug('Загрузка дистрибутива Гранд Смета 2023.2.2')
            window.refresh()
            try:
                if flag_yadisk:
                    grand_smeta13_2_2_yadisk(disk=disk)
                else:
                    grand_smeta13_2_2(headers=headers)
                log.debug(f"Загружен дистрибутив Гранд Смета 2023.2.2")
            except (Exception, UnavailableError):
                log.error(f"Не удалось загрузить дистрибутив Гранд Смета 2023.2.2 {format_exc()}")
            finally:
                downloader += count
                window['progress_1'].update(downloader)

        # Гранд Смета 2023.2.1
        if values.get('grand_smeta13_2_1'):
            count = dict_files["grand_smeta13_2_1"]
            print('Загрузка дистрибутива Гранд Смета 2023.2.1')
            log.debug('Загрузка дистрибутива Гранд Смета 2023.2.1')
            window.refresh()
            try:
                if flag_yadisk:
                    grand_smeta13_2_1_yadisk(disk=disk)
                else:
                    grand_smeta13_2_1(headers=headers)
                log.debug(f"Загружен дистрибутив Гранд Смета 2023.2.1")
            except (Exception, UnavailableError):
                log.error(f"Не удалось загрузить дистрибутив Гранд Смета 2023.2.1 {format_exc()}")
            finally:
                downloader += count
                window['progress_1'].update(downloader)

        # Гранд Смета 2023.2.0
        if values.get('grand_smeta13_2_0'):
            count = dict_files["grand_smeta13_2_0"]
            print('Загрузка дистрибутива Гранд Смета 2023.2.0')
            log.debug('Загрузка дистрибутива Гранд Смета 2023.2.0')
            window.refresh()
            try:
                if flag_yadisk:
                    grand_smeta13_2_0_yadisk(disk=disk)
                else:
                    grand_smeta13_2_0(headers=headers)
                log.debug(f"Загружен дистрибутив Гранд Смета 2023.2.0")
            except (Exception, UnavailableError):
                log.error(f"Не удалось загрузить дистрибутив Гранд Смета 2023.2.0 {format_exc()}")
            finally:
                downloader += count
                window['progress_1'].update(downloader)

        # Гранд Смета 2023.1.3
        if values.get('grand_smeta13_1_3'):
            count = dict_files["grand_smeta13_1_3"]
            print('Загрузка дистрибутива Гранд Смета 2023.1.3')
            log.debug('Загрузка дистрибутива Гранд Смета 2023.1.3')
            window.refresh()
            try:
                if flag_yadisk:
                    grand_smeta13_1_3_yadisk(disk=disk)
                else:
                    grand_smeta13_1_3(headers=headers)
                log.debug(f"Загружен дистрибутив Гранд Смета 2023.1.3")
            except (Exception, UnavailableError):
                log.error(f"Не удалось загрузить дистрибутив Гранд Смета 2023.1.3 {format_exc()}")
            finally:
                downloader += count
                window['progress_1'].update(downloader)

        # Гранд Смета 2023.1.2
        if values.get('grand_smeta13_1_2'):
            count = dict_files["grand_smeta13_1_2"]
            print('Загрузка дистрибутива Гранд Смета 2023.1.2')
            log.debug('Загрузка дистрибутива Гранд Смета 2023.1.2')
            window.refresh()
            try:
                if flag_yadisk:
                    grand_smeta13_1_2_yadisk(disk=disk)
                else:
                    grand_smeta13_1_2(headers=headers)
                log.debug(f"Загружен дистрибутив Гранд Смета 2023.1.2")
            except (Exception, UnavailableError):
                log.error(f"Не удалось загрузить дистрибутив Гранд Смета 2023.1.2 {format_exc()}")
            finally:
                downloader += count
                window['progress_1'].update(downloader)

        # Гранд Смета 2023.1.1
        if values.get('grand_smeta13_1_1'):
            count = dict_files["grand_smeta13_1_1"]
            print('Загрузка дистрибутива Гранд Смета 2023.1.1')
            log.debug('Загрузка дистрибутива Гранд Смета 2023.1.1')
            window.refresh()
            try:
                if flag_yadisk:
                    grand_smeta13_1_1_yadisk(disk=disk)
                else:
                    grand_smeta13_1_1(headers=headers)

                log.debug(f"Загружен дистрибутив Гранд Смета 2023.1.1")
            except (Exception, UnavailableError):
                log.error(f"Не удалось загрузить дистрибутив Гранд Смета 2023.1.1 {format_exc()}")
            finally:
                downloader += count
                window['progress_1'].update(downloader)

        # Гранд Смета 2023.1.0
        if values.get('grand_smeta13_1_0'):
            count = dict_files["grand_smeta13_1_0"]
            print('Загрузка дистрибутива Гранд Смета 2023.1.0')
            log.debug('Загрузка дистрибутива Гранд Смета 2023.1.0')
            window.refresh()
            try:
                if flag_yadisk:
                    grand_smeta13_1_0_yadisk(disk=disk)
                else:
                    grand_smeta13_1_0(headers=headers)
                log.debug(f"Загружен дистрибутив Гранд Смета 2023.1.0")
            except (Exception, UnavailableError):
                log.error(f"Не удалось загрузить дистрибутив Гранд Смета 2023.1.0 {format_exc()}")
            finally:
                downloader += count
                window['progress_1'].update(downloader)

        # Гранд Смета 2022.3.3
        if values.get('grand_smeta12_3_3'):
            count = dict_files["grand_smeta12_3_3"]
            print('Загрузка дистрибутива Гранд Смета 2022.3.3')
            log.debug('Загрузка дистрибутива Гранд Смета 2022.3.3')
            window.refresh()
            try:
                if flag_yadisk:
                    grand_smeta12_3_3_yadisk(disk=disk)
                else:
                    grand_smeta12_3_3(headers=headers)
                log.debug(f"Загружен дистрибутив Гранд Смета 2022.3.3")
            except (Exception, UnavailableError):
                log.error(f"Не удалось загрузить дистрибутив Гранд Смета 2022.3.3 {format_exc()}")
            finally:
                downloader += count
                window['progress_1'].update(downloader)

        # 2020
        # window['progress_1'].update(downloader)
        if values.get('base2020'):
            count = dict_files["base2020"]
            log.error('base2020')
            for number in range(count):
                name = f"0{number}" if number < 10 else f"{number}"
                print(f'Загрузка файла NB1080{name}.zip')
                log.debug(f'Загрузка файла NB1080{name}.zip')
                window.refresh()
                try:
                    if flag_yadisk:
                        base2020_yadisk(number=name, disk=disk, path=values.get('path_save_base'))
                    else:
                        base2020(number=name, headers=headers, path=values.get('path_save_base'))
                    log.debug(f"Загружен NB1080{number}")
                except (Exception, UnavailableError):
                    log.error(f"Не удалось загрузить NB1080{number} {format_exc()}")
                finally:
                    downloader += 1
                    window['progress_1'].update(downloader)

        # 2017
        if values.get('base2017'):
            count = dict_files["base2017"]
            for number in range(count):
                print(f"Загрузка файла NB10700{number}.zip")
                log.debug(f"Загрузка файла NB10700{number}.zip")
                window.refresh()
                try:
                    if flag_yadisk:
                        base2017_yadisk(number=number, disk=disk, path=values.get('path_save_base'))
                    else:
                        base2017(number=number, headers=headers, path=values.get('path_save_base'))
                    log.debug(f"Загружен NB10700{number}")
                except (Exception, UnavailableError):
                    log.error(f"Не удалось загрузить NB10700{number} {format_exc()}")
                finally:
                    downloader += 1
                    window['progress_1'].update(downloader)

        # РТ
        if values.get('rt'):
            count = dict_files["rt"]

            for number in range(count):
                print(f"Загрузка файла NB10416{number}.zip")
                log.debug(f"Загрузка файла NB10416{number}.zip")
                window.refresh()
                try:
                    rt_yadisk(number=number, disk=disk, path=values.get('path_save_base'))
                    log.debug(f"Загружен NB10416{number}")
                except (Exception, UnavailableError):
                    log.error(f"Не удалось загрузить NB10416{number} {format_exc()}")
                finally:
                    downloader += 1
                    window['progress_1'].update(downloader)

        # 2022
        if values.get('base2022'):
            list_number = [3, 5, 6, 7]

            for number in list_number:
                print(f'Загрузка файла NB12100{number}.zip')
                log.debug(f'Загрузка файла NB12100{number}.zip')
                window.refresh()
                try:
                    if flag_yadisk:
                        base2022_yandex(number=number, disk=disk, path=values.get('path_save_base'))
                    else:
                        base2022(number=number, headers=headers, path=values.get('path_save_base'))
                    log.debug(f"Загружен NB12100{number}")
                except (Exception, UnavailableError):
                    log.error(f"Не удалось загрузить NB12100{number} {format_exc()}")
                finally:
                    downloader += 1
                    window['progress_1'].update(downloader)

        # Библиотека сметчика
        if values.get('bib_smetcica'):

            all_number = ['01', '10', '11', '15', '16',
                          '20', '30', '40', '60', '61',
                          '65', '70', '80']

            for number in all_number:
                print(f'Загрузка файла NB1120{number}.zip')
                log.debug(f'Загрузка файла NB1120{number}.zip')
                window.refresh()
                try:
                    if flag_yadisk:
                        bib_smetcica_yadisk(number=number,  disk=disk, path=values.get('path_save_base'))
                    else:
                        bib_smetcica(number=number, headers=headers, path=values.get('path_save_base'))
                    log.debug(f"Загружен NB1120{number}")
                except (Exception, UnavailableError):
                    log.error(f"Не удалось загрузить NB1120{number} {format_exc()}")
                finally:
                    downloader += 1
                    window['progress_1'].update(downloader)

        # 2001 2009
        if values.get('base2001_2009'):
            count = dict_files["base2001_2009"]

            for number in range(count):

                print(f'Загрузка файла NB10400{number}.zip')
                log.debug(f'Загрузка файла NB10400{number}.zip')
                window.refresh()
                try:
                    if flag_yadisk:
                        base2001_2009_yadisk(number=str(number), disk=disk, path=values.get('path_save_base'))
                    else:
                        base2001_2009(number=str(number), headers=headers, path=values.get('path_save_base'))
                    log.debug(f"Загружен NB10400{number}")
                except (Exception, UnavailableError):
                    log.error(f"Не удалось загрузить NB10400{number} {format_exc()}")
                finally:
                    downloader += 1
                    window['progress_1'].update(downloader)

        # 2001 2014
        if values.get('base2001_2014'):
            count = dict_files["base2001_2014"]
            for number in range(count):
                print(f'Загрузка файла NB10500{number}.zip')
                log.debug(f'Загрузка файла NB10500{number}.zip')
                window.refresh()
                try:
                    if flag_yadisk:
                        base2001_2014_yadisk(number=str(number), disk=disk, path=values.get('path_save_base'))
                    else:
                        base2001_2014(number=str(number), headers=headers, path=values.get('path_save_base'))
                    log.debug(f"Загружен NB10500{number}")
                except (Exception, UnavailableError):
                    log.error(f"Не удалось загрузить NB10500{number} {format_exc()}")
                finally:
                    downloader += 1
                    window['progress_1'].update(downloader)

        # Укрупненные нормативы
        if values.get("ucrup_norm"):
            count = dict_files["ucrup_norm"]
            print(f'Загрузка файла nb100009.zip')
            log.debug(f'Загрузка файла nb100009.zip')
            window.refresh()
            try:
                ucrup_norm(headers=headers, path=values.get('path_save_base'))
                log.debug(f"Загружен nb100009.zip")
            except Exception:
                log.error(f"Не удалось загрузить nb100009.zip {format_exc()}")
            finally:
                downloader += count
                window['progress_1'].update(downloader)

        # Проектно-изыскательские работы
        if values.get("pir"):
            count = dict_files["pir"]
            print(f'Загрузка файла nb110010.zip')
            log.debug(f'Загрузка файла nb110010.zip')
            window.refresh()
            try:
                pir(headers=headers, path=values.get('path_save_base'))
                log.debug(f"Загружен nb110010.zip")
            except Exception:
                log.error(f"Не удалось загрузить nb110010.zip {format_exc()}")
            finally:
                downloader += count
                window['progress_1'].update(downloader)

        # Ведомcтвенные и прочие сборники
        if values.get("ved_sbor"):
            count = dict_files["ved_sbor"]
            print(f'Загрузка файла nb100003.zip')
            log.debug(f'Загрузка файла nb100003.zip')
            window.refresh()
            try:
                if flag_yadisk:
                    ved_sbor_yadisk(disk=disk, path=values.get('path_save_base'))
                else:
                    ved_sbor(headers=headers, path=values.get('path_save_base'))
                log.debug(f"Загружен nb100003.zip")
            except (Exception, UnavailableError):
                log.error(f"Не удалось загрузить nb100003.zip {format_exc()}")
            finally:
                downloader += count
                window['progress_1'].update(downloader)

        # Лицензии
        if values.get('lic'):
            count = dict_files["lic"]
            print('Загрузка лицензий')
            log.debug('Загрузка лицензий')
            window.refresh()
            try:
                lic(path=values.get('path_save_lic'))
                log.debug(f"Загружены лицензии ")
            except Exception:
                log.error(f"Не удалось переместить лицензии {format_exc()}")
            finally:
                downloader += count
                window['progress_1'].update(downloader)

        stop = time()
        all_time = round(stop - start, 2)

        hour = int(all_time / 60 // 60)
        minutes = int(all_time // 60 - 60 * hour)
        seconds = int(round(all_time - (hour * 60 * 60 + minutes * 60), 0))

        hour = hour if hour > 9 else f"0{hour}"
        minutes = minutes if minutes > 9 else f"0{minutes}"
        seconds = seconds if seconds > 9 else f"0{seconds}"

        print(f"Готово за {hour}:{minutes}:{seconds}")
        log.debug(f"Готово за {hour}:{minutes}:{seconds}")


def ucrup_norm(headers: Dict, path: str) -> None:
    """
    Загрузка архива c официального сайта Гранд Смета www.grandsmeta.ru
    нормативной базы "Укрупненные нормативы" с распаковкой в указанную директорию path
    :param headers: Заголовок get-запроса
    :param path: Путь распаковки
    :return: None
    """
    listdir = os.listdir('Download')
    path_arh = os.path.join('Download', f"nb100009.zip")
    if f'nb100009.zip' in listdir:
        with ZipFile(path_arh) as zipp:
            zipp.extractall(path)
    else:
        url = 'https://cdn.grandsmeta.ru/ftp/grandsmeta/data/nb100009.zip'

        res = get(url=url, headers=headers)

        with open(path_arh, 'wb') as file:
            file.write(res.content)

        with ZipFile(path_arh) as zipp:
            zipp.extractall(path)


def ucrup_norm_yadisk(disk: YaDisk, path: str) -> None:
    """
    Загрузка архива c яндекс диска
    нормативной базы "Укрупненные нормативы" с распаковкой в указанную директорию path
    :param disk: Диск
    :param path: Путь распаковки
    :return: None
    """
    listdir = os.listdir('Download')
    file_or_path = os.path.join('Download', f"NB100009.zip")

    if f'NB100009.zip' in listdir:
        src_path = f'disk:/Загрузки/ГС/GRAND Смета/Базы/Прочие/NB100009.zip'
        disk.download(src_path, file_or_path)

    with ZipFile(file_or_path) as zipp:
        zipp.extractall(path)


def pir(headers: Dict, path: str) -> None:
    """
    Загрузка архива c официального сайта Гранд Смета www.grandsmeta.ru
    нормативной базы "Проектно-изыскательские работы" с распаковкой в указанную директорию path
    :param headers: Заголовок get-запроса
    :param path: Путь распаковки
    :return: None
    """
    listdir = os.listdir('Download')
    path_arh = os.path.join('Download', f"nb110010.zip")

    if f'nb110010.zip' in listdir:
        with ZipFile(path_arh) as zipp:
            zipp.extractall(path)
    else:
        url = 'https://cdn.grandsmeta.ru/ftp/grandsmeta/data/nb110010.zip'

        res = get(url=url, headers=headers)

        with open(path_arh, 'wb') as file:
            file.write(res.content)

        with ZipFile(path_arh) as zipp:
            zipp.extractall(path)


def pir_yadisk(disk: YaDisk, path: str) -> None:
    """
    Загрузка архива c яндекс диска
    нормативной базы "Проектно-изыскательские работы" с распаковкой в указанную директорию path
    :param disk: Диск
    :param path: Путь распаковки
    :return: None
    """
    listdir = os.listdir('Download')
    file_or_path = os.path.join('Download', f"NB110010.zip")

    if f'NB110010.zip' not in listdir:
        src_path = f'disk:/Загрузки/ГС/GRAND Смета/Базы/Прочие/NB110010.zip'
        disk.download(src_path, file_or_path)

    with ZipFile(file_or_path) as zipp:
        zipp.extractall(path)


def ved_sbor(headers: Dict, path: str) -> None:
    """
    Загрузка архива c официального сайта Гранд Смета www.grandsmeta.ru
    нормативной базы "Ведомственные и прочие сборники" с распаковкой в указанную директорию path
    :param headers: Заголовок get-запроса
    :param path: Путь распаковки
    :return: None
    """
    listdir = os.listdir('Download')
    path_arh = os.path.join('Download', f"nb100003.zip")

    if f'nb100003.zip' in listdir:
        with ZipFile(path_arh) as zipp:
            zipp.extractall(path)
    else:
        url = 'https://cdn.grandsmeta.ru/ftp/grandsmeta/data/nb100003.zip'

        res = get(url=url, headers=headers)

        with open(path_arh, 'wb') as file:
            file.write(res.content)

        with ZipFile(path_arh) as zipp:
            zipp.extractall(path)


def ved_sbor_yadisk(disk: YaDisk, path: str) -> None:
    """
    Загрузка архива c яндекс диска
    нормативной базы "Ведомственные и прочие сборники" с распаковкой в указанную директорию path
    :param disk: Диск
    :param path: Путь распаковки
    :return: None
    """
    listdir = os.listdir('Download')
    file_or_path = os.path.join('Download', f"nb100003.zip")

    if f'nb100003.zip' not in listdir:
        src_path = f'disk:/Загрузки/ГС/GRAND Смета/Базы/Прочие/nb100003.zip'
        disk.download(src_path, file_or_path)

    with ZipFile(file_or_path) as zipp:
        zipp.extractall(path)


def base2001_2014(number: str, headers: Dict, path: Union[str] = None) -> None:
    """
    Загрузка архива c официального сайта Гранд Смета www.grandsmeta.ru
    нормативной базы 2014 в редакции 2009 года с распаковкой в указанную директорию path
    :param number: Номер базы
    :param headers: Заголовок get-запроса
    :param path: Путь распаковки
    :return: None
    """
    listdir = os.listdir('Download')
    name = f'NB10500{number}'
    path_arh = os.path.join('Download', f"{name}.zip")
    if f'{name}.zip' in listdir:
        with ZipFile(path_arh) as zipp:
            zipp.extractall(path=path)

    else:
        url = f'https://cdn.grandsmeta.ru/ftp/grandsmeta/data/2014/{name}.zip'

        res = get(url=url, headers=headers)

        with open(path_arh, 'wb') as file:
            file.write(res.content)

        with ZipFile(path_arh) as zipp:
            zipp.extractall(path)


def base2001_2014_yadisk(number: str, disk: YaDisk, path: Union[str] = None) -> None:
    """
    Загрузка архива c яндекс диска
    нормативной базы 2001 в редакции 2014 года с распаковкой в указанную директорию path
    :param number: Номер базы
    :param disk: Диск
    :param path: Путь распаковки
    :return: None
    """
    listdir = os.listdir('Download')
    name = f'NB10500{number}.zip'
    file_or_path = os.path.join('Download', name)

    if name not in listdir:
        src_path = f'disk:/Загрузки/ГС/GRAND Смета/Базы/2001(в ред. 2014)/{name}'
        disk.download(src_path, file_or_path)

    with ZipFile(file_or_path) as zipp:
        zipp.extractall(path)


def base2001_2009(number: str, headers: Dict, path: Union[str] = None) -> None:
    """
    Загрузка архива c официального сайта Гранд Смета www.grandsmeta.ru
    нормативной базы 2001 в редакции 2009 года с распаковкой в указанную директорию path
    :param number: Номер базы
    :param headers: Заголовок get-запроса
    :param path: Путь распаковки
    :return: None
    """
    listdir = os.listdir('Download')
    name = f'NB10400{number}'
    path_arh = os.path.join('Download', f"{name}.zip")
    if f'{name}.zip' in listdir:
        with ZipFile(path_arh) as zipp:
            zipp.extractall(path=path)

    else:
        url = f'https://cdn.grandsmeta.ru/ftp/grandsmeta/data/2009/{name}.zip'

        res = get(url=url, headers=headers)

        with open(path_arh, 'wb') as file:
            file.write(res.content)

        with ZipFile(path_arh) as zipp:
            zipp.extractall(path)


def base2001_2009_yadisk(number: str, disk: YaDisk, path: Union[str] = None) -> None:
    """
    Загрузка архива c яндекс диска
    нормативной базы 2001 в редакции 2009 года с распаковкой в указанную директорию path
    :param number: Номер базы
    :param disk: Диск
    :param path: Путь распаковки
    :return: None
    """
    listdir = os.listdir('Download')
    name = f'NB10400{number}.zip'
    file_or_path = os.path.join('Download', name)

    if name not in listdir:
        src_path = f'disk:/Загрузки/ГС/GRAND Смета/Базы/2001(в ред. 2009)/{name}'
        disk.download(src_path, file_or_path)

    with ZipFile(file_or_path) as zipp:
        zipp.extractall(path)


def base2020(number: str, headers: Dict, path: Union[str] = None) -> None:
    """
    Загрузка архива c официального сайта Гранд Смета www.grandsmeta.ru
    нормативной базы 2020 с распаковкой в указанную директорию path
    :param number: Номер базы
    :param headers: Заголовок get-запроса
    :param path: Путь распаковки
    :return: None
    """
    listdir = os.listdir('Download')
    name = f'NB1080{number}'
    path_arh = os.path.join('Download', f"{name}.zip")
    if f'{name}.zip' in listdir:
        with ZipFile(path_arh) as zipp:
            zipp.extractall(path=path)

    else:
        url = f'https://ftp.grandsmeta.ru/grandsmeta/data/2020/{name}.zip'

        res = get(url=url, headers=headers)

        with open(path_arh, 'wb') as file:
            file.write(res.content)

        with ZipFile(path_arh) as zipp:
            zipp.extractall(path)


def base2020_yadisk(number: str, disk: YaDisk, path: Union[str] = None) -> None:
    """
    Загрузка архива c яндекс диска
    нормативной базы 2020 с распаковкой в указанную директорию path
    :param number: Номер базы
    :param disk: Диск
    :param path: Путь распаковки
    :return: None
    """
    listdir = os.listdir('Download')
    name = f'NB1080{number}.zip'
    file_or_path = os.path.join('Download', name)

    if name not in listdir:
        src_path = f'disk:/Загрузки/ГС/GRAND Смета/Базы/2020/{name}'
        disk.download(src_path, file_or_path)

    with ZipFile(file_or_path) as zipp:
        zipp.extractall(path)


def base2022(number: int, headers: Dict, path: str) -> None:
    """
    Загрузка архива c официального сайта Гранд Смета www.grandsmeta.ru
    нормативной базы 2022 с распаковкой в указанную директорию path
    :param number: Номер базы
    :param headers: Заголовок get-запроса
    :param path: Путь распаковки
    :return: None
    """
    listdir = os.listdir('Download')

    name = f'NB12100{number}'
    path_arh = os.path.join('Download', f"{name}.zip")

    if f'{name}.zip' in listdir:
        with ZipFile(path_arh) as zipp:
            zipp.extractall(path)
    else:
        url = f'https://cdn.grandsmeta.ru/ftp/grandsmeta/data/2022/{name}.zip'

        res = get(url=url, headers=headers)

        with open(path_arh, 'wb') as file:
            file.write(res.content)

        with ZipFile(path_arh) as zipp:
            zipp.extractall(path)


def base2022_yandex(number: int, disk: YaDisk, path: str) -> None:
    """
    Загрузка архива c яндекс диска
    нормативной базы 2022 с распаковкой в указанную директорию path
    :param number: Номер базы
    :param disk: Диск
    :param path: Путь распаковки
    :return: None
    """
    listdir = os.listdir('Download')

    name = f'NB12100{number}.zip'
    file_or_path = os.path.join('Download', name)

    if name not in listdir:
        src_path = f'disk:/Загрузки/ГС/GRAND Смета/Базы/2022/{name}'
        disk.download(src_path, file_or_path)

    with ZipFile(file_or_path) as zipp:
        zipp.extractall(path)


def bib_smetcica(number: int, headers: Dict, path: Union[str] = None) -> None:
    """
    Загрузка архива c официального сайта Гранд Смета www.grandsmeta.ru
    нормативной базы библиотеки сметчика с распаковкой в указанную директорию path
    :param number: Номер базы
    :param headers: Заголовок get-запроса
    :param path: Путь распаковки
    :return: None
    """
    listdir = os.listdir('Download')
    path_arh = os.path.join('Download', f"NB1120{number}.zip")

    if f'NB1120{number}.zip' in listdir:
        with ZipFile(path_arh) as zipp:
            zipp.extractall(path)
    else:
        url = f'https://ftp.grandsmeta.ru/grandsmeta/data/si/NB1120{number}.zip'

        res = get(url=url, headers=headers)

        with open(path_arh, 'wb') as file:
            file.write(res.content)

        with ZipFile(path_arh) as zipp:
            zipp.extractall(path)

    print(f'Файл NB1120{number}.zip загружен')


def bib_smetcica_yadisk(number: int, disk: YaDisk, path: Union[str] = None) -> None:
    """
    Загрузка архива c яндекс диска
    нормативной базы библиотеки сметчика с распаковкой в указанную директорию path
    :param number: Номер базы
    :param disk: Диск
    :param path: Путь распаковки
    :return: None
    """
    listdir = os.listdir('Download')
    file_or_path = os.path.join('Download', f"NB1120{number}.zip")

    if f'NB1120{number}.zip' not in listdir:
        src_path = f'disk:/Загрузки/ГС/GRAND Смета/Базы/Библиотека сметчика/NB1120{number}.zip'
        disk.download(src_path, file_or_path)

    with ZipFile(file_or_path) as zipp:
        zipp.extractall(path)


def base2017(number: int, headers: Dict, path: str) -> None:
    """
    Загрузка архива c официального сайта Гранд Смета www.grandsmeta.ru
    нормативной базы 2017 с распаковкой в указанную директорию path
    :param number: Номер базы
    :param headers: Заголовок get-запроса
    :param path: Путь распаковки
    :return: None
    """
    listdir = os.listdir('Download')
    path_arh = os.path.join('Download', f"NB10700{number}.zip")

    if f'NB10700{number}.zip' in listdir:
        with ZipFile(path_arh) as zipp:
            zipp.extractall(path)

    else:
        url = f'https://ftp.grandsmeta.ru/grandsmeta/data/2017/nb10700{number}.zip'
        res = get(url=url, headers=headers)

        with open(path_arh, 'wb') as file:
            file.write(res.content)

        with ZipFile(path_arh) as zipp:
            zipp.extractall(path)


def base2017_yadisk(number: int, disk: YaDisk, path: str) -> None:
    """
    Загрузка архива c яндекс диска
    нормативной базы 2017 с распаковкой в указанную директорию path
    :param number: Номер базы
    :param disk: Диск
    :param path: Путь распаковки
    :return: None
    """
    listdir = os.listdir('Download')
    file_or_path = os.path.join('Download', f"NB10700{number}.zip")

    if f'NB10700{number}.zip' not in listdir:
        src_path = f'disk:/Загрузки/ГС/GRAND Смета/Базы/2017/NB10700{number}.zip'
        disk.download(src_path, file_or_path)

    with ZipFile(file_or_path) as zipp:
        zipp.extractall(path)

    print(f"Файл NB10700{number}.zip установлен")


def rt_yadisk(number: int, disk: YaDisk, path: str):
    """
    Загрузка архива c яндекс диска
    нормативной базы РТ с распаковкой в указанную директорию path
    :param number: Номер базы
    :param disk: Диск
    :param path: Путь распаковки
    :return: None
    """
    listdir = os.listdir('Download')
    file_or_path = os.path.join('Download', f"NB10416{number}.zip")

    if f'NB10416{number}.zip' not in listdir:
        src_path = f'disk:/Загрузки/ГС/GRAND Смета/Базы/РТ/NB10416{number}.zip'
        disk.download(src_path, file_or_path)

    with ZipFile(file_or_path) as zipp:
        zipp.extractall(path)

    print(f"Файл NB10416{number}.zip установлен")


def grand_smeta13_1_3(headers: Dict) -> None:
    """
    Загружает c официального сайта Гранд Смета www.grandsmeta.ru
    и распаковываем дистрибутив программы Гранд Смета 2023.1.2 в директорию Download
    :param headers: Заголовок get-запроса
    :return: None
    """

    url = 'https://cdn.grandsmeta.ru/ftp/grandsmeta/distrib/smeta2023.1.3.zip'
    res = get(url=url, headers=headers)
    path_arh = os.path.join('Download', "smeta2023.1.3.zip")
    with open(path_arh, 'wb') as file:
        file.write(res.content)

    with ZipFile(path_arh) as zipp:
        zipp.extractall('Download')


def grand_smeta13_1_3_yadisk(disk: YaDisk) -> None:
    """
    Загружает c яндекс диска
    и распаковываем дистрибутив программы Гранд Смета 2023.1.3 в директорию Download
    :param disk: Диск
    :return: None
    """

    src_path = 'disk:/Загрузки/ГС/GRAND Смета/Дистрибутивы/smeta2023.1.3.zip'
    file_or_path = os.path.join('Download', "smeta2023.1.3.zip")
    disk.download(src_path, file_or_path)

    with ZipFile(file_or_path) as zipp:
        zipp.extractall('Download')


def grand_smeta13_1_2(headers: Dict) -> None:
    """
    Загружает c официального сайта Гранд Смета www.grandsmeta.ru
    и распаковываем дистрибутив программы Гранд Смета 2023.1.2 в директорию Download
    :param headers: Заголовок get-запроса
    :return: None
    """

    url = 'https://cdn.grandsmeta.ru/ftp/grandsmeta/distrib/smeta2023.1.2.zip'
    res = get(url=url, headers=headers)
    path_arh = os.path.join('Download', "smeta2023.1.2.zip")
    with open(path_arh, 'wb') as file:
        file.write(res.content)

    with ZipFile(path_arh) as zipp:
        zipp.extractall('Download')


def grand_smeta13_1_2_yadisk(disk: YaDisk) -> None:
    """
    Загружает c яндекс диска
    и распаковываем дистрибутив программы Гранд Смета 2023.1.2 в директорию Download
    :param disk: Диск
    :return: None
    """

    src_path = 'disk:/Загрузки/ГС/GRAND Смета/Дистрибутивы/smeta2023.1.2.zip'
    file_or_path = os.path.join('Download', "smeta2023.1.2.zip")
    disk.download(src_path, file_or_path)

    with ZipFile(file_or_path) as zipp:
        zipp.extractall('Download')


def grand_smeta13_3_0(headers: Dict) -> None:
    """
    Загружает c официального сайта Гранд Смета www.grandsmeta.ru
    и распаковываем дистрибутив программы Гранд Смета 2023.3.0 в директорию Download
    :param headers: Заголовок get-запроса
    :return: None
    """

    url = 'https://cdn.grandsmeta.ru/ftp/grandsmeta/distrib/smeta2023.3.0.zip'
    res = get(url=url, headers=headers)
    path_arh = os.path.join('Download', "smeta2023.3.0.zip")
    with open(path_arh, 'wb') as file:
        file.write(res.content)

    with ZipFile(path_arh) as zipp:
        zipp.extractall('Download')


def grand_smeta13_2_4(headers: Dict) -> None:
    """
    Загружает c официального сайта Гранд Смета www.grandsmeta.ru
    и распаковываем дистрибутив программы Гранд Смета 2023.2.4 в директорию Download
    :param headers: Заголовок get-запроса
    :return: None
    """

    url = 'https://cdn.grandsmeta.ru/ftp/grandsmeta/distrib/smeta2023.2.4.zip'
    res = get(url=url, headers=headers)
    path_arh = os.path.join('Download', "smeta2023.2.4.zip")
    with open(path_arh, 'wb') as file:
        file.write(res.content)

    with ZipFile(path_arh) as zipp:
        zipp.extractall('Download')


def grand_smeta13_2_4_yadisk(disk: YaDisk) -> None:
    """
    Загружает c яндекс диска
    и распаковываем дистрибутив программы Гранд Смета 2023.2.4 в директорию Download
    :param disk: Диск
    :return: None
    """

    src_path = 'disk:/Загрузки/ГС/GRAND Смета/Дистрибутивы/smeta2023.2.4.zip'
    file_or_path = os.path.join('Download', "smeta2023.2.4.zip")
    disk.download(src_path, file_or_path)

    with ZipFile(file_or_path) as zipp:
        zipp.extractall('Download')


def grand_smeta13_2_3(headers: Dict) -> None:
    """
    Загружает c официального сайта Гранд Смета www.grandsmeta.ru
    и распаковываем дистрибутив программы Гранд Смета 2023.2.3 в директорию Download
    :param headers: Заголовок get-запроса
    :return: None
    """

    url = 'https://cdn.grandsmeta.ru/ftp/grandsmeta/distrib/smeta2023.2.3.zip'
    res = get(url=url, headers=headers)
    path_arh = os.path.join('Download', "smeta2023.2.3.zip")
    with open(path_arh, 'wb') as file:
        file.write(res.content)

    with ZipFile(path_arh) as zipp:
        zipp.extractall('Download')


def grand_smeta13_2_3_yadisk(disk: YaDisk) -> None:
    """
    Загружает c яндекс диска
    и распаковываем дистрибутив программы Гранд Смета 2023.2.3 в директорию Download
    :param disk: Диск
    :return: None
    """

    src_path = 'disk:/Загрузки/ГС/GRAND Смета/Дистрибутивы/smeta2023.2.3.zip'
    file_or_path = os.path.join('Download', "smeta2023.2.3.zip")
    disk.download(src_path, file_or_path)

    with ZipFile(file_or_path) as zipp:
        zipp.extractall('Download')


def grand_smeta13_2_2(headers: Dict) -> None:
    """
    Загружает c официального сайта Гранд Смета www.grandsmeta.ru
    и распаковываем дистрибутив программы Гранд Смета 2023.2.2 в директорию Download
    :param headers: Заголовок get-запроса
    :return: None
    """

    url = 'https://cdn.grandsmeta.ru/ftp/grandsmeta/distrib/smeta2023.2.2.zip'
    res = get(url=url, headers=headers)
    path_arh = os.path.join('Download', "smeta2023.2.2.zip")
    with open(path_arh, 'wb') as file:
        file.write(res.content)

    with ZipFile(path_arh) as zipp:
        zipp.extractall('Download')


def grand_smeta13_2_2_yadisk(disk: YaDisk) -> None:
    """
    Загружает c яндекс диска
    и распаковываем дистрибутив программы Гранд Смета 2023.2.2 в директорию Download
    :param disk: Диск
    :return: None
    """

    src_path = 'disk:/Загрузки/ГС/GRAND Смета/Дистрибутивы/smeta2023.2.2.zip'
    file_or_path = os.path.join('Download', "smeta2023.2.2.zip")
    disk.download(src_path, file_or_path)

    with ZipFile(file_or_path) as zipp:
        zipp.extractall('Download')


def grand_smeta13_2_1(headers: Dict) -> None:
    """
    Загружает c официального сайта Гранд Смета www.grandsmeta.ru
    и распаковываем дистрибутив программы Гранд Смета 2023.2.1 в директорию Download
    :param headers: Заголовок get-запроса
    :return: None
    """

    url = 'https://cdn.grandsmeta.ru/ftp/grandsmeta/distrib/smeta2023.2.1.zip'
    res = get(url=url, headers=headers)
    path_arh = os.path.join('Download', "smeta2023.2.1.zip")
    with open(path_arh, 'wb') as file:
        file.write(res.content)

    with ZipFile(path_arh) as zipp:
        zipp.extractall('Download')


def grand_smeta13_2_1_yadisk(disk: YaDisk) -> None:
    """
    Загружает c яндекс диска
    и распаковываем дистрибутив программы Гранд Смета 2023.2.1 в директорию Download
    :param disk: Диск
    :return: None
    """

    src_path = 'disk:/Загрузки/ГС/GRAND Смета/Дистрибутивы/smeta2023.2.1.zip'
    file_or_path = os.path.join('Download', "smeta2023.2.1.zip")
    disk.download(src_path, file_or_path)

    with ZipFile(file_or_path) as zipp:
        zipp.extractall('Download')


def grand_smeta13_2_0(headers: Dict) -> None:
    """
    Загружает c официального сайта Гранд Смета www.grandsmeta.ru
    и распаковываем дистрибутив программы Гранд Смета 2023.2.0 в директорию Download
    :param headers: Заголовок get-запроса
    :return: None
    """

    url = 'https://cdn.grandsmeta.ru/ftp/grandsmeta/distrib/smeta2023.2.0.zip'
    res = get(url=url, headers=headers)
    path_arh = os.path.join('Download', "smeta2023.2.0.zip")
    with open(path_arh, 'wb') as file:
        file.write(res.content)

    with ZipFile(path_arh) as zipp:
        zipp.extractall('Download')


def grand_smeta13_2_0_yadisk(disk: YaDisk) -> None:
    """
    Загружает c яндекс диска
    и распаковываем дистрибутив программы Гранд Смета 2023.2.0 в директорию Download
    :param disk: Диск
    :return: None
    """

    src_path = 'disk:/Загрузки/ГС/GRAND Смета/Дистрибутивы/smeta2023.2.0.zip'
    file_or_path = os.path.join('Download', "smeta2023.2.0.zip")
    disk.download(src_path, file_or_path)

    with ZipFile(file_or_path) as zipp:
        zipp.extractall('Download')


def grand_smeta13_1_1(headers: Dict) -> None:
    """
    Загружает c официального сайта Гранд Смета www.grandsmeta.ru
    и распаковываем дистрибутив программы Гранд Смета 2023.1.1 в директорию Download
    :param headers: Заголовок get-запроса
    :return: None
    """

    url = 'https://cdn.grandsmeta.ru/ftp/grandsmeta/distrib/smeta2023.1.1.zip'
    res = get(url=url, headers=headers)
    path_arh = os.path.join('Download', "smeta2023.1.1.zip")
    with open(path_arh, 'wb') as file:
        file.write(res.content)

    with ZipFile(path_arh) as zipp:
        zipp.extractall('Download')


def grand_smeta13_1_1_yadisk(disk: YaDisk) -> None:
    """
    Загружает c яндекс диска
    и распаковываем дистрибутив программы Гранд Смета 2023.1.1 в директорию Download
    :param disk: Диск
    :return: None
    """

    src_path = 'disk:/Загрузки/ГС/GRAND Смета/Дистрибутивы/smeta2023.1.1.zip'
    file_or_path = os.path.join('Download', "smeta2023.1.1.zip")
    disk.download(src_path, file_or_path)

    with ZipFile(file_or_path) as zipp:
        zipp.extractall('Download')


def grand_smeta13_1_0(headers: Dict) -> None:
    """
    Загружает c официального сайта Гранд Смета www.grandsmeta.ru
    и распаковываем дистрибутив программы Гранд Смета 2023.1.0 в директорию Download
    :param headers: Заголовок get-запроса
    :return: None
    """

    url = 'https://cdn.grandsmeta.ru/ftp/grandsmeta/distrib/smeta2023.1.0.zip'
    res = get(url=url, headers=headers)
    path_arh = os.path.join('Download', "smeta2023.1.0.zip")
    with open(path_arh, 'wb') as file:
        file.write(res.content)

    with ZipFile(path_arh) as zipp:
        zipp.extractall('Download')


def grand_smeta13_1_0_yadisk(disk: YaDisk) -> None:
    """
    Загружает c яндекс диска
    и распаковываем дистрибутив программы Гранд Смета 2023.1.0 в директорию Download
    :param disk: Диск
    :return: None
    """

    src_path = 'disk:/Загрузки/ГС/GRAND Смета/Дистрибутивы/smeta2023.1.0.zip'
    file_or_path = os.path.join('Download', "smeta2023.1.0.zip")
    disk.download(src_path, file_or_path)

    with ZipFile(file_or_path) as zipp:
        zipp.extractall('Download')


def grand_smeta12_3_3(headers: Dict) -> None:
    """
    Загружает c официального сайта Гранд Смета www.grandsmeta.ru
    и распаковываем дистрибутив программы Гранд Смета 2022.3.3 в директорию Download
    :param headers: Заголовок get-запроса
    :return: None
    """

    url = 'https://cdn.grandsmeta.ru/ftp/grandsmeta/distrib/smeta2022.3.3.zip'
    res = get(url=url, headers=headers)
    path_arh = os.path.join('Download', "smeta2022.3.3.zip")
    with open(path_arh, 'wb') as file:
        file.write(res.content)

    with ZipFile(path_arh) as zipp:
        zipp.extractall('Download')


def grand_smeta12_3_3_yadisk(disk: YaDisk) -> None:
    """
    Загружает c яндекс диска
    и распаковываем дистрибутив программы Гранд Смета 2022.3.3 в директорию Download
    :param disk: Диск
    :return: None
    """

    src_path = 'disk:/Загрузки/ГС/GRAND Смета/Дистрибутивы/smeta2022.3.3.zip'
    file_or_path = os.path.join('Download', "smeta2022.3.3.zip")
    disk.download(src_path, file_or_path)

    with ZipFile(file_or_path) as zipp:
        zipp.extractall('Download')


def lic(path: str) -> None:
    """
    Перемещает все файлы в директории Лицензии с расширением .lic в указанный путь
    :param path: Путь перемещения
    :return: None
    """
    listdir = os.listdir('Лицензии')
    for file in listdir:
        if file.endswith('.lic'):
            log.debug(path)
            log.debug(file)
            move(os.path.join('Лицензии', file), os.path.join(path, file))


if __name__ == '__main__':
    gui()
