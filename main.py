#  https://github.com/netology-code/py-diplom-basic
#  Нужно написать программу для резервного копирования фотографий с профиля(аватарок) пользователя vk в облачное хранилище
#  Яндекс.Диск.
#  Для названий фотографий использовать количество лайков, если количество лайков одинаково, то добавить дату загрузки.
#  Информацию по сохраненным фотографиям сохранить в json-файл.
#  ------------------Задание по пунктам -----------------------------------------------------------
#  1. Получать фотографии с профиля. Для этого нужно использовать метод  photos.get(https://vk.com/dev/photos.get).
#  2. Сохранять фотографии максимального размера(ширина/высота в пикселях) на Я.Диске.
#  3. Для имени фотографий использовать количество лайков.
#  4. Сохранять информацию по фотографиям в json-файл с результатами.

'''
 Входные данные

Пользователь вводит:

1. id пользователя vk;
2. токен с Полигона Яндекс.Диска.
Важно: Токен публиковать в github не нужно!

# Выходные данные:

1. json-файл с информацией по файлу:
    [{
    "file_name": "34.jpg",
    "size": "z"
    }]

2.Измененный Я.диск, куда добавились фотографии.'''

# Обязательные требования к программе:
# 1. Использовать REST API Я.Диска и ключ, полученный с полигона.
# 2. Для загруженных фотографий нужно создать свою папку.
# 3. Сохранять указанное количество фотографий(по умолчанию 5) наибольшего размера (ширина/высота в пикселях) на Я.Диске
# 4. Сделать прогресс-бар или логирование для отслеживания процесса программы.
# 5. Код программы должен удовлетворять PEP8.

# Необязательные требования к программе:

# 1. Сохранять фотографии и из других альбомов.
# 2. Сохранять фотографии из других социальных сетей. Одноклассники и Инстаграмм
# 3. Сохранять фотографии на Google.Drive.


import copy
import json
import os
from urllib.parse import urlparse
# from pprint import pprint
import requests


#  класс yandex по работе с api
class YaUploader:
    def __init__(self, token: str, ya_folder: str):
        self.token = token
        self.y_directory = ya_folder
        self.create_dir_y()

    def get_headers(self):
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'OAuth {}'.format(self.token)
                   }
        return headers

    def create_dir_y(self):
        """Метод создает новую папку на яндекс диске"""
        _url = 'https://cloud-api.yandex.net/v1/disk/resources'
        headers = self.get_headers()
        params = {
            'path': self.y_directory,
            'overwrite': 'true'
        }
        response = requests.put(_url, headers=headers, params=params)
        if response.status_code != 201:
            print(f'Папка с именем: {self.y_directory} уже существует!')
        else:
            print(f'Папка: {self.y_directory} создана на Yandex disc')

    def upload_file_y(self, file_path: str, url):
        """Метод загружает файл file_path на яндекс диск"""
        up_url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        headers = self.get_headers()
        params = {'url': url, 'path': file_path}
        response = requests.post(up_url, headers=headers, params=params)
        response.raise_for_status()
        if response.status_code == 202:
            print(f'File uploaded to Yandex Disk')


#  класс VK по работе с api
class VK:
    def __init__(self, _vk_id: int, token: str, version: float,  count: int):
        self.token = token
        self.vk = _vk_id  # id пользователя vk
        self.v = version  # версия api vk

        self.count = count  # количество фоток по умолчанию 5

    #     Получить фотографии с профиля vk.
    def get_photos_vk(self):
        link_vk = 'https://api.vk.com/method/photos.get'
        params = {'owner_id': self.vk,
                  'access_token': self.token,
                  'album_id': 'profile',
                  'photo_sizes': 1,
                  'count': 5,
                  'extended': 1,
                  'feed_type': "likes",
                  'v': self.v,
                  }
        photos_vk = requests.get(link_vk, params=params)
        if photos_vk.status_code != 200:
            print('Ошибка')
        else:
            return photos_vk.json()

    @staticmethod
    def clear_data_and_save_json(self, dict_data):
        #  Создаем папку с названием альбома
        if not os.path.exists('saved'):
            os.mkdir('saved')
        photo_folder = 'saved/album{0}'.format(self.vk)
        if not os.path.exists(photo_folder):
            os.mkdir(photo_folder)
        # Переходим в неё
        os.chdir(photo_folder)
        # Добавляю путь к локальный файлам.
        prep_dict = {'path_local': photo_folder}
        dict_data.append(prep_dict)
        # Копируем данные
        urls_dict = copy.deepcopy(dict_data)
        # Убираем url, file_name_real_name из выходных данных:
        for i in dict_data:
            if 'url' in i and \
                    'file_name_real_name' in i:
                del i["url"]
                del i["file_name_real_name"]
        # Сохраняем в лог файл на диск
        with open('photos_log.json', 'w') as file:
            json.dump(dict_data, file, indent=2, ensure_ascii=False)

        return urls_dict

    def logging_vk(self, answer):
        count = 1
        # Обработка ответа от VK
        ll = answer['response']['items']
        photo_lst = []
        print("Download from VK. Please wait...")
        for item in ll:
            if count < self.count:
                photo_dict = {}

                # выбираем тип фото z
                for i in item['sizes']:
                    if i['type'] == 'z':
                        # Формируем название файла фото по кол-ву лайков
                        photo_dict['file_name'] = str(item['likes']['count']) + '.jpg'
                        photo_dict['size'] = i['type']
                        #  Показывать пользователю в консоли для лога
                        photo_dict['file_name_real_name'] = os.path.basename(urlparse(i['url']).path)
                        photo_dict['url'] = i['url']
                        print(f'{count}, photo {photo_dict["file_name_real_name"]}, from {photo_dict["url"]}')
                        count += 1
                    else:
                        continue
                    photo_lst.append(photo_dict)
        print(f'Downloaded from VK profile.\n'
              f'For more information see  "photos_log.json"')
        return photo_lst


if __name__ == '__main__':
    print('input data and press enter'.upper())
    TOKEN_Y = input(f"Input token from Yandex.Disk Polygon: ")
    vk_id = int(input("Input vk user id: "))
    vk_token = str(input(f"Input token VK: "))
    print('--------------------------------------------')
    vk_v = 5.89
    # vk_v = 5.130   #  Current version
    count_photos = 5  # Количество скаченных фото по умолчанию

    # Инициализация класс VK -> v_obj
    v_obj = VK(_vk_id=vk_id, token=vk_token, version=vk_v, count=count_photos)

    # Получили данные из профиля VK пользователя
    data = v_obj.get_photos_vk()

    # Логирование + обработка
    full_logs = v_obj.logging_vk(data)

    # Сохранить фото на ПК оффлайн.
    photo_links_vk = v_obj.clear_data_and_save_json(self=v_obj, dict_data=full_logs)
    for p in photo_links_vk:
        if 'url' in p:
            rr = requests.get(p['url'])
            with open(p['file_name'], 'wb') as f:
                f.write(rr.content)
        else:
            continue
        # Сохранить фото на ПК офлайн.
    print('')
    # Сохраняем фото на yandex disk в папку по названию альбому
    ya_folder = photo_links_vk[::-1][0]['path_local'].split('/')[1]

    uploader = YaUploader(token=TOKEN_Y, ya_folder=ya_folder)

    print(f"Total files: {len(photo_links_vk) - 1}.  " )
    for link in photo_links_vk:
        if 'url' in link and 'file_name' in link:
            # print(link['url'])
            uploader.upload_file_y(ya_folder + '/' + link['file_name'], link['url'])

    print(f'Upload completed successfully to directory "{ya_folder}".')
