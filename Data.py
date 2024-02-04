import sqlite3
from csvhandler import csv2list, xl2list
from random import choice
import hashlib



class QuizBotData(object):
    def __init__(self, dbname:str="Quiz.db"):
        self.dbname = dbname
        self.db = sqlite3.connect(self.dbname)
        self.cursor = self.db.cursor()
        self.__key = ""
        self.__table = ""

    def __generate_key(self):
        x = ""
        table_name = ""
        characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        for i in range(16):
            x += choice(tuple(characters))
        for i in range(16):
            table_name += choice(tuple(characters[:25]))
        self.__key = x
        self.__table = table_name
        x = hashlib.sha256(x.encode("utf-8")).hexdigest()
        return x

    def create_question_table(self):
        try:
            self.cursor.execute(f"""CREATE TABLE {self.__table}(
                                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                                        Type varchar(250), 
                                        Lang varchar(250),
                                        Question varchar(2000), 
                                        OptionA varchar (250), 
                                        OptionB varchar (250),
                                        OptionC varchar (250), 
                                        OptionD varchar (250),
                                        OptionE varchar (250),
                                        Answer varchar (250), 
                                        Level varchar (250),
                                        Subject varchar (250),
                                        Chapter varchar (250), 
                                        Status varchar (250),
                                        Action varchar (250)
                                        
                                    );
                                    """)
            print(f"Table named {self.__table} created in {self.dbname}")
        except Exception as E:
            print(E)

    def create_quiz_data_table(self):
        try:
            self.cursor.execute(f"""CREATE TABLE QUIZ_DATA(
                                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                    key varchar (250) NOT NULL,
                                                    table_name varchar(250), 
                                                    userid varchar (250), 
                                                    user_fullname varchar (250), 
                                                    time varchar (250), 
                                                    description varchar (250)
                                                );
                                                """)
        except Exception as E:
            print(E)

    def bind(self, userdata):
        statement = f"INSERT INTO QUIZ_DATA(key, table_name, userid, user_fullname, time, description) values(?,?,?,?,?,?)"
        user_id = userdata.get("user id")
        fullname = userdata.get("username")
        time = userdata.get("time")
        description = userdata.get("description")
        values = (self.__key, self.__table, user_id, fullname, time, description)
        try:
            self.cursor.execute(statement,values)
            self.db.commit()
        except Exception as E:
            self.create_quiz_data_table()
            self.cursor.execute(statement,values)
            self.db.commit()



    def upload_csv(self, csvfile, userdata):
        self.__generate_key()
        self.create_question_table()
        statement = f"""INSERT INTO {self.__table}
        (Type, Lang, Question, OptionA, OptionB ,OptionC, OptionD,OptionE,Answer, Level,Subject,Chapter, Status ,Action)
        values(?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""
        self.cursor.executemany(statement, csv2list(csvfile)[1:])
        self.db.commit()
        print("Data inserted")
        self.bind(userdata)
        return self.__key

    def upload_excel(self, excel_file, userdata):
        self.__generate_key()
        self.create_question_table()
        statement = f"""INSERT INTO {self.__table}
                (Type, Lang, Question, OptionA, OptionB ,OptionC, OptionD,OptionE,Answer, Level,Subject,Chapter, Status ,Action)
                values(?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""
        self.cursor.executemany(statement, xl2list(excel_file)[1:])
        self.db.commit()
        print("Data inserted")
        self.bind(userdata)
        return self.__key

    def get_quiz_table_name(self, key):
        try:
            query = f"""SELECT * FROM QUIZ_DATA WHERE key='{key}'"""
            data = self.cursor.execute(query)
            quiz_data = data.fetchone()
            query = f"""SELECT * FROM {quiz_data[2]}"""
            question_data = self.cursor.execute(query)
            question_data = question_data.fetchall()
            return {"quiz_data": quiz_data, "question_data": question_data}
        except:
            return -1


