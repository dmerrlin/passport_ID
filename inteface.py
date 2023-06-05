from PySide2 import QtWidgets
from PySide2 import QtGui
from PySide2.QtGui import QImage, QPixmap
from PySide2 import QtCore
from PySide2.QtWidgets import QFileDialog
from PySide2.QtWidgets import QMessageBox
from PySide2.QtWidgets import QMenu
import numpy
from datetime import datetime
import sys
import os
import cv2
from ui import Ui_MainWindow
from settings import Ui_Dialog
from contyr import scan
import pytesseract
from AES import decrypt, encrypt

pytesseract.pytesseract.tesseract_cmd = 'Tesseract-OCR\\tesseract.exe'

class ExampleAppSetting(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__()

        self.setupUi(self)

class ExampleApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__()
        self.logic = 0
        self.camera = 0
        self.e = 7
        self.n = 33
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна


    def displayImage(self, img, window=1):
        qformat = QImage.Format_Indexed8
        if len(img.shape) == 3:
            if (img.shape[2]) == 4:
                qformat = QImage.Format_RGBA888
            else:
                qformat = QImage.Format_RGB888
        img = QImage(img, img.shape[1], img.shape[0],  qformat)
        img = img.rgbSwapped()
        self.imgLabel.setPixmap(QPixmap.fromImage(img))
        self.imgLabel.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)

def parse_string(str):
    doc = str[:2]
    ret = "Документ:" + doc + "\n"
    counry = str[2] + str[3] + str[4]
    ret += "Страна:" + counry + "\n"
    i = 5
    firstname = ""
    while( str[i] != "<"):
        firstname += str[i]
        i+=1
    while (str[i] == "<"):
        i += 1
    ret += "Фамилия:" + firstname + "\n"
    name = ""
    while (str[i] != "<"):
        name += str[i]
        i += 1
    while (str[i] == "<"):
        i += 1
    ret += "Имя: " + name + "\n"
    patronymic= ""
    while( str[i] != "<"):
        patronymic += str[i]
        i+=1

    while (str[i] != "\n"):
        i += 1
    ret += "Отчество: " + patronymic + "\n"
    doc_number = ""
    for j in range(9):
        doc_number += str[i+1+j]
    ret += "Номер документа: " + doc_number + "\n"
    i += 10
    hash = str[i]
    nationality = ""
    for j in range(3):
        nationality += str[i+1+j]
    i += 4
    ret += "Национальность: " + nationality + "\n"
    bitrth_date = ""
    for j in range(6):
        bitrth_date += str[i+j]
    ret += "Дата рождения: " + bitrth_date + "\n"
    i += 6
    hash2 = str[i]
    sex = str[i+1]
    ret += "Пол: " + sex + "\n"
    i += 2
    expiry_date = ""
    for j in range(6):
        expiry_date += str[i+j]
    i += 7
    hash3 = str[i-1]
    personal_number = ""
    for j in range(14):
        personal_number += str[i+j]
    ret += "Персональный номер: " +personal_number + "\n"
    i += 14
    hash4 = str[i]
    hash5 = str[i+1]
    return ret

