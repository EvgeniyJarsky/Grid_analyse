from chardet.universaldetector import UniversalDetector
import numpy as np
from bs4 import BeautifulSoup
from os import path
import time
import csv
import pandas as pd
import datetime
import os
import configparser
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

def createConfig(path='config\config.txt'):
    """
    Create a config file
    """
    config = configparser.ConfigParser()
    config.add_section("Main windos size")
    config.set("Main windos size", "Height", "100")
    config.set("Main windos size", "Width", "100")

    # путь для открытия отчетов - запоминается последний
    config.add_section('HTML file path')
    config.set('HTML file path', 'file path','')

    config.add_section('file path for temp files')
    # config.set('HTML file path for temp scv files', 'file path', 'temp\\')
    config.set('file path for temp files', 'file path', 'temp\\')

    config.add_section('file path for scv files')
    # config.set('HTML file path for scv files', 'file path', 'csv\\')
    config.set('file path for scv files', 'file path', 'csv\\')

    config.add_section('file path for set files')
    # config.set('HTML file path for scv files', 'file path', 'csv\\')
    config.set('file path for set files', 'file path', '')


    with open(path, "w") as config_file:
        config.write(config_file)

def SetGetConfig(set_get,section,param,value=0,path = 'config\config.txt'):
    if not os.path.exists(path):
        createConfig(path)

    config = configparser.ConfigParser()
    config.read(path)

    if set_get == 'set':
        config.set(section,param,value)
        with open(path, "w") as config_file:
            config.write(config_file)
    # SetGetConfig('get', 'HTML file path', 'file path')
    # SetGetConfig('set', 'HTML file path', 'file path', file_path)
    if set_get == 'get':
        value_ = config.get(section,param)
        return value_

# file = 'C:/Users/Evgeniy/PycharmProjects/bs/html/text.txt'

# file = 'C:/Users/Evgeniy/PycharmProjects/bs/html/MT5short3_withSL.html'# content = f.read().encode('cp1251')
# file = 'C:/Users/Evgeniy/PycharmProjects/bs/html/MT5Long.html'# content = f.read().encode('cp1251')


# Check file
# file = 'C:/Users/Evgeniy/PycharmProjects/bs/html/MT4_html.htm'# content = f.read().encode('cp1251')
# file = 'C:/Users/Evgeniy/PycharmProjects/bs/html/MT5short3_withSL.html'# content = f.read().encode('cp1251')



# file = 'C:/Users/Evgeniy/PycharmProjects/bs/html/MT4_short_SL.htm'# content = f.read().encode('cp1251')

# file = 'C:/Users/Evgeniy/PycharmProjects/bs/MT4LongWithTP.htm'# content = f.read()
#
# file = 'C:/Users/Evgeniy/PycharmProjects/bs/html/MT4_QLT_EN.htm'
# file = 'C:/Users/Evgeniy/PycharmProjects/bs/html/MT5_QLT_eng.html'

