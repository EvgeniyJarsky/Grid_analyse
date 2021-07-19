#todo добавить проверку что бы не добавлять отчеты с одинаковым именем
#todo вывести настройки и сохранять их в сет-файл


from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication,QDialog, QLabel, QLineEdit, QTabWidget, QWidget, QVBoxLayout, QDialogButtonBox, QTableWidget,\
    QPushButton, QHBoxLayout, QTableWidgetItem, QFrame, QSplitter, QFileDialog, QHeaderView, QGridLayout,\
    QListView, QTextEdit, QListWidget, QMessageBox, QProgressBar, QSizePolicy, QProgressBar
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
import sys
from chardet.universaldetector import UniversalDetector
import numpy as np
from bs4 import BeautifulSoup
from os import path
import time
import csv
import pandas as pd
import datetime
import random
from library import Main_info, write_to_csv, prepare_pandas_table_data, String_to_time, conver_min_to_hour_and_min, delete_zero
# from library import duration_in_min
from library import createConfig, SetGetConfig, MplCanvas
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import plotly
import plotly.graph_objs as go
import os

path = 'config\config.txt'

def Draw_interactive_graf(list):
    df = pd.read_csv("final_multi_csv.csv")
    data = []
    for sym in list:
        graf = go.Scatter(x=df['date'], y=df[sym], name=sym)
        data.append(graf)
    plotly.offline.plot(data)

class PlotCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.plot()

    def plot(self):
        data = [random.random() for i in range(10)]
        ax = self.figure.add_subplot(111)
        ax.plot(data, 'r-')
        ax.set_title('Здесь надо построить график')
        # ax.grid()
        self.draw()


