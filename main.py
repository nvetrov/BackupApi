import json
import os
from urllib.parse import urlparse

import requests


# TODO: Проверить имя
#  класс yandex по работе с api
class YaUploader:
    def __init__(self, token: str, ya_f: str):
        self.token = token
        self.y_directory = ya_f
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
            print(f'Folder named: {self.y_directory} already exists!')
        else:
            print(f'Folder: {self.y_directory} created on Yandex Disk')

    # Загружать файл на яндекс Диск.
    def upload_file_y(self, file_path: str, url):
        """Метод загружает файл file_path на яндекс диск"""
        up_url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        headers = self.get_headers()
        params = {'url': url, 'path': file_path}
        response = requests.post(up_url, headers=headers, params=params)
        response.raise_for_status()
        if response.status_code == 202:
            print(f'File uploaded to Yandex Disk\n'
                  f"({params['url']}, {params['path']}\n")

    def get_url_y(self, photo_lists):
        for link in photo_lists:
            # if 'url' in link and 'file_name' in link:
            if 'path_local' not in link:
                uploader.upload_file_y(ya_folder + '/' + link['file_name'], link['url'])
        return len(photo_lists)


#  класс VK по работе с api
class VK:
    def __init__(self, _vk_id: int, token: str, version: float, count: int):
        self.token = token
        self.vk = _vk_id  # id пользователя vk
        self.v = version  # версия api vk
        self.count = count  # количество фоток по умолчанию 5

    # Получить фотографии с профиля vk.
    def connect_vk(self):
        link_vk = 'https://api.vk.com/method/photos.get'
        params = {'owner_id': self.vk,
                  'access_token': self.token,
                  'album_id': 'profile',
                  'photo_sizes': 1,
                  'count': self.count,
                  'extended': 1,
                  'feed_type': "likes",
                  'v': self.v,
                  }
        photos_vk = requests.get(link_vk, params=params)
        if photos_vk.status_code != 200:
            print('No != 200')
        else:
            return photos_vk.json()

    # Сохранить лог -> json
    def save_json_log_vk(self, dict_data):
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

        # Удаляем дубликаты имена файлов
        names = []
        for dct in dict_data:
            count = 1
            if "file_name" in dct:
                if dct['file_name'] in names:
                    dct['file_name'] = dct['file_name'][:-4] + '_' + str(count) + dct['file_name'][-4:]
                    names.append(dct['file_name'])
                    count += 1
                else:
                    names.append(dct['file_name'])
            else:
                continue

        # Сохраняем в лог файл на диск
        with open(f'{self.vk}.json', 'w') as file:
            json.dump(dict_data, file, indent=2, ensure_ascii=False)

        return dict_data

    # Собераем ссылки для скачивания фотографий из VK.
    def parse_profile_vk(self, answer):
        count = 0
        # Обработка ответа от VK
        ll = answer['response']['items']
        if len(ll) == 0:
            print(f'Photo not found in profile id{self.vk})')
            exit()
        photo_lst = []
        for item in ll:
            if count < self.count:

                photo_dict = dict()
                photo_dict['file_name'] = str(item['likes']['count']) + '_' + \
                                          str(os.path.basename(urlparse(item['sizes'][-1]['url']).path))
                photo_dict['size'] = item['sizes'][-1]['type']
                photo_dict['url'] = item['sizes'][-1]['url']
                photo_lst.append(photo_dict)
                count += 1
        return photo_lst


if __name__ == '__main__':
    print('input data and press enter'.upper())
    # TOKEN_Y = input(f"Input token(Yandex.Disk Polygon): ")
    #
    # vk_id = int(input("Input vk user id: "))
    # vk_token = str(input(f"Input token VK: "))
    print('--------------------------------------------')
    vk_v = 5.89
    # vk_v = 5.130   #  Current version
    count_photos = 10  # Количество скаченных фото по умолчанию

    # Инициализация класс VK -> v_obj
    v_obj = VK(_vk_id=vk_id, token=vk_token, version=vk_v, count=count_photos)

    # Получили данные из профиля VK пользователя
    r = v_obj.connect_vk()

    # Логирование
    full_logs = v_obj.parse_profile_vk(r)
    photo_links_vk = v_obj.save_json_log_vk(dict_data=full_logs)


    # Название альбома на ЯДиске
    ya_folder = photo_links_vk[::-1][0]['path_local'].split('/')[1]

    uploader = YaUploader(token=TOKEN_Y, ya_f=ya_folder)

    # Сохранение фото на Y.Диск
    c = uploader.get_url_y(photo_lists=photo_links_vk)

    print(f'Upload completed successfully to directory "{ya_folder}".')
    print(f'Saved photos:{c - 1}')