if __name__ == '__main__':
    # Новый экземпляр QApplication
    app = QtWidgets.QApplication(sys.argv)
    # Сздание инстанса класса
    UI = ExampleApp()
    UI.show()

    def click():
        dialog_name = "Пожалуйста выберите файл"
        folder_init_name = "D:/"
        filter = "Изображения(*.png *.xpm *.jpg)"
        filename = QFileDialog.getOpenFileName(UI, dialog_name, folder_init_name, filter)
        image = cv2.imread(filename[0])
        try:
            mrz = scan(image)
            config = r'--oem 3 --psm 6'
            text = pytesseract.image_to_string(mrz, lang='mrz', config=config)
            UI.textEdit_2.setText(text)
            UI.textEdit.setText(parse_string(text))
            f = open('settings.txt', 'r')
            if f.readline() == "True\n":
                open_key = f.readline()
                filename = f.readline()
                f.close()
                current_datetime = datetime.now()
                f = open(filename.rstrip()+"/"+str(current_datetime.year)+"-"+str(current_datetime.month)+"-"+str(current_datetime.day)+"_"+str(current_datetime.hour)+"_"+str(current_datetime.minute)+"_"+str(current_datetime.second)+"logs.txt", 'w')
                encrypted = encrypt(UI.textEdit_2.toPlainText()+"&"+UI.textEdit.toPlainText(), open_key.rstrip())
                decrypted = decrypt(eval(str(encrypted)), open_key.rstrip())
                print(bytes.decode(decrypted))
                f.write(str(encrypted))
                f.close()
        except:
            UI.textEdit_2.setText("Ошибка при сканирование")

    def analysisCliced():
        dialog_name = "Пожалуйста выберите файл"
        folder_init_name = "D:/"
        filter = "Анализ(*.txt)"
        filename = QFileDialog.getOpenFileName(UI, dialog_name, folder_init_name, filter)
        f = open('settings.txt', 'r')
        if f.readline() == "True\n":
            open_key = f.readline()
            f.close()
            f = open(filename[0], 'r')
            try:
                encrypted = f.read()
                decrypted = decrypt(eval(str(encrypted)), open_key.rstrip())
                text = str(bytes.decode(decrypted))
            except:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Error")
                msg.setInformativeText('Неверный ключ')
                msg.setWindowTitle("Error")
                msg.exec_()
        else:
            f.close()
            f = open(filename[0], 'r')
            text = f.read()
        ui = False
        ui1 = ""
        ui2 = ""
        for i in range(len(text)):
            if text[i] == "&":
                ui = True
                i+=1
            if ui == False:
                ui1 += text[i]
            else:
                ui2 += text[i]
        UI.textEdit_2.setText(ui1)
        UI.textEdit.setText(ui2)

    def onClicked():
        if UI.camera == 0:
            UI.camera = 1
            UI.pushButton_2.setText("Выключить камеру")
        else:
            UI.camera = 0
            UI.pushButton_2.setText("Включить камеру")
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        while (cap.isOpened() and UI.camera == 1):
            ret, frame = cap.read()
            if ret == True:
                print('here')
                UI.displayImage(frame, 1)
                cv2.waitKey()
                if UI.logic == 1:
                    UI.logic = 0
                    try:
                        mrz = scan(image)
                        config = r'--oem 3 --psm 6'
                        text = pytesseract.image_to_string(mrz, lang='mrz', config=config)
                        UI.textEdit_2.setText(text)
                        UI.textEdit.setText(parse_string(text))
                        f = open('settings.txt', 'r')
                        if f.readline() == "True\n":
                            open_key = f.readline()
                            filename = f.readline()
                            f.close()
                            current_datetime = datetime.now()
                            f = open(filename.rstrip() + "/" + str(current_datetime.year) + "-" + str(
                                current_datetime.month) + "-" + str(current_datetime.day) + "_" + str(
                                current_datetime.hour) + "_" + str(current_datetime.minute) + "_" + str(
                                current_datetime.second) + "logs.txt", 'w')
                            encrypted = encrypt(UI.textEdit_2.toPlainText() + UI.textEdit.toPlainText(), open_key.rstrip())
                            decrypted = decrypt(eval(str(encrypted)), open_key.rstrip())
                            print(bytes.decode(decrypted))
                            f.write(str(encrypted))
                            f.close()

                    except:
                        UI.textEdit_2.setText("Ошибка при сканирование")
                    UI.camera = 0
            else:
                print('not found')
        cap.release()
        cv2.destroyAllWindows()

    def test():
        if UI.camera == 0:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error")
            msg.setInformativeText('Сначала нужно включить камеру')
            msg.setWindowTitle("Error")
            msg.exec_()
        else:
            UI.logic = 1

    def settings_open():
        global UI_setting
        UI_setting = ExampleAppSetting()
        f = open('settings.txt', 'r')
        if f.readline() == "True\n":
            UI_setting.checkBox.setCheckState(QtCore.Qt.Checked)
        else:
            UI_setting.checkBox.setCheckState(QtCore.Qt.Unchecked)
        UI_setting.lineEdit.setText(f.readline())
        UI_setting.lineEdit_2.setText(f.readline())
        f.close()
        UI_setting.show()
        def click_close():
            UI_setting.close()

        def openFileDialog_setting():
            dialog_name = "Пожалуйста выберите файл"
            folder_init_name = "D:/"
            filename = QFileDialog.getExistingDirectory(UI_setting, dialog_name, folder_init_name)
            UI_setting.lineEdit_2.setText(filename)

        def save_setting():
            if os.path.exists(UI_setting.lineEdit_2.displayText()) == True:
                f = open('settings.txt', 'w')
                f.write(str(UI_setting.checkBox.isChecked())+"\n")
                f.write(UI_setting.lineEdit.displayText()+"\n")
                f.write(UI_setting.lineEdit_2.displayText()+"\n")
                f.close()
                UI_setting.close()
            else:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Error")
                msg.setInformativeText('Такой паки не существует')
                msg.setWindowTitle("Error")
                msg.exec_()

        UI_setting.pushButton_3.clicked.connect(openFileDialog_setting)
        UI_setting.pushButton_2.clicked.connect(click_close)
        UI_setting.pushButton.clicked.connect(save_setting)
    UI.pushButton_2.clicked.connect(onClicked)

    def click_close():
        UI.camera = 0
        UI.close()


    UI.pushButton_3.clicked.connect(click)
    UI.pushButton_4.clicked.connect(test)
    UI.pushButton_5.clicked.connect(settings_open)
    UI.pushButton_7.clicked.connect(analysisCliced)
    fileMenu = QMenu("Открыть", UI)
    fileMenu.addAction("Открыть анализ",analysisCliced)
    fileMenu.addAction("Читать файл", click)
    fileMenu.addAction("Включить камеру",onClicked)
    fileMenu.addAction("Сделать анализ с кадра камеры",test)
    UI.menuBar.addMenu(fileMenu)
    UI.menuBar.addAction("Настройки",settings_open)
    UI.menuBar.addAction("Выход", click_close)


    # Запуск
    sys.exit(app.exec_())