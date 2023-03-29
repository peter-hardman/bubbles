import sys
import random
import math

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import QtGui

TOTAL_BUBBLE_AREA = 20000
MAX_AREA = 9000
AREA_WIDTH = 640  # 2048
AREA_HEIGHT = 480  # 1152
TIMER_INTERVAL = 10
MIN_HIGHLIGHT_RADIUS = 10
INFO_LIFETIME = 100

import ctypes

user32 = ctypes.windll.user32


class Bubble(QRect, QWidget):

    def __init__(self, boundsRect, parent):

        self.parent = parent
        self.bounds = boundsRect
        self.radius = random.randint(10, 30)  # was 1 to 3
        self.area = math.pi * self.radius * self.radius
        width = self.bounds.width()
        height = self.bounds.height()
        self.locationX = width / 2 + float(random.randint(-self.radius, self.radius))
        self.locationY = height / 2 + float(random.randint(-self.radius, self.radius))

        self.create_colors()
        self.velocityX = 1.00 * random.randint(-10, 10)  # float (random.randint(-100,100)/10)
        self.velocityY = 1.00 * random.randint(-10, 10)  # float(random.randint(-100, 100) / 10)

        self.show_info_count = 0
        self.age = 0
        self.alive = True

    def showInfo(self):
        self.show_info_count = INFO_LIFETIME
        print("info")

    def create_colors(self):
        MIN = 0xDD
        red = 0x00
        green = 0x00
        blue = 0x00
        #   Try to make colors more intense by only making RGB at start.
        x = random.randint(1, 6)
        if x == 1:
            red = random.randint(MIN, 0xFF)
        if x == 2:
            green = random.randint(MIN, 0xFF)
        if x == 3:
            blue = random.randint(MIN, 0xFF)
        if x == 4:
            red = random.randint(MIN, 0xFF)
            green = random.randint(MIN, 0xFF)
        if x == 5:
            red = random.randint(MIN, 0xFF)
            blue = random.randint(MIN, 0xFF)
        if x == 6:
            green = random.randint(MIN, 0xFF)
            blue = random.randint(MIN, 0xFF)

        self.set_colors(red, green, blue)

    def set_colors(self, new_red, new_green, new_blue):

        if new_red > 0xFF:
            new_red = 0xFF
        if new_green > 0xFF:
            new_green = 0xFF
        if new_blue > 0xFF:
            new_blue = 0xFF

        self.color_red = int(new_red)
        self.color_green = int(new_green)
        self.color_blue = int(new_blue)

        self.high_color_red = self.color_red + 0x40
        self.high_color_green = self.color_green + 0x40
        self.high_color_blue = self.color_blue + 0x40

        if self.high_color_red > 0xFF:
            self.high_color_red = 0xFF
        if self.high_color_green > 0xFF:
            self.high_color_green = 0xFF
        if self.high_color_blue > 0xFF:
            self.high_color_blue = 0xFF

    def merge_colors(self, victim):
        r = self.color_red
        g = self.color_green
        b = self.color_blue

        rv = victim.color_red
        gv = victim.color_green
        bv = victim.color_blue

        new_red = r + ((rv - r) * (victim.area / self.area))
        new_green = g + ((gv - g) * (victim.area / self.area))
        new_blue = b + ((bv - b) * (victim.area / self.area))

        #        print ("[",r,g,b,"][",rv,gv,bv, "][",new_red,new_green,new_blue,"]")
        self.set_colors(new_red, new_green, new_blue)

    def birth(self, new_birth):
        # when we get too large, we start to emit bubbles from ourselves which are proportional to total area.
        # Have some randomness to the size of the ones emitted.

        new_birth.area = self.area * random.randint(1, 20) * 0.001
        new_birth.radius = math.sqrt(new_birth.area / math.pi)

        self.area = self.area - new_birth.area
        self.radius = math.sqrt(self.area / math.pi)
        # put the new bubble somewhere on our circumference.
        angle = random.randint(1, 360)

        new_birth.locationX = self.locationX + (self.radius + new_birth.radius) * math.sin(angle * math.pi / 180)
        new_birth.locationY = self.locationY + (self.radius + new_birth.radius) * math.cos(angle * math.pi / 180)

        # Always fire the new_birth away from us. Make the speed proportional to the size.
        new_birth.velocityX = 0.3*(new_birth.radius) * math.sin(angle * math.pi / 180)
        new_birth.velocityY = 0.3*(new_birth.radius) * math.cos(angle * math.pi / 180)
        new_birth.create_colors()

    def consume(self, victim):
        # This function consumes a victim.
        # First merge so that total area is preserved.
        old_area = self.area
        self.area = old_area + victim.area
        # Recalculate the radius of the new bubble.
        self.radius = math.sqrt(self.area / math.pi)
        # Merge so that new location is on center of "mass" of the two parts.
        new_x = self.locationX + (victim.locationX - self.locationX) / (self.area / victim.area)
        new_y = self.locationY + (victim.locationY - self.locationY) / (self.area / victim.area)
        self.locationX = new_x
        self.locationY = new_y

        # merge velocities.
        new_vx = ((old_area * self.velocityX) + (victim.area * victim.velocityX)) / self.area
        new_vy = ((old_area * self.velocityY) + (victim.area * victim.velocityY)) / self.area

        self.velocityX = new_vx
        self.velocityY = new_vy

        # merge colors.  This is more difficult that you might think in an RGB space because white is 0xFFFFFF
        self.merge_colors(victim)

    #        new_red,new_green,new_blue = rgb_mix_colors(old_area,victim.area, (self.color_red, self.color_green,
    #                                     self.color_blue), (victim.color_red, victim.color_green, victim.color_blue))
    #        self.color_red = new_red
    #        self.color_green = new_green
    #        self.color_blue = new_blue

    #        self.high_color_red = self.color_red + 0x40
    #        self.high_color_green = self.color_green + 0x40
    #        self.high_color_blue = self.color_blue + 0x40

    #        if self.high_color_red > 0xFF:
    #            self.high_color_red = 0xFF
    #        if self.high_color_green > 0xFF:
    #           self.high_color_green = 0xFF
    #       if self.high_color_blue > 0xFF:
    #            self.high_color_blue = 0xFF

    def move(self):
        self.age = self.age + 1
        FRICTION = 0  # -0.000001*self.area
        # Check for collisions with walls
        if self.locationX - self.radius <= self.bounds.left():
            #  self.locationX = self.bounds.left() + (self.radius+1)
            self.velocityX = self.velocityX * -1.0

        if self.locationX + self.radius >= self.bounds.right():
            #   self.locationX= self.bounds.right()-(self.radius+1)
            self.velocityX = self.velocityX * -1.0

        if self.locationY + self.radius <= self.bounds.bottom():
            #   self.locationY = self.bounds.bottom() + (self.radius+1)
            self.velocityY = self.velocityY * -1.0

        if self.locationY - self.radius >= self.bounds.top():
            #   self.locationY = self.bounds.top() - (self.radius+1)
            self.velocityY = self.velocityY * -1.0

        # update the velocity by introducing friction (or some mysterious force that acclerates particles like dark matter)
        self.velocityX = self.velocityX + self.velocityX * FRICTION
        self.velocityY = self.velocityY + self.velocityY * FRICTION

        # Update the position based on the velocity
        self.locationX = self.locationX + self.velocityX
        self.locationY = self.locationY + self.velocityY

    def draw(self):
        if self.alive:
            painter = QtGui.QPainter(self.parent.pixmap())
            painter.setRenderHint(QtGui.QPainter.Antialiasing)
            brush = QtGui.QBrush()
            brush.setStyle(Qt.SolidPattern)
            brush.isOpaque()
            brush.setColor(QtGui.QColor(self.color_red, self.color_green, self.color_blue))
            #   This next block would have put a white border around each sphere.
            pen = QtGui.QPen()
            pen.setWidth(1)
            pen.setColor(QtGui.QColor('white'))
            painter.setPen(pen)

            pen = QtGui.QPen()
            pen.setWidth(1)
            pen.setColor(QtGui.QColor(self.color_red, self.color_green, self.color_blue))
            painter.setPen(pen)
            painter.setBrush(brush)

            g = QtGui.QRadialGradient(self.locationX - self.radius / 1.75, self.locationY - self.radius / 1.75,
                                      self.radius)
            g.setColorAt(1, QtGui.QColor(self.color_red, self.color_green, self.color_blue))
            g.setColorAt(0, QtGui.QColor('white'))
            painter.setBrush(g)

            painter.drawEllipse(self.locationX - self.radius, self.locationY - self.radius, self.radius * 2,
                                self.radius * 2)

            # Draw highlights.

            if self.radius > MIN_HIGHLIGHT_RADIUS:
                pen = QtGui.QPen()
                pen.setWidth(1)
                pen.setColor(QtGui.QColor(self.high_color_red, self.high_color_green, self.high_color_blue))
                painter.setPen(pen)
                # Draw horizontal arc
                painter.drawArc(self.locationX - self.radius, self.locationY - self.radius / 3, self.radius * 2,
                                self.radius / 2, 16 * 180, 16 * 180)
                # Draw vertical arc
                painter.drawArc(self.locationX - self.radius / 3, self.locationY - self.radius, self.radius / 2,
                                self.radius * 2, 16 * 270, 16 * 180)

            #   This next block draws a black dot in the center to show where it is. Helps for debugging.
            #            pen.setColor(QtGui.QColor('black'))
            #            brush.setColor(QtGui.QColor('black'))
            #            painter.setPen(pen)
            #            painter.setBrush(brush)
            #            painter.drawPoint(self.locationX , self.locationY)
            #   End block.
            if (self.show_info_count > 0):
                painter.setFont(QtGui.QFont("Arial", 8))
                painter.setPen(QtGui.QColor('White'))
                status_str = "Area =" + str(int(self.area))
                painter.drawText(self.locationX + 5, self.locationY + 0, status_str)
                status_str = "Age =" + str(self.age)
                painter.drawText(self.locationX + 5, self.locationY + 15, status_str)
                status_str = "X=" + str(int(self.locationX)) + " Y=" + str(int(self.locationY))
                painter.drawText(self.locationX + 5, self.locationY + 30, status_str)
                status_str = "vX=%.2f vY=%.2f" % (self.velocityX, self.velocityY)
                painter.drawText(self.locationX + 5, self.locationY + 45, status_str)

                self.show_info_count = self.show_info_count - 1
            painter.end()
        else:
            pass


