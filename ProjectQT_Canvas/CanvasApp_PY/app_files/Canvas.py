from PyQt6.QtWidgets import QWidget, QApplication, QLabel, QMainWindow, QPushButton, QLineEdit, QSlider, QFileDialog
from PyQt6.QtGui import QPixmap, QPainter, QPen, QColor, QIcon, QCursor, QImage
from PyQt6.QtCore import Qt, QSize, QDir
import sys
import datetime
import os
import shutil
import sqlite3
from pathlib import Path

APP_ICONS = Path('resources/icons')
PEN_ICONS = Path('resources/pen_icons')
COLOR_ICONS = Path('resources/color_icons')
SAVED_PICTURES = Path('../Saved_Pictures')
BACKUPS_DIR = Path('resources/temp/backups')
COMMITTED_BACKUPS_DIR = Path('resources/temp/committed_backups')
BACKUPS_DB = Path('backups.db')
COMMITTED_BACKUPS_DB = Path('committed_backups.db')
TEMP_DIR = Path('resources/temp')

PENCIL_BUCKET_ICON = APP_ICONS.joinpath('PencilBucket_Icon.png')
ERASER_ICON = APP_ICONS.joinpath('Eraser_Icon.png')
PALETTE_ICON = APP_ICONS.joinpath('Palette_Icon.png')
FILE_ICON = APP_ICONS.joinpath('File_Icon.png')
SMALL_CIRCLE_ICON = APP_ICONS.joinpath('SmallCircle_Icon.png')
BIG_CIRCLE_ICON = APP_ICONS.joinpath('BigCircle_Icon.png')
STEP_BACK_ICON = APP_ICONS.joinpath('StepBack_Icon.png')
STEP_FORWARD_ICON = APP_ICONS.joinpath('StepForward_Icon.png')
NEW_CANVAS_ICON = APP_ICONS.joinpath('NewCanvas_Icon.png')
SAVE_IMAGE_ICON = APP_ICONS.joinpath('SaveImage_Icon.png')
UPLOAD_IMAGE_ICON = APP_ICONS.joinpath('UploadImage_Icon.png')
SQUARE_ICON = APP_ICONS.joinpath('Square_Icon.png')
CHALK_ICON = PEN_ICONS.joinpath('Chalk_Icon.png')
MARKER_ICON = PEN_ICONS.joinpath('Marker_Icon.png')
PEN_ICON = PEN_ICONS.joinpath('Pen_Icon.png')
PENCIL_ICON = PEN_ICONS.joinpath('Pencil_Icon.png')

GlobalIDCounter = 0
LocalCommittedIDCounter = 0


