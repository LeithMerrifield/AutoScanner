from collections.abc import Callable, Iterable, Mapping
from typing import Any
import pyodbc
from cryptography.fernet import Fernet
import base64
import subprocess
from threading import Thread

# InitialDate = "2023-12-02 23:21:01"
# CompletionTime = "00:05:11"
# Author = "leith"
# ItemList = '{"Item 1": ["SKU", "QTY"], "Item 2": ["SKU", "QTY"]}'


class CustomThread(Thread):
    def __init__(
        self,
        group: None = None,
        target: Callable[..., object] | None = None,
        name: str | None = None,
        args: Iterable[Any] = ...,
        kwargs: Mapping[str, Any] | None = None,
        *,
        daemon: bool | None = None,
    ) -> None:
        Thread.__init__(group, target, name, args, kwargs, daemon=daemon)
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)

    def join(self):
        Thread.join(self, *self._args)
        return self._return


class sqlobject:
    def __init__(self) -> None:
        SERVER = "autoscanner-database.database.windows.net"
        DATABASE = "ScannerTelemetry"
        USERNAME = "leith"
        self.PASSWORD1 = b""
        self.PASSWORD2 = b""
        password = self.decrypt_pass()
        self.connection_string = f"Driver={{ODBC Driver 18 for SQL Server}};Server=tcp:autoscanner-database.database.windows.net,1433;Database=ScannerTelemetry;Uid=leith;Pwd={password};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
        self.conn = None
        self.cursor = None

    def decrypt_pass(self):
        ip = subprocess.check_output("curl icanhazip.com").strip().decode()
        padding = "stinkier"
        padding2 = "stinky"
        keystring = ip + padding + ip
        flag = False

        if len(keystring) != 32:
            keystring = ip + padding2 + ip
            flag = True

        key = base64.urlsafe_b64encode(keystring.encode())
        f = Fernet(key)

        if flag:
            return f.decrypt(self.PASSWORD2).decode()
        else:
            return f.decrypt(self.PASSWORD1).decode()

    def insert_single_database(self, initial_date, completion_time, author, item_list):
        QUERY = f"INSERT INTO PickTasks (InitialDate,CompletionTime,Author,ItemList) Values ('{initial_date}','{completion_time}','{author}','{item_list}');"
        self.cursor.execute(QUERY)

    def make_connection(self):
        self.conn = pyodbc.connect(self.connection_string)
        self.cursor = self.conn.cursor()

    def insert_many_database(self, query_list: list):
        # needs to not be empty
        self.make_connection()
        self.cursor.executemany(
            "INSERT INTO PickTasks (InitialDate,CompletionTime,Author,ItemList) Values (?,?,?,?)",
            query_list,
        )
        self.commit_to_database()

    def get_all(self):
        self.cursor.execute("SELECT * FROM PickTasks;")
        return self.cursor.fetchall()

    def commit_to_database(self):
        self.cursor.commit()


SQLtest = sqlobject()
SQLtest

# InitialDate = "2023-12-02 23:21:01"
# CompletionTime = "00:05:11"
# Author = "leith"
# ItemList = '{"Item 1": ["SKU", "QTY"], "Item 2": ["SKU", "QTY"]}'
