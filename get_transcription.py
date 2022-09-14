#!/usr/bin/python3
# -*- coding: UTF-8 -*-
#
import json
import mysql.connector


def get_transcription(ID: str):
    with open('config.json', 'r', encoding='utf-8') as file:
        CONFIG = json.load(file)
    host = CONFIG['DB']['host']
    user = CONFIG['DB']['user']
    passwd = CONFIG['DB']['password']
    db = CONFIG['DB']['name_db']
    try:
        cnx = mysql.connector.connect(host=host, user=user, passwd=passwd, db=db)
        cursor = cnx.cursor(dictionary=True)
        cursor.execute(f"SELECT isIVR, recognizedText FROM voicetech.phone_ivr_journeys WHERE interactionID  = '{ID}'")
        result = cursor.fetchall()
    except Exception as e:
        # with open('get_transcription.log', 'a', encoding='utf8') as file:
        #     file.write(str(e) + '\n')
        return 'Transcription none'
    try:
        dialog = []
        for line in result:
            if line['recognizedText'] != '':
                if line['isIVR'] == 0:
                    dialog.append(f"C: {line['recognizedText']}")
                else:
                    dialog.append(f"R: {line['recognizedText']}")
        return dialog
    except Exception as e:
        pass



if __name__ == '__main__':
    print(get_transcription('df4f75d519252f2415d56807ea4c70bd'))
