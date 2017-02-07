#!/usr/bin/python3

import sys
import json
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import os
 
class AnnotationsTable(QTableWidget):
    def __init__(self, file_name, base_folder, *args):
        QTableWidget.__init__(self, *args)
        self.file_name = file_name
        self.base_folder = base_folder
        self.data = {'File Name': [], "Location": [], "Annotation": []}
        self.update_data()
        self.horizontalHeader().setStretchLastSection(True)
        self.setFixedSize(self.horizontalHeader().length() + 60, self.verticalHeader().length() + 100);
        self.cellClicked.connect(self.click_event)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(1000)

    def update_data(self):
        f = open(self.file_name)
        annotations = json.loads(f.read())
        file_index = annotations['by_file']
        self.data = {'File Name': [], "Location": [], "Annotation": []}
        for annotated_file in file_index:
            for location in file_index[annotated_file]:
                file_label = annotated_file.replace(self.base_folder, "")
                if file_label.startswith("/"):
                    file_label = file_label[1:]
                if file_label.startswith("\\"):
                    file_label = file_label[1:]
                self.data['File Name'].append(file_label)
                self.data['Location'].append(location)
                self.data['Annotation'].append(file_index[annotated_file][location]['text'])
        self.setRowCount(len(self.data['File Name']))
        self.setmydata()
        self.resizeColumnsToContents()
        self.resizeRowsToContents()
        self.horizontalHeader().setStretchLastSection(True)

    def setmydata(self):
 
        horHeaders = []
        for n, key in enumerate(["File Name", "Location", "Annotation"]):
            horHeaders.append(key)
            for m, item in enumerate(self.data[key]):
                newitem = QTableWidgetItem(item)
                self.setItem(m, n, newitem)
        self.setHorizontalHeaderLabels(horHeaders)

    def click_event(self, row, col):
        path = os.path.join(self.base_folder, self.item(row, 0).text())
        print( path + "," + self.item(row, 1).text())
        sys.stdout.flush()
 
def main(args):
    app = QApplication(args)
    table = AnnotationsTable(sys.argv[1], sys.argv[2], 0, 3)
    table.show()
    sys.exit(app.exec_())

 
if __name__=="__main__":
    main(sys.argv)