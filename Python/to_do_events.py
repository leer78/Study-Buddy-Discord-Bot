from events import Event
import datetime
import discord
import csv


class CreateToDoCommand(Event):

    to_do_item: str

    def __init__(self, start_time: datetime.datetime, length: datetime.timedelta, user_id: discord.User, to_do_item: str):
        super().__init__(start_time, length, user_id)
        self.to_do_item = to_do_item

    def run_event(self, event_queue):
        #  Adds the to do item to the users to do list
        print("Grr, I am doing stuff")
        items = []

        with open('database/to_do_lists/' + str(self.user_id) + '.csv', 'a') as creation:
            creation.close()

        with open('database/to_do_lists/' + str(self.user_id) + '.csv', 'r') as to_do_list:
            reader = csv.reader(to_do_list)
            for row in reader:
                items.append(row)

            to_do_list.close()

        items.append([len(items) + 1, self.to_do_item])
        print(str(self.user_id) + ": That should have been a user id")
        with open('database/to_do_lists/' + str(self.user_id) + '.csv', 'w', newline='') as to_do_list:
            writer = csv.writer(to_do_list)
            for item in items:
                writer.writerow(item)

            to_do_list.close()

    def clone_event(self):
        return CreateToDoCommand(self.start_time, self.length, self.user_id, self.to_do_item)


class DeleteToDoCommand(Event):
    to_do_number: str

    def __init__(self, start_time: datetime.datetime, length: datetime.timedelta, user_id: discord.User, to_do_number: str):
        super().__init__(start_time, length, user_id)
        self.to_do_number = to_do_number

    def run_event(self, event_queue):
        items = []
        with open('database/to_do_lists/' + str(self.user_id) + '.csv', 'r') as to_do_list:
            reader = csv.reader(to_do_list)
            for row in reader:
                items.append(row)


        for item in items:
            if item[0] == self.to_do_number:
                items.remove(item)
                break

        with open('database/to_do_lists/' + str(self.user_id) + '.csv', 'w', newline='') as to_do_list:
            writer = csv.writer(to_do_list)
            for item in items:
                writer.writerow(item)

    def clone_event(self):
        return DeleteToDoCommand(self.start_time, self.length, self.user_id, self.to_do_number)


class ViewToDoCommand(Event):

    def __init__(self, start_time: datetime.datetime, length: datetime.timedelta, user_id: discord.User):
        super().__init__(start_time, length, user_id)

    def run_event(self, event_queue):
        output_message = ''

        with open('database/to_do_lists/' + str(self.user_id) + '.csv', 'r') as to_do_list:
            reader = csv.reader(to_do_list)

            for row in reader:
                output_message += row[0] + '. ' + row[1] + '\n'

        return output_message

    def clone_event(self):
        return ViewToDoCommand(self.start_time, self.length, self.user_id)