# file = 'C:/Users/Evgeniy/PycharmProjects/bs/html/QLT 1.7 Ostap.Bender GBPCHF m-5 v1.0 2014-2020.htm'
# file = 'C:/Users/Evgeniy/PycharmProjects/bs/html/QLT 1.62 (set 1.55) audjpy 01.05.2011-03.06.2017.htm'
# file = 'C:/Users/Evgeniy/PycharmProjects/bs/html/MT5short3_withSL.html'
def duration_in_min(start_time, end_time):
    date1 = datetime.datetime.strptime(start_time, '%Y.%m.%d %H:%M')
    date2 = datetime.datetime.strptime(end_time, '%Y.%m.%d %H:%M')
    delta_sec = (date2 - date1).total_seconds()
    delta_min = delta_sec / 60
    delta_hours = int(delta_min // 60)
    delta_days = delta_hours // 24
    delta_min_ = int(delta_min - delta_hours * 60)
    weekends = 0
    start_date = date1
    for day in range(0, delta_days):
        start_date = start_date + datetime.timedelta(days=1)
        if start_date.weekday() == 5 or start_date.weekday() == 6:
            weekends += 1
    # print(f'Weekends = {weekends}')
    time_period_without_weekends = (delta_hours - weekends * 24) * 60 + delta_min_
    return time_period_without_weekends

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

def get_main_information(file, data_type):
    '''
    прочитаем информацию для вывода основной информации об отчете - валюта, депозит и т.д.
    :param file:  file = 'C:/Users/Evgeniy/PycharmProjects/bs/MT5_QLT_eng.html'
    data_type: symbol, expert_name, period, setting, deposit, period, profit
    :return:
    '''
    n = 0
    n_max = 4
    with open(file, encoding=(detect_encoding(file))) as f:
        language = detect_languge(file)
        if language == 'EN':
            symbol = 'Symbol'
            period = 'Period'
            deposit = 'Initial deposit'
            maximal_drawdown = 'Maximal drawdown'
            profit = 'Total net profit'
        if language == 'RU':
            symbol = 'Символ'
            period = 'Период'
            deposit = 'Начальный депозит'
            maximal_drawdown = 'Максимальная просадка'
            profit = 'Чистая прибыль'
        for line in f:
            if symbol in line:
                soup = BeautifulSoup(line, 'html.parser')
                symbolMT4 = soup.contents[0].contents[1].get_text()
                symbolMT4 = symbolMT4.split('(')[0]
            if period in line:
                soup = BeautifulSoup(line, 'html.parser')
                periodMT4 = soup.contents[0].contents[1]
    return symbolMT4

def prepare_pandas_table_data(main_list):
        '''
        main_list = [line[1],time_start_grid_buy, line[0], 'buy', Dic_Buy_list, profit_buy, price_start_grid_buy,
                                     line[6], last_price_grid, 0, line[11], close_price_buy/sell]
        main_list = [line[1],time_start_grid_buy, line[0], 'buy', Dic_Buy_list, profit_buy, price_start_grid_buy,
                                     line[6], last_price_grid, 0, line[11]]
        :param main_list:
        :return:
        '''
        symbol_ = main_list[0]  # символ
        n = len(main_list[11])
        if n == 0: n = 1# там где одно колено возвращает 0, тогда берем 1
        avrg_close_price = sum(main_list[11])/n
        # avrg_close_price=0
        date_close = String_to_time(main_list[2])  # дата
        year_ = String_to_time(main_list[2]).year  # год
        month_ = String_to_time(main_list[2]).month  # месяц
        type_of_grid = main_list[3]  # тип сетки
        grid = int(len(main_list[4]) / 2)  # количество колен в сетке
        sum_lot = round(sum([deals for deals in main_list[4] if deals > 0]), 2)  # суммарный лот
        if main_list[9] == 0:
            sum_commision = 0
        else:
            sum_commision = round(sum(main_list[9]), 2)  # суммарная комиссия
        sum_profit = round((sum(main_list[5]) - sum_commision), 2)  # профит минус комиссия
        # todo определить размер сетки в пунктах
        length = len(list(str(main_list[8]).split('.')[1]))  # количество знаков после запятой в цене
        digits = 10000
        if length == 2 or length == 3:
            digits = 100
        grid_size = round(abs(float(main_list[6]) - float(main_list[8])) * digits, 0)  # размер сетки в пунктах
        # time_grid = round(((date_close - String_to_time(main_list[1])).total_seconds()) / 60,
        #                   0)  # время существования сетки в минутах
        time_grid = duration_in_min(main_list[1], main_list[2])
        balance = main_list[10]  # баланс на время закрытия сетки
        list_of_grid = {"Date": date_close, 'Year': year_, 'Month': month_, 'Type_of_grid': type_of_grid,
                        'Grid': grid, 'Sum_lot': sum_lot, 'Sum_profit': sum_profit, 'Sum_commision': sum_commision,
                        'Grid_size': grid_size, 'Time_grid': time_grid, 'Balance': balance, 'ClosePrice': avrg_close_price,
                        'StartPrice': main_list[6], 'EndPrice': main_list[8]}
        return list_of_grid

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



def colculate_test_period(period):
    '''
    2011.05.02 17:14 - 2011.05.02 17:14

    '2015.06.01 - 2015.10.30'
    73
    year = 6 and 1 months
    :param period:
    :return:
    '''

    def months(d_start, d_finish):
        '''
        вычисляет количество месяцев между датами
        :param d_start: дата начала торгов в отчете
        :param d_finish: дата конца торгов в отчете
        :return: int количество месяцев
        '''
        return d_finish.month - d_start.month + 12 * (d_finish.year - d_start.year)

    period = period.split(' - ')
    testing_dates = {'start': period[0], 'finish': period[1]}
    testper = f"{testing_dates['start']} - {testing_dates['finish']}"
    # для MT5 ужно добавить часы
    if len(testing_dates['start']) == 10:
        start = testing_dates['start']
        finish = testing_dates['finish']
        testing_dates['start'] = start + ' 00:00' #f'{start} 00:00'
        testing_dates['finish'] = finish + ' 23:59'
        testper = f"{testing_dates['start']} - {testing_dates['finish']}"
    months2 = months(String_to_time(testing_dates['start']), String_to_time(testing_dates['finish']))
    year = months2 // 12
    months1 = months2 % 12
    all = []
    all_string = f'{testper}; {year} лет и {months1} месяцев или {months2} месяцев'
    all.append(all_string)
    all.append(months2)
    return all

class Main_info:
    '''
    Класс определяет валюту, таймфрейм, период тестирования

    '''
    def __init__(self, file_path=0, type_report=0, language=0, symbol=0, csv_name=0, pandas_table =0,
                 num_max_grid=0, table1=0, total_profit=0, time_frame=0, period = 0, table2 = 0,
                 table3=0, deposit=0, drawdown=0, month=0, profitability=0, digits=0, set_file=0):
        self.file_path = file_path
        self.type_report = type_report
        self.language = language
        self.csv_name = csv_name
        self.pandas_table = pandas_table
        self.num_max_grid = num_max_grid
        self.table1 = table1
        self.table2 = table2
        self.table3 = table3
        self.total_profit = total_profit
        self.time_frame = time_frame
        self.period = period
        self.deposit = deposit
        self.drawdown = drawdown
        self.month = month#количество месяце в отчете
        self.profitability = profitability
        self.digits = digits
        self.set_file = set_file

    def detect_type_of_report(self):
        '''
        определяем кодировку файла
        :param file: file - путь к файлу  file = 'C:/Users/Evgeniy/PycharmProjects/bs/MT5Long.html'
        :return: str 'UTF-16' тогда это MT5 или 'None' тогда это MT4
        '''
        detector = UniversalDetector()
        l = 0
        maxl = 3
        with open(self.file_path, 'rb') as f:
            for line in f:
                l += 1
                detector.feed(line)
                if l >= maxl:
                    cod = detector.result['encoding']
                    break#todo если убрать этот break то работать будет долго
                if detector.done:
                    detector.close()
                    break
            cod = detector.result['encoding']
            self.type_report = cod

    def detect_language(self):
        # self.language = language
        if self.type_report == 'MetaTrader4':
            cod = None
        else:
            cod = 'UTF-16'
        with open(self.file_path, encoding=self.type_report) as f:
            language = 'None'
            for line in f:
                if 'Symbol' in line:
                    language = 'EN'
                    break
                if 'Символ' in line:
                    language = 'RU'
                    break
        self.language = language

    def get_set(self):
        '''
        загружаем настройки
        S_1="<====GeneralSettings====>"
        '''
        def delete_double_quotes(string):
            '''
            удаляем ковычки
            '''
            if string[-1] == '\"':
                string = string.replace('=\"','=')[0:-1]
            return string

        start = False
        if self.type_report == None:
            if self.language == 'RU':
                key_word = 'Параметры'
            else:
                key_word = 'Parameters'

            with open(self.file_path, encoding=self.type_report) as f:
                for line in f:
                    if line == '</td></tr>':# признак конца таблицы параметров
                        if start == True:
                            break
                    if '</td></tr>' in line:# если строка содержит и настройки и признак конца таблицы
                        if start == True:
                            self.set_file += line[0:-11]
                            break

                    if start == True:
                        self.set_file += line

                    if key_word in line:
                        start=True
                        soup = BeautifulSoup(line, 'html.parser')
                        a = soup.get_text()
                        a = a.replace(key_word,'')
                        # self.deposit = ''.join(sym.rstrip().split())
                        self.set_file = a
            b = ''.join(self.set_file.rstrip().split())
            self.set_file = b
            self.set_file = self.set_file.split(';')
            string = ''
            for item in self.set_file:
                if item == '': continue
                else:
                    item = delete_double_quotes(item)
                string += (item + '\n')
            self.set_file = string
        else:# для MT5
            if self.language == 'RU':
                key_word = 'Параметры:'
            else:
                key_word = 'Inputs:'
            start = False
            with open(self.file_path, encoding=self.type_report) as f:
                for line in f:
                    if start == True:
                        if 'Broker:' in line or 'Брокер:' in line:
                            break
                        if '<b>' in line:
                            soup = BeautifulSoup(line, 'html.parser')
                            a = soup.get_text()
                            self.set_file += soup.get_text()
                    if key_word in line:
                        start = True
                        line_ = next(f)
                        soup = BeautifulSoup(line_, 'html.parser')
                        self.set_file = soup.get_text()
        self.set_file = self.set_file

    def get_deposit(self):
        if self.type_report == None:
            with open(self.file_path, encoding=self.type_report) as f:
                if self.language == 'EN':
                    deposit = 'Initial deposit'
                    # period = 'Period'
                    # deposit = 'Initial deposit'
                    # maximal_drawdown = 'Maximal drawdown'
                    # profit = 'Total net profit'
                if self.language == 'RU':
                    deposit = 'Начальный депозит'
                    # period = 'Период'
                    # deposit = 'Начальный депозит'
                    # maximal_drawdown = 'Максимальная просадка'
                    # profit = 'Чистая прибыль'
                for line in f:
                    if deposit in line:
                        soup = BeautifulSoup(line, 'html.parser')
                        depo = soup.contents[0].contents[1].text
                        break
            self.deposit = depo
        if self.type_report == 'UTF-16':
            n =0
            with open(self.file_path, encoding=self.type_report) as f:
                if self.language == 'EN':
                    deposit = 'Initial Deposit'
                if self.language == 'RU':
                    deposit = 'Начальный депозит'
                for line in f:
                    if n ==1:
                        soup = BeautifulSoup(line, 'html.parser')
                        sym = soup.text# тут получаем название символа с двумя лишними пробелами впереди
                        self.deposit = ''.join(sym.rstrip().split())#удаляем все пробелы в строке
                        break
                    if deposit in line:
                        soup = BeautifulSoup(line, 'html.parser')
                        n = 1
                        continue

    def get_drawdown(self):
        if self.type_report == None:
            with open(self.file_path, encoding=self.type_report) as f:
                if self.language == 'EN':
                    maximal_drawdown = 'Maximal drawdown'
                if self.language == 'RU':
                    maximal_drawdown = 'Максимальная просадка'
                for line in f:
                    if maximal_drawdown in line:
                        soup = BeautifulSoup(line, 'html.parser')
                        dd = soup.contents[0].contents[3].text
                        break
            self.drawdown = dd
        if self.type_report == 'UTF-16':
            n =0
            with open(self.file_path, encoding=self.type_report) as f:
                if self.language == 'EN':
                    maximal_drawdown = 'Balance Drawdown Maximal'
                if self.language == 'RU':
                    maximal_drawdown = 'Максимальная просадка'
                for line in f:
                    if n ==1:
                        soup = BeautifulSoup(line, 'html.parser')
                        sym = soup.text# тут получаем название символа с двумя лишними пробелами впереди
                        self.drawdown = ''.join(sym.rstrip().split())#удаляем все пробелы в строке
                        break
                    if maximal_drawdown in line:
                        soup = BeautifulSoup(line, 'html.parser')
                        n = 1
                        continue

    def get_symbol(self):
        if self.type_report == None:
            with open(self.file_path, encoding=self.type_report) as f:
                if self.language == 'EN':
                    symbol = 'Symbol'
                    # period = 'Period'
                    # deposit = 'Initial deposit'
                    # maximal_drawdown = 'Maximal drawdown'
                    # profit = 'Total net profit'
                if self.language == 'RU':
                    symbol = 'Символ'
                    # period = 'Период'
                    # deposit = 'Начальный депозит'
                    # maximal_drawdown = 'Максимальная просадка'
                    # profit = 'Чистая прибыль'
                for line in f:
                    if symbol in line:
                        soup = BeautifulSoup(line, 'html.parser')
                        symbolMT4 = soup.contents[0].contents[1].get_text()
                        symbolMT4 = symbolMT4.split('(')[0]
                        break
                    # if period in line:
                    #     soup = BeautifulSoup(line, 'html.parser')
                    #     periodMT4 = soup.contents[0].contents[1]
            self.symbol = symbolMT4
        if self.type_report == 'UTF-16':
            n =0
            with open(self.file_path, encoding=self.type_report) as f:
                if self.language == 'EN':
                    symbol = 'Symbol'
                if self.language == 'RU':
                    symbol = 'Символ'
                for line in f:
                    if n ==1:
                        soup = BeautifulSoup(line, 'html.parser')
                        sym = soup.text# тут получаем название символа с двумя лишними пробелами впереди
                        self.symbol = sym[1:7]#обрезаем два лишних пробела впереди
                        break
                    if symbol in line:
                        soup = BeautifulSoup(line, 'html.parser')
                        n = 1
                        continue

    def get_total_profit(self):
        if self.type_report == None:
            with open(self.file_path, encoding=self.type_report) as f:
                if self.language == 'EN':
                    # symbol = 'Symbol'
                    # period = 'Period'
                    # deposit = 'Initial deposit'
                    # maximal_drawdown = 'Maximal drawdown'
                    profit = 'Total net profit'
                if self.language == 'RU':
                    # symbol = 'Символ'
                    # period = 'Период'
                    # deposit = 'Начальный депозит'
                    # maximal_drawdown = 'Максимальная просадка'
                    profit = 'Чистая прибыль'
                for line in f:
                    if profit in line:
                        soup = BeautifulSoup(line, 'html.parser')
                        profit_ = soup.contents[0].contents[1].get_text()
                        profit_ = profit_.split('(')[0]
                    # if period in line:
                    #     soup = BeautifulSoup(line, 'html.parser')
                    #     periodMT4 = soup.contents[0].contents[1]
            self.total_profit = profit_
        if self.type_report == 'UTF-16':
            n =0
            with open(self.file_path, encoding=self.type_report) as f:
                if self.language == 'EN':
                    profit = 'Total Net Profit'
                if self.language == 'RU':
                    profit = 'Чистая прибыль'
                for line in f:
                    if n ==1:
                        soup = BeautifulSoup(line, 'html.parser')
                        profit_ = soup.text# тут получаем название символа с двумя лишними пробелами впереди
                        profit_ = profit_[0:-2]
                        self.total_profit = ''.join(profit_.split())#удаляем все пробелы в строке
                        break
                    if profit in line:
                        soup = BeautifulSoup(line, 'html.parser')
                        n = 1
                        continue

    def get_csv_file_name(self):
        full_name = path.basename(self.file_path)
        self.csv_name = path.splitext(full_name)[0] + '.csv'
        #  = name
        # return name + '.csv'

    def create_csv_file_of_deal_MT4(self):
        '''
        Создаем csv файл со сделками
        :return:
        '''
        deal_list = {'time': 'time', 'symbol': 'symbol', 'order_type': 'order_type', 'direction': 'direction',
                     'lot': 'lot', 'num_order': 'num_order', 'price': 'price', 'sl': 'sl',
                     'tp': 'tp', 'commisions': 0, 'profit': 'profit', 'balance': 'balance'}
        with open(SetGetConfig('get', 'file path for temp files', 'file path') + self.csv_name, mode='w', encoding='utf-8') as w_file:
            file_writer = csv.writer(w_file, delimiter=",", lineterminator="\r")
            file_writer.writerow([deal_list['time'], deal_list['symbol'], deal_list['order_type'],
                                  deal_list['direction'], deal_list['lot'], deal_list['num_order'],
                                  deal_list['price'], deal_list['sl'], deal_list['tp'], deal_list['commisions'],
                                  deal_list['profit'], deal_list['balance']])
        with open(self.file_path, encoding=self.type_report) as f:
            for line in f:
                if '<td>buy</td>' in line or '<td>close</td>' in line or '<td>s/l</td>' in line or \
                        '<td>t/p</td>' in line or '<td>close at stop</td>' in line or '<td>sell</td>' in line or \
                        '<td>in</td>' in line or '<td>out</td>' in line:
                    soup = BeautifulSoup(line, 'html.parser')

                    deal_list['time'] = soup.contents[0].contents[1].get_text()
                    deal_list['symbol'] = self.symbol
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
                    write_to_csv(deal_list, SetGetConfig('get', 'file path for temp files',\
                                                         'file path') + self.csv_name)
                    # write_to_csv(deal_list, SetGetConfig('get', self.csv_name)

    def create_csv_file_of_deal_MT5(self):
        deal_list = {'time': 'time', 'symbol': 'symbol', 'order_type': 'order_type', 'direction': 'direction',
                     'lot': 'lot', 'num_order': 'num_order', 'price': 'price', 'sl': 'sl',
                     'tp': 'tp', 'commisions': 'commisions', 'profit': 'profit', 'balance': 'balance'}
        with open(SetGetConfig('get', 'file path for scv files', 'file path')+self.csv_name, mode='w', encoding='utf-8') as w_file:
            file_writer = csv.writer(w_file, delimiter=",", lineterminator="\r")
            file_writer.writerow([deal_list['time'], deal_list['symbol'], deal_list['order_type'],
                                  deal_list['direction'], deal_list['lot'], deal_list['num_order'],
                                  deal_list['price'], deal_list['sl'], deal_list['tp'], deal_list['commisions'],
                                  deal_list['profit'], deal_list['balance']])
        with open(self.file_path, encoding=self.type_report) as f:
            for line in f:
                if 'filled' in line: continue
                if '<td>buy</td>' in line or '<td>close</td>' in line or '<td>s/l</td>' in line or \
                        '<td>t/p</td>' in line or '<td>close at stop</td>' in line or '<td>sell</td>' in line or \
                        '<td>in</td>' in line or '<td>out</td>' in line:
                    soup = BeautifulSoup(line, 'html.parser')
                    x = soup.contents[1].contents[3].get_text()
                    list_MT5 = [0, 2, 3, 5, 6, 8, 11, 4, 7, 10]
                    deal_list['time'] = soup.contents[1].contents[0].get_text()
                    deal_list['symbol'] = soup.contents[1].contents[2].get_text()
                    deal_list['order_type'] = soup.contents[1].contents[3].get_text()
                    deal_list['lot'] = soup.contents[1].contents[5].get_text()
                    deal_list['price'] = soup.contents[1].contents[6].get_text()
                    deal_list['commisions'] = soup.contents[1].contents[8].get_text()
                    try:
                        # deal_list['balance'] = soup.contents[1].contents[11].get_text()
                        deal_list['balance'] = float(''.join(((soup.contents[1].contents[11].get_text()).split())))
                    except:
                        deal_list['balance'] = 0
                    deal_list['direction'] = soup.contents[1].contents[4].get_text()
                    deal_list['num_order'] = soup.contents[1].contents[7].get_text()
                    deal_list['profit'] = soup.contents[1].contents[10].get_text()
                    write_to_csv(deal_list, SetGetConfig('get', 'file path for temp files', 'file path')+self.csv_name)

    def get_digits(self):
        n = 0# сколько строчек пройти что бы определить количество цыфр после запятой, хотя кажется достаточно одного прохода т.к. 0 тоже пришется в конце
        k = 0
        digits = 0
        with open(self.file_path, encoding=self.type_report) as f:
            for line in f:
                if 'filled' in line: continue
                if n > 3: break
                if '<td>buy</td>' in line or '<td>sell</td>' in line:
                    soup = BeautifulSoup(line, 'html.parser')
                    if self.type_report == 'UTF-16':
                        x = soup.contents[1].contents[6].get_text()
                    else:
                        x = soup.contents[0].contents[5].get_text()
                    y = len(x.split('.')[1])
                    if y > digits:
                        digits = y
                    n +=1
            if digits == 5:
                self.digits = 10000
            elif digits == 4:
                self.digits =1000
            else:
                self.digits = 100
            print(self.digits)

    def create_pandas_table_MT4(self):
        summa_buy = 0 # профит
        summa_sell = 0 # профит
        Dic_Buy = {} # список лотов ордеров
        Dic_Sell = {} # список лотов ордеров
        profit_buy = []
        profit_sell = []
        time_start_grid_buy = 0
        time_start_grid_sell = 0
        price_start_grid_buy = 0
        price_start_grid_sell = 0
        # last_price_grid = 0
        last_price_grid_sell = 0# здесь будем запоминать наибольшую цену открытия сетки
        last_price_grid_buy = 0
        close_price_buy = []
        close_price_sell = []
        pandas_table = pd.DataFrame()  # инициализируем пустую таблицу сделок
        # file_csv = get_file_name(file)
        with open(SetGetConfig('get', 'file path for temp files', 'file path')+self.csv_name, mode='r', encoding='utf-8') as file_r:
            reader = csv.reader(file_r)
            for line in reader:
                if line[0] == 'time':  # если это шапка таблицы то пропускаем
                    continue
                if line[2] == 'buy':  # если это строка покупки
                    if len(Dic_Buy) == 0:  # если словарь сделок пустой запомним время начала сетки
                        time_start_grid_buy = line[0]
                        price_start_grid_buy = line[6]
                        # if time_start_grid_buy == '2020.07.17 14:00':
                        #     print('here!!!')
                    Dic_Buy[line[5]] = round(float(line[4]), 2)
                    summa_buy = round(sum(Dic_Buy.values()), 2)
                    # last_price_grid = line[6]
                    if last_price_grid_buy == 0:
                        last_price_grid_buy = line[6]
                    elif line[6] < last_price_grid_buy:
                        last_price_grid_buy = line[6]
                    continue
                if line[2] == 'sell':  # если это строка прожажи
                    if len(Dic_Sell) == 0:  # если словарь сделок пустой запомним время начала сетки
                        time_start_grid_sell = line[0]
                        price_start_grid_sell = line[6]
                    Dic_Sell[line[5]] = round(float(line[4]), 2)
                    summa_sell = round(sum(Dic_Sell.values()), 2)
                    # last_price_grid = line[6]
                    if last_price_grid_sell == 0:
                        last_price_grid_sell = line[6]
                    elif line[6] > last_price_grid_sell:
                        last_price_grid_sell = line[6]
                    continue
                keywords = ('close','t/p','s/l','close at stop')
                # if (line[2] == 'close' or line[2] == 't/p' or line[2] == 's/l' or line[2] == 'close at stop') \
                #         and (summa_buy != 0 or summa_sell != 0):
                if (line[2] in keywords and (summa_buy != 0 or summa_sell != 0)):
                    if len(Dic_Buy) != 0:  # если есть сетка buy
                        for k in Dic_Buy:
                            if k == line[5]:
                                Dic_Buy[str(line[5]) + 'close'] = -round(float(line[4]), 2)
                                # a = float(line[10])
                                profit_buy.append(float(line[10]))
                                close_price_buy.append(float(line[6]))#собираем цены закрытия что бы высчитать среднюю
                                break
                    summa_buy = round(sum(Dic_Buy.values()), 2)

                    if len(Dic_Sell) != 0:  # если есть сетка sell
                        for k in Dic_Sell:
                            if k == line[5]:
                                Dic_Sell[str(line[5]) + 'close'] = -round(float(line[4]), 2)
                                profit_sell.append(float(line[10]))
                                close_price_sell.append(float(line[6]))#собираем цены закрытия что бы высчитать среднюю
                                break
                    summa_sell = round(sum(Dic_Sell.values()), 2)

                if summa_buy == 0 and len(Dic_Buy) != 0:  # если количество открытых ордеров равно закрытым значит сетка
                    # закрылась
                    Dic_Buy_list = list(Dic_Buy.values())
                    main_list = [line[1], time_start_grid_buy, line[0], 'buy', Dic_Buy_list, profit_buy,
                                 price_start_grid_buy,
                                 line[6], last_price_grid_buy, 0, line[11], close_price_buy]
                    last_price_grid_buy = 0
                    pandas_table = pandas_table.append(prepare_pandas_table_data(main_list), ignore_index=True)

                    Dic_Buy.clear()
                    profit_buy.clear()
                    time_start_grid_buy = 0
                    main_list.clear()
                    close_price_buy.clear()

                if summa_sell == 0 and len(Dic_Sell) != 0:  # если количество открытых ордеров равно закрытым значит сетка
                    # подготавливаем данные для обработки и занесеня в таблицу
                    # data start|data end|buy/sell|grid|orders|profit|start price|close price|commision|balance
                    Dic_Sell_list = list(Dic_Sell.values())
                    main_list = [line[1], time_start_grid_sell, line[0], 'sell', Dic_Sell_list, profit_sell,
                                 price_start_grid_sell,
                                 line[6], last_price_grid_sell, 0, line[11], close_price_sell]
                    last_price_grid_sell = 0
                    pandas_table = pandas_table.append(prepare_pandas_table_data(main_list), ignore_index=True)

                    Dic_Sell.clear()
                    profit_sell.clear()
                    time_start_grid_sell = 0
                    main_list.clear()
                    close_price_sell.clear()
        self.pandas_table = pandas_table
        self.pandas_table.to_csv(SetGetConfig('get', 'file path for temp files', 'file path')+'pandas_table.csv')

    def create_pandas_table_MT5(self):
            summa_lots_buy = 0
            summa_lots_sell = 0
            Dic_Buy = []
            Dic_Sell = []
            profit_buy = []
            profit_sell = []
            time_start_grid_buy = 0
            time_start_grid_sell = 0
            price_start_grid_buy = 0
            price_start_grid_sell = 0
            commision_buy = []
            commision_sell = []
            last_price_grid = 0
            last_price_grid_sell = 0  # здесь будем запоминать наибольшую цену открытия сетки
            last_price_grid_buy = 0
            close_price_buy = []
            close_price_sell = []
            pandas_table = pd.DataFrame()  # инициализируем пустую таблицу сделок
            # file_csv = get_file_name(file)
            with open(SetGetConfig('get', 'file path for temp files', 'file path') + self.csv_name, mode='r', encoding='utf-8') as file_r:
                reader = csv.reader(file_r)
                for line in reader:
                    if line[0] == 'time':  # если это шапка таблицы то пропускаем
                        continue
                    if line[2] == 'buy' and line[3] == 'in':  # если это строка покупки
                        if len(Dic_Buy) == 0:  # если сетка бай еще не существует
                            time_start_grid_buy = line[0]
                            price_start_grid_buy = line[6]
                        Dic_Buy.append(round(float(line[4]), 2))
                        summa_lots_buy = round(sum(Dic_Buy), 2)
                        commision_buy.append(round(float(line[9]), 2))
                        # last_price_grid = line[6]
                        if last_price_grid_buy == 0:
                            last_price_grid_buy = line[6]
                        elif line[6] > last_price_grid_buy:
                            last_price_grid_buy = line[6]
                        continue
                    if line[2] == 'sell' and line[3] == 'in':  # если это строка продажи
                        if len(Dic_Sell) == 0:  # если сетка селл еще не существует
                            time_start_grid_sell = line[0]
                            price_start_grid_sell = line[6]
                        Dic_Sell.append(round(float(line[4]), 2))
                        summa_lots_sell = round(sum(Dic_Sell), 2)
                        commision_sell.append(round(float(line[9]), 2))
                        # last_price_grid = line[6]
                        if last_price_grid_sell == 0:
                            last_price_grid_sell = line[6]
                        elif line[6] > last_price_grid_sell:
                            last_price_grid_sell = line[6]
                        continue
                    if line[2] == 'sell' and line[3] == 'out' and summa_lots_buy != 0:  # если ордер бай закрывается
                        Dic_Buy.append(-round(float(line[4]), 2))
                        profit_buy.append(float(line[10]))
                        summa_lots_buy = round(sum(Dic_Buy), 2)
                        commision_buy.append(round(float(line[9]), 2))
                        close_price_buy.append(float(line[6]))
                    if summa_lots_buy == 0 and len(Dic_Buy) != 0:  # если сетка закрылась
                        # symbol|data start|data end|buy/sell|orders|profit|start price|close price|lastPriceGrid|commision|balance
                        main_list = [line[1], time_start_grid_buy, line[0], 'buy', Dic_Buy, profit_buy,
                                     price_start_grid_buy,
                                     line[6], last_price_grid_buy, commision_buy, line[11], close_price_buy]
                        pandas_table = pandas_table.append(prepare_pandas_table_data(main_list), ignore_index=True)
                        # print(main_list)
                        Dic_Buy.clear()
                        profit_buy.clear()
                        time_start_grid_buy = 0
                        commision_sell.clear()
                        main_list.clear()
                        close_price_buy.clear()
                        last_price_grid_buy = 0
                        continue

                    if line[2] == 'buy' and line[3] == 'out' and summa_lots_sell != 0:
                        Dic_Sell.append(-round(float(line[4]), 2))
                        profit_sell.append(float(line[10]))
                        summa_lots_sell = round(sum(Dic_Sell), 2)
                        commision_sell.append(round(float(line[9]), 2))
                        close_price_sell.append(float(line[6]))
                    if summa_lots_sell == 0 and len(Dic_Sell) != 0:
                        # symbol|data start|data end|buy/sell|orders|profit|start price|close price|lastPriceGrid|commision|balance
                        main_list = [line[1], time_start_grid_sell, line[0], 'sell', Dic_Sell, profit_sell,
                                     price_start_grid_sell,
                                     line[6], last_price_grid_sell, commision_sell, line[11], close_price_sell]
                        pandas_table = pandas_table.append(prepare_pandas_table_data(main_list), ignore_index=True)
                        # print(main_list)
                        Dic_Sell.clear()
                        profit_sell.clear()
                        time_start_grid_sell = 0
                        commision_sell.clear()
                        main_list.clear()
                        close_price_sell.clear()
                        last_price_grid_sell = 0

            # return pandas_table
            self.pandas_table = pandas_table
            self.pandas_table.to_csv(SetGetConfig('get', 'file path for temp files', 'file path') + 'pandas_table.csv')

    def create_csv_file_of_deals(self):
        if self.type_report == None:
            self.create_csv_file_of_deal_MT4()
        if self.type_report == 'UTF-16':
            self.create_csv_file_of_deal_MT5()

    def create_pandas_table(self):
        if self.type_report == None:
            self.create_pandas_table_MT4()
        if self.type_report == 'UTF-16':
            self.create_pandas_table_MT5()

    def get_max_grid(self):
        '''
        максимальное колличество колен сетки
        '''
        # self.num_max_grid = 0
        for row in self.pandas_table.itertuples():
            if row[5] > self.num_max_grid:
                self.num_max_grid = int(row[5])
        # print(f'Max grid = {num_max_grid}')

    def create_final_table1(self):
        table1 = np.zeros((self.num_max_grid, 42))  # 42 количество столбцов в таблице
        for row in self.pandas_table.itertuples():
            #подсчет количества сеток
            if row[13] == 'sell':
                n = 0
            else:n = 1
            m = int(row[5]-1)# ячейка с количеством колен, уменьшенная на 1 , т.к в матрице нумерация с 0
            table1[m][n] +=1
            #подсчет суммы лотов
            if row[13] == 'sell':
                n = 3
            else:
                n = 4
            table1[m][n] += row[10]
            #общая прибыль
            if row[13] == 'sell':
                n = 6
            else:
                n = 7
            table1[m][n] += row[11]

            #максимальный размер сетки в пунктах
            if row[13] == 'sell':
                n = 15
            else:
                n = 16
            if row[6] > table1[m][n]:
                table1[m][n] = row[6]

            #Средний размер сетки
            if row[13] == 'sell':
                n = 30
            else:
                n = 31
            table1[m][n] += row[6]
            table1[m][n+2] +=1

            #максимальное количество пунктов до профита
            if row[13] == 'sell':
                n = 20
            else:
                n = 21
            a = row[2]
            b = row[4]
            points = abs(float(a)-float(b))#todo надо определить количество знаков после запятой Digits
            if points > table1[m][n]:
                table1[m][n] = points

            #среднее колличество пунктов до профита
            if row[13] == 'sell':
                n = 34
            else:
                n = 35
            a = row[2]
            b = row[4]
            points = abs(float(a) - float(b))  # todo надо определить количество знаков после запятой Digits
            table1[m][n] += points
            table1[m][n + 2] += 1

            #максимальное время жизни сетки в минутах
            if row[13] == 'sell':
                n = 25
            else:
                n = 26
            if row[12] > table1[m][n]:
                table1[m][n] = row[12]

            #среднее время существования сетки
            if row[13] == 'sell':
                n = 38
            else:
                n = 39
            table1[m][n] += row[12]
            table1[m][n + 2] += 1
            # сформировал все кроме % от общей прибыли - это надо считать в завершенное матрице

            for i in range(self.num_max_grid):
                table1[i][2] = table1[i][0] + table1[i][1]# сумма сеток бай и селл
                table1[i][5] = table1[i][3] + table1[i][4]  # сумма лотов бай и селл
                table1[i][8] = table1[i][7] + table1[i][6]  # сумма общая прибыль
                if table1[i][0] != 0:
                    table1[i][9] = table1[i][6] / table1[i][0]  # средняя прибыль селл
                if table1[i][1] != 0:
                    table1[i][10] = table1[i][7] / table1[i][1]  # средняя прибыль buy

                if table1[i][2] != 0:
                    table1[i][11] = (table1[i][9]*table1[i][0] + table1[i][10]*table1[i][1])/table1[i][2]

                x = float(self.total_profit)# изначатьно self.total_profit string
                if x != 0:
                    table1[i][12] = table1[i][6]/x*100#процент от общей прибыли селл
                    table1[i][13] = table1[i][7] / x * 100#процент от общей прибыли бай
                    table1[i][14] = table1[i][12] + table1[i][13]#процент от общей прибыли сумма
                #определяем средний размер сетки
                if i != 0:# для одного колена нет длины сетки
                    if table1[i][32] != 0:#если количество сеток равно 0
                        table1[i][17] = table1[i][30]/table1[i][32]
                    if table1[i][33] != 0:#если количество сеток равно 0
                        table1[i][18] = table1[i][31]/table1[i][33]
                    if table1[i][2] != 0:
                        table1[i][19] = (table1[i][17]*table1[i][0] + table1[i][18]*table1[i][1])/table1[i][2]
                #34,35 среднее количество пунктов до профита
                if table1[i][36] != 0:
                    table1[i][22] = table1[i][34]/table1[i][36]
                if table1[i][37] != 0:
                    table1[i][23] = table1[i][35]/table1[i][37]
                if table1[i][2] != 0:
                    table1[i][24] = (table1[i][22]*table1[i][0] + table1[i][23]*table1[i][1])/table1[i][2]
                # среднее время жизни сетки 38, 39
                if table1[i][40] != 0:
                    table1[i][27] = table1[i][38]/table1[i][40]
                if table1[i][41] != 0:
                    table1[i][28] = table1[i][39]/table1[i][41]
                if table1[i][2] != 0:
                    if table1[i][2] != 0:
                        table1[i][29] = (table1[i][27]*table1[i][0] + table1[i][28]*table1[i][1])/table1[i][2]
        # создана первая таблица теперь надо отформатировать данные и можно публиковать
        pandas_final_table1 = pd.DataFrame()  # инициализируем пустую таблицу 1
        # list_of_grid = {"Date": date_close, 'Year': year_, 'Month': month_, 'Type_of_grid': type_of_grid}
        for i in range(self.num_max_grid):
            grid = f'{int(table1[i][0])}/{int(table1[i][1])}/{int(table1[i][2])}'
            sum_lots = f'{round(table1[i][3],2)}/{round(table1[i][4],2)}/{round(table1[i][5],2)}'
            all_profit = f'{round(table1[i][6], 2)}/{round(table1[i][7], 2)}/{round(table1[i][8], 2)}'
            avrg_profit = f'{round(table1[i][9], 2)}/{round(table1[i][10], 2)}/{round(table1[i][11], 2)}'
            procent_profit = f'{round(table1[i][12], 2)}/{round(table1[i][13], 2)}/{round(table1[i][14], 2)}'
            max_grid_size = f'{int(table1[i][15])}/{int(table1[i][16])}'
            avrg_grid_size = f'{int(table1[i][17])}/{int(table1[i][18])}/{int(table1[i][19])}'
            max_points_to_profit = f'{int(table1[i][20]*self.digits)}/{int(table1[i][21]*self.digits)}'
            avrg_points_to_profit = f'{int(table1[i][22]*self.digits)}/{int(table1[i][23]*self.digits)}/{int(table1[i][24]*self.digits)}'

            max_time_grid = f'{int(table1[i][25])}/{int(table1[i][26])}'
            avrg_time_grid = f'{int(table1[i][27])}/{int(table1[i][28])}/{int(table1[i][29])}'
            dic = {'grid':grid, 'sum_lots':sum_lots, 'all_profit':all_profit, 'avrg_profit':avrg_profit,
                   'procent_profit':procent_profit, 'max_grid_size':max_grid_size, 'avrg_grid_size':avrg_grid_size,
                   'max_points_to_profit':max_points_to_profit, 'avrg_points_to_profit':avrg_points_to_profit,
                   'max_time_grid':max_time_grid, 'avrg_time_grid':avrg_time_grid}
            pandas_final_table1 = pandas_final_table1.append(dic, ignore_index=True)
        self.table1 = pandas_final_table1

    def get_time_frame(self):
        if self.type_report == None:
            with open(self.file_path, encoding=self.type_report) as f:
                if self.language == 'EN':
                    # symbol = 'Symbol'
                    tf = 'Period'
                    # deposit = 'Initial deposit'
                    # maximal_drawdown = 'Maximal drawdown'
                    # profit = 'Total net profit'
                if self.language == 'RU':
                    # symbol = 'Символ'
                    tf = 'Период'
                    # deposit = 'Начальный депозит'
                    # maximal_drawdown = 'Максимальная просадка'
                    # profit = 'Чистая прибыль'
                for line in f:
                    if tf in line:
                        soup = BeautifulSoup(line, 'html.parser')
                        tfMT4 = soup.contents[0].contents[1].get_text()
                        tfMT4 = tfMT4.split('(')[0]
                        break
                    # if period in line:
                    #     soup = BeautifulSoup(line, 'html.parser')
                    #     periodMT4 = soup.contents[0].contents[1]
            self.time_frame = tfMT4
        if self.type_report == 'UTF-16':
            n = 0
            with open(self.file_path, encoding=self.type_report) as f:
                if self.language == 'EN':
                    tf = 'Period'
                if self.language == 'RU':
                    tf = 'Период'
                for line in f:
                    if n == 1:
                        soup = BeautifulSoup(line, 'html.parser')
                        per = soup.text  # тут получаем название символа с двумя лишними пробелами впереди
                        self.time_frame = per[1:3]  # обрезаем два лишних пробела впереди
                        break
                    if tf in line:
                        soup = BeautifulSoup(line, 'html.parser')
                        n = 1
                        continue

    def get_testing_period(self):
        if self.type_report == None:
            with open(self.file_path, encoding=self.type_report) as f:
                if self.language == 'EN':
                    # symbol = 'Symbol'
                    tf = 'Period'
                    # deposit = 'Initial deposit'
                    # maximal_drawdown = 'Maximal drawdown'
                    # profit = 'Total net profit'
                if self.language == 'RU':
                    # symbol = 'Символ'
                    tf = 'Период'
                    # deposit = 'Начальный депозит'
                    # maximal_drawdown = 'Максимальная просадка'
                    # profit = 'Чистая прибыль'
                for line in f:
                    if tf in line:
                        soup = BeautifulSoup(line, 'html.parser')
                        tfMT4 = soup.contents[0].contents[1].get_text()
                        a = tfMT4.split(')')[1]
                        b = a.split('(')[0]
                        tfMT4 = b.strip()
                        c = colculate_test_period(tfMT4)[0]
                        self.period = c
                        self.month = colculate_test_period(tfMT4)[1]
                        break
        if self.type_report == 'UTF-16':
            n = 0
            with open(self.file_path, encoding=self.type_report) as f:
                if self.language == 'EN':
                    tf = 'Period'
                if self.language == 'RU':
                    tf = 'Период'
                for line in f:
                    if n == 1:
                        soup = BeautifulSoup(line, 'html.parser')
                        per = soup.text  # тут получаем название символа с двумя лишними пробелами впереди
                        a = per.split('(')[1][0:-2]
                        self.period = colculate_test_period(a)[0]
                        self.month = colculate_test_period(a)[1]
                        break
                    if tf in line:
                        soup = BeautifulSoup(line, 'html.parser')
                        n = 1
                        continue
        if self.month == 0:# чтобы не делить на 0
            self.month =1

    def make_table2_3(self):
        first_year = self.period[0:4]
        last_year = self.period[19:23]
        row_ = int(last_year) - int(first_year)

        row_ += 2

        table2 = np.zeros((row_, 15))
        table3 = np.zeros((row_, 15))

        for row in self.pandas_table.itertuples():
            month_ = int(row[7])# месяц записи
            year_ = row[3].year  # год записи
            line = year_ - int(first_year)
            table2[line,month_] += row[11] - row[9]# профит минус комиссия
            table2[line][0] = year_
            table3[line][0] = year_

            #запоним таблицу 3, максимальными коленами за месяц
            if table3[line,month_] < row[5]:
                table3[line, month_] = row[5]
        # посчитаем сумму прибыли за года
        for j in range(row_):
            for i in range(1,13):
                table2[j][14] += table2[j,i]
                table3[j][14] += table3[j, i]# это значение нам понадобиться что бы узнать среднее колено за год
        self.table2 = table2
        # посчитаем среднюю прибыль
        for j in range(row_):
            k = 0# количество ненулевых месяцев для таблицы 2
            n = 0# количество ненулевых месяцев для таблицы 3
            for i in range(1,13):
                # посчитаем количество не нулевых месяцев
                if table2[j][i] != 0:
                    k += 1
                if table3[j][i] != 0:
                    n += 1
            if k != 0:
                table2[j][13] = table2[j][14]/k
            if n != 0:
                table3[j][13] = table3[j][14]/n
        #заполним последнюю строку таблицы 2 и 3
        for i in range(1, 14):
            sum2 = 0
            k2 = 0
            sum3 = 0
            k3 = 0
            for j in range(row_-1):
                if table2[j][i] != 0:
                    sum2 += table2[j][i]
                    k2 += 1
                if table3[j][i] != 0:
                    sum3 += table3[j][i]
                    k3 += 1
            if k2 != 0:
                table2[row_-1,i] = sum2/k2
            if k3 != 0:
                table3[row_-1,i] = sum3/k3
        #посчитаем общую прибыль за весь период
        for j in range(row_-1):
            table2[row_-1][14] += table2[j][14]
        self.table3 = table3

    def get_profitability(self):
        # self.deposit = deposit
        # self.drawdown = drawdown
        # self.month = month
        # self.total_profit
        in_month = round((float(self.total_profit) / float(self.month)/float(self.deposit)*100),2)
        in_year = round((in_month*12),2)
        dd = self.drawdown.split('(')[0]
        k = float(self.total_profit)/self.month*12/float(dd)
        self.profitability = f'{in_month}% в месяц; {in_year}% в год; Кэф = {round(k,2)}'




    def get_expert_name(self):
        pass




# start_time = time.time()
# report = Main_info(file_path=file)
# print('путь файла==' + report.file_path)
# report.detect_type_of_report()
# # print(report.type_report)
# report.detect_language()
# print(report.language)
#
# report.get_set()
# print(f'set of FILE = {report.set_file}')
# # for item in report.set_file:
# #     print(item)

# report.get_symbol()
# # print(report.symbol)
# report.get_csv_file_name()
# # print(report.csv_name)
# report.get_total_profit()
#
# report.create_csv_file_of_deals()
# report.create_pandas_table()
# # print(report.pandas_table)
# report.get_max_grid()
# # print(report.num_max_grid)
# report.create_final_table1()
# # print("Table1")
# # print(report.table1)
# rep = report.table1
# report.get_time_frame()
# print(f'Time Frame = {report.time_frame}')
#
# report.get_testing_period()
# print(f'Testing period = {report.period}')#2019.01.01 - 2019.01.15
# #
# report.make_table2_3()
#
#
# report.get_deposit()
# print(f'depo ====== {report.deposit}')
#
# report.get_drawdown()
# print(f'DD ====== {report.drawdown}')
#
# report.get_profitability()
# print(f'рентабельность ===== {report.profitability}')
#
# report.get_digits()
#
#
# all_time = time.time() - start_time
# print('Proccesing Time = ', str(all_time))




