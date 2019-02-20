import pyglet

pyglet.resource.path = ['../resources']
pyglet.resource.reindex()

game_window = pyglet.window.Window()



def center_image(image):
    """Sets an image's anchor point to its center"""
    image.anchor_x = image.width // 2
    image.anchor_y = image.height // 2

car = pyglet.sprite.Sprite(img=pyglet.resource.image('car.png'), x=game_window.width/2, y=game_window.height/2)

@game_window.event
def on_draw():
    game_window.clear()

    car.draw()

def update(dt):
    pass

if __name__ == "__main__":
    pyglet.app.run()