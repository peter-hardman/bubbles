import sys
import random
import math
#from PyQt5 import QtCore, QtGui, QtWidgets, uic
#from PyQt5.QtCore import Qt

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import QtGui

MAX_BUBBLE_AREA =  20000
MAX_AREA = 5000
AREA_WIDTH =2000
AREA_HEIGHT =1000
TIMER_INTERVAL =10

def rgb_to_hsv(r, g, b):
    # R, G, B values are divided by 255
    # to change the range from 0..255 to 0..1:
    r, g, b = r / 255.0, g / 255.0, b / 255.0

    # h, s, v = hue, saturation, value
    cmax = max(r, g, b)  # maximum of r, g, b
    cmin = min(r, g, b)  # minimum of r, g, b
    diff = cmax - cmin  # diff of cmax and cmin.

    # if cmax and cmax are equal then h = 0
    if cmax == cmin:
        h = 0

    # if cmax equal r then compute h
    elif cmax == r:
        h = (60 * ((g - b) / diff) + 360) % 360

    # if cmax equal g then compute h
    elif cmax == g:
        h = (60 * ((b - r) / diff) + 120) % 360

    # if cmax equal b then compute h
    elif cmax == b:
        h = (60 * ((r - g) / diff) + 240) % 360

    # if cmax equal zero
    if cmax == 0:
        s = 0
    else:
        s = (diff / cmax) * 100

    # compute v
    v = cmax * 100
    return h, s, v

def rgb_mix_colors(area1,area2, *colors):
    """ color mix
    :param rgb_scale: scale of values
    :param colors: list of colors (tuple of rgb values)
    :return: relative mix of rgb colors """
    r = g = b = 0

#    print( colors[0][0],colors[0][1],colors[0][2])
#    print( colors[1][0], colors[1][1], colors[1][2])

    r= colors[0][0]+ math.fabs(colors[0][0]-colors[1][0])*(area2/area1)
    g = colors[0][1] + math.fabs(colors[0][1] - colors[1][1]) * (area2 / area1)
    b = colors[0][2] + math.fabs(colors[0][2] - colors[1][2]) * (area2 / area1)

    return int(r), int(g), int(b)


class Bubble(QRect,QWidget):

    def __init__(self,boundsRect,parent):

        self.parent= parent
        self.bounds = boundsRect
        self.radius = random.randint(1,3)
        self.area = math.pi * self.radius*self.radius
        width = self.bounds.width()
        height = self.bounds.height()
        self.locationX = width/2+float(random.randint( -self.radius,  self.radius))
        self.locationY = height/2+float(random.randint(-self.radius, self.radius))
        self.color = random.randint(0,0xFFFFFF)

        self.velocityX = 1.00 * random.randint(-10,10) #float (random.randint(-100,100)/10)
        self.velocityY = 1.00 * random.randint(-10,10) #float(random.randint(-100, 100) / 10)

        self.alive = True

    def birth(self,new_birth):
        print ("birth")
        # when we get too large, we start to emit bubbles from ourselves which are proportional to total area.
        new_birth.area = self.area * random.randint(1,20)*0.001
        new_birth.radius=math.sqrt(new_birth.area/math.pi)
        self.area=self.area-new_birth.area
        # put the new bubble somewhere on our circumference.
        #For now just hack it to always be the y=0, x-axis.
        angle= random.randint(1,360)

        new_birth.locationX=self.locationX+(self.radius+new_birth.radius)*math.sin(angle*math.pi/180)
        new_birth.locationY = self.locationY+(self.radius+new_birth.radius)*math.cos(angle*math.pi/180)

        # Always fire the new_birth away from us.
        new_birth.velocityX=(new_birth.radius)*math.sin(angle*math.pi/180)
        new_birth.velocityY =(new_birth.radius)*math.cos(angle*math.pi/180)

        new_birth.color=self.color


    def consume(self,victim):

        # Merge so that total area is preserved.
        old_area=self.area
        self.area= old_area+victim.area
#        if new_area>300:
#            new_area=300

        self.radius = math.sqrt(self.area/math.pi)

        # Merge so that new location is on center of "mass" of the two parts.
        newX = self.locationX +  (victim.locationX-self.locationX)/(self.area/victim.area)
        newY = self.locationY +  (victim.locationY-self.locationY)/(self.area/victim.area)

        self.locationX = newX
        self.locationY = newY

        #merge velocities.
        new_Vx = ((old_area*self.velocityX) + (victim.area*victim.velocityX))/ self.area
        new_Vy = ((old_area * self.velocityY) + (victim.area * victim.velocityY)) / self.area

        self.velocityX = new_Vx
        self.velocityY = new_Vy

        # merge colors.  This is more difficult that you might think in an RGB space because white is 0xFFFFFF
        red=    (self.color & 0xFF0000)>>16
        green=  (self.color & 0x00FF00)>>8
        blue =  (self.color & 0x0000FF)

        victim_red =   (victim.color & 0xFF0000) >> 16
        victim_green = (victim.color & 0x00FF00) >> 8
        victim_blue =  (victim.color & 0x0000FF)

#        print(victim_red, victim_green, victim_blue)
#        new_red =  int(red - (red- victim_red) / 2)
#       new_green = int(green - (green - victim_green) / 2)
#        new_blue = int(blue - (blue - victim_blue) / 2)

        new_red,new_green,new_blue = rgb_mix_colors(old_area,victim.area, (red, green, blue), (victim_red, victim_green, victim_blue))

        # new color is proportional to amount consumed.
        new_color= int((( new_red & 0x0000FF)<<16) + ((new_green& 0x0000FF)<<8) + (new_blue& 0x0000FF))
        self.color=new_color

    def move(self):
        FRICTION = 0 #-0.000001*self.area
        #Check for collisions with walls
        if self.locationX-self.radius <= self.bounds.left():
          #  self.locationX = self.bounds.left() + (self.radius+1)
            self.velocityX =self.velocityX * -1.0

        if self.locationX+self.radius >= self.bounds.right():
         #   self.locationX= self.bounds.right()-(self.radius+1)
            self.velocityX =self.velocityX * -1.0

        if self.locationY+self.radius <= self.bounds.bottom():
         #   self.locationY = self.bounds.bottom() + (self.radius+1)
            self.velocityY =self.velocityY* -1.0

        if self.locationY-self.radius >= self.bounds.top():
         #   self.locationY = self.bounds.top() - (self.radius+1)
            self.velocityY =self.velocityY * -1.0

        #update the velocity by introducing friction (or dark matter)
        self.velocityX = self.velocityX + self.velocityX*FRICTION
        self.velocityY = self.velocityY + self.velocityY*FRICTION

        # Update the position based on the velocity
        self.locationX = self.locationX + self.velocityX
        self.locationY = self.locationY + self.velocityY

    def draw(self):
        if self.alive:
            painter = QtGui.QPainter(self.parent.pixmap())
            brush = QtGui.QBrush()
            brush.setStyle(Qt.SolidPattern)
            brush.isOpaque()
            brush.setColor(QtGui.QColor(self.color))
            pen = QtGui.QPen()
#            pen.setWidth(1)
#            pen.setColor(QtGui.QColor('white'))
#            painter.setPen(pen)
            painter.setBrush(brush)
            painter.drawEllipse(self.locationX-self.radius, self.locationY-self.radius, self.radius*2, self.radius*2)

#            pen.setColor(QtGui.QColor('black'))
#            brush.setColor(QtGui.QColor('black'))
#            painter.setPen(pen)
#            painter.setBrush(brush)
#            painter.drawPoint(self.locationX , self.locationY)
            painter.end()
        else:
            pass

class AppForm(QMainWindow):
    def __init__(self, parent=None):
        super().__init__()

        QMainWindow.__init__(self, parent)

        self.create_main_frame()
        self.main_frame.show()
        self.frame_count=0
        self.bubbles = []
        i = 0
        while i < 10:
            b = Bubble(self.main_frame.frameRect(),self.main_frame)
            self.bubbles.append(b)
            i += 1
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.on_timer)

        self.timer_interval = TIMER_INTERVAL
        self.timer.start(self.timer_interval)

        self.total_bubble_area=0

    def update_bubbles(self):

        #update the position of the bubbles.
        for b in self.bubbles:
            b.move()
        # check for collisions.  For now assume 1 per loop.
        for b in self.bubbles:
            for a in self.bubbles:
                if (a!=b) and (a.alive) and (b.alive):
                    x = a.locationX-b.locationX;
                    y = a.locationY-b.locationY;
                    distance = math.sqrt( (x*x)+(y*y))
                    if (distance < (a.radius+b.radius)):
#                        print ("collision")
                        if (a.radius>b.radius):
                            #print ("a consumes b")
                            b.alive=False
                            a.consume(b)
                        else:
                            #print("b consumes a")
                            a.alive = False
                            b.consume(a)

        for b in self.bubbles:
            if b.alive == False:
                self.bubbles.remove(b)

        for b in self.bubbles:
            if b.area> MAX_AREA:
                new_bubble = Bubble(self.main_frame.frameRect(), self.main_frame)
                b.birth(new_bubble)
                self.bubbles.append(new_bubble)

        # draw new list.
        for b in self.bubbles:
            b.draw()

    def on_timer(self):
        self.frame_count = self.frame_count + 1
#        print("on_timer")
        print(len(self.bubbles),self.total_bubble_area)
        # add a bubble
        if self.total_bubble_area<MAX_BUBBLE_AREA:
            b = Bubble(self.main_frame.frameRect(), self.main_frame)
            self.total_bubble_area+=b.area
            self.bubbles.append(b)

        self.draw_background()
        self.draw_status()

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
        status_str = "Frames ="+str(self.frame_count)
        painter.drawText(10,20,status_str)
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


    def create_main_frame(self):
        self.main_frame = QLabel()
        self.main_frame.setMinimumWidth(AREA_WIDTH)
        self.main_frame.setMinimumHeight(AREA_HEIGHT)
        canvas = QtGui.QPixmap(AREA_WIDTH, AREA_HEIGHT)
        self.main_frame.setPixmap(canvas)
        self.setCentralWidget(self.main_frame)
        layout = QVBoxLayout()
        layout.addWidget(self.main_frame)
        self.setLayout(layout)

def main():
    app = QApplication(sys.argv)
    form = AppForm()
    form.show()
    app.exec_()

if __name__ == "__main__":

#    tracemalloc.start()
    main()
    print("The end")