class CanvasApp(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Canvas')
        self.setGeometry(300, 100, 1290, 825)  # 1280-720
        self.setFixedSize(1290, 825)

        self.colorPalette = [Qt.GlobalColor.black, Qt.GlobalColor.white,
                             Qt.GlobalColor.lightGray, Qt.GlobalColor.darkGray, Qt.GlobalColor.cyan,
                             Qt.GlobalColor.darkCyan, Qt.GlobalColor.blue, Qt.GlobalColor.darkBlue,
                             Qt.GlobalColor.red, Qt.GlobalColor.darkRed, Qt.GlobalColor.magenta,
                             Qt.GlobalColor.darkMagenta, Qt.GlobalColor.green, Qt.GlobalColor.darkGreen,
                             Qt.GlobalColor.yellow, Qt.GlobalColor.darkYellow]

        self.currentColor = QColor(self.colorPalette[0])
        self.makePaleColor()
        self.currentWidth = 10

        self.basicPen = QPen()
        self.basicPen.setCapStyle(Qt.PenCapStyle.RoundCap)
        self.basicPen.colorToughness = 'normal'
        self.basicPen.name = 'Ручка'

        self.basicPencil = QPen()
        self.basicPencil.setCapStyle(Qt.PenCapStyle.SquareCap)
        self.basicPencil.colorToughness = 'pale'
        self.basicPencil.name = 'Карандаш'

        self.basicMarker = QPen()
        self.basicMarker.setCapStyle(Qt.PenCapStyle.FlatCap)
        self.basicMarker.colorToughness = 'pale'
        self.basicMarker.name = 'Маркер'

        self.basicChalk = QPen()
        self.basicChalk.setCapStyle(Qt.PenCapStyle.FlatCap)
        self.basicChalk.colorToughness = 'normal'
        self.basicChalk.name = 'Мел'

        self.allPens = [self.basicPen, self.basicPencil, self.basicMarker, self.basicChalk]

        self.eraser = QPen()
        self.eraser.setCapStyle(Qt.PenCapStyle.RoundCap)
        self.eraser.setWidth(self.currentWidth)
        self.eraser.setColor(QColor(self.colorPalette[1]))

        self.canvasBox = QLabel(self)
        self.canvas = QPixmap(1280, 720)
        self.canvas.fill(Qt.GlobalColor.white)
        self.canvasBox.setPixmap(self.canvas)
        self.canvasBox.setGeometry(5, 100, 1280, 720)

        self.toolboxBackgroundBox = QLabel(self)
        self.toolboxBackground = QPixmap(1290, 100)
        self.toolboxBackground.fill(Qt.GlobalColor.lightGray)
        self.toolboxBackgroundBox.setPixmap(self.toolboxBackground)
        self.toolboxBackgroundBox.setGeometry(0, 0, 1290, 95)

        self.statsBackgroundBox = QLabel(self)
        self.statsBackground = QPixmap(215, 80)
        self.statsBackground.fill(QColor(240, 240, 240))
        self.statsBackgroundBox.setPixmap(self.statsBackground)
        self.statsBackgroundBox.setGeometry(1040, 9, 215, 80)

        self.penChangeMenuButton = QPushButton(self)
        self.penChangeMenuButton.setGeometry(170, 10, 60, 60)
        self.penChangeMenuButton.setIcon(QIcon(str(PENCIL_BUCKET_ICON)))
        self.penChangeMenuButton.setIconSize(QSize(55, 55))
        self.penChangeMenuButtonLabel = QLabel(self)
        self.penChangeMenuButtonLabel.setGeometry(160, 72, 85, 17)
        self.penChangeMenuButtonLabel.setText('Сменить кисть')

        self.eraserButton = QPushButton(self)
        self.eraserButton.setGeometry(270, 10, 60, 60)
        self.eraserButton.setIcon(QIcon(str(ERASER_ICON)))
        self.eraserButton.setIconSize(QSize(50, 50))
        self.eraserButton.clicked.connect(self.setEraser)
        self.eraserButtonLabel = QLabel(self)
        self.eraserButtonLabel.setGeometry(281, 72, 85, 17)
        self.eraserButtonLabel.setText('Ластик')

        self.colorChangeMenuButton = QPushButton(self)
        self.colorChangeMenuButton.setGeometry(370, 10, 60, 60)
        self.colorChangeMenuButton.setIcon(QIcon(str(PALETTE_ICON)))
        self.colorChangeMenuButton.setIconSize(QSize(50, 50))
        self.colorChangeMenuButtonLabel = QLabel(self)
        self.colorChangeMenuButtonLabel.setGeometry(361, 72, 85, 17)
        self.colorChangeMenuButtonLabel.setText('Сменить цвет')

        self.fileWorkMenuButton = QPushButton(self)
        self.fileWorkMenuButton.setGeometry(40, 10, 60, 60)
        self.fileWorkMenuButton.setIcon(QIcon(str(FILE_ICON)))
        self.fileWorkMenuButton.setIconSize(QSize(56, 56))
        self.fileWorkMenuButtonLabel = QLabel(self)
        self.fileWorkMenuButtonLabel.setGeometry(20, 72, 105, 17)
        self.fileWorkMenuButtonLabel.setText('Работа с файлами')

        self.widthChangeSlider = QSlider(Qt.Orientation.Horizontal, self)
        self.widthChangeSlider.setGeometry(770, 27, 200, 40)
        self.widthChangeSlider.setMinimum(1)
        self.widthChangeSlider.setMaximum(30)
        self.widthChangeSlider.setValue(10)
        self.widthChangeSlider.setTickInterval(1)
        self.widthChangeSlider.sliderReleased.connect(self.changeWidth)
        self.widthChangeSlider.valueChanged.connect(self.changeWidth)
        self.widthChangeSlider.setStyleSheet("""QSlider::groove:horizontal {  
                                                    height: 10px;
                                                    margin: 0px;
                                                    border-radius: 5px;
                                                    background: #f0f0f0;
                                                }
                                                QSlider::handle:horizontal {
                                                    background: #877b80;
                                                    border: 1px solid #909090;
                                                    width: 17px;
                                                    margin: -5px 0; 
                                                    border-radius: 9px;
                                                }
                                                QSlider::sub-page:qlineargradient {
                                                    background: #000000;
                                                    border-radius: 5px;
                                                }""")
        self.smallCircleLabel = QLabel(self)
        self.smallCircleLabel.setGeometry(776, 63, 20, 20)
        self.smallCircleLabel.setPixmap(QPixmap(str(SMALL_CIRCLE_ICON)))
        self.bigCircleLabel = QLabel(self)
        self.bigCircleLabel.setGeometry(949, 57, 30, 30)
        self.bigCircleLabel.setPixmap(QPixmap(str(BIG_CIRCLE_ICON)))
        self.widthChangeSliderLabel = QLabel(self)
        self.widthChangeSliderLabel.setGeometry(798, 13, 140, 20)
        self.widthChangeSliderLabel.setText('Изменить толщину пера')
        self.widthChangeSliderLabel.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.stepBackButton = QPushButton(self)
        self.stepBackButton.setGeometry(520, 10, 60, 60)
        self.stepBackButton.setIcon(QIcon(str(STEP_BACK_ICON)))
        self.stepBackButton.setIconSize(QSize(50, 50))
        self.stepBackButton.clicked.connect(self.stepBack)
        self.stepBackButton.setEnabled(False)
        self.stepBackButtonLabel = QLabel(self)
        self.stepBackButtonLabel.setGeometry(520, 73, 60, 17)
        self.stepBackButtonLabel.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.stepBackButtonLabel.setText('Отменить')

        self.stepForwardButton = QPushButton(self)
        self.stepForwardButton.setGeometry(620, 10, 60, 60)
        self.stepForwardButton.setIcon(QIcon(str(STEP_FORWARD_ICON)))
        self.stepForwardButton.setIconSize(QSize(50, 50))
        self.stepForwardButton.clicked.connect(self.stepForward)
        self.stepForwardButton.setEnabled(False)
        self.stepForwardButtonLabel = QLabel(self)
        self.stepForwardButtonLabel.setGeometry(620, 73, 60, 17)
        self.stepForwardButtonLabel.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.stepForwardButtonLabel.setText('Вернуть')

        self.currentPen = self.basicPen
        self.isEraser = False
        self.applyPenSettings()

        self.currentPenLabel = QLabel(self)
        self.currentPenLabel.setGeometry(1050, 15, 80, 17)
        self.currentPenLabel.setText('Текущее перо:')
        self.currentPenValue = QLabel(self)
        self.currentPenValue.setGeometry(1139, 15, 80, 17)
        self.currentPenValue.setText(self.currentPen.name)

        self.currentColorLabel = QLabel(self)
        self.currentColorLabel.setGeometry(1050, 40, 115, 17)
        self.currentColorLabel.setText('Текущий цвет (RGB):')
        self.currentColorValue = QLabel(self)
        self.currentColorValue.setGeometry(1170, 40, 120, 17)
        self.currentColorValue.setText(f'({str(self.currentColor.red())}, {str(self.currentColor.green())}, '
                                       f'{str(self.currentColor.blue())})')

        self.currentWidthLabel = QLabel(self)
        self.currentWidthLabel.setGeometry(1050, 65, 110, 17)
        self.currentWidthLabel.setText('Текущая толщина:')
        self.currentWidthValue = QLabel(self)
        self.currentWidthValue.setGeometry(1161, 65, 80, 17)
        self.currentWidthValue.setText(str(self.currentWidth))

        self.latestPaintedPixel = None
        self.previousCanvas = self.canvasBox.pixmap()
        self.clickIsInCanvas = False

    def mouseMoveEvent(self, current):
        if self.clickIsInCanvas:
            temp_canvas = self.canvasBox.pixmap()
            painter = QPainter(temp_canvas)
            painter.setPen(self.currentPen if not self.isEraser else self.eraser)
            painter.drawLine(int(current.position().x()) - 5, int(current.position().y()) - 100,
                             self.latestPaintedPixel[0], self.latestPaintedPixel[1])
            self.latestPaintedPixel = (int(current.position().x()) - 5, int(current.position().y()) - 100)
            painter.end()
            self.canvasBox.setPixmap(temp_canvas)

    def mousePressEvent(self, current):
        if 5 <= int(current.position().x()) <= 1285 and 100 <= int(current.position().y()) <= 820:
            self.clickIsInCanvas = True
            temp_canvas = self.canvasBox.pixmap()
            painter = QPainter(temp_canvas)
            painter.setPen(self.currentPen if not self.isEraser else self.eraser)
            painter.drawPoint(int(current.position().x()) - 5, int(current.position().y()) - 100)
            self.latestPaintedPixel = int(current.position().x()) - 5, int(current.position().y()) - 100
            painter.end()
            self.canvasBox.setPixmap(temp_canvas)

    def mouseReleaseEvent(self, current):
        self.clickIsInCanvas = False
        if self.previousCanvas.toImage() != self.canvasBox.pixmap().toImage():
            self.saveBackup()
            self.previousCanvas = self.canvasBox.pixmap()
            eraseAllCommittedBackups()
            self.stepForwardButton.setEnabled(False)
            self.stepBackButton.setEnabled(True)

    def changeWidth(self):
        self.currentWidth = self.sender().value()
        self.applyPenSettings()
        if self.isEraser:
            self.setEraser()
        self.currentWidthValue.setText(str(self.currentWidth))

    def saveBackup(self):
        global GlobalIDCounter

        backup = self.previousCanvas
        backup_time = datetime.datetime.now().strftime('%d_%b_%Y_%H_%M_%S_%f')
        backup.save(str(BACKUPS_DIR.joinpath(f'{backup_time}.jpg')), 'jpg', 100)
        con = sqlite3.connect(str(BACKUPS_DB))
        cur = con.cursor()
        sql = f"INSERT INTO backups (id, file_name) VALUES ({GlobalIDCounter}, '{backup_time}')"
        cur.execute(sql)
        con.commit()
        cur.connection.close()
        GlobalIDCounter += 1

    def applyPenSettings(self):
        self.currentPen.setWidth(self.currentWidth)
        if self.currentPen.colorToughness == 'normal':
            self.currentPen.setColor(self.currentColor)
        else:
            self.makePaleColor()
            self.currentPen.setColor(self.paleCurrentColor)

    def stepBack(self):
        global LocalCommittedIDCounter

        backup_return = self.canvasBox.pixmap()
        backup_return_time = datetime.datetime.now().strftime('%d_%b_%Y_%H_%M_%S_%f')
        backup_return.save(str(COMMITTED_BACKUPS_DIR.joinpath(f'{backup_return_time}.jpg')), 'jpg', 100)

        con = sqlite3.connect(str(COMMITTED_BACKUPS_DB))
        cur = con.cursor()
        sql = f"INSERT INTO com_backups (id, file_name) VALUES ({LocalCommittedIDCounter}, '{backup_return_time}')"
        cur.execute(sql)
        con.commit()
        cur.connection.close()

        con = sqlite3.connect(str(BACKUPS_DB))
        cur = con.cursor()
        sql = f"SELECT id, file_name FROM backups WHERE id = (SELECT MAX(id) FROM backups)"
        previous_canvas_name = cur.execute(sql).fetchone()[1]
        previous_canvas = QPixmap(str(BACKUPS_DIR.joinpath(f'{previous_canvas_name}.jpg')))
        self.canvasBox.setPixmap(previous_canvas)

        sql = f'DELETE FROM backups WHERE file_name = "{previous_canvas_name}"'
        cur.execute(sql)
        con.commit()
        cur.connection.close()

        os.remove(str(BACKUPS_DIR.joinpath(f'{previous_canvas_name}.jpg')))
        self.previousCanvas = self.canvasBox.pixmap()
        LocalCommittedIDCounter += 1

        if not os.listdir(str(BACKUPS_DIR)):
            self.stepBackButton.setEnabled(False)
        self.stepForwardButton.setEnabled(True)

    def stepForward(self):
        global GlobalIDCounter

        backup = self.canvasBox.pixmap()
        backup_time = datetime.datetime.now().strftime('%d_%b_%Y_%H_%M_%S_%f')
        backup.save(str(BACKUPS_DIR.joinpath(f'{backup_time}.jpg')), 'jpg', 100)

        con = sqlite3.connect(str(BACKUPS_DB))
        cur = con.cursor()
        sql = f"INSERT INTO backups (id, file_name) VALUES ({GlobalIDCounter}, '{backup_time}')"
        cur.execute(sql)
        con.commit()
        cur.connection.close()

        con = sqlite3.connect(str(COMMITTED_BACKUPS_DB))
        cur = con.cursor()
        sql = f"SELECT id, file_name FROM com_backups WHERE id = (SELECT MAX(id) FROM com_backups)"
        new_canvas_name = cur.execute(sql).fetchone()[1]
        new_canvas = QPixmap(str(COMMITTED_BACKUPS_DIR.joinpath(f'{new_canvas_name}.jpg')))
        self.canvasBox.setPixmap(new_canvas)

        sql = f'DELETE FROM com_backups WHERE file_name = "{new_canvas_name}"'
        cur.execute(sql)
        con.commit()
        cur.connection.close()

        os.remove(str(COMMITTED_BACKUPS_DIR.joinpath(f'{new_canvas_name}.jpg')))
        self.previousCanvas = self.canvasBox.pixmap()
        GlobalIDCounter += 1

        if not os.listdir(str(COMMITTED_BACKUPS_DIR)):
            self.stepForwardButton.setEnabled(False)
        self.stepBackButton.setEnabled(True)

    def setEraser(self):
        self.eraser.setWidth(self.currentWidth)
        square_cursor = QPixmap(str(SQUARE_ICON)).scaled(QSize(self.currentWidth, self.currentWidth))
        self.canvasBox.setCursor(QCursor(square_cursor))
        self.isEraser = True
        self.currentPenValue.setText('Ластик')
        self.currentColorValue.setText('(255, 255, 255)')
        if self.latestPaintedPixel is None:
            self.latestPaintedPixel = (0, 0)

    def makePaleColor(self):
        self.paleCurrentColor = QColor(self.currentColor)
        self.paleCurrentColor.setAlpha(90)


class PenChangeMenu(QWidget):

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Пенал')
        self.setGeometry(800, 350, 300, 300)
        self.setFixedSize(300, 300)

        self.penChangeButtons = []
        for i in range(len(self.main_window.allPens)):
            icons = [PEN_ICON, PENCIL_ICON, MARKER_ICON, CHALK_ICON]
            button = QPushButton(self)
            label = QLabel(self)
            button.setGeometry(50 + 120 * (i // 2), 30 + 130 * (i % 2), 80, 80)
            button.setIcon(QIcon(str(icons[i])))
            button.setIconSize(QSize(70, 70))
            button.clicked.connect(self.changePen)
            label.setGeometry(50 + 120 * (i // 2), 105 + 130 * (i % 2), 80, 35)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setText(self.main_window.allPens[i].name)
            self.penChangeButtons.append((button, self.main_window.allPens[i]))

        self.main_window.penChangeMenuButton.clicked.connect(self.showOrActivate)

    def showOrActivate(self):
        if self.isHidden():
            self.show()
        else:
            self.activateWindow()

    def changePen(self):
        button_index = None
        for i in range(len(self.penChangeButtons)):
            if self.penChangeButtons[i][0] == self.sender():
                button_index = i
        new_pen = self.penChangeButtons[button_index][1]
        self.main_window.currentPen = new_pen
        self.main_window.isEraser = False
        self.main_window.canvasBox.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        self.main_window.applyPenSettings()
        self.main_window.currentPenValue.setText(self.main_window.currentPen.name)
        self.main_window.currentColorValue.setText(f'({str(self.main_window.currentColor.red())}, '
                                                   f'{str(self.main_window.currentColor.green())}, '
                                                   f'{str(self.main_window.currentColor.blue())})')
        self.hide()


class ColorChangeMenu(QWidget):

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Палитра')
        self.setGeometry(650, 350, 600, 300)
        self.setFixedSize(600, 300)

        self.helpLabel = QLabel(self)
        self.helpLabel.setGeometry(0, 165, 600, 50)
        self.helpLabel.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.helpLabel.setText('Выберите цвет из палитры или введите в поля ниже \n'
                               'значения красной, зелёной и синей компоненты цвета соответственно \n'
                               '(RGB: от 0 до 255 включительно)')

        self.colorChangeButtons = []
        for i in range(len(self.main_window.colorPalette)):
            button = QPushButton(self)
            button.setGeometry(65 + 60 * (i // 2), 30 + 70 * (i % 2), 50, 50)
            button.setIcon(QIcon(str(COLOR_ICONS.joinpath(self.main_window.colorPalette[i].name + '.png'))))
            button.setIconSize(QSize(50, 50))
            button.clicked.connect(self.changeColor)
            self.colorChangeButtons.append((button, QColor(self.main_window.colorPalette[i])))

        self.errorLabel = QLabel(self)
        self.errorLabel.setGeometry(200, 265, 200, 30)
        self.errorLabel.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.errorLabel.setText('Введены некорректные данные!')
        self.errorLabel.hide()

        colors = ['red', 'green', 'blue']
        self.colorChangeLines = []
        for i in range(len(colors)):
            line = QLineEdit(self)
            line.setGeometry(115 + 90 * i, 228, 80, 24)
            self.colorChangeLines.append((colors[i], line))

        self.colorConfirmButton = QPushButton(self)
        self.colorConfirmButton.setGeometry(390, 225, 100, 30)
        self.colorConfirmButton.setText('Подтвердить')

        self.colorConfirmButton.clicked.connect(self.confirmColor)
        self.main_window.colorChangeMenuButton.clicked.connect(self.showOrActivate)

    def showOrActivate(self):
        if self.isHidden():
            self.show()
        else:
            self.activateWindow()

    def changeColor(self):
        button_index = None
        for i in range(len(self.colorChangeButtons)):
            if self.colorChangeButtons[i][0] == self.sender():
                button_index = i
        new_color = self.colorChangeButtons[button_index][1]
        self.main_window.currentColor = new_color
        self.main_window.applyPenSettings()
        if not self.main_window.isEraser:
            self.main_window.currentColorValue.setText(f'({str(self.main_window.currentColor.red())}, '
                                                       f'{str(self.main_window.currentColor.green())}, '
                                                       f'{str(self.main_window.currentColor.blue())})')
        self.hide()

    def confirmColor(self):
        for i in range(3):
            try:
                rgb_number = int(self.colorChangeLines[i][1].text())
            except ValueError:
                self.errorLabel.show()
                return
            if rgb_number > 255 or rgb_number < 0:
                self.errorLabel.show()
                return
        color = QColor.fromRgb(int(self.colorChangeLines[0][1].text()),
                               int(self.colorChangeLines[1][1].text()),
                               int(self.colorChangeLines[2][1].text()))
        self.main_window.currentColor = color
        self.main_window.applyPenSettings()
        for i in self.colorChangeLines:
            i[1].setText('')
        self.errorLabel.hide()
        if not self.main_window.isEraser:
            self.main_window.currentColorValue.setText(f'({str(self.main_window.currentColor.red())}, '
                                                       f'{str(self.main_window.currentColor.green())}, '
                                                       f'{str(self.main_window.currentColor.blue())})')
        self.hide()


class FileWorkMenu(QWidget):

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Холсты')
        self.setGeometry(750, 320, 400, 380)
        self.setFixedSize(400, 380)

        self.uploadImageButton = QPushButton(self)
        self.uploadImageButton.setGeometry(50, 40, 100, 100)
        self.uploadImageButton.setIcon(QIcon(str(UPLOAD_IMAGE_ICON)))
        self.uploadImageButton.setIconSize(QSize(95, 95))
        self.uploadImageButton.clicked.connect(self.openImage)
        self.uploadImageButtonLabel = QLabel(self)
        self.uploadImageButtonLabel.setText('Открыть\nизображение')
        self.uploadImageButtonLabel.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.uploadImageButtonLabel.setGeometry(50, 145, 100, 50)

        self.saveImageButton = QPushButton(self)
        self.saveImageButton.setGeometry(250, 40, 100, 100)
        self.saveImageButton.setIcon(QIcon(str(SAVE_IMAGE_ICON)))
        self.saveImageButton.setIconSize(QSize(85, 85))
        self.saveImageButton.clicked.connect(self.saveImage)
        self.saveImageButtonLabel = QLabel(self)
        self.saveImageButtonLabel.setText('Сохранить\nизображение')
        self.saveImageButtonLabel.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.saveImageButtonLabel.setGeometry(250, 145, 100, 50)

        self.newCanvasButton = QPushButton(self)
        self.newCanvasButton.setGeometry(150, 220, 100, 100)
        self.newCanvasButton.setIcon(QIcon(str(NEW_CANVAS_ICON)))
        self.newCanvasButton.setIconSize(QSize(85, 85))
        self.newCanvasButton.clicked.connect(self.clearCanvas)
        self.newCanvasButtonLabel = QLabel(self)
        self.newCanvasButtonLabel.setText('Новый холст')
        self.newCanvasButtonLabel.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.newCanvasButtonLabel.setGeometry(150, 325, 100, 50)

        self.main_window.fileWorkMenuButton.clicked.connect(self.showOrActivate)

    def showOrActivate(self):
        if self.isHidden():
            self.show()
        else:
            self.activateWindow()

    def startOver(self):
        eraseAllBackups()
        eraseAllCommittedBackups()
        self.main_window.stepBackButton.setEnabled(False)
        self.main_window.stepForwardButton.setEnabled(False)

    def clearCanvas(self):
        new_canvas = QPixmap(1280, 720)
        new_canvas.fill(Qt.GlobalColor.white)
        self.main_window.canvasBox.setPixmap(new_canvas)
        self.main_window.canvasBox.setGeometry(5, 100, 1280, 720)
        self.startOver()
        self.main_window.previousCanvas = new_canvas
        self.hide()

    def saveImage(self):
        self.hide()
        dialog = QFileDialog(self)
        dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        dialog.setDirectory(QDir(str(SAVED_PICTURES)))
        dialog.setNameFilter('*.jpg')
        dialog.setDefaultSuffix('.jpg')
        clicked_ok = dialog.exec()
        if clicked_ok:
            self.main_window.canvasBox.pixmap().save(dialog.selectedFiles()[0])

    def openImage(self):
        self.hide()
        dialog = QFileDialog(self)
        dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
        dialog.setDirectory(QDir(str(SAVED_PICTURES)))
        dialog.setNameFilter('*.jpg')
        dialog.setDefaultSuffix('.jpg')
        clicked_ok = dialog.exec()
        if clicked_ok:
            self.startOver()
            image = QImage(dialog.selectedFiles()[0])
            if image.width() > 1280 or image.height() > 720:
                if image.width() - 1280 > image.height() - 720:
                    coefficient = 1280 / image.width()
                    image = image.scaled(1280, int(image.height() * coefficient))
                else:
                    coefficient = 720 / image.height()
                    image = image.scaled(int(image.width() * coefficient), 720)
            new_canvas = QPixmap(1280, 720)
            new_canvas.fill(Qt.GlobalColor.white)
            painter = QPainter(new_canvas)
            painter.begin(self)
            painter.drawPixmap(0, 0, QPixmap.fromImage(image))
            painter.end()
            self.main_window.previousCanvas = new_canvas
            self.main_window.canvasBox.setPixmap(self.main_window.previousCanvas)


def createBackupsDatabase():
    os.remove(str(BACKUPS_DB))
    connect = sqlite3.connect(str(BACKUPS_DB))
    cursor = connect.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS backups (
                          id INTEGER,
                          file_name TEXT
                          )""")
    cursor.connection.close()


def createCommittedBackupsDatabase():
    os.remove(str(COMMITTED_BACKUPS_DB))
    connect = sqlite3.connect(str(COMMITTED_BACKUPS_DB))
    cursor = connect.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS com_backups (
                              id INTEGER,
                              file_name TEXT
                              )""")
    cursor.connection.close()


def eraseAllCommittedBackups():
    shutil.rmtree(str(COMMITTED_BACKUPS_DIR))
    os.mkdir(str(COMMITTED_BACKUPS_DIR))
    createCommittedBackupsDatabase()


def eraseAllBackups():
    shutil.rmtree(str(BACKUPS_DIR))
    os.mkdir(str(BACKUPS_DIR))
    createBackupsDatabase()


def createTempDir():
    shutil.rmtree(str(TEMP_DIR), ignore_errors=True)
    os.mkdir(str(TEMP_DIR))
    os.mkdir(str(BACKUPS_DIR))
    os.mkdir(str(COMMITTED_BACKUPS_DIR))


def createSavedPicturesDir():
    shutil.rmtree(str(SAVED_PICTURES), ignore_errors=True)
    os.mkdir(str(SAVED_PICTURES))


if __name__ == '__main__':
    createSavedPicturesDir()
    createTempDir()
    createBackupsDatabase()
    createCommittedBackupsDatabase()
    app = QApplication(sys.argv)
    canvasApp_window = CanvasApp()
    canvasApp_window.show()
    pens_window = PenChangeMenu(canvasApp_window)
    color_window = ColorChangeMenu(canvasApp_window)
    file_window = FileWorkMenu(canvasApp_window)
    report = app.exec()
    eraseAllBackups()
    eraseAllCommittedBackups()
    sys.exit(report)
