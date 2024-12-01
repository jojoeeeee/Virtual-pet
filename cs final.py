import sys
import os
import random
from PyQt5 import QtWidgets, QtGui, QtCore

class DeskPet(QtWidgets.QLabel): 
    def __init__(self):
        super().__init__()
        self.initUI()
        self.childPets = []
        self.isDragging = False
        self.isMoving = False
        self.change = False

    def initUI(self):
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setGeometry(500, 500, 130, 130)
        self.currentAction = self.startIdle
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.updateAnimation)
        self.changeDirectionTimer = QtCore.QTimer(self)  # 添加定时器
        self.changeDirectionTimer.timeout.connect(self.changeDirection)  # 定时器触发时调用changeDirection方法
        self.startIdle()
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showMenu)
        self.setMouseTracking(True)
        self.dragging = False

    def loadImages(self, path):
        return [QtGui.QPixmap(os.path.join(path, f)) for f in os.listdir(path) if f.endswith('.png')]

    def startIdle(self):
        self.setFixedSize(130, 130)
        self.currentAction = self.startIdle
        self.images = self.loadImages("Deskpet/resource/xianzhi")
        self.currentImage = 0
        self.timer.start(100)
        self.moveSpeed = 0
        self.movingDirection = 0
        if self.changeDirectionTimer.isActive():
            self.changeDirectionTimer.stop()  # 停止方向改变的定时器

    def startWalk(self):
        self.setFixedSize(130, 130)
        if not self.isDragging:
            self.currentAction = self.startWalk
            direction = random.choice(["zuo", "you"])
            self.images = self.loadImages(f"Deskpet/resource/sanbu/{direction}")
            self.currentImage = 0
            self.movingDirection = -1 if direction == "zuo" else 1
            self.moveSpeed = 10
            self.timer.start(100)
            self.changeDirectionTimer.start(3000)  # 启动定时器

    def movePet(self):
        screen = QtWidgets.QDesktopWidget().screenGeometry()
        new_x = self.x() + self.movingDirection * self.moveSpeed
        if new_x < 10:
            new_x = 10
            if self.currentAction == self.startWalk:
                self.movingDirection *= -1
                # 停止加载原先的图片
                self.timer.stop()
                self.images = []  # 清空当前图片列表
                if self.movingDirection == -1:  # 向左移动
                    self.images = self.loadImages("Deskpet/resource/sanbu/zuo")
                else:  # 向右移动
                    self.images = self.loadImages("Deskpet/resource/sanbu/you")

                self.currentImage = 0
                self.timer.start(100)
        elif new_x > screen.width() - self.width() - 10:
            new_x = screen.width() - self.width() - 10
            if self.currentAction == self.startWalk:
                self.movingDirection *= -1
                # 停止加载原先的图片
                self.timer.stop()
                self.images = []  # 清空当前图片列表
                # 根据移动方向加载对应的图片
                if self.movingDirection == -1:  # 向左移动
                    self.images = self.loadImages("Deskpet/resource/sanbu/zuo")
                else:  # 向右移动
                    self.images = self.loadImages("Deskpet/resource/sanbu/you")

                self.currentImage = 0
                self.timer.start(100)
        self.deskpet_rect = self.geometry()
        for child in self.childPets:
            if isinstance(child, XiaobaiWindow):
                self.xiaobai_rect = child.geometry()
                if self.deskpet_rect.intersects(self.xiaobai_rect):
                    child.close()
                    self.startMeet()
        self.move(new_x, self.y())

    def startMeet(self):
        self.setFixedSize(150, 150)
        self.currentAction = self.startMeet
        self.images = self.loadImages("Deskpet/resource/meet")
        self.currentImage = 0
        self.moveSpeed = 0
        self.movingDirection = 0
        self.timer.start(30)

    def startLift(self):
        self.setFixedSize(160, 160)
        self.currentAction = self.startLift
        self.images = self.loadImages("Deskpet/resource/linqi")
        self.currentImage = 0
        self.moveSpeed = 0
        self.movingDirection = 0
        self.timer.start(100)

    def startFall(self):
        self.setFixedSize(150, 150)
        self.currentAction = self.startFall
        self.images = self.loadImages("Deskpet/resource/xialuo")
        self.currentImage = 0
        self.movingDirection = 0
        self.moveSpeed = 5
        self.stopOtherActions()
        self.timer.start(30)

    def stopOtherActions(self):
        self.timer.stop()
        if self.currentAction == self.startWalk:
            self.changeDirectionTimer.stop()  # 停止方向判定定时器
            self.startIdle()
        elif self.currentAction == self.startLift:
            self.startIdle()
        elif self.currentAction == self.startFall:
            pass
        else:
            self.startIdle()

    def updateAnimation(self):
        self.setPixmap(self.images[self.currentImage])
        self.currentImage = (self.currentImage + 1) % len(self.images)
        if hasattr(self, 'movingDirection'):
            if self.currentAction == self.startFall:
                self.fallPet()
            else:
                self.movePet()

    def fallPet(self):
        self.setFixedSize(130, 130)
        screen = QtWidgets.QDesktopWidget().screenGeometry()
        new_y = self.y() + self.moveSpeed
        if new_y > screen.height() - self.height() - 10:
            new_y = screen.height() - self.height() - 10
            self.timer.stop()
            self.startIdle()
        self.move(self.x(), new_y)

    def showMenu(self, position):
        menu = QtWidgets.QMenu()
        if self.currentAction == self.sleep:
            menu.addAction("Snack", self.Snack)
            menu.addAction("Wakeup", self.WakeUp)
            menu.addSeparator()
            menu.addAction("Hide", self.minimizeWindow)
            menu.addAction("Exit", self.close)
        else:
            menu.addAction("Walk", self.startWalk)
            menu.addAction("Fall", self.startFall)
            menu.addAction("Exercise", self.exercise)
            menu.addAction("Eat", self.eating)
            menu.addAction("Sleep", self.sleep)
            menu.addAction("pipi", self.pipi)
            menu.addAction("clone", self.clonePet)
            menu.addAction("transform", self.transform)
            menu.addAction("summon", self.summonXiaobai)
            menu.addAction("Test", self.startMeet)
            child_menu = menu.addMenu("Extracontent")
            child_menu.addAction("Q/A", self.starttalk)
            child_menu.addAction("Mini-game", self.transform)
            menu.addSeparator()
            menu.addAction("Stop", self.startIdle)
            menu.addAction("Hide", self.minimizeWindow)
            menu.addAction("Close", self.close)
        menu.exec_(self.mapToGlobal(position))

    def Snack(self):
        self.setFixedSize(160, 130)
        self.currentAction = self.sleep
        self.images = self.loadImages("Deskpet/resource/snack")
        self.currentImage = 0
        self.timer.start(100)
        self.moveSpeed = 0
        self.movingDirection = 0
        QtCore.QTimer.singleShot(len(self.images) * 100, self.sleep)


    def transform(self):
        self.setFixedSize(160, 130)
        self.currentAction = self.transform
        self.images = self.loadImages("Deskpet/resource/xiandanchaoren")
        self.currentImage = 0
        self.timer.start(100)
        self.moveSpeed = 0
        self.movingDirection = 0

    def pipi(self):
        self.setFixedSize(300, 130)
        self.currentAction = self.pipi
        self.images = self.loadImages("Deskpet/resource/pipi")
        self.currentImage = 0
        self.timer.start(25)
        self.moveSpeed = 0
        self.movingDirection = 0

    def exercise(self):
        self.setFixedSize(150,180 )
        self.currentAction = self.exercise
        self.images = self.loadImages("Deskpet/resource/yundong")
        self.currentImage = 0
        self.timer.start(125)
        self.moveSpeed = 0
        self.movingDirection = 0

    def eating(self):
        self.setFixedSize(160, 90)
        self.currentAction = self.eating
        self.images = self.loadImages("Deskpet/resource/eat")
        self.currentImage = 0
        self.timer.start(25)
        self.moveSpeed = 0
        self.movingDirection = 0
        QtCore.QTimer.singleShot(len(self.images) * 30, self.startIdle)

    def sleep(self):
        self.setFixedSize(315, 500)
        self.currentAction = self.sleep
        self.images = self.loadImages("Deskpet/resource/sleep")
        self.currentImage = 0
        self.timer.start(155)
        self.moveSpeed = 0
        self.movingDirection = 0

    def showWakeUpMenu(self):
        self.setFixedSize(130, 130)
        self.sleeping = True
        menu = QtWidgets.QMenu()
        menu.addAction("唤醒", self.wakeUp)
        menu.exec_(self.mapToGlobal(self.pos()))

    def WakeUp(self):
        self.setFixedSize(180, 180)
        self.sleeping = False
        self.currentAction = self.WakeUp
        self.images = self.loadImages("Deskpet/resource/waken")
        self.currentImage = 0
        self.timer.start(30)
        # 延时，等待所有图片加载完成
        QtCore.QTimer.singleShot(len(self.images) * 30, self.finishWakeUp)

    def Ninjia(self):
        self.setFixedSize(160, 150)
        self.sleeping = False
        self.currentAction = self.Ninjia
        self.images = self.loadImages("Deskpet/resource/Ninjia")
        self.currentImage = 0
        self.timer.start(30)
        # 延时，等待所有图片加载完成
        QtCore.QTimer.singleShot(len(self.images) * 30, self.startIdle)

    def Ninjia2(self):
        new_pet = DeskPet()
        self.childPets.append(new_pet)
        self.setFixedSize(160, 150)
        self.sleeping = False
        self.currentAction = self.Ninjia2
        self.images = self.loadImages("Deskpet/resource/Ninjia2")
        self.currentImage = 0
        self.timer.start(30)
        # 延时，等待所有图片加载完成
        QtCore.QTimer.singleShot(len(self.images) * 30, self.startIdle)

    def finishWakeUp(self):
        self.movingDirection = 0
        self.wakeUpImagesLoaded = True
        self.setFixedSize(180, 180)
        self.timer.stop()
        self.currentAction = self.startIdle
        self.images = self.loadImages("Deskpet/resource/xianzhi")
        self.currentImage = 0
        self.timer.start(100)

    def clonePet(self):
        new_pet = DeskPet()
        self.childPets.append(new_pet)
        self.Ninjia()
        new_pet.show()
        new_pet.Ninjia2()

    def starttalk(self):
        starttalk = ChatApp()
        starttalk.show()
        self.childPets.append(starttalk)

    def summonXiaobai(self):
        xiaobai = XiaobaiWindow()
        xiaobai.show()
        self.childPets.append(xiaobai)

    def closeEvent(self, event):
        for child in self.childPets:
            child.close()  # 关闭所有子窗口
        super().closeEvent(event)

    def minimizeWindow(self):
        self.showMinimized()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.dragging = True
            self.isDragging = True
            self.drag_position = event.globalPos() - self.pos()
            self.prevAction = self.currentAction
            self.startLift()

            event.accept()

    def mouseMoveEvent(self, event):
        if QtCore.Qt.LeftButton and self.dragging:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.dragging = False
            self.isDragging = False

            # 根据需要重新启动changeDirectionTimer
            if self.currentAction == self.startWalk:
                self.changeDirectionTimer.start()

            self.prevAction()  # 或者 self.startIdle(), 根据之前的动作恢复状态
            event.accept()

    def changeDirection(self):
        if self.currentAction == self.startFall or self.currentAction == self.eating or self.currentAction == self.transform or self.currentAction == self.sleep or self.currentAction == self.pipi or self.currentAction == self.exercise or self.currentAction == self.WakeUp or self.currentAction == self.startIdle or self.startMeet:
            return  # 如果正在执行下落动作，不改变方向

        if random.random() < 0.5:  # 随机选择是否改变方向
            self.movingDirection *= -1
            self.change = True
            if self.change == True:
                # 停止加载原先的图片
                self.timer.stop()
                self.images = []  # 清空当前图片列表
                self.startWalk()
                self.change = False

class XiaobaiWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setGeometry(500, 500, 125, 100)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.updateAnimation)
        self.images = self.loadImages("Deskpet/resource/xiaobai")
        self.currentImage = 0
        self.timer.start(20)
        self.dragPosition = QtCore.QPoint()
        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(0, 0, 140, 100)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.dragPosition = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            self.move(event.globalPos() - self.dragPosition)
            event.accept()

    def showMenu(self, position):
        menu = QtWidgets.QMenu()
        menu.addAction("Hide", self.minimizeWindow)
        menu.addAction("Back", self.close)
        menu.exec_(self.mapToGlobal(position))

    def loadImages(self, path):
        return [QtGui.QPixmap(os.path.join(path, f)) for f in os.listdir(path) if f.endswith('.png')]

    def updateAnimation(self):
        self.label.setPixmap(self.images[self.currentImage])
        self.currentImage = (self.currentImage + 1) % len(self.images)

    def minimizeWindow(self):
        self.showMinimized()

    def closeEvent(self, event):
        self.timer.stop()
        super().closeEvent(event)

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.ContextMenu:
            self.showMenu(event.pos())
            return True
        return super().eventFilter(obj, event)

    def showEvent(self, event):
        self.installEventFilter(self)

class ChatApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Chat window')
        layout = QtWidgets.QVBoxLayout()
        label = QtWidgets.QLabel("Hi，I am developer ”PP“\nWhat do you wanna ask？\n（The chat's content is imperfect and its functionality is flawed）")
        layout.addWidget(label)

        button1 = QtWidgets.QPushButton("Where are you come from?")
        button1.clicked.connect(self.on_button1_clicked)
        layout.addWidget(button1)

        button2 = QtWidgets.QPushButton("What kind of person are you？")
        button2.clicked.connect(self.on_button2_clicked)
        layout.addWidget(button2)

        button3 = QtWidgets.QPushButton("I wanna have a good time with you(〃ﾉωﾉ)")
        layout.addWidget(button3)

        self.new_window = None  # 新窗口实例作为成员变量
        self.setLayout(layout)

    def on_button1_clicked(self):
        self.new_window = QtWidgets.QWidget()
        self.new_window.setWindowTitle('New window')
        layout = QtWidgets.QVBoxLayout()
        label = QtWidgets.QLabel("I am from Guangdong\n#What else you wanna talk about？")
        layout.addWidget(label)

        button4 = QtWidgets.QPushButton("What do you like to eat?")
        button4.clicked.connect(self.on_button4_clicked)
        layout.addWidget(button4)

        button3 = QtWidgets.QPushButton("I wanna play games with you(〃ﾉωﾉ)")
        layout.addWidget(button3)

        self.new_window.setLayout(layout)
        self.new_window.show()


    def on_button2_clicked(self):
        self.new_window = QtWidgets.QWidget()
        self.new_window.setWindowTitle('New Window')
        layout = QtWidgets.QVBoxLayout()
        label = QtWidgets.QLabel("A handsome, gentle and lovely, handsome man!\n#What else you wanna talk about")
        layout.addWidget(label)

        button5 = QtWidgets.QPushButton("You are so handsome, there must be a lot of girls like you!")
        button5.clicked.connect(self.on_button5_clicked)
        layout.addWidget(button5)

        button3 = QtWidgets.QPushButton("I really really like you(〃ﾉωﾉ)")
        layout.addWidget(button3)

        self.new_window.setLayout(layout)
        self.new_window.show()

    def on_button4_clicked(self):
        QtWidgets.QMessageBox.information(self, "Answer", "My favorite it Mcdonald!")

    def on_button5_clicked(self):
        QtWidgets.QMessageBox.information(self, "Answer", "Blahblahblah……(´◑д◐｀)")

app = QtWidgets.QApplication(sys.argv)
pet = DeskPet()
pet.show()
chat_app = ChatApp()
sys.exit(app.exec_())