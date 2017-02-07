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
        self.search = None
        self.update_data()
        self.horizontalHeader().setStretchLastSection(True)
        
        self.cellClicked.connect(self.click_event)

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
                annotation = file_index[annotated_file][location]['text']
                if self.search is None or \
                    (self.search and (self.search in file_label \
                        or self.search in annotation)):
                    self.data['File Name'].append(file_label)
                    self.data['Location'].append(location)
                    self.data['Annotation'].append(annotation)
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

    def handle_search(self, text):
        if text == "":
            self.search = None
        else:
            self.search = text
        self.update_data()

 
def main(args):
    app = QApplication(args)
    main_window = QMainWindow()
    main_widget = QWidget(main_window)
    main_window.setCentralWidget(main_widget)
    frame_layout = QVBoxLayout(main_widget)
    table = AnnotationsTable(sys.argv[1], sys.argv[2], 0, 3)
    frame_layout.addWidget(table)
    horizontal_widget = QWidget()
    horizontal_layout = QHBoxLayout()
    search_bar = QLineEdit()
    search_bar.textChanged.connect(table.handle_search)
    search_label = QLabel("Search Annotations:")
    refresh_button = QPushButton("Refresh Annotations")
    refresh_button.clicked.connect(table.update_data)
    horizontal_layout.addWidget(search_label)
    horizontal_layout.addWidget(search_bar)
    horizontal_layout.addWidget(refresh_button)
    horizontal_widget.setLayout(horizontal_layout)
    frame_layout.addWidget(horizontal_widget)
    main_widget.setLayout(frame_layout)

    main_window.show()
    sys.exit(app.exec_())

 
if __name__=="__main__":
    main(sys.argv)