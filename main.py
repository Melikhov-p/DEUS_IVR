import PySimpleGUI as sg
from trader import Trader
from get_transcription import get_transcription

layout_search_by_id = [  # Отрисовка для поиска звонка по ИД
    [sg.Text('DIALOG ID'), sg.InputText(key='-dialog_id-'),
     sg.Submit(button_text='Найти'), sg.Submit(button_text='Очистить'), sg.Text('MODE: '), sg.Submit(button_text='PHONE')],
    [sg.Output(size=(60, 20), key='-output-'), sg.Output(size=(40, 20), key='-meta_data-')],
    [sg.Output(size=(104, 15), key='-dialog_transcription-')],
    [sg.Cancel(button_text='Выход'), sg.Text('', text_color='red', key='-error-', auto_size_text=True, font='Tahoma')]
]

layout_search_by_telephone = [  # Отрисовка для поиска ИД звонков по номеру телефона
    [sg.Text('PHONE'), sg.InputText(key='-phone-'),
     sg.Submit(button_text='Найти звонки'), sg.Combo(['MFC', 'MED'], default_value='MFC', key='-dep-'), sg.Text('MODE: '), sg.Submit(button_text='ID')],
    [sg.Output(size=(60, 15), key='-hits_by_phone-')]
]

layouts = [[sg.Column(layout_search_by_id, key='-layout_id-'), sg.Column(layout_search_by_telephone, visible=False, key='-layout_phone-')]]

window = sg.Window('DEUS IVR', layouts)
while True:
    event, values = window.read()
    trader = Trader()
    # print(event, values) #debug
    if event == 'Выход' or event == sg.WIN_CLOSED:
        break
    if event == 'Найти':
        dialog_id = values['-dialog_id-']
        if dialog_id != '':
            window['-error-'].update('')
            response = trader.get_elastic_record(dialog_id)[0]
            window['-output-'].update('')
            for key, value in response['_source'].items():
                if key == 'transcription':
                    continue
                window['-output-'].write(f'{key}: {value} \n')
            window['-meta_data-'].update(f"id: {response['_id']}")
            transcription = get_transcription(dialog_id)
            window['-dialog_transcription-'].update('')
            for line in transcription:
                window['-dialog_transcription-'].write(line + '\n')
        else:
            window['-error-'].update('ЗАПОЛНИТЕ ПОЛЕ DIALOG ID')
    if event == 'Найти звонки':
        hits = trader.get_records_by_phone(values['-phone-'], values['-dep-'])
        # window['-hits_by_phone-'].update()
        for hit in hits:
            window['-hits_by_phone-'].write(f"ID: {hit['_id']} ||")
    if event == 'PHONE':
        window['-layout_id-'].update(visible=False)
        window['-layout_phone-'].update(visible=True)
    if event == 'ID':
        window['-layout_id-'].update(visible=True)
        window['-layout_phone-'].update(visible=False)
    if event == 'Очистить':
        window['-dialog_id-'].update('')
        window['-output-'].update('')
        window['-meta_data-'].update('')
        window['-dialog_transcription-'].update('')
        window['-phone-'].update('')
        window['-hits_by_phone-'].update('')
window.close()
