" Result "
#from rough import submitted_data, correct_answeri_id

import prettytable as pt



class Personalised_User_Result(object):
    def __init__(self, user_id:int, collected_data:list[dict], correct_options:dict):
        self.user_id = user_id
        self.collected_data = collected_data
        self.correct_options = correct_options
        self.username = ""
        self.first_name = ""
        self.last_name = ""
        self.full_name = ""
        self.option_ids = {}
        self.attempted_question = []
        self.total_questions = len(self.correct_options)
        self.total_attempted = 0
        self.got_correct = 0
        self.percent = 0
        self.time_taken_in_sec = 0
        self.time_taken_in_min = ""
        self.func()

    def set_properties(self, data: dict):
        self.username = data["username"]
        self.first_name = data["firstname"]
        self.last_name = data["lastname"]
        self.get_full_name()

    def get_full_name(self):
        """if self.first_name ==  None:
            if self.last_name !=  None:
                self.full_name = self.first_name + " " + self.last_name
            else:
                self.full_name = self.first_name
        else:
            self.full_name = self.first_name"""
        if self.first_name == None:
            self.full_name = self.last_name
        elif self.last_name == None:
            self.full_name = self.first_name
        else:
            self.full_name = self.first_name +" "+self.last_name


    def get_option_ids(self, data):
        poll_id = data["poll_id"]
        option_id = data["option_ids"]
        if poll_id not in self.option_ids.keys():
            self.option_ids[poll_id] = option_id
        else:
            pass

    def get_attempted_question(self, data):
        poll_id = data["poll_id"]
        if poll_id not in self.attempted_question:
            self.attempted_question.append(poll_id)
        else:
            pass
        self.total_attempted = len(self.attempted_question)

    def get_score(self):
        score = 0
        for poll_id in self.attempted_question:
            correct_ans = self.correct_options.get(poll_id)
            submitted_ans = self.option_ids.get(poll_id)[0]
            if correct_ans == submitted_ans:
                score += 1
            else:
                continue
        self.got_correct = score
        self.percent = round((self.got_correct / self.total_questions) * 100, 2)
        return score


    def calc_time(self, data):
        self.time_taken_in_sec += data["time_taken"]

    def sec2min(self):
        min = self.time_taken_in_sec//60
        sec = round(self.time_taken_in_sec % 60)
        self.time_taken_in_min = f"{min} min {sec} sec"

    def func(self):
        for data in self.collected_data:
            if self.user_id in data.values():
                self.set_properties(data)
                self.get_option_ids(data)
                self.get_attempted_question(data)
                self.get_score()
                self.calc_time(data)
                self.sec2min()
            else:
                continue

class Answer_Stats(object):
    def __init__(self, collected_data, correct_options):
        self.collected_data = collected_data
        self.correct_options = correct_options
        self.user_ids = set({})
        self.poll_ids = set({})
        self.result = []
        self.func()

    def func(self):
        for data in self.collected_data:
            self.user_ids.add(data["user_id"])
            self.poll_ids.add(data["poll_id"])

    def generate_leaderboard(self):
        for userid in self.user_ids:
            temp = {}
            user = Personalised_User_Result(userid, self.collected_data, self.correct_options)
            temp["user_id"] = user.user_id
            temp["username"] = user.username
            temp["firstname"] = user.first_name
            temp["lastname"] = user.last_name
            temp["fullname"] = user.full_name
            temp["score"] = user.got_correct
            temp["percentage"] = user.percent
            temp["attempted"] = user.total_attempted
            temp["total questions"] = user.total_questions
            temp["time_taken"] = user.time_taken_in_min
            temp["time_taken_in_sec"] = user.time_taken_in_sec
            temp["attempted_poll_id"] = user.attempted_question
            temp["option_ids"] = user.option_ids
            self.result.append(temp)
        self.result = sorted(self.result, key=lambda x: (-x.get("percentage"), x.get("time_taken_in_sec")))

    def get_table(self):
        table = pt.PrettyTable(['Full Name', 'Score', 'Percentage', 'Time Taken'])
        table.align['Full Name'] = 'l'
        table.align['Score'] = 'r'
        table.align['Percentage'] = 'r'
        table.align['Time Taken'] = 'r'
        for i in self.result:
            table.add_row([i.get('fullname'), i.get('score'), i.get('percentage'), i.get('time_taken')])
        return table

