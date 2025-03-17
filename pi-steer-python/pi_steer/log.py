import csv
import datetime

class Log():
    def __init__(self, name) -> None:
        self.data = []
        self.count = 0
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S ")
        self.name = date + name

    def log_csv(self, data):
        self.count += 1
        self.data.append(data)
        if self.count % 100:
            try:
                with open(self.name+'.csv', 'a') as file:
                    writer = csv.writer(file)
                    writer.writerows(self.data)
            except Exception as err:
                print('CSV file write error', err)
            self.data = []

    def log_text(self, text):
        self.count += 1
        self.data.append(text)
        if self.count % 10:
            try:
                with open(self.name+'.txt', 'a') as file:
                    file.writelines(self.data)
            except Exception as err:
                print('CSV file write error', err)
            self.data = []
