from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import Utils



class DataPreviewWindow(QDialog):

    def __init__(self, data):
        super().__init__()
        self.processedData = data

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.buttonGroup = QWidget()
        self.buttonGroupLayout = QHBoxLayout(self.buttonGroup)
        self.adjustmentscompleted = QPushButton("Готово")
        self.adjustmentscompleted.clicked.connect(self.accept)
        self.buttonGroupLayout.addWidget(self.adjustmentscompleted)
        self.cancelbutton = QPushButton("Отмена")
        self.cancelbutton.clicked.connect(self.reject)
        self.buttonGroupLayout.addWidget(self.cancelbutton)

        self.dataPreviewTable = QTableWidget()
        self.layout.addWidget(self.dataPreviewTable)
        self.layout.addWidget(self.buttonGroup)
#        self.initdatapreview()
        self.setWindowTitle("Предпросмотр данных")
        if data.columnCount() > 10:
            self.resize(700, 550)
        else:
            self.resize(700, 50*data.columnCount() + 50)
        self.show()

    def initdatapreview(self):
        self.dataPreviewTable.setColumnCount(5)
        self.dataPreviewTable.setRowCount(self.processedData.columnCount())
        self.dataPreviewTable.setHorizontalHeaderLabels(["Колонка", "Среднее\nзначение","Среднеквадратичное\nотклонение",
                                                         "Весовой\n коэффициент", "Включить в\nрассмотрение?"
                                                         ])
        columnheaders = self.processedData.getColumnNames()
        for i, column in enumerate(self.processedData.getColumns()):
            self.dataPreviewTable.setItem(i, 0, QTableWidgetItem(columnheaders[i]))
            self.dataPreviewTable.setItem(i, 1, QTableWidgetItem(str(column.getAverageValue())))
            self.dataPreviewTable.setItem(i, 2, QTableWidgetItem(str(column.getStandartDerivation())))

            weighteditor = QLineEdit(str(column.getWeight()))
            weighteditor.editingFinished.connect(lambda column=column, weighteditor=weighteditor: self.adjustweight(column, weighteditor))
            self.dataPreviewTable.setCellWidget(i, 3, weighteditor)
            checkboxcontainer = QWidget()
            checkboxcontainer.setStyleSheet("background-color:#cccccc;")
            containerlayout = QVBoxLayout(checkboxcontainer)
            containerlayout.setAlignment(Qt.AlignCenter)
            checkbox = QCheckBox("Да")
            containerlayout.addWidget(checkbox)
            self.dataPreviewTable.setCellWidget(i, 4, checkboxcontainer)
            checkbox.setChecked(True)
            checkbox.stateChanged.connect(lambda event, column=column, checkbox=checkbox: self.checkboxstatechanged(column, checkbox))
        self.dataPreviewTable.resizeColumnsToContents()

    def checkboxstatechanged(self, column, checkbox):
        if checkbox.isChecked():
            checkbox.setText("Да")
            column.setSignificance(True)
        else:
            checkbox.setText("Нет")
            column.setSignificance(False)

    def adjustweight(self, column, lineedit):
        try:
            column.setWeight(int(lineedit.text()))
        except ValueError:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Весовой коэффициент задан некорректно")
            msg.setWindowTitle("Внимание")
            msg.exec_()
            lineedit.setText("1")

    @staticmethod
    def preprocessData(data):
        dialog = DataPreviewWindow(data)
        result = dialog.exec_()
        if result:
            return dialog.processedData
        return None



