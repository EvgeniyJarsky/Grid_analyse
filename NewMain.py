import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QHBoxLayout, \
    QVBoxLayout, QPushButton, QGridLayout, QLabel, QListView, QFrame, QSplitter, \
    QTabWidget, QTableWidget, QFileDialog, QListWidget, QMessageBox, QTableWidgetItem, QTextEdit
from PyQt5 import QtGui, QtWidgets, QtCore
from NewLib import *
from ReportClass import *
from PyQt5.QtGui import QPixmap

import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
import datetime
import plotly


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.sum_list = 0  # список всех добавленных отчетов

        self.setWindowTitle('Анализ сеточников')
        self.top = int(confFile.getParam(confFile.filePath, 'Main windos sizes', 'top'))
        self.left = int(confFile.getParam(confFile.filePath, 'Main windos sizes', 'left'))
        self.width = int(confFile.getParam(confFile.filePath, 'Main windos sizes', 'width'))
        self.height = int(confFile.getParam(confFile.filePath, 'Main windos sizes', 'height'))
        self.setGeometry(self.left, self.top, self.width, self.height)

        tab_widget = QTabWidget()
        tab_widget.setMinimumHeight(300)
        tab_widget.addTab(TableTab(), 'Основная информация')
        tab_widget.addTab(LotsAnalyse(), 'Анализ лотности')
        tab_widget.addTab(WorkWithSets(), 'Работа с сетами')
        tab_widget.addTab(DataBase(), 'База Данных')

        widget = QWidget()
        self.setCentralWidget(widget)
        main_grid_layout = QGridLayout()

        frame0 = QFrame()  # Top with buttons
        # w0.setFrameShape(QFrame.StyledPanel)
        frame0.setGeometry(0, 0, 600, 10)
        frame0.setMaximumHeight(40)

        frame1 = QFrame()  # left ListWidget
        frame1.setMinimumHeight(50)
        frame1.setMaximumHeight(200)
        frame1.setFrameShape(QFrame.StyledPanel)
        frame1.setGeometry(0, 0, 300, 100)

        frame2 = QFrame()  # right for labels
        frame2.setMinimumHeight(150)
        frame2.setMaximumHeight(200)
        frame2.setFrameShape(QFrame.StyledPanel)
        frame2.setGeometry(0, 0, 600, 100)

        splitter_h = QSplitter(Qt.Horizontal)
        splitter_v = QSplitter(Qt.Vertical)
        splitter_h.addWidget(frame1)
        splitter_h.addWidget(frame2)

        splitter_v.addWidget(frame0)
        splitter_v.addWidget(splitter_h)
        splitter_v.addWidget(tab_widget)

        main_grid_layout.addWidget(splitter_v, 0, 0)

        widget.setLayout(main_grid_layout)

        buttons_list = ('Add File', 'Del File', 'Clear ALL', 'Add to BD')
        w0_hbox = QHBoxLayout()
        add_file_button = QPushButton(buttons_list[0])
        add_file_button.clicked.connect(self.show_dialog)
        del_file_button = QPushButton(buttons_list[1])
        del_file_button.clicked.connect(self.delete_item)
        clear_all_button = QPushButton(buttons_list[2])
        clear_all_button.clicked.connect(lambda: self.listView.clear())
        clear_all_button.clicked.connect(self.clear_labels)

        add_to_bd_button = QPushButton(buttons_list[3])
        w0_hbox.addWidget(add_file_button)
        w0_hbox.addWidget(del_file_button)
        w0_hbox.addWidget(clear_all_button)
        w0_hbox.addWidget(add_to_bd_button)
        frame0.setLayout(w0_hbox)
        # -----------------------------------

        self.listView = QListWidget()
        self.listView.clicked.connect(self.show_selected_line)
        # self.listView.setStyleSheet('background-color:gray')
        w1_hbox = QHBoxLayout()
        w1_hbox.addWidget(self.listView)
        frame1.setLayout(w1_hbox)

        label_list = ('Файл отчета',
                      'Валюта',
                      'Тайм фрейм',
                      'Период тестирования',
                      'Начальный депозит',
                      'Чистая прибыль',
                      'Максимальная просадка',
                      'Рентабельность',
                      )
        w2_hbox = QHBoxLayout()
        w2_vbox1 = QVBoxLayout()
        w2_vbox2 = QVBoxLayout()
        for label in label_list:
            w2_vbox1.addWidget(QLabel(label))
            # w2Vbox2.addWidget(QLabel(emptyString))
        self.set_name_value = QLabel()
        self.set_name_value.setText('---')
        w2_vbox2.addWidget(self.set_name_value)

        self.curency_value = QLabel()
        self.curency_value.setText('---')
        w2_vbox2.addWidget(self.curency_value)

        self.time_frame_value = QLabel()
        self.time_frame_value.setText('---')
        w2_vbox2.addWidget(self.time_frame_value)

        self.testing_period_value = QLabel()
        self.testing_period_value.setText('---')
        w2_vbox2.addWidget(self.testing_period_value)

        self.deposit_value = QLabel()
        self.deposit_value.setText('---')
        w2_vbox2.addWidget(self.deposit_value)

        self.profit_value = QLabel()
        self.profit_value.setText('---')
        w2_vbox2.addWidget(self.profit_value)

        self.max_down_value = QLabel()
        self.max_down_value.setText('---')
        w2_vbox2.addWidget(self.max_down_value)

        self.profitability_value = QLabel()
        self.profitability_value.setText('---')
        w2_vbox2.addWidget(self.profitability_value)

        w2_hbox.addLayout(w2_vbox1)
        w2_hbox.addLayout(w2_vbox2)
        frame2.setLayout(w2_hbox)

        widget.setLayout(main_grid_layout)

    def show_selected_line(self):
        # при выборе файла сета в окне - справа выводиться информация об отчете
        global report
        path_to_file = self.listView.currentItem().text()  # возвращает текущую строку
        report = Report(path_to_file)

        self.set_name_value.setText(report.fileName)

        self.curency_value.setText(report.symbol)

        self.time_frame_value.setText(report.timeFrame)

        self.testing_period_value.setText(report.testingPeriod)

        self.deposit_value.setText(report.deposit)

        self.profit_value.setText(report.profit)

        self.max_down_value.setText(report.drawdown)

        self.profitability_value.setText(report.profitability)

    def get_list_of_listview(self):
        # получаем список файлов уже добавленных файлов отчетов
        this_reports_was_added = []
        num_of_items = self.listView.count()
        for item in range(num_of_items):
            base_path = self.listView.item(item).text()
            only_file_name = base_path.split('/')[-1]
            this_reports_was_added.append(only_file_name)
        return this_reports_was_added

    def show_dialog(self):
        # добавляем файл в список отчетов
        # проверям сохраненный путь, если путь не сущестует то открываем корневую папку
        try:
            fname = QFileDialog.getOpenFileName(self, 'Open file',
                                                confFile.getParam(confFile.filePath, 'HTML file path', 'file path'),
                                                "Any files (*.ht*)")
        except:
            fname = QFileDialog.getOpenFileName(self, 'Open file', '',
                                                "Any files (*.ht*)")
        if fname[0] == '':
            return 0
        file = fname[0]
        # сохраняем последний путь открытия файла
        try:
            confFile.setParam(confFile.filePath, 'HTML file path', 'file path', file)
        except:
            print('Ошибка сохранения файла, путь содержит русский шрифт')
        # todo need to check valid file
        # проверка на одинаковые имена файлов при добавлении нового
        only_file_name = file.split('/')[-1]
        if only_file_name in self.get_list_of_listview():
            QMessageBox.question(self, '!!!Внимание!!!', "Файл с таким именем уже добавлен!!!", QMessageBox.Ok)
            return 0
        self.listView.addItem(file)
        global sum_list
        sum_list.append(file)  # суммарный список всех добавленных точетов для анализа лотности

    def clear_labels(self):
        # Очищаем данные Label и глобальные переменные
        self.set_name_value.setText('---')
        self.time_frame_value.setText('---')
        self.curency_value.setText('---')
        self.time_frame_value.setText('---')
        self.testing_period_value.setText('---')
        self.deposit_value.setText('---')
        self.profit_value.setText('---')
        self.max_down_value.setText('---')
        self.profitability_value.setText('---')
        global report, sum_list
        sum_list = []
        # если удаляется подряд несколько отчетов то уже при удалении первого отчета report удален,
        # и потом del report выдает ошибку
        try:
            del report
        except:
            pass

    def delete_item(self):
        # функция удаляет выбранный    отчет
        list_items = self.listView.selectedItems()
        if not list_items:
            print('Не выбрана строка для удаления')
            QMessageBox.question(self, 'Внимание!!!', "Выбирите файл\n отчета!!!", QMessageBox.Ok)
            return
        self.clear_labels()
        for item in list_items:
            self.listView.takeItem(self.listView.row(item))
        global sum_list
        sum_list = self.get_list_of_listview()

    def closeEvent(self, event):
        # функция выполняется призакрытии программы
        reply = QtWidgets.QMessageBox.question(self, 'Внимание', 'Вы уверены что хотите выйти?',
                                               QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            # delete report
            global report
            try:
                del report
            except:
                pass
            # detect window size
            top = str(self.geometry().top())
            left = str(self.geometry().left())
            width = str(self.geometry().width())
            height = str(self.geometry().height())
            tup = (top, left, width, height)
            # rewrite gonfig file with new sizes
            confFile.setParam(confFile.filePath, 'Main windos sizes', 'top', tup[0])
            confFile.setParam(confFile.filePath, 'Main windos sizes', 'left', tup[1])
            confFile.setParam(confFile.filePath, 'Main windos sizes', 'width', tup[2])
            confFile.setParam(confFile.filePath, 'Main windos sizes', 'height', tup[3])
            event.accept()
        else:
            event.ignore()


class TableTab(QWidget):
    def __init__(self):
        super().__init__()

        global report

        self.table1 = QTableWidget(self)
        self.table1.setBackgroundRole(5)
        self.table1.setColumnCount(11)
        self.table1.setRowCount(2)
        self.table1.setHorizontalHeaderLabels(["Кол-во\nсделок\nsell/buy/all", "Сумма лотов\nсделок\nsell/buy/all",
                                               "Общая\nприбыль $\nsell/buy/all", "Средняя\nприбыль $\nsell/buy/all",
                                               "% от общей\nприбыли\nsell/buy/all",
                                               "Макс размер\nсетки в\nпунктах\nsell/buy",
                                               'Средний размер\nсетки в\nпунктах\nsell/buy/all',
                                               'Макс кол-во\nпунктов до\nдо ТР\nsell/buy',
                                               'Среднее кол-во\nпунктов до\nдо ТР\nsell/buy/all',
                                               'Макс время\nжизни сетки\nЧасы:Минуты\nsell/buy',
                                               'Среднее время\nжизни сетки\nЧасы:Минуты\nsell/buy/all'])
        self.table1.resizeColumnsToContents()

        self.table2 = QTableWidget(self)
        self.table2.setColumnCount(15)
        self.table2.setRowCount(2)
        self.table2.setHorizontalHeaderLabels(["Годы", "Январь", "Февраль", "Март", "Апрель", "Май", 'Июнь',
                                               'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь',
                                               'Средняя\n$', 'Итого\nгод$'])
        self.table2.resizeColumnsToContents()

        self.table3 = QTableWidget(self)
        self.table3.setColumnCount(14)
        self.table3.setRowCount(2)
        self.table3.setHorizontalHeaderLabels(["Годы", "Январь", "Февраль", "Март", "Апрель", "Май", 'Июнь',
                                               'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь',
                                               'Средняя\n'])
        self.table3.resizeColumnsToContents()

        self.pic = QLabel('For graphic')
        self.pic.setAlignment(Qt.AlignCenter)


        self.button = QPushButton(self)
        self.button.setText("Расчитать сетку")
        self.button.clicked.connect(self.show_dialog)
        # self.button.clicked.connect(lambda: self.sc.deleteLater())
        # self.button.clicked.connect(lambda: splitter0.addWidget(self.sc))

        splitter0 = QSplitter(Qt.Horizontal)
        splitter0.addWidget(self.table1)
        splitter0.addWidget(self.pic)
        splitter0.setSizes([300, 100])

        splitter1 = QSplitter(Qt.Horizontal)
        widget1 = QWidget()
        label1 = QLabel('Доходность по месяцам и общая $$$')
        label1.setAlignment(Qt.AlignCenter)
        v_layout = QVBoxLayout()
        v_layout.addWidget(label1)
        v_layout.addWidget(self.table2)
        widget1.setLayout(v_layout)

        widget2 = QWidget()
        label2 = QLabel('Максимальный размер сеток по месяцам и общий')
        label2.setAlignment(Qt.AlignCenter)
        v_layout2 = QVBoxLayout()
        v_layout2.addWidget(label2)
        v_layout2.addWidget(self.table3)
        widget2.setLayout(v_layout2)

        splitter1.addWidget(widget1)
        splitter1.addWidget(widget2)
        splitter1.setSizes([100, 120])

        splitter2 = QSplitter(Qt.Vertical)
        splitter2.addWidget(splitter0)
        splitter2.addWidget(splitter1)

        hbox = QHBoxLayout()
        hbox.addWidget(self.button, QtCore.Qt.AlignRight)

        self.grid = QGridLayout()
        self.grid.setSpacing(10)
        self.grid.addWidget(splitter2, 1, 0)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox)

        vbox.addLayout(self.grid)

        self.setLayout(vbox)

    def show_dialog(self):
        # проверим выбран ли отчет
        if isinstance(report, Report):
            report.get_digits()
            report.deals_list()
            report.get_grid_list()
            num = report.get_max_grid_num()
            report.get_digits()
            report.create_final_table1()
            report.make_table2_3()
        else:
            QMessageBox.question(self, 'Внимание!!!', "Выбирите файл\n отчета!!!", QMessageBox.Ok)
            return 0
        path_to_pic = get_file_path_to_pic(report.pathToFile)
        if path_to_pic is not False:
            pixmap =  QPixmap(path_to_pic)
            pixmap.scaled(64,64)
            self.pic.setPixmap(pixmap)
            self.pic.setScaledContents(True)



        self.table1.setRowCount(num)  # создаем таблицу в виджете
# перебираем пандас таблицу и запоняем массив
        n = 0
        for row in report.table1.itertuples():
            self.table1.setItem(n, 0, QTableWidgetItem(row[6]))  # кол-во сеток
            self.table1.setItem(n, 1, QTableWidgetItem(row[11]))  # сумма лотов
            self.table1.setItem(n, 2, QTableWidgetItem(row[1]))  # общая прибыль
            self.table1.setItem(n, 3, QTableWidgetItem(row[4]))  # средняя прибыль
            self.table1.setItem(n, 4, QTableWidgetItem(row[10]))  # процент от общей прибыли
            self.table1.setItem(n, 5, QTableWidgetItem(row[7]))  # максимальные размер сетки
            self.table1.setItem(n, 6, QTableWidgetItem(row[2]))  # средний размер метки
            self.table1.setItem(n, 7, QTableWidgetItem(row[8]))  # максимальное кол-во пипсов до профита
            self.table1.setItem(n, 8, QTableWidgetItem(row[3]))  # среднее кол-во пипсов до профита
            self.table1.setItem(n, 9, QTableWidgetItem(
                conver_min_to_hour_and_min(row[9])))  # максимальные время жизни сетки
            self.table1.setItem(n, 10, QTableWidgetItem(conver_min_to_hour_and_min(row[5])))  # среднее время жизни сетки
            n += 1
        self.table1.resizeColumnsToContents()

