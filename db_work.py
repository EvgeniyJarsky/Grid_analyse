# create table list(file_path text, selected integer);
import sqlite3
from contextlib import contextmanager


@contextmanager
def db_ops(db_name):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    yield cur
    conn.commit()
    conn.close()


def insert_data(db_path, table_name,  file_path, selected=0):
    # create table list(file_path text, selected integer);
    # db_path - путь к файлу БД
    # table_name - имя таблицы
    # file_path - путь к файлу
    # selected - выбран или нет
    with db_ops(db_path) as cursor:
        insert_query = f"INSERT INTO {table_name} VALUES (?, ?);"
        cursor.execute(insert_query, (file_path, selected))


def get_all_data(db_path):
    """
    возврашаел либо спикок строк, либо 0 если таблица пустая
    return 0 or list: [('first', 0), ('second', 0), ('selected', 1)]
    """
    rez = []
    with db_ops(db_path) as cursor:
        insert_query = f"SELECT * FROM list;"
        cursor.execute(insert_query)
        for row in cursor:
            rez.append(row)
        if len(rez) == 0:
            return 0
        return rez


def get_all(db_path):
    """
    возврашаел либо спикок строк, либо 0 если таблица пустая
    return 0 or list: [('first', 0), ('second', 0), ('selected', 1)]
    """
    with db_ops(db_path) as cursor:
        insert_query = f"SELECT * FROM list;"
        cursor.execute(insert_query)
        list_ = cursor.fetchall()
        return [item[0] for item in list_]


def get_selected(db_path):
    with db_ops(db_path) as cursor:
        insert_query = f"SELECT * FROM list WHERE selected IS 1;"
        cursor.execute(insert_query)
        rez = cursor.fetchone()
        if rez is None:
            return False
        return rez[0]


def mark_selected(db_path, path_to_file):
    with db_ops(db_path) as cursor:
        # сначала сбросим признак выбранности во всех записях
        insert_query = f"UPDATE list SET selected = 0;"
        cursor.execute(insert_query)
        # помечаем выбранную строку 1
        insert_query = f"UPDATE list SET selected = 1 WHERE file_path IS '{path_to_file}';"
        cursor.execute(insert_query)
# UPDATE list SET selected = 1 WHERE file_path IS "second";

def clear_db(db_path, table_name):
    """
    Удаляем все строки в таблице table_name
    input:
    db_path - путь к файлу БД
    table_name - имя таблицы
    return - None
    """
    with db_ops(db_path) as cursor:
        insert_query = f"DELETE FROM {table_name};"
        cursor.execute(insert_query)


def delete_selected(db_path, table_name):
    """
    Удаляем выделеную строку в таблице table_name
    input:
    db_path - путь к файлу БД
    table_name - имя таблицы
    line: строчка которую нало удалить
    return - None
    """
    with db_ops(db_path) as cursor:
        insert_query = f"DELETE FROM {table_name} WHERE selected IS 1;"
        cursor.execute(insert_query)


if __name__ == "__main__":
    # insert_data("database.db", "list",  "first", 0)
    # insert_data("database.db", "list",  "second", 0)
    # insert_data("database.db", "list",  "third", 1)
    # print(get_all_data("database.db"))
    # print(get_all("database.db"))
    print('SELECTED')
    # print(get_selected("database.db"))
    # print("DELETE DATA")
    # clear_db("database.db", "list")
    # delete_selected("database.db", "list")
    # mark_selected("database.db", "second")