class Tab(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Анализ сеточников')
        # self.setWindowIcon('icon.png')

        self.clear_temp()

        self.set_name = QLabel()
        self.set_name.setText('Файл отчета')
        self.set_name_value = QLabel()
        self.set_name_value.setText('---')

        self.curency = QLabel()
        self.curency.setText('Валюта')
        self.curency_value = QLabel()
        self.curency_value.setText('---')

        self.time_frame = QLabel()
        self.time_frame.setText('Тайм фрейм')
        self.time_frame_value = QLabel()
        self.time_frame_value.setText('---')

        self.testing_period = QLabel()
        self.testing_period.setText('Период тестирования')
        self.testing_period_value = QLabel()
        self.testing_period_value.setText('---')

        self.deposit = QLabel()
        self.deposit.setText('Начальный депозит')
        self.deposit_value = QLabel()
        self.deposit_value.setText('---')

        self.profit = QLabel()
        self.profit.setText('Чистая прибыль')
        self.profit_value = QLabel()
        self.profit_value.setText('---')

        self.max_down = QLabel()
        self.max_down.setText('Максимальная просадка')
        self.max_down_value = QLabel()
        self.max_down_value.setText('---')

        self.profitability = QLabel()
        self.profitability.setText('Рентабельность')
        self.profitability_value = QLabel()
        self.profitability_value.setText('---')

        hbox = QHBoxLayout()
        hbox2 = QHBoxLayout()
        vbox = QVBoxLayout()
        tabWidget = QTabWidget()

        button = QPushButton()
        button.setText('Add File')
        button.clicked.connect(self.showDialog)

        button2 = QPushButton()
        button2.setText('Delete')
        button2.clicked.connect(self.delete_item)

        button3 = QPushButton()
        button3.setText('Clear All')
        button3.clicked.connect(lambda: self.liEdt.clear())
        button3.clicked.connect(self.clear_labels)
        button3.clicked.connect(lambda: self.list_.clear())

        self.liEdt = QListWidget()
        self.liEdt.clicked.connect(self.show_selected_line)

        self.grid = QGridLayout()
        self.grid.addWidget(self.set_name,0,0)
        self.grid.addWidget(self.set_name_value, 0, 1)
        self.grid.addWidget(self.curency, 1, 0)
        self.grid.addWidget(self.curency_value, 1, 1)
        self.grid.addWidget(self.time_frame, 2, 0)
        self.grid.addWidget(self.time_frame_value, 2, 1)
        self.grid.addWidget(self.testing_period,3,0)
        self.grid.addWidget(self.testing_period_value, 3, 1)
        self.grid.addWidget(self.deposit, 4, 0)
        self.grid.addWidget(self.deposit_value, 4, 1)
        self.grid.addWidget(self.profit, 5, 0)
        self.grid.addWidget(self.profit_value, 5, 1)
        self.grid.addWidget(self.max_down, 6, 0)
        self.grid.addWidget(self.max_down_value, 6, 1)
        self.grid.addWidget(self.profitability, 7, 0)
        self.grid.addWidget(self.profitability_value, 7, 1)


        hbox.addWidget(button)
        hbox.addWidget(button2)
        hbox.addWidget(button3)

        hbox2.addWidget(self.liEdt)
        hbox2.addLayout(self.grid)

        self.list_ = []# list of all files

        tabWidget.addTab(First(line=self.set_name_value), 'Основная информация')
        tabWidget.addTab(Analyse(list_=self.list_), 'Анализ детальный')
        tabWidget.addTab(Set_file(line=self.set_name_value), 'Работа с set файлами')

        vbox.addLayout(hbox)
        vbox.addLayout(hbox2)
        vbox.addWidget(tabWidget)


        self.setLayout(vbox)

    def clear_labels(self):
        '''
        Очищаем данные Label
        '''
        self.set_name_value.setText('---')
        self.time_frame_value.setText('---')
        self.curency_value.setText('---')
        self.time_frame_value.setText('---')
        self.testing_period_value.setText('---')
        self.deposit_value.setText('---')
        self.profit_value.setText('---')
        self.max_down_value.setText('---')
        self.profitability_value.setText('---')

    def show_selected_line(self):
        index = self.liEdt.selectedIndexes()[0].row()# возращает номер строчки в списке(начинаються с 0) на который кликнул

        line = self.liEdt.currentItem().text() # возвращает текущую строку
        # self.set_name_value.setText(line.split('/')[-1])#todo что бы показать имя отчета а не весь
        #  todo путь надо переностить в отдельную переменную
        self.set_name_value.setText(line)
        report = Main_info(file_path=line)
        report.detect_type_of_report()
        report.detect_language()
        report.get_symbol()

        self.curency_value.setText(report.symbol)
        report.get_time_frame()
        self.time_frame_value.setText(report.time_frame)
        report.get_testing_period()
        self.testing_period_value.setText(report.period)
        report.get_deposit()
        self.deposit_value.setText(report.deposit)
        report.get_total_profit()
        self.profit_value.setText(report.total_profit)
        report.get_drawdown()
        self.max_down_value.setText(report.drawdown)
        report.get_profitability()
        self.profitability_value.setText(report.profitability)
        return line



    def showDialog(self):
        '''
        добавляем файл в список отчетов
        :return: None
        '''
        #проверям сохраненный путь, если путь не сущестует то открываем корневую папку
        try:
            fname = QFileDialog.getOpenFileName(self, 'Open file', SetGetConfig('get','HTML file path', 'file path'),
                                            "Any files (*.ht*)")
        except:
            QFileDialog.getOpenFileName(self, 'Open file', '',
                                        "Any files (*.ht*)")
        if fname[0] == '':
            return 0
        file = fname[0]
        # todo надо проверить на добавление одного и того же отчета
        # index = self.liEdt.count()
        # try: index2 = self.liEdt.row(index)
        # except: pass
        # line = self.liEdt.findItems(file, QtCore.Qt.MatchExactly)
        # if line != []:
        #     # a = line.row()
        #     if line.text() == file:
        #         buttonReply = QMessageBox.question(self, 'Внимание!!!', "Файл с таким именем\n уже существует!!!",
        #                                            QMessageBox.Ok)
        # print(f'linecurent = {line}')
        # file_path = os.path.dirname(file)
        try: SetGetConfig('set', 'HTML file path', 'file path', file)
        except: print('Ошибка сохранения файла, путь содержит русский шрифт')
        self.list_.append(file)
        print(self.list_)
        self.liEdt.addItem(file)
        return self.list_


    def delete_item(self):
        listItems = self.liEdt.selectedItems()
        line = self.liEdt.currentItem().text() # возвращает текущую строку
        self.list_.remove(line)# delete string from list
        if not listItems:
            print('Не выбрана строка для удаления')
            return
        self.clear_labels()
        for item in listItems:
            self.liEdt.takeItem(self.liEdt.row(item))

    def clear_temp(self):
        '''
        очищаем временную папку перед выходом из программы
        '''
        files = os.listdir(SetGetConfig('get', 'file path for temp files', 'file path'))
        for i in files:
            file_full_path = SetGetConfig('get', 'file path for temp files', 'file path') + i
            os.remove(file_full_path)

    def closeEvent(self, event):
            reply = QtWidgets.QMessageBox.question(self,'Внимание','Вы уверены что хотите выйти?',\
                                                   QtWidgets.QMessageBox.Yes,QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.Yes:
                self.clear_temp()
                event.accept()
            else:
                event.ignore()



class First(QWidget):
    def __init__(self, line=0):
        super().__init__()

        self.line = line

        self.table = QTableWidget(self)
        self.table.setBackgroundRole(5)
        self.table.setColumnCount(11)
        self.table.setRowCount(2)
        self.table.setHorizontalHeaderLabels(["Кол-во\nсделок\nsell/buy/all", "Сумма лотов\nсделок\nsell/buy/all",\
                                              "Общая\nприбыль $\nsell/buy/all", "Средняя\nприбыль $\nsell/buy/all",\
                                              "% от общей\nприбыли\nsell/buy/all", "Макс размер\nсетки в\nпунктах\nsell/buy",\
                                              'Средний размер\nсетки в\nпунктах\nsell/buy/all', 'Макс кол-во\nпунктов до\nдо ТР\nsell/buy',\
                                              'Среднее кол-во\nпунктов до\nдо ТР\nsell/buy/all', 'Макс время\nжизни сетки\nЧасы:Минуты\nsell/buy',\
                                              'Среднее время\nжизни сетки\nЧасы:Минуты\nsell/buy/all'])
        self.table.resizeColumnsToContents()

        self.table2 = QTableWidget(self)
        self.table2.setColumnCount(15)
        self.table2.setRowCount(2)
        self.table2.setHorizontalHeaderLabels(["Годы", "Январь", "Февраль", "Март", "Апрель", "Май", 'Июнь',\
                                              'Июль', 'Август','Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь',\
                                               'Средняя\n$', 'Итого\nгод$'])
        self.table2.resizeColumnsToContents()

        self.table3 = QTableWidget(self)
        self.table3.setColumnCount(14)
        self.table3.setRowCount(2)
        self.table3.setHorizontalHeaderLabels(["Годы", "Январь", "Февраль", "Март", "Апрель", "Май", 'Июнь', \
                                               'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь', \
                                               'Средняя\n'])
        self.table3.resizeColumnsToContents()

        self.sc = self.show_graf(SetGetConfig('get', 'file path for temp files', 'file path') + 'pandas_table.csv')
        self.toolbar = NavigationToolbar(self.sc, self)

        self.button = QPushButton(self)
        self.button.setText("Расчитать сетку")
        self.button.clicked.connect(self.showDialog)
        self.button.clicked.connect(lambda: self.sc.deleteLater())
        self.button.clicked.connect(lambda: self.toolbar.deleteLater())
        self.button.clicked.connect(lambda: self.show_graf(SetGetConfig('get', 'file path for temp files', 'file path') + 'pandas_table.csv'))
        self.button.clicked.connect(self.create_toolbar)
        self.button.clicked.connect(lambda: hbox.addWidget(self.toolbar,QtCore.Qt.AlignLeft))
        self.button.clicked.connect(lambda: splitter0.addWidget(self.sc))

        # self.lab_graph = QLabel('График')
        # pixmap = QPixmap("MT4_QLT_EN.gif")
        # self.lab_graph.setPixmap(pixmap)


        # self.lab_graph = PlotCanvas(self, width=5, height=4)

        # self.lbl = QLineEdit('File Path')


        # self.lbl2 = QLabel(self)
        # self.lbl2.setText('Label2')
        # self.lbl2.setFrameShape(QTableWidget.StyledPanel)

        # self.lbl3 = QLabel(self)
        # self.lbl3.setText('Label3')
        # self.lbl3.setFrameShape(QTableWidget.StyledPanel)
        #
        # self.lbl4 = QLabel(self)
        # self.lbl4.setText('Label4')
        # self.lbl4.setFrameShape(QTableWidget.StyledPanel)
        #
        # self.lbl5 = QLabel(self)
        # self.lbl5.setText('Label5')
        # self.lbl5.setFrameShape(QTableWidget.StyledPanel)
        #
        # self.lbl6 = QLabel(self)
        # self.lbl6.setText('Label6')
        # self.lbl6.setFrameShape(QTableWidget.StyledPanel)
        #
        # self.lbl7 = QLabel(self)
        # self.lbl7.setText('Кол-во сеток')
        # self.lbl7.setFrameShape(QTableWidget.StyledPanel)

        splitter0 = QSplitter(Qt.Horizontal)
        splitter0.addWidget(self.table)
        # splitter0.addWidget(self.toolbar)
        splitter0.addWidget(self.sc)
        splitter0.setSizes([100, 120])

        splitter1 = QSplitter(Qt.Horizontal)
        splitter1.addWidget(self.table2)
        splitter1.addWidget(self.table3)
        splitter1.setSizes([100,120])

        splitter2 = QSplitter(Qt.Vertical)
        splitter2.addWidget(splitter0)
        splitter2.addWidget(splitter1)

        hbox = QHBoxLayout()
        hbox.addWidget(self.button,QtCore.Qt.AlignRight)
        hbox.addWidget(self.toolbar,QtCore.Qt.AlignLeft)

        self.grid = QGridLayout()
        self.grid.setSpacing(10)
        self.grid.addWidget(splitter2, 1, 0)
        # self.grid.addWidget(self.toolbar,1,0)
        # self.grid.addWidget(self.lab_graph, 2, 0)
        # self.grid.addWidget(self.table3, 1, 1)


        # hbox.addWidget(self.lbl2)

        # lbox = QGridLayout()
        # lbox.setSpacing(0)
        # lbox.addWidget(self.lbl5, 1, 1, QtCore.Qt.AlignTop)
        # lbox.addWidget(self.lbl6, 2, 0, QtCore.Qt.AlignTop)
        # lbox.addWidget(self.lbl7, 0, 0,1,2, QtCore.Qt.AlignHCenter)
        # lbox.addWidget(self.lbl3,1,0, QtCore.Qt.AlignTop)
        # lbox.addWidget(self.lbl4,2,1, QtCore.Qt.AlignTop)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        # vbox.addWidget(self.table)
        # vbox.addWidget(self.table2)
        # vbox.addWidget(self.table3)

        vbox.addLayout(self.grid)

        self.setLayout(vbox)

    def showDialog(self):

        # self.pbar = QProgressBar(self)
        # self.pbar.setGeometry(30, 40, 200, 25)

        file = self.line.text()
        if file == '---':
            buttonReply = QMessageBox.question(self, 'Внимание!!!', "Выбирите файл\n отчета!!!", QMessageBox.Ok)
            if buttonReply == QMessageBox.Ok:
                return 0
            return 0


        report = Main_info(file_path=file)
        # print('путь файла==' + report.file_path)
        report.detect_type_of_report()
        # print(report.type_report)
        report.get_digits()
        report.detect_language()
        # print(report.language)
        report.get_symbol()
        # print(report.symbol)
        report.get_csv_file_name()
        # print(report.csv_name)
        report.get_total_profit()
        # print('Profit' + report.total_profit)
        report.create_csv_file_of_deals()
        report.create_pandas_table()
        # print(report.pandas_table)
        report.get_max_grid()
        # print(report.num_max_grid)
        report.create_final_table1()
        # print(report.table1)
        report.get_time_frame()
        report.get_testing_period()
        report.make_table2_3()

        self.table.setRowCount(report.num_max_grid)#создаем таблицу в виджете
        # перебираем пандас таблицу и запоняем массив
        n =0
        for row in report.table1.itertuples():
            self.table.setItem(n, 0, QTableWidgetItem(row[6]))#кол-во сеток
            self.table.setItem(n, 1, QTableWidgetItem(row[11]))#сумма лотов
            self.table.setItem(n, 2, QTableWidgetItem(row[1]))  # общая прибыль
            self.table.setItem(n, 3, QTableWidgetItem(row[4]))  # средняя прибыль
            self.table.setItem(n, 4, QTableWidgetItem(row[10]))  # процент от общей прибыли
            self.table.setItem(n, 5, QTableWidgetItem(row[7]))  # максимальные размер сетки
            self.table.setItem(n, 6, QTableWidgetItem(row[2]))  # средний размер метки
            self.table.setItem(n, 7, QTableWidgetItem(row[8]))  # максимальное кол-во пипсов до профита
            self.table.setItem(n, 8, QTableWidgetItem(row[3]))  # среднее кол-во пипсов до профита
            self.table.setItem(n, 9, QTableWidgetItem(conver_min_to_hour_and_min(row[9])))  # максимальные время жизни сетки
            self.table.setItem(n, 10, QTableWidgetItem(conver_min_to_hour_and_min(row[5])))  # среднее время жизни сетки
            n += 1
        self.table.resizeColumnsToContents()

        #Строим 2 таблицу
        a = report.table2
        size = a.shape#(2, 15)

        self.table2.setRowCount(size[0])  # создаем таблицу в виджете

        for j in range(size[0]):
            for i in range(size[1]):
                b = str(round(a[j][i],2))
                self.table2.setItem(j,i,QTableWidgetItem(b))
        self.table2.setItem(size[0]-1, 0, QTableWidgetItem('Среднее'))
        self.table2.resizeColumnsToContents()
        # строим таблицу3
        a = report.table3
        size = a.shape  # (2, 14)
        self.table3.setRowCount(size[0])  # создаем таблицу в виджете
        for j in range(size[0]):
            for i in range(size[1]-1):
                b = str(round(a[j][i], 2))
                self.table3.setItem(j, i, QTableWidgetItem(b))
        self.table3.setItem(size[0] - 1, 0, QTableWidgetItem('Среднее'))
        self.table3.resizeColumnsToContents()

    def create_toolbar(self):
        self.toolbar = NavigationToolbar(self.sc, self)
        return self.toolbar

    def show_graf(self,file):
        if os.path.exists(file):
            self.sc = MplCanvas(self, width=5, height=4, dpi=100)
            data_frame = pd.read_csv(file)
            data_frame.plot(x='Date', y='Balance', ax=self.sc.axes)
        else:
            self.sc = MplCanvas(self, width=5, height=4, dpi=100)
            data_frame = pd.read_csv(SetGetConfig('get', 'file path for scv files', 'file path') + 'balance.csv')
            data_frame.plot(x='Date', y='Example', ax=self.sc.axes)
        return self.sc




class Analyse(QWidget):
    def __init__(self, list_):
        super().__init__()

        self.list_ = list_

        vbox = QVBoxLayout()

        self.sc = self.show_graf(SetGetConfig('get', 'file path for temp files', 'file path') + 'final_csv.csv')

        # toolbar = NavigationToolbar(self.sc, self)

        self.btn = QPushButton('MultRaport')
        self.btn.clicked.connect(self.Make_mult_report)
        self.btn.clicked.connect(lambda: self.sc.deleteLater())
        self.btn.clicked.connect(lambda: self.toolbar.deleteLater())
        self.btn.clicked.connect(lambda: self.show_graf(SetGetConfig('get', 'file path for temp files', 'file path') + 'final_csv.csv'))
        self.btn.clicked.connect(self.create_toolbar)
        self.btn.clicked.connect(lambda: vbox.addWidget(self.toolbar))
        self.btn.clicked.connect(lambda: vbox.addWidget(self.sc))
        # self.btn.clicked.connect(lambda: self.sc.show())

        self.toolbar = NavigationToolbar(self.sc, self)



        vbox.addWidget(self.btn)
        vbox.addWidget(self.toolbar)
        vbox.addWidget(self.sc)

        self.setLayout(vbox)

    def create_toolbar(self):
        self.toolbar = NavigationToolbar(self.sc, self)
        return self.toolbar

    def show_graf(self,file):
        if os.path.exists(file):
            self.sc = MplCanvas(self, width=5, height=4, dpi=100)
            data_frame = pd.read_csv(file)
            symbol = data_frame.columns[1:-2]
            data_frame.plot(x='date', y=symbol, ax=self.sc.axes)
        else:
            self.sc = MplCanvas(self, width=5, height=4, dpi=100)
            data_frame = pd.read_csv(SetGetConfig('get', 'file path for scv files', 'file path') + 'empty_graph.csv')
            symbol = data_frame.columns[1:-2]
            data_frame.plot(x='date', y=symbol, ax=self.sc.axes)
        return self.sc

    def Make_mult_report(self,sc):
        '''
        Сформируем суммарный CSV файл со всеми сделками и всеми парами
        :return:
        '''
        #todo исключить пока не компилируется
        buttonAsk = QMessageBox.question(self, 'Внимание', "Построить интерактивный\n график?", QMessageBox.Yes,QMessageBox.No)
        # first_time = time.time()
        symbol = []

        if len(self.list_) == 0:#если не выбрано ни оодного отчета
            buttonReply = QMessageBox.question(self, '!!!Внимание!!!', "Выбирите файлы\n отчета!!!", QMessageBox.Ok)
            if buttonReply == QMessageBox.Ok:
                return 0
        else:
            pandas_list = pd.DataFrame()
            for line in self.list_:
                report = Main_info(file_path=line)
                report.detect_type_of_report()
                report.detect_language()
                report.get_symbol()
                report.get_csv_file_name()
                report.get_total_profit()
                report.create_csv_file_of_deals()

                symbol.append(report.symbol)

                pandas_from_csv = pd.read_csv(SetGetConfig('get', 'file path for temp files', 'file path') + report.csv_name)
                pandas_list = pd.concat([pandas_list,pandas_from_csv], sort=False, axis=0)

            # second_time = time.time()
            # proc_time = second_time - first_time
            # print(f'ALL TIME = {proc_time}')
            # t = f'Засчет занял\n{proc_time}'
            # buttonReply = QMessageBox.question(self, '1 BLOCK', t, QMessageBox.Ok)

            pandas_list = pandas_list.sort_values(by=['time'], ascending=True)

            dic = {'profit': 0, 'date': 0}
            for i in symbol:
                dic[i] = 0
            # print(dic)
# Index=0, time='2012.01.09 00:46', symbol='EURUSD ', order_type='buy', direction='direction', lot=0.01, num_order=1, price=1.27007, sl=0.0, tp=0.0, _10=0, profit=nan, balance=0.0
            pandas_multi_table = pd.DataFrame()
            for row in pandas_list.itertuples():
                dic['date'] = row[1]
                if np.isnan(row[11]):
                    profit = 0
                else:
                    profit = row[11]
                dic['profit'] += profit
                k=-1# коэффициент принимает 1 или -1 на него умножается лоты в зависимости это вход или выход из позы
                if row[4] == 'direction':#если это MT4
                    list = ('sell','buy')
                    if row[3] in list:
                        k = 1
                else:#иначе это MT5
                    if row[4] == 'in':
                        k = 1

                dic[row[2]] += k*row[5]

                pandas_multi_table = pandas_multi_table.append(dic,ignore_index=True)

            pandas_multi_table.to_csv(SetGetConfig('get', 'file path for temp files', 'file path') + 'final_csv.csv')

            # second_time = time.time()
            # proc_time = second_time - first_time
            # print(f'ALL TIME = {proc_time}')
            # t = f'Засчет занял\n{proc_time}'
            # buttonReply = QMessageBox.question(self, '2BLOCK', t, QMessageBox.Ok)
#todo этот код не работатет в скомпилированном коде
            if buttonAsk == QMessageBox.Yes:
                # построим график который будет интерактивным
                data = []
                for sym in symbol:
                   graf = go.Scatter(x=pandas_multi_table['date'], y=pandas_multi_table[sym], name=sym)
                   data.append(graf)
                plotly.offline.plot(data)
            else: f=2



class Set_file(QWidget):
    def __init__(self, line=0):
        super().__init__()

        self.line = line

        # file = self.line.text()
        # if file == '---':
        #     buttonReply = QMessageBox.question(self, 'Внимание!!!', "Выбирите файл\n отчета!!!", QMessageBox.Ok)
        #     if buttonReply == QMessageBox.Ok:
        #         return 0
        #     return 0

        self.load_set = QPushButton('Загрузить настройки')
        self.load_set.clicked.connect(self.load_settings)
        self.compress_set = QPushButton('Сжать set-файл')
        self.compress_set.clicked.connect(self.compress)
        self.save_set = QPushButton('Сохранить set-файл')
        self.save_set.clicked.connect(self.save_set_file)

        self.text_edit = QTextEdit()

        hbox = QHBoxLayout()
        hbox.addWidget(self.load_set)
        hbox.addWidget(self.save_set)
        hbox.addWidget(self.compress_set)


        vbox = QVBoxLayout()

        vbox.addLayout(hbox)
        vbox.addWidget(self.text_edit)

        self.setLayout(vbox)

    def load_settings(self):
        file = self.line.text()
        if file == '---':
            buttonReply = QMessageBox.question(self, 'Внимание!!!', "Выбирите файл\n отчета!!!", QMessageBox.Ok)
            if buttonReply == QMessageBox.Ok:
                return 0
            return 0
        report = Main_info(file_path=file)
        report.detect_type_of_report()
        report.detect_language()
        report.get_set()
        self.text_edit.setText(report.set_file)

    def save_set_file(self):
        # folder = QFileDialog.getExistingDirectory(self, 'Выбрать папку', '.')
        set_text = self.text_edit.toPlainText()
        folder = QFileDialog.getSaveFileName(self, 'Save  file', 'set_file.set')
        if folder[0] == '':
            return 0
        with open(folder[0], mode='w', encoding='utf-8') as w_file:
            w_file.writelines(set_text)

    def compress(self):
        string =''
        try:
            fname = QFileDialog.getOpenFileName(self, 'Open file', SetGetConfig('get', 'file path for set files', 'file path'),
                                            "Any files (*.set)")
        except:
            fname = QFileDialog.getOpenFileName(self, 'Open file','',"Any files (*.set)")
        if fname[0] == '':
            return 0
        file = fname[0]
        file_path = os.path.dirname(file)
        SetGetConfig('set', 'file path for set files', 'file path', file_path)

        with open(fname[0], mode='r') as file:
            current_setting = 0
            for line in file:
                if current_setting == 0:
                    string += delete_zero(line)
                    current_setting = line.split('=')[0]
                else:
                    a = current_setting + ',F='
                    b = current_setting + ',1='
                    c = current_setting + ',2='
                    d = current_setting + ',3='
                    if a in line or b in line or c in line or d in line:
                        continue
                    else:
                        string += delete_zero(line)
                        current_setting = line.split('=')[0]
        string = string
        self.text_edit.setText(string)
        # with open(folder[0], mode='w', encoding='utf-8') as w_file:
        #     w_file.writelines(set_text)

if __name__ == "__main__":
    App = QApplication(sys.argv)
    tabDialog = Tab()
    tabDialog.show()
    App.exec()
