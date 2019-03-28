from graphics import *
import time

def make_rect(corner, width, height):
    corner2 = corner.clone()
    corner2.move(width, height)
    return Rectangle(corner, corner2)

def test():
    box_size = 120
    win = GraphWin('Test', 500, 500)
    
    for i in range(0,3):
        for j in range(0,3):
            obj = make_rect(Point(50 + box_size*j, 50 + box_size*i), box_size, box_size)
            obj.setFill('white')
            obj.draw(win)
            obj_destination = Text(Point(50 + box_size*j + box_size/2, 50 + box_size*i + box_size/2), '(' + str(i) + ', ' + str(j) + ')')
            obj_destination.draw(win)
    """obj = make_rect(Point(50 + box_size*0, 50 + box_size*0), box_size, box_size)
    obj.setFill('blue')
    obj.draw(win)
    obj = make_rect(Point(50 + box_size*1, 50 + box_size*0), box_size, box_size)
    obj.setFill('red')
    obj.draw(win)
    obj = make_rect(Point(50 + box_size*2, 50 + box_size*0), box_size, box_size)
    obj.setFill('green')
    obj.draw(win)
    obj = make_rect(Point(50 + box_size*0, 50 + box_size*1), box_size, box_size)
    obj.setFill('purple')
    obj.draw(win)"""

    while True:
        time.sleep(100)


if __name__ == "__main__":
    test()