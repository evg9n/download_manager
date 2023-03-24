from PyInstaller.__main__ import run
from os import rename, path, remove
from shutil import rmtree


def py_to_exe(path_file: str, new_name_file: str = None, path_icon: str = ''):
    """
    Конвертирует один файл скрипта python в exe с выводом графического окна,
    данный скрипт должен находиться в одной директории с конвертируемым файлом и файлом иконки
    :param path_file: путь к конвертируемому файлу
    :param new_name_file: новое имя файла без расширения
    :param path_icon: путь к иконке
    :return:
    """
    path_dir, name_file = path.split(path_file)
    name_file_exe = name_file[:len(name_file) - 3] + '.exe'
    name_file_spec = name_file[:len(name_file) - 3] + '.spec'
    if new_name_file is None:
        new_name_file = path.join(path_dir, name_file_exe)
    else:
        new_name_file = path.join(path_dir, f'{new_name_file}.exe')

    run([
        path_file,
        '--noconfirm',
        '--onefile',
        '--windowed',
        f'--icon={path_icon}'
    ])

    rename(path.join('dist', name_file_exe), new_name_file)
    rmtree('dist')
    rmtree('build')
    remove(name_file_spec)


if __name__ == '__main__':
    py_to_exe(path_file=r'main1.py',
              new_name_file='m',
              path_icon=r'icon.ico')
