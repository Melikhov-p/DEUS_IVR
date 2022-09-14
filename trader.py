import requests
import json
from tqdm import tqdm
from pprint import pprint
import time


class Trader:
    def __init__(self):
        try:
            with open('config.json', 'r', encoding='utf-8') as file:
                self.CONFIG = json.load(file)
        except Exception as e:
            print(f'Конфиг-файл не найден. || {str(e)}')

    def get_elastic_record(self, dialog_ids: str):  # Получение записи из эластика по ИД звонка
        dialog_ids = dialog_ids.split()
        dep = self.detect_dep(dialog_ids[0])
        if dep == 'MFC':
            elastic_host = self.CONFIG['ELASTIC_MFC']['host']
            elastic_index = self.CONFIG['ELASTIC_MFC']['index']
            elastic_type = self.CONFIG['ELASTIC_MFC']['type']
        elif dep == 'MED':
            elastic_host = self.CONFIG['ELASTIC_MED']['host']
            elastic_index = self.CONFIG['ELASTIC_MED']['index']
            elastic_type = self.CONFIG['ELASTIC_MED']['type']

        responses = []
        with requests.Session() as session:
            for dialog_id in tqdm(dialog_ids, desc='Поиск записей...', colour='GREEN'):
                try:
                    response = session.get(f'{elastic_host}/{elastic_index}/{elastic_type}/{dialog_id}')
                    responses.append(response.json())
                except Exception as e:
                    print(f'Ошибка получения записи || {str(e)}')
        return responses

    def detect_dep(self, dialog_id: str):  # Определение департамента если не указан
        mfc_url = f"{self.CONFIG['ELASTIC_MFC']['host']}/{self.CONFIG['ELASTIC_MFC']['index']}/{self.CONFIG['ELASTIC_MFC']['type']}/"
        med_url = f"{self.CONFIG['ELASTIC_MED']['host']}/{self.CONFIG['ELASTIC_MED']['index']}/{self.CONFIG['ELASTIC_MED']['type']}/"
        with requests.Session() as session:
            # for dialog_id in tqdm(dialog_ids, desc='Определение департамента...', colour='GREEN'):
            try:
                response = session.get(mfc_url+dialog_id).json()['found']
            except Exception as e:
                print(f'Ошибка определения департамента || {str(e)}')
            if response:
                DEP = 'MFC'
            elif not response:
                try:
                    response = session.get(med_url+dialog_id).json()['found']
                except Exception as e:
                    print(f'Ошибка определения департамента || {str(e)}')
                if response:
                    DEP = 'MED'
                elif not response:
                    DEP = None
        return DEP

    def get_records_by_phone(self, phone: str, dep: str = 'MFC'):  # Поиск ИД звонков по номеру телефона
        if dep == 'MFC':
            elastic_host = self.CONFIG['ELASTIC_MFC']['host']
            elastic_index = self.CONFIG['ELASTIC_MFC']['index']
            prefix = 'telephone'
            if phone[0] != '7':
                phone = '7' + phone[1:]
        elif dep == 'MED':
            elastic_host = self.CONFIG['ELASTIC_MED']['host']
            elastic_index = self.CONFIG['ELASTIC_MED']['index']
            prefix = 'phone'
            if not phone.startswith('+'):
                phone = '+' + phone
            if phone[1] != '7':
                phone = phone[:1] + '7' + phone[2:]
        with requests.Session() as session:
            try:
                response_hits = session.get(f'{elastic_host}/{elastic_index}/_search?q={prefix}:{phone}').json()['hits']
            except Exception as e:
                print('Ошибка получения записей telephone || ' + str(e))
            if response_hits['total'] == 1:
                return response_hits['hits']

if __name__ == '__main__':
    trader = Trader()
    start_timestamp = time.time()
    # DEP = trader.detect_dep('a858f5f77205c8d480bf7c302e581c9d')
    # print(DEP)
    print(trader.get_elastic_record('a858f5f77205c8d480bf7c302e581c9d'))
    # print(trader.get_records_by_phone('79087885632'))
    task_time = round(time.time() - start_timestamp, 2)
    print(f'Total time: {task_time}')
