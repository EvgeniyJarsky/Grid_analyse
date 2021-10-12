from chardet.universaldetector import UniversalDetector
from bs4 import BeautifulSoup
import datetime
import os.path
import os
import pandas as pd
import numpy as np


def string_to_time(time):
    # :param time: string 2015.02.16 19:59:58
    # :return: type datatime  2015-02-16 19:59:58
    year = int(time[0:4])
    month = int(time[5:7])
    day = int(time[8:10])
    hour = int(time[11:13])
    minut = int(time[14:16])
    sec = int(time[-2:])
    time = datetime.datetime(year, month, day, hour, minut, sec)
    # print(year + month + day + hour + minut + sec)
    return time


def get_coding(path_to_file):
    """
    определяем кодировку файла
    path_to_file = 'C:/Users/Evgeniy/PycharmProjects/bs/MT5Long.html'
    :param path_to_file
    :return: str 'UTF-16' тогда это MT5 или 'None' тогда это MT4
    """
    detector = UniversalDetector()
    count = 0
    maxl = 3
    with open(path_to_file, 'rb') as f:
        for line in f:
            count += 1
            detector.feed(line)
            if count >= maxl:
                cod = detector.result['encoding']
                break  # todo если убрать этот break то работать будет долго
            if detector.done:
                detector.close()
                break
        cod = detector.result['encoding']
        return cod


def get_file_name(path_to_file):
    return os.path.basename(path_to_file)


def get_language(path_to_file, coding):
    # if self.type_report == 'MetaTrader4':
    #     cod = None
    # else:
    #     cod = 'UTF-16'
    with open(path_to_file, encoding=coding) as f:
        language = 'None'
        for line in f:
            if 'Symbol' in line:
                language = 'EN'
                break
            if 'Символ' in line:
                language = 'RU'
                break
    return language


def get_symbol(path_to_file, coding, language):
    if coding is None:
        with open(path_to_file, encoding=coding) as f:
            if language == 'EN':
                symbol = 'Symbol'
            if language == 'RU':
                symbol = 'Символ'
            for line in f:
                if symbol in line:
                    soup = BeautifulSoup(line, 'html.parser')
                    symbol_mt4 = soup.contents[0].contents[1].get_text()
                    symbol_mt4 = symbol_mt4.split('(')[0]
                    break
        return symbol_mt4
    else:
        with open(path_to_file, encoding=coding) as f:
            if language == 'EN':
                symbol = 'Symbol'
            if language == 'RU':
                symbol = 'Символ'
            for line in f:
                if symbol in line:
                    line = next(f)
                    soup = BeautifulSoup(line, 'html.parser')
                    symbol_mt5 = soup.text[1:7]
                    return symbol_mt5


def get_time_frame(path_to_file, coding, language):
    if coding is None:
        with open(path_to_file, encoding=coding) as f:
            if language == 'EN':
                keyword = 'Period'
            if language == 'RU':
                keyword = 'Период'
            for line in f:
                if keyword in line:
                    soup = BeautifulSoup(line, 'html.parser')
                    time_frame = soup.contents[0].contents[1].get_text().split('(')[0]
                    # tfMT4 = tfMT4.split('(')[0]
                    return time_frame
    else:
        with open(path_to_file, encoding=coding) as f:
            if language == 'EN':
                keyword = 'Period'
            if language == 'RU':
                keyword = 'Период'
            for line in f:
                if keyword in line:
                    line = next(f)
                    time_frame = BeautifulSoup(line, 'html.parser').text[1:3]
                    return time_frame


