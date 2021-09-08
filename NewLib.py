import configparser
import os
import logging
from chardet.universaldetector import UniversalDetector
from bs4 import BeautifulSoup
import datetime
from os import path
import csv

logging.basicConfig(filename="logs.log", level=logging.INFO)


def conver_min_to_hour_and_min(min_list):
    '''
    конвертируем переменную ххх/ххх или ххх/ххх/ххх в формат чч:мм/чч:мм или чч:мм/чч:мм/чч:мм
    :param min_list: min_list это строка вида ххх/ххх или ххх/ххх/ххх где ххх - минуты
    :return: строку чч:мм/чч:мм или чч:мм/чч:мм/чч:мм
    '''
    time_ = min_list.split('/')
    l = len(time_)
    if l == 2:
        time_sell = int(time_[0])
        time_sell_hour = time_sell // 60
        time_sell_min = time_sell - (time_sell // 60) * 60
        # Если минута одним числом то добавим нолик спереди
        if len(str(time_sell_min)) == 1:
            time_sell_min = f'{0}{time_sell_min}'
        time_sell_finished = f'{time_sell_hour}:{time_sell_min}'

        time_buy = int(time_[1])
        time_buy_hour = time_buy // 60
        time_buy_min = time_buy - (time_buy // 60) * 60
        # Если минута одним числом то добавим нолик спереди
        if len(str(time_buy_min)) == 1:
            time_buy_min = f'{0}{time_buy_min}'
        time_buy_finished = f'{time_buy_hour}:{time_buy_min}'

        finished_time = time_sell_finished + '/' + time_buy_finished
    else:
        time_sell = int(time_[0])
        time_sell_hour = time_sell // 60
        time_sell_min = time_sell - (time_sell // 60) * 60
        # Если минута одним числом то добавим нолик спереди
        if len(str(time_sell_min)) == 1:
            time_sell_min = f'{0}{time_sell_min}'
        time_sell_finished = f'{time_sell_hour}:{time_sell_min}'

        time_buy = int(time_[1])
        time_buy_hour = time_buy // 60
        time_buy_min = time_buy - (time_buy // 60) * 60
        # Если минута одним числом то добавим нолик спереди
        if len(str(time_buy_min)) == 1:
            time_buy_min = f'{0}{time_buy_min}'
        time_buy_finished = f'{time_buy_hour}:{time_buy_min}'
        time_buy_finished = f'{time_buy_hour}:{time_buy_min}'

        time_all = int(time_[2])
        time_all_hour = time_all // 60
        time_all_min = time_all - (time_all // 60) * 60
        # Если минута одним числом то добавим нолик спереди
        if len(str(time_all_min)) == 1:
            time_all_min = f'{0}{time_all_min}'
        time_all_finished = f'{time_all_hour}:{time_all_min}'
        time_all_finished = f'{time_all_hour}:{time_all_min}'

        finished_time = time_sell_finished + '/' + time_buy_finished + '/' + time_all_finished
    return finished_time


def createConfig(filepath):
    """
    Create a config file
    функция задает настройки по умолчанию и создает файл настройки, если его не существует
    """
    config = configparser.ConfigParser()

    config.add_section("Main windos sizes")
    config.set("Main windos sizes", "Top", "200")
    config.set("Main windos sizes", "Left", "200")
    config.set("Main windos sizes", "Width", "800")
    config.set("Main windos sizes", "Height", "400")

    # путь для открытия отчетов - запоминается последний
    config.add_section('HTML file path')
    config.set('HTML file path', 'file path', '')

    config.add_section('file path for temp files')
    # config.set('HTML file path for temp scv files', 'file path', 'temp\\')
    config.set('file path for temp files', 'file path', 'temp\\')

    config.add_section('file path for scv files')
    # config.set('HTML file path for scv files', 'file path', 'csv\\')
    config.set('file path for scv files', 'file path', 'csv\\')

    config.add_section('file path for set files')
    # config.set('HTML file path for scv files', 'file path', 'csv\\')
    config.set('file path for set files', 'file path', '')

    with open(filepath, "w") as config_file:
        config.write(config_file)

class ConfigFile():
    '''
    Класс работы с файлом настроек
    требуется import os, logging
    '''



    def __init__(self, filePath=''):
        self.filePath = filePath
        self.existFile = os.path.isfile(self.filePath)


    def setParam(self,filepath,section,param,value):
        if self.existFile != True:
            createConfig(filepath)
        config = configparser.ConfigParser()
        config.read(self.filePath)
        config.set(section, param, value)
        try:
             with open(self.filePath, "w") as config_file:
                config.write(config_file)
                logging.INFO(f'Section={section}, parametr={param}, value={value} - saved sucssesful!!!')
        except: logging.error('Ошибка записи в файл настроек')


    def getParam(self,filepath,section,param):
        if self.existFile != True:
            createConfig(filepath)
        config = configparser.ConfigParser()
        try:
            config.read(self.filePath)
        except:
            logging.error('Ошибка чтения файла настроек')
        f = config.get(section,param)
        return config.get(section,param)


def String_to_time(time):
    '''

    :param time: string 2015.02.16 19:59:58
    :return: type datatime  2015-02-16 19:59:58
    '''
    year = int(time[0:4])
    month =int(time[5:7])
    day = int(time[8:10])
    hour = int(time[11:13])
    minut = int(time[14:16])
    sec = int(time[-2:])
    time = datetime.datetime(year, month, day, hour, minut, sec)
    # print(year + month + day + hour + minut + sec)
    return time

def write_to_csv(dic,scv_file_name):
    '''
    создаем файл csv с именем файла отчета и записываем все сделки
    '''
    # file_csv = get_file_name(file)
    with open(scv_file_name,mode='a',encoding='utf-8') as w_file:
        file_writer = csv.writer(w_file, delimiter=",", lineterminator="\r")
        file_writer.writerow([dic['time'], dic['symbol'], dic['order_type'],
                              dic['direction'], dic['lot'], dic['num_order'],
                              dic['price'], dic['sl'], dic['tp'], dic['commisions'],
                              dic['profit'], dic['balance']])

def delete_zero(string):
    string0 = string.split('=')[0]
    string1 = string.split('=')[1]
    try:
        string1 = float(string1)
    except:
        return string
    if string1 == int(string1):
        string1 = int(string1)
    if string1 == 0:
        string1 = str(0)
    else:
        string1 = str(string1)
    string = string0 + '=' + string1 + '\n'
    string = string
    return string

def get_file_path_to_pic(file_path):
    '''
    input: путь к файлу отчета
    return: путь к файлу-картинке графика
    '''
    extension = 'gif'
    file_name = os.path.basename(file_path).split('.')[0] + '.' + extension
    directory = os.path.dirname(file_path)
    path_to_file = directory + "/" +  file_name
    check_file = os.path.exists(path_to_file)
    if check_file:
        return path_to_file
    else:
        return False


# ------------------------------------------------------------------
def get_csv_file_name(pathToFile):
        full_name = pathToFile.basename(pathToFile)
        csv_name = pathToFile.splitext(full_name)[0] + '.csv'
        return csv_name

def create_csv_file_of_deal_MT4():
        '''
        Создаем csv файл со сделками
        :return:
        '''
        global pathToFile, coding, symbol
        csv_name = get_csv_file_name(pathToFile)
        deal_list = {'time': 'time', 'symbol': 'symbol', 'order_type': 'order_type', 'direction': 'direction',
                     'lot': 'lot', 'num_order': 'num_order', 'price': 'price', 'sl': 'sl',
                     'tp': 'tp', 'commisions': 0, 'profit': 'profit', 'balance': 'balance'}
        with open(ConfigFile.getParam('file path for scv files','file path') + csv_name, mode='w', encoding='utf-8') as w_file:
            file_writer = csv.writer(w_file, delimiter=",", lineterminator="\r")
            file_writer.writerow([deal_list['time'], deal_list['symbol'], deal_list['order_type'],
                                  deal_list['direction'], deal_list['lot'], deal_list['num_order'],
                                  deal_list['price'], deal_list['sl'], deal_list['tp'], deal_list['commisions'],
                                  deal_list['profit'], deal_list['balance']])
        with open(pathToFile, encoding=coding) as f:
            for line in f:
                if '<td>buy</td>' in line or '<td>close</td>' in line or '<td>s/l</td>' in line or \
                        '<td>t/p</td>' in line or '<td>close at stop</td>' in line or '<td>sell</td>' in line or \
                        '<td>in</td>' in line or '<td>out</td>' in line:
                    soup = BeautifulSoup(line, 'html.parser')

                    deal_list['time'] = soup.contents[0].contents[1].get_text()
                    deal_list['symbol'] = symbol
                    deal_list['order_type'] = soup.contents[0].contents[2].get_text()
                    deal_list['num_order'] = soup.contents[0].contents[3].get_text()
                    deal_list['lot'] = soup.contents[0].contents[4].get_text()
                    deal_list['price'] = soup.contents[0].contents[5].get_text()
                    deal_list['sl'] = soup.contents[0].contents[6].get_text()
                    deal_list['tp'] = soup.contents[0].contents[7].get_text()
                    deal_list['profit'] = soup.contents[0].contents[8].get_text()
                    try:
                        deal_list['balance'] = soup.contents[0].contents[9].get_text()
                    except:
                        deal_list['balance'] = 0
                    # SetGetConfig('get', 'HTML file path for temp scv files', 'file path')
                    write_to_csv(deal_list, ConfigFile.getParam('file path for scv files','file path') + csv_name)
                    # write_to_csv(deal_list, SetGetConfig('get', self.csv_name)