class AppForm(QMainWindow):
    def __init__(self, parent=None):
        super().__init__()

        # QMainWindow.__init__(self, parent)

        # print(parent)

        self.create_main_frame()
        self.main_frame.show()
        self.frame_count = 0
        self.bubbles = []
        i = 0
        while i < 20:
            b = Bubble(self.main_frame.frameRect(), self.main_frame)
            self.bubbles.append(b)
            i += 1
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.on_timer)

        self.timer_interval = TIMER_INTERVAL
        self.timer.start(self.timer_interval)

        self.total_bubble_area = 0

    def keyPressEvent(self, e):
        print(e.key())
        self.close()

    def mousePressEvent(self, e):

        print(e.x(), e.y())
        for b in self.bubbles:
            distance = math.sqrt(
                (b.locationX - e.x()) * (b.locationX - e.x()) + (b.locationY - e.y()) * (b.locationY - e.y()))
            if distance < b.radius:
                print("Found bubble")
                b.showInfo()
                break

    def update_gravity(self):
        accelerationX = 0
        accelerationY = 0
        G_const = 5.0e-9
        for b in self.bubbles:
            for a in self.bubbles:
                if (a != b):
                    # calculate forces
                    r = (a.locationX - b.locationX) ** 2 + (a.locationY - b.locationY) ** 2
                    r = math.sqrt(r)
                    if r:
                        tmp = G_const * a.area**2 / r ** 2
                        accelerationX += tmp * (a.locationX - b.locationX)
                        accelerationY += tmp * (a.locationY - b.locationY)

            b.velocityX = b.velocityX + accelerationX
            b.velocityY = b.velocityY + accelerationY

    def update_bubbles(self):  # Update the position of the bubbles.
        for b in self.bubbles:
            b.move()
        # check for collisions.  For now assume 1 per loop.
        for b in self.bubbles:
            for a in self.bubbles:
                if (a != b) and (a.alive) and (b.alive):
                    x = a.locationX - b.locationX
                    y = a.locationY - b.locationY
                    distance = math.sqrt((x * x) + (y * y))
                    if (distance < (a.radius + b.radius)):
                        if (a.radius > b.radius):
                            b.alive = False
                            a.consume(b)
                        else:
                            a.alive = False
                            b.consume(a)

        for b in self.bubbles:
            if b.alive == False:
                self.bubbles.remove(b)

        for b in self.bubbles:
            if b.area > MAX_AREA:
                new_bubble = Bubble(self.main_frame.frameRect(), self.main_frame)
                b.birth(new_bubble)
                self.bubbles.append(new_bubble)

        # draw new list.
        for b in self.bubbles:
            b.draw()

    def on_timer(self):
        self.frame_count = self.frame_count + 1
        #        print("on_timer")
        #        print(len(self.bubbles),self.total_bubble_area)
        # add a bubble
        if self.total_bubble_area < TOTAL_BUBBLE_AREA:
            b = Bubble(self.main_frame.frameRect(), self.main_frame)
            self.total_bubble_area += b.area
            self.bubbles.append(b)

        self.draw_background()
        self.draw_status()

        self.update_gravity()
        self.update_bubbles()
        self.update()

    def draw_status(self):
        painter = QtGui.QPainter(self.main_frame.pixmap())
        sbrush = QtGui.QBrush()
        sbrush.setStyle(Qt.SolidPattern)
        sbrush.setColor(QtGui.QColor('white'))
        status_rect = QRect(0, 0, 100, 50)
        #        painter.fillRect(status_rect, sbrush)
        painter.setPen(QtGui.QColor('white'))
        status_str = "Frames =" + str(self.frame_count)
        painter.drawText(10, 20, status_str)
        status_str = "Bubbles =" + str(len(self.bubbles))
        painter.drawText(10, 40, status_str)

        status_str = "Total Area =" + str(self.total_bubble_area)
        painter.drawText(10, 60, status_str)

        painter.end()

    def draw_background(self):
        painter = QtGui.QPainter(self.main_frame.pixmap())
        bbrush = QtGui.QBrush()
        bbrush.setStyle(Qt.SolidPattern)
        bbrush.setColor(QtGui.QColor('black'))
        rect = QRect(0, 0, painter.device().width(), painter.device().height())
        painter.fillRect(rect, bbrush)
        painter.end()

    def location_on_the_screen(self):
        ag = QDesktopWidget().availableGeometry()
        sg = QDesktopWidget().screenGeometry()

        widget = self.geometry()
        x = ag.width() - widget.width()
        y = 2 * ag.height() - sg.height() - widget.height()
        self.move(x, y)

    def create_main_frame(self):

        ONE_SCREEN = False
        monitor_0 = QDesktopWidget().screenGeometry(0)
        monitor_1 = QDesktopWidget().screenGeometry(1)

        if ONE_SCREEN:
            width = monitor_0.width()
            height = monitor_0.height()
        else:
            width = monitor_0.width() + monitor_1.width()
            height = monitor_0.height() + monitor_1.height()



        self.main_frame = QLabel()
        self.main_frame.setMinimumWidth(width)
        self.main_frame.setMinimumHeight(height)
        canvas = QtGui.QPixmap(width, height)
        self.main_frame.setPixmap(canvas)
        self.setCentralWidget(self.main_frame)
        layout = QVBoxLayout()
        layout.addWidget(self.main_frame)
        self.setLayout(layout)
        self.setFixedSize(layout.sizeHint())
        self.location_on_the_screen()
        if ONE_SCREEN:
            self.move(monitor_0.left(), monitor_0.top())
        else:
            self.move(min(monitor_0.left(), monitor_1.left()), min(monitor_0.top(), monitor_1.top()))



def main():
    app = QApplication(sys.argv)

    form = AppForm()
    form.setWindowFlag(Qt.FramelessWindowHint)
    form.show()
    app.exec_()


if __name__ == "__main__":
    #    tracemalloc.start()
    main()
#    print("The end")