def get_testing_period(path_to_file, coding, language):
    def colculate_test_period(period_):
        # 2011.05.02 17:14 - 2011.05.02 17:14
        #
        # '2015.06.01 - 2015.10.30'
        # 73
        # year = 6 and 1 months
        # :param period:
        # :return:
        def months(d_start, d_finish):
            # вычисляет количество месяцев между датами
            # :param d_start: дата начала торгов в отчете
            # :param d_finish: дата конца торгов в отчете
            # :return: int количество месяцев
            return d_finish.month - d_start.month + 12 * (d_finish.year - d_start.year)

        period_ = period_.split(' - ')
        testing_dates = {'start': period_[0], 'finish': period_[1]}
        testper = f"{testing_dates['start']} - {testing_dates['finish']}"
        # для MT5 ужно добавить часы
        if len(testing_dates['start']) == 10:
            start = testing_dates['start']
            finish = testing_dates['finish']
            testing_dates['start'] = start + ' 00:00'  # f'{start} 00:00'
            testing_dates['finish'] = finish + ' 23:59'
            testper = f"{testing_dates['start']} - {testing_dates['finish']}"
        months2 = months(string_to_time(testing_dates['start']), string_to_time(testing_dates['finish']))
        year = months2 // 12
        months1 = months2 % 12
        period_list = []
        all_string = f'{testper}; {year} лет и {months1} месяцев или {months2} месяцев'
        period_list.append(all_string)
        period_list.append(months2)
        return period_list

    if coding is None:
        with open(path_to_file, encoding=coding) as f:
            if language == 'EN':
                keyword = 'Period'
            if language == 'RU':
                keyword = 'Период'
            for line in f:
                if keyword in line:
                    soup = BeautifulSoup(line, 'html.parser')
                    period = soup.contents[0].contents[1].get_text()
                    period = period.split(')')[1].split('(')[0].strip()
                    period = colculate_test_period(period)
                    return period
    else:
        with open(path_to_file, encoding=coding) as f:
            if language == 'EN':
                keyword = 'Period'
            if language == 'RU':
                keyword = 'Период'
            for line in f:
                if keyword in line:
                    line = next(f)
                    soup = BeautifulSoup(line, 'html.parser')
                    period = soup.text.split('(')[1][0:-2]
                    period = colculate_test_period(period)
                    return period


def get_deposit(path_to_file, coding, language):
    if coding is None:
        with open(path_to_file, encoding=coding) as f:
            if language == 'EN':
                keyword = 'Initial deposit'
            if language == 'RU':
                keyword = 'Начальный депозит'
            for line in f:
                if keyword in line:
                    soup = BeautifulSoup(line, 'html.parser')
                    depo = soup.contents[0].contents[1].text
                    return depo
    else:
        with open(path_to_file, encoding=coding) as f:
            if language == 'EN':
                keyword = 'Initial Deposit'
            if language == 'RU':
                keyword = 'Начальный депозит'
            for line in f:
                if keyword in line:
                    line = next(f)
                    soup = BeautifulSoup(line, 'html.parser')
                    deposit = ''.join(soup.text.rstrip().split())
                    return deposit


def get_total_profit(path_to_file, coding, language):
    if coding is None:
        with open(path_to_file, encoding=coding) as f:
            if language == 'EN':
                keyword = 'Total net profit'
            if language == 'RU':
                keyword = 'Чистая прибыль'
            for line in f:
                if keyword in line:
                    soup = BeautifulSoup(line, 'html.parser')
                    profit = soup.contents[0].contents[1].get_text().split('(')[0]
                    return profit
    else:
        with open(path_to_file, encoding=coding) as f:
            if language == 'EN':
                profit = 'Total Net Profit'
            if language == 'RU':
                profit = 'Чистая прибыль'
            for line in f:
                if profit in line:
                    line = next(f)
                    soup = BeautifulSoup(line, 'html.parser')
                    profit = ''.join((soup.text[0:-2]).split())
                    return profit


def get_drawdown(path_to_file, coding, language):
    if coding is None:
        with open(path_to_file, encoding=coding) as f:
            if language == 'EN':
                maximal_drawdown = 'Maximal drawdown'
            if language == 'RU':
                maximal_drawdown = 'Максимальная просадка'
            for line in f:
                if maximal_drawdown in line:
                    soup = BeautifulSoup(line, 'html.parser')
                    dd = soup.contents[0].contents[3].text
                    return dd
    else:
        with open(path_to_file, encoding=coding) as f:
            if language == 'EN':
                maximal_drawdown = 'Balance Drawdown Maximal'
            if language == 'RU':
                maximal_drawdown = 'Максимальная просадка'
            for line in f:
                if maximal_drawdown in line:
                    line = next(f)
                    soup = BeautifulSoup(line, 'html.parser')
                    dd = ''.join(soup.text.rstrip().split())
                    return dd


def get_profitability(deposit, dd, month, profit):
    # что бы не было деления на ноль
    if month == 0:
        month = 1
    in_month = round((float(profit) / float(month) / float(deposit) * 100), 2)
    in_year = round((in_month * 12), 2)
    dd = dd.split('(')[0]
    k = float(profit) / month * 12 / float(dd)
    profitability = f'{in_month}% в месяц; {in_year}% в год; Кэф = {round(k, 2)}'
    return profitability


def get_csv_file_name(path_to_file):
    full_name = os.path.basename(path_to_file)
    csv_name = os.path.splitext(full_name)[0] + '.csv'
    return csv_name


class Report:
    def __init__(self, path_to_file):
        self.pathToFile = path_to_file  # полный путь к файлу
        self.fileName = get_file_name(self.pathToFile)  # имя файла с расширрением
        self.coding = get_coding(self.pathToFile)  # кодировка файла
        self.language = get_language(self.pathToFile, self.coding)  # язык отчета
        self.symbol = get_symbol(self.pathToFile, self.coding, self.language)  # символ
        self.timeFrame = get_time_frame(self.pathToFile, self.coding, self.language)  # период на котором тестировался
        # советник
        self.testingPeriod = get_testing_period(self.pathToFile, self.coding, self.language)[0]  # период тестирования
        self.deposit = get_deposit(self.pathToFile, self.coding, self.language)  # начальный депозит
        self.profit = get_total_profit(self.pathToFile, self.coding, self.language)  # суммарная прибыль
        self.drawdown = get_drawdown(self.pathToFile, self.coding, self.language)  # просадка
        months = get_testing_period(self.pathToFile, self.coding, self.language)[1]  # общее количество месяцев теста
        self.profitability = get_profitability(self.deposit, self.drawdown, months, self.profit)  # рентабельность
        self.csvFileName = get_csv_file_name(self.pathToFile)  # имя файла csv созданное на основе имени файла отчета

        self.grid_table = 0
        self.table = 0
        self.grid_table = 0
        self.num_max_grid = 0
        self.digits = 0
        self.table1 = 0
        self.table2 = 0
        self.table3 = 0
        self.set_faile = 0

    def deals_list(self):
        # создаем Пандас таблицу сделок
        def one_in_line(line_, itertupl):
            # проверяет есть ли одно из слов кортежа  в строке
            for words in itertupl:
                if words in line_:
                    return True
            return False

        table = pd.DataFrame()
        with open(self.pathToFile, encoding=self.coding) as file:
            keywords = ('<td>buy</td>',
                        '<td>close</td>',
                        '<td>s/l</td>',
                        '<td>t/p</td>',
                        '<td>close at stop</td>',
                        '<td>sell</td>',
                        '<td>in</td>',
                        '<td>out</td>'
                        )
            deal = {'time': 'time', 'symbol': 'symbol', 'order_type': 'order_type', 'direction': 'direction',
                    'lot': 'lot', 'num_order': 'num_order', 'price': 'price', 'sl': 'sl',
                    'tp': 'tp', 'commisions': 0, 'profit': 'profit', 'balance': 'balance'}
            start_string = '<table width=820 cellspacing=1 cellpadding=3 border=0>'
            signal_var = 0
            for line in file:
                if start_string in line:
                    signal_var = 1
                if signal_var == 0:
                    continue
                if one_in_line(line, keywords):
                    soup = BeautifulSoup(line, 'html.parser')
                    deal['time'] = soup.contents[0].contents[1].get_text()
                    deal['symbol'] = self.symbol
                    deal['order_type'] = soup.contents[0].contents[2].get_text()
                    deal['num_order'] = soup.contents[0].contents[3].get_text()
                    deal['lot'] = soup.contents[0].contents[4].get_text()
                    deal['price'] = soup.contents[0].contents[5].get_text()
                    deal['sl'] = soup.contents[0].contents[6].get_text()
                    deal['tp'] = soup.contents[0].contents[7].get_text()
                    deal['profit'] = soup.contents[0].contents[8].get_text()
                    try:
                        deal['balance'] = soup.contents[0].contents[9].get_text()
                    except:
                        deal['balance'] = 0
                    table = table.append(deal, ignore_index=True)
        self.table = table
        return self.table

    def get_grid_list(self):
        # таблица сеток - одна строка - одна сетка
        #
        #
        #         0-balance
        # 1-commisions
        # 2- direction
        # 3 - lot
        # 4- num_order
        # 5 buy/sell
        # 6- price
        # 7-profit
        # 8-sl
        # 9-symbol
        # 10-time
        # 11-tp
        #
        # balance                      0
        # commisions                   0
        # direction            direction
        # lot                       0.01
        # num_order                    1
        # order_type                sell
        # price                  1.71946
        # profit
        # sl                     0.00000
        # symbol                 GBPCAD
        # time          2020.01.24 20:35
        # tp                     0.00000
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
            if n == 0: n = 1  # там где одно колено возвращает 0, тогда берем 1
            avrg_close_price = sum(main_list[11]) / n
            # avrg_close_price=0
            date_close = string_to_time(main_list[2])  # дата
            year_ = string_to_time(main_list[2]).year  # год
            month_ = string_to_time(main_list[2]).month  # месяц
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
                            'Grid_size': grid_size, 'Time_grid': time_grid, 'Balance': balance,
                            'ClosePrice': avrg_close_price,
                            'StartPrice': main_list[6], 'EndPrice': main_list[8]}
            return list_of_grid

        summa_buy = 0  # профит
        summa_sell = 0  # профит
        dic_buy = {}  # список лотов ордеров
        dic_sell = {}  # список лотов ордеров
        profit_buy = []
        profit_sell = []
        time_start_grid_buy = 0
        time_start_grid_sell = 0
        price_start_grid_buy = 0
        price_start_grid_sell = 0
        # last_price_grid = 0
        last_price_grid_sell = 0  # здесь будем запоминать наибольшую цену открытия сетки
        last_price_grid_buy = 0
        close_price_buy = []
        close_price_sell = []
        grid_list = pd.DataFrame()

        for row in self.table.itertuples():
            # Pandas(Index=0, balance=0.0, commisions=0.0, direction='direction', lot='0.01', num_order='1',
            #        order_type='sell', price='1.71946', profit='', sl='0.00000', symbol='GBPCAD ',
            #        time='2020.01.24 20:35', tp='0.00000')
            # ********************************************************************************************************
            if getattr(row, 'order_type') == 'buy':  # если это строка покупки
                if len(dic_buy) == 0:  # если словарь сделок пустой запомним время начала сетки и цену открытия
                    # первого ордера
                    time_start_grid_buy = getattr(row, 'time')
                    price_start_grid_buy = getattr(row, 'price')
                # запоминаем в виде словаря номер ордера item[4] и лот(item[3])
                dic_buy[getattr(row, 'num_order')] = round(float(getattr(row, 'lot')), 2)
                # summa_buy сумма всех лотов открытой сетки, т.к. при закрытии позы лот запоминается со знаком "-",
                # то сумма всех лотов когда закроется последний ордер сетки, будет равно 0
                summa_buy = round(sum(dic_buy.values()), 2)
                # если цена последнего открытого ордера равна 0, то запоминаем время открытия сетки
                if last_price_grid_buy == 0:
                    last_price_grid_buy = getattr(row, 'price')
                # если цена открытия текущего колена ниже чем предыдущая цена открытия. т.е сетка растянулась
                # запоминаем цену открытия текущего колена
                elif getattr(row, 'price') < last_price_grid_buy:
                    last_price_grid_buy = getattr(row, 'price')
                continue
            # *********************************************************************************************************
            if getattr(row, 'order_type') == 'sell':  # если это строка продажи
                if len(dic_sell) == 0:  # если словарь сделок пустой запомним время начала сетки
                    time_start_grid_sell = getattr(row, 'time')
                    price_start_grid_sell = getattr(row, 'price')
                dic_sell[getattr(row, 'num_order')] = round(float(getattr(row, 'lot')), 2)
                summa_sell = round(sum(dic_sell.values()), 2)
                if last_price_grid_sell == 0:
                    last_price_grid_sell = getattr(row, 'price')
                elif getattr(row, 'price') > last_price_grid_sell:
                    last_price_grid_sell = getattr(row, 'price')
                continue
            # **********************************************************************************************************
            keywords = ('close', 't/p', 's/l', 'close at stop')
            if getattr(row, 'order_type') in keywords and (
                    summa_buy != 0 or summa_sell != 0):  # если это строка закрытия позы
                # *********************************************
                if len(dic_buy) != 0:  # если есть сетка buy
                    # перебираем dic_buy и сраниваем номер ордера с тем который закрылся
                    for order_number in dic_buy:
                        if getattr(row, 'num_order') == order_number:
                            dic_buy[str(getattr(row, 'num_order')) + 'close'] = -round(float(getattr(row, 'lot')), 2)
                            profit_buy.append(
                                float(getattr(row, 'profit')))  # todo надо посмотреть а что если профита нет?
                            # собираем цены закрытия что бы высчитать среднюю
                            close_price_buy.append(float(getattr(row, 'price')))
                            break
                # посчитаем сумму лотов buy ордеров (ордера закрытия занесены со знаком минус)
                summa_buy = round(sum(dic_buy.values()), 2)
                # ************************************************
                # *********************************************
                if len(dic_sell) != 0:  # если есть сетка sell
                    # перебираем dic_sell и сраниваем номер ордера с тем который закрылся
                    for order_number in dic_sell:
                        if getattr(row, 'num_order') == order_number:
                            dic_sell[str(getattr(row, 'num_order')) + 'close'] = -round(float(getattr(row, 'lot')), 2)
                            profit_sell.append(
                                float(getattr(row, 'profit')))  # todo надо посмотреть а что если профита нет?
                            # собираем цены закрытия что бы высчитать среднюю
                            close_price_sell.append(float(getattr(row, 'price')))
                            break
                # посчитаем сумму лотов buy ордеров (ордера закрытия занесены со знаком минус)
                summa_sell = round(sum(dic_sell.values()), 2)
            # ************************************************
            # если количество открытых ордеров равно закрытым значит сетка закрылась
            if summa_buy == 0 and len(dic_buy) != 0:
                dic_buy_list = list(dic_buy.values())  # список лотов сетки
                symbol = getattr(row, 'symbol')
                close_date = getattr(row, 'time')
                something = '???'  # todo я не знаю что это за параметр, в расчетах не учавствует
                balance = getattr(row, 'balance')
                grid_list_sum_info = (
                    symbol,
                    time_start_grid_buy,
                    close_date,
                    'buy',
                    dic_buy_list,
                    profit_buy,
                    price_start_grid_buy,
                    something,
                    last_price_grid_buy,
                    0,  # comission
                    balance,
                    close_price_buy
                )
                grid_list = grid_list.append(prepare_pandas_table_data(grid_list_sum_info), ignore_index=True)
                # очистим переменные
                dic_buy.clear()
                profit_buy.clear()
                time_start_grid_buy = 0
                grid_list_sum_info = 0
                close_price_buy.clear()
                # *****************************************************************************************************
                # если количество открытых ордеров равно закрытым значит сетка закрылась
                if summa_sell == 0 and len(dic_sell) != 0:
                    dic_sell_list = list(dic_sell.values())  # список лотов сетки
                    symbol = getattr(row, 'symbol')
                    close_date = getattr(row, 'time')
                    something = '???'  # todo я не знаю что это за параметр, в расчетах не учавствует
                    balance = getattr(row, 'balance')
                    grid_list_sum_info = (
                        symbol,
                        time_start_grid_sell,
                        close_date,
                        'sell',
                        dic_sell_list,
                        profit_sell,
                        price_start_grid_sell,
                        something,
                        last_price_grid_sell,
                        0,  # comission
                        balance,
                        close_price_sell
                    )
                    grid_list = grid_list.append(prepare_pandas_table_data(grid_list_sum_info), ignore_index=True)
                    # очистим переменные
                    dic_sell.clear()
                    profit_sell.clear()
                    time_start_grid_sell = 0
                    grid_list_sum_info = 0
                    close_price_sell.clear()
        # преобразуем типы данных в столбцах
        grid_list['Grid'] = grid_list['Grid'].astype('int')
        grid_list['Grid_size'] = grid_list['Grid_size'].astype('int')
        grid_list['Month'] = grid_list['Month'].astype('int')
        grid_list['Time_grid'] = grid_list['Time_grid'].astype('int')
        grid_list['Year'] = grid_list['Year'].astype('int')

        self.grid_table = grid_list
        return self.grid_table

    def get_max_grid_num(self):
        # максимальное количество колен в сетке
        # для расчета должны быть свормированы self.table  и потом self.grid_table
        self.num_max_grid = self.grid_table['Grid'].max()
        return self.num_max_grid

    def get_digits(self):
        count = 0  # сколько строчек пройти что бы определить количество цыфр после запятой, хотя кажется достаточно одного прохода т.к. 0 тоже пришется в конце
        digits = 0
        with open(self.pathToFile, encoding=self.coding) as f:
            for line in f:
                if 'filled' in line: continue
                if count > 3: break
                if '<td>buy</td>' in line or '<td>sell</td>' in line:
                    soup = BeautifulSoup(line, 'html.parser')
                    if self.coding == 'UTF-16':
                        x = soup.contents[1].contents[6].get_text()
                    else:
                        x = soup.contents[0].contents[5].get_text()
                    digits_after_point = len(x.split('.')[1])
                    if digits_after_point > digits:
                        digits = digits_after_point
                    count += 1
            if digits == 5:
                self.digits = 10000
            elif digits == 4:
                self.digits = 1000
            else:
                self.digits = 100
            return self.digits

    def create_final_table1(self):
        # создаем пустую матрицу
        table1 = np.zeros((self.num_max_grid, 42))  # 42 количество столбцов в таблице
        for row in self.grid_table.itertuples():
            # подсчет количества сеток
            if row[13] == 'sell':
                n = 0
            else:
                n = 1
            m = int(row[5] - 1)  # ячейка с количеством колен, уменьшенная на 1 , т.к в матрице нумерация с 0
            table1[m][n] += 1
            # подсчет суммы лотов
            if row[13] == 'sell':
                n = 3
            else:
                n = 4
            table1[m][n] += row[10]
            # общая прибыль
            if row[13] == 'sell':
                n = 6
            else:
                n = 7
            table1[m][n] += row[11]

            # максимальный размер сетки в пунктах
            if row[13] == 'sell':
                n = 15
            else:
                n = 16
            if row[6] > table1[m][n]:
                table1[m][n] = row[6]

            # Средний размер сетки
            if row[13] == 'sell':
                n = 30
            else:
                n = 31
            table1[m][n] += row[6]
            table1[m][n + 2] += 1

            # максимальное количество пунктов до профита
            if row[13] == 'sell':
                n = 20
            else:
                n = 21
            a = row[2]
            b = row[4]
            points = abs(float(a) - float(b))  # todo надо определить количество знаков после запятой Digits
            if points > table1[m][n]:
                table1[m][n] = points

            # среднее колличество пунктов до профита
            if row[13] == 'sell':
                n = 34
            else:
                n = 35
            a = row[2]
            b = row[4]
            points = abs(float(a) - float(b))  # todo надо определить количество знаков после запятой Digits
            table1[m][n] += points
            table1[m][n + 2] += 1

            # максимальное время жизни сетки в минутах
            if row[13] == 'sell':
                n = 25
            else:
                n = 26
            if row[12] > table1[m][n]:
                table1[m][n] = row[12]

            # среднее время существования сетки
            if row[13] == 'sell':
                n = 38
            else:
                n = 39
            table1[m][n] += row[12]
            table1[m][n + 2] += 1
            # сформировал все кроме % от общей прибыли - это надо считать в завершенное матрице

            for i in range(self.num_max_grid):
                table1[i][2] = table1[i][0] + table1[i][1]  # сумма сеток бай и селл
                table1[i][5] = table1[i][3] + table1[i][4]  # сумма лотов бай и селл
                table1[i][8] = table1[i][7] + table1[i][6]  # сумма общая прибыль
                if table1[i][0] != 0:
                    table1[i][9] = table1[i][6] / table1[i][0]  # средняя прибыль селл
                if table1[i][1] != 0:
                    table1[i][10] = table1[i][7] / table1[i][1]  # средняя прибыль buy

                if table1[i][2] != 0:
                    table1[i][11] = (table1[i][9] * table1[i][0] + table1[i][10] * table1[i][1]) / table1[i][2]

                x = float(self.profit)  # изначатьно self.total_profit string
                if x != 0:
                    table1[i][12] = table1[i][6] / x * 100  # процент от общей прибыли селл
                    table1[i][13] = table1[i][7] / x * 100  # процент от общей прибыли бай
                    table1[i][14] = table1[i][12] + table1[i][13]  # процент от общей прибыли сумма
                # определяем средний размер сетки
                if i != 0:  # для одного колена нет длины сетки
                    if table1[i][32] != 0:  # если количество сеток равно 0
                        table1[i][17] = table1[i][30] / table1[i][32]
                    if table1[i][33] != 0:  # если количество сеток равно 0
                        table1[i][18] = table1[i][31] / table1[i][33]
                    if table1[i][2] != 0:
                        table1[i][19] = (table1[i][17] * table1[i][0] + table1[i][18] * table1[i][1]) / table1[i][2]
                # 34,35 среднее количество пунктов до профита
                if table1[i][36] != 0:
                    table1[i][22] = table1[i][34] / table1[i][36]
                if table1[i][37] != 0:
                    table1[i][23] = table1[i][35] / table1[i][37]
                if table1[i][2] != 0:
                    table1[i][24] = (table1[i][22] * table1[i][0] + table1[i][23] * table1[i][1]) / table1[i][2]
                # среднее время жизни сетки 38, 39
                if table1[i][40] != 0:
                    table1[i][27] = table1[i][38] / table1[i][40]
                if table1[i][41] != 0:
                    table1[i][28] = table1[i][39] / table1[i][41]
                if table1[i][2] != 0:
                    if table1[i][2] != 0:
                        table1[i][29] = (table1[i][27] * table1[i][0] + table1[i][28] * table1[i][1]) / table1[i][2]
        # создана первая таблица теперь надо отформатировать данные и можно публиковать
        pandas_final_table1 = pd.DataFrame()  # инициализируем пустую таблицу 1
        # list_of_grid = {"Date": date_close, 'Year': year_, 'Month': month_, 'Type_of_grid': type_of_grid}
        for i in range(self.num_max_grid):
            grid = f'{int(table1[i][0])}/{int(table1[i][1])}/{int(table1[i][2])}'
            sum_lots = f'{round(table1[i][3], 2)}/{round(table1[i][4], 2)}/{round(table1[i][5], 2)}'
            all_profit = f'{round(table1[i][6], 2)}/{round(table1[i][7], 2)}/{round(table1[i][8], 2)}'
            avrg_profit = f'{round(table1[i][9], 2)}/{round(table1[i][10], 2)}/{round(table1[i][11], 2)}'
            procent_profit = f'{round(table1[i][12], 2)}/{round(table1[i][13], 2)}/{round(table1[i][14], 2)}'
            max_grid_size = f'{int(table1[i][15])}/{int(table1[i][16])}'
            avrg_grid_size = f'{int(table1[i][17])}/{int(table1[i][18])}/{int(table1[i][19])}'
            max_points_to_profit = f'{int(table1[i][20] * self.digits)}/{int(table1[i][21] * self.digits)}'
            avrg_points_to_profit = f'{int(table1[i][22] * self.digits)}/{int(table1[i][23] * self.digits)}/{int(table1[i][24] * self.digits)}'

            max_time_grid = f'{int(table1[i][25])}/{int(table1[i][26])}'
            avrg_time_grid = f'{int(table1[i][27])}/{int(table1[i][28])}/{int(table1[i][29])}'
            dic = {'grid': grid, 'sum_lots': sum_lots, 'all_profit': all_profit, 'avrg_profit': avrg_profit,
                   'procent_profit': procent_profit, 'max_grid_size': max_grid_size, 'avrg_grid_size': avrg_grid_size,
                   'max_points_to_profit': max_points_to_profit, 'avrg_points_to_profit': avrg_points_to_profit,
                   'max_time_grid': max_time_grid, 'avrg_time_grid': avrg_time_grid}
            pandas_final_table1 = pandas_final_table1.append(dic, ignore_index=True)
        self.table1 = pandas_final_table1

    def make_table2_3(self):
        first_year = self.testingPeriod[0:4]
        last_year = self.testingPeriod[19:23]
        row_ = int(last_year) - int(first_year)

        row_ += 2

        table2 = np.zeros((row_, 15))
        table3 = np.zeros((row_, 15))

        for row in self.grid_table.itertuples():
            month_ = int(row[7])  # месяц записи
            year_ = row[3].year  # год записи
            line = year_ - int(first_year)
            table2[line, month_] += row[11] - row[9]  # профит минус комиссия
            table2[line][0] = year_
            table3[line][0] = year_

            # запоним таблицу 3, максимальными коленами за месяц
            if table3[line, month_] < row[5]:
                table3[line, month_] = row[5]
        # посчитаем сумму прибыли за года
        for j in range(row_):
            for i in range(1, 13):
                table2[j][14] += table2[j, i]
                table3[j][14] += table3[j, i]  # это значение нам понадобиться что бы узнать среднее колено за год
        self.table2 = table2
        # посчитаем среднюю прибыль
        for j in range(row_):
            k = 0  # количество ненулевых месяцев для таблицы 2
            n = 0  # количество ненулевых месяцев для таблицы 3
            for i in range(1, 13):
                # посчитаем количество не нулевых месяцев
                if table2[j][i] != 0:
                    k += 1
                if table3[j][i] != 0:
                    n += 1
            if k != 0:
                table2[j][13] = table2[j][14] / k
            if n != 0:
                table3[j][13] = table3[j][14] / n
        # заполним последнюю строку таблицы 2 и 3
        for i in range(1, 14):
            sum2 = 0
            k2 = 0
            sum3 = 0
            k3 = 0
            for j in range(row_ - 1):
                if table2[j][i] != 0:
                    sum2 += table2[j][i]
                    k2 += 1
                if table3[j][i] != 0:
                    sum3 += table3[j][i]
                    k3 += 1
            if k2 != 0:
                table2[row_ - 1, i] = sum2 / k2
            if k3 != 0:
                table3[row_ - 1, i] = sum3 / k3
        # посчитаем общую прибыль за весь период
        for j in range(row_ - 1):
            table2[row_ - 1][14] += table2[j][14]
        self.table3 = table3

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
        if self.coding == None:
            if self.language == 'RU':
                key_word = 'Параметры'
            else:
                key_word = 'Parameters'

            with open(self.pathToFile, encoding=self.coding) as f:
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
            with open(self.pathToFile, encoding=self.coding) as f:
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
        return self.set_file

    def __del__(self):
        print(f'Объект {self.pathToFile} удален!!!')


if __name__ == "__main__":
    a = Report(
        'E:\CLOUD_MEGA\!Роботы\!!СЕТКА_1_43\!Сеты\GBPCAD\(EA) - Setka v1.43-ADX-IMP-191224-R285-SR7 Ostap.Bender GBPCAD LS v2,53 2012-2019\MyTDS\Dukas(100-400)ms1spread.htm')
    a.deals_list()
    # print(a.table)

    tabl = a.table

    grid_table = a.get_grid_list()
    print(grid_table)
    maxgrid = a.get_max_grid_num()
    digits = a.get_digits()
    a.create_final_table1()
    print('table 1 created')
    del a

'''
0-balance
1-commisions
2- direction
3 - lot
4- num_order
5 buy/sell
6- price
7-profit
8-sl
9-symbol
10-time
11-tp

balance                      0
commisions                   0
direction            direction
lot                       0.01
num_order                    1
order_type                sell
price                  1.71946
profit                        
sl                     0.00000
symbol                 GBPCAD 
time          2020.01.24 20:35
tp                     0.00000
'''