# Строим 2 и 3 таблицы
        a = report.table2
        size = a.shape  # (2, 15)

        self.table2.setRowCount(size[0])  # создаем таблицу в виджетеe

        for j in range(size[0]):
            for i in range(size[1]):
                b = str(round(a[j][i], 2))
                self.table2.setItem(j, i, QTableWidgetItem(b))
        self.table2.setItem(size[0] - 1, 0, QTableWidgetItem('Среднее'))
        self.table2.resizeColumnsToContents()
        # строим таблицу3
        a = report.table3
        size = a.shape  # (2, 14)
        self.table3.setRowCount(size[0])  # создаем таблицу в виджете
        for j in range(size[0]):
            for i in range(size[1] - 1):
                b = str(round(a[j][i], 2))
                self.table3.setItem(j, i, QTableWidgetItem(b))
        self.table3.setItem(size[0] - 1, 0, QTableWidgetItem('Среднее'))
        self.table3.resizeColumnsToContents()


class LotsAnalyse(QWidget):
    def __init__(self):
        super().__init__()

        vbox = QVBoxLayout()
        self.btn = QPushButton('MultRaport')
        self.graph = MplCanvas(self, width=5, height=4, dpi=100)

        self.btn.clicked.connect(self.pandas_table_for_graph)
        self.btn.clicked.connect(lambda : vbox.addWidget(self.graph))

        vbox.addWidget(self.btn)
        vbox.addWidget(self.graph)
        self.setLayout(vbox)

    # def sum_list(self):
    #     list_os_tables = self.get_mult_report()
    #     if len(list_os_tables) == 0:
    #         return 0
    #     fig = go.Figure()
    #     for table in list_os_tables:
    #         y = table['lots'].tolist()
    #         x = table['date'].tolist()  # '2021.08.09 08:25'
    #         time_list = [datetime.datetime.strptime(time_str, '%Y.%m.%d %H:%M') for time_str in x]
    #         fig.add_trace(go.Scatter(x=table[time_list], y=table['lots'], name='qwerty'))
    #     fig.show()

    def pandas_table_for_graph(self):
        # подготавливаем пандас таблицу что бы по ней построить графики лотности
        global sum_list
        # если список файлов пустой то ничего не делаем
        if len(sum_list) == 0:
            QMessageBox.question(self, '!!!Внимание!!!', "Добавте файлы\n отчета!!!", QMessageBox.Ok)
            return 0
        mult_table = get_mult_table(sum_list)
        headers = mult_table.columns.tolist()
        headers.remove('date') #  список заголовков без столбца с датой
        for rep in headers:
            mult_table.plot(x='date', y=rep, ax=self.graph.axes)
        return self.graph


class WorkWithSets(QWidget):
    def __init__(self):
        super().__init__()
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
        if isinstance(report, Report) is False:
            QMessageBox.question(self, 'Внимание!!!', "Выбирите файл\n отчета!!!", QMessageBox.Ok)
            return 0
        set = report.get_set()
        self.text_edit.setText(set)

    def save_set_file(self):
        set_text = self.text_edit.toPlainText()
        folder = QFileDialog.getSaveFileName(self,
                                             'Save  file',
                                             confFile.getParam(confFile.filePath,
                                                               'file path for set files',
                                                               'file path'
                                                               ),
                                             "Any files (*.set)",
                                             )
        if folder[0] == '':
            return 0
        file = folder[0]
        file_path = os.path.dirname(file)
        confFile.setParam(confFile.filePath, 'file path for set files', 'file path', file_path)
        with open(folder[0], mode='w', encoding='utf-8') as w_file:
            w_file.writelines(set_text)

    def compress(self):
        string =''
        try:
            fname = QFileDialog.getOpenFileName(self,
                                                'Open file',
                                                confFile.getParam(confFile.filePath,
                                                                    'file path for set files',
                                                                    'file path'
                                                                    ),
                                                "Any files (*.set)")
        except:
            fname = QFileDialog.getOpenFileName(self, 'Open file','',"Any files (*.set)")
        if fname[0] == '':
            return 0
        file = fname[0]
        file_path = os.path.dirname(file)
        confFile.setParam(confFile.filePath, 'file path for set files', 'file path', file_path)

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


class DataBase(QWidget):
    def __init__(self):
        super().__init__()
        pass


if __name__ == "__main__":

    report = 0
    sum_list = []

    confFile = ConfigFile('config\\config.ini')
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
