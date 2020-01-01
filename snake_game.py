import pygame as pg
import sys
import random
import queue

# TODO: Walls, queue for keypress, scene stuff, 2 player, difficulty(?)

""" ######################
         PREAMBLE
    ###################### """

""" Dictionaries for direction/velocity mapping - stolen from https://github.com/Mekire """
DIRECT_DICT = {"left" : (-1, 0), "right" : (1, 0),
               "up" : (0,-1), "down" : (0, 1)}

KEY_MAPPING = {pg.K_LEFT : "left", pg.K_RIGHT : "right",
               pg.K_UP : "up", pg.K_DOWN : "down"}

OPPOSITES = {"left" : "right", "right" : "left",
             "up" : "down", "down" : "up"}

""" Colour Mapping """
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARK_GREY = (70, 70, 70)
GREY = (211, 211, 211)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
COLOUR_MAP = {"snake": GREEN, "apple": RED, "wall": BLACK, "surface": GREY, "background": DARK_GREY }

""" ################
        CLASSES
    ################ """

""" ####################### Object Classes ########################## """

class Square:
    """ All other objects in the game will be built up from this """
    def __init__(self, pos, colour, length):
        self.xi, self.yi = pos # i for index, p for pixel
        self.colour = colour
        self.length = length

    def display(self):
        xp, yp = self.sq_to_pixs(self.xi, self.yi) # (x = left side, y = top edge)
        pg.draw.rect(screen, self.colour, (xp, yp, self.length, self.length), 0)

    def sq_to_pixs(self, x, y):
    # Converts index of square to pixel coords
        px = (x+1)*(2*MARGIN + SQUARE_SIZE) - MARGIN - SQUARE_SIZE
        py = (y+1)*(2*MARGIN + SQUARE_SIZE) - MARGIN
        return (px, py)

    def index_coords(self): # TODO - remove for direct ref?
        return (self.xi, self.yi)

class Arena:
    """ A grid within which the game takes place """
    def __init__(self, size, square_length, colour):
        self.size = size # i.e. number of squares = size**2 for square arena
        self.length = square_length # i.e. per square dimension
        self.colour = colour
        self.squares = [ [] for i in range(self.size) ]
        for y in range(self.size):
            for x in range(self.size):
                self.squares[y].append(Square((x,y), self.colour, self.length))

    def display(self):
        for y in self.squares:
            for square in y:
                square.display()

class Snake:
    """ Class for the agent(s) """
    def __init__(self, pos, colour, square_length):
        self.xi, self.yi = pos
        self.colour = colour
        self.size = 3
        self.length = square_length
        self.direction = "right"
        self.direction_queue = queue.Queue(4) # TODO
        self.points = 0
        self.growing = False
        self.alive = True
        self.squares = []
        for x in range(self.size): # horizontal initial orientation
            self.squares.append(Square((self.xi - x, self.yi), self.colour, self.length))

    def display(self):
        for square in self.squares:
            square.display()

    def food_check(self, apple):
        if self.squares[0].index_coords() == apple.square.index_coords():
            self.growing = True
            self.points += apple.points_value
            apple.respawn([self])
        
    def collision_check(self, walls = None):
        xh, yh = self.squares[0].index_coords()
        body = self.squares[-1:0:-1] # going backwards thru array as forwards [0:-1:1] didnt work...

        def _collide(obstacles):
            for sq in obstacles:
                _x, _y = sq.index_coords()
                if (_x == xh) and (_y == yh):
                    self.alive = False

        _collide(body)
        if walls is not None:
            _collide(walls)
            
    def update(self):
         # Add new head based on velocity and old head
        velocity = DIRECT_DICT[self.direction]
        head_coords = [ (self.squares[0].index_coords()[i] + velocity[i]) for i in (0,1) ]
        # Wrap around screen if reach the end
        for i in (0, 1):
            if head_coords[i] < 0:
                head_coords[i] = SQUARES_PER_ARENA_SIDE - 1
            elif head_coords[i] > SQUARES_PER_ARENA_SIDE - 1:
                head_coords[i] = 0

        self.squares.insert(0, Square(head_coords, self.colour, self.length))
        if self.growing:
            self.growing = False
        else:
            del self.squares[-1]

    """
    def queue_key_press(self, key):
        for keys in KEY_MAPPING:
            if key in keys:
                try:
                    self.direction_queue.put(KEY_MAPPING[keys], block=False)
                    break
                except queue.Full:
                    pass
    """

class Player(Snake):
    """ Human controlled snake via arrow keys """
    def __init__(self, pos, colour, size):
        Snake.__init__(self, pos, colour, size)
    
    def get_key(self, event):
        if event.type == pg.KEYDOWN and event.key in KEY_MAPPING:
                new_direction = KEY_MAPPING[event.key]
                if new_direction != OPPOSITES[self.direction]:
                    self.direction = new_direction

class Apple:
    """ Food our (veggie) snake is greedily after """
    def __init__(self, colour, length, points_value, snake):
        self.colour = colour
        self.length = length
        self.xi, self.yi = self._rand_coords()
        self.points_value = points_value
        self.square = Square((self.xi, self.yi), self.colour, self.length)

    def _rand_coords(self):
        rand_num = lambda x: random.randint(0, x)
        _x = rand_num(SQUARES_PER_ARENA_SIDE-1)
        _y = rand_num(SQUARES_PER_ARENA_SIDE-1)
        return _x, _y

    def respawn(self, obstacles):
        _x, _y = self._rand_coords()
        for ob in obstacles:
            for sq in ob.squares:
                while sq.index_coords() == (_x, _y):
                    _x, _y = self._rand_coords()
        self.square.xi, self.square.yi = _x, _y
       
    def display(self):
        self.square.display()


""" ################ SCENES ####################### """    

class Scene:
    """ Overload most of this - barebones structure
    A bit pointless in current state but easily expanded """
    def __init__(self):
        self.done = False
    
    def when_activated(self):
        pass

    def reset(self):
        self.done = False

    def render(self):
        pass

    def process_event(self, event):
        pass

class StartUp(Scene):
    def __init__(self):
        Scene.__init__(self)

    def render(self):
        # test placeholder
        pass

    def when_activated(self):
        print("Press any key to continue")
    
    def process_event(self, event):
        if event.type == pg.KEYDOWN:
            self.done = True

class GamePlayState(Scene):
    def __init__(self):
        Scene.__init__(self)
        self.arena = Arena(SQUARES_PER_ARENA_SIDE, SQUARE_SIZE, COLOUR_MAP["surface"])
        self.snake = Player(SNAKE_START, COLOUR_MAP["snake"], SQUARE_SIZE)
        self.apple = Apple(COLOUR_MAP["apple"], SQUARE_SIZE, 1, self.snake)
        self.font = pg.font.SysFont("courier new", 50)

    def render(self):
        screen.fill(COLOUR_MAP["background"])
        self.arena.display()
        self.apple.display()
        self.snake.display()
        text = self.font.render(str(self.snake.points), True, [255,255,255])
        screen.blit(text, (500, 400))

    def process_event(self, event):
        self.snake.get_key(event)
        self.snake.update()
        self.snake.food_check(self.apple)
        self.snake.collision_check()
        if self.snake.alive == False:
            print("GAME OVER")
            print(self.snake.points)
            self.done = True
                

""" ################## CONTROL CLASS  #########################"""

class Control:
    def __init__(self):
        self.clock = pg.time.Clock()
        self.fps = FPS
        self.done = False
        self.scene_array = [StartUp(), GamePlayState()]
        self.scene_index = 0 # dirty way whilst dict method needs tinkering
        #self.scene_dict = {"START": StartUp(), "GAME": GamePlayState()}
        self.scene = self.scene_array[self.scene_index]
        #self.scene = self.scene_dict["START"]
        self.scene.when_activated()

    def event_handler(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True
            elif event.type == pg.KEYDOWN:
                self.scene.process_event(event)

    def scene_checker(self):
        if self.scene.done:
            self.scene.reset() # for reuse  - TODO
            self.scene_index = (self.scene_index + 1) % len(self.scene_array)
            self.scene = self.scene_array[self.scene_index]
            self.scene.when_activated()
            #self.scene = self.scene_dict[self.scene.next]

    def draw(self):
        self.scene.render()

    def main_loop(self):
        self.event_handler()
        self.scene_checker()
        self.draw()


""" ################ RUN GAME ################ """

""" Game paramaters """
SQUARE_SIZE = 20 # pixels
SQUARES_PER_ARENA_SIDE = 20 # squares
MARGIN = 2 # pixels
SNAKE_START = (int(SQUARES_PER_ARENA_SIDE/2), int(SQUARES_PER_ARENA_SIDE/2)) # square coords

pg.init()
#clock = pg.time.Clock()
# Square.display() and a few others
#  need a direct reference to "screen"
#  - TODO impliment better
w, h = 680, 680
SCREEN_SIZE = [w, h]
FPS = 10
screen = pg.display.set_mode(SCREEN_SIZE)

Game = Control()
while not Game.done:
    Game.main_loop()
    pg.display.update()
    #clock.tick(FPS)
pg.quit()

"""
# Testing
pg.init()
clock = pg.time.Clock()
FPS = 10
w, h = 780, 780
screen_size = [w, h]
screen = pg.display.set_mode(screen_size)

arena = Arena(SQUARES_PER_ARENA_SIDE, SQUARE_SIZE, COLOUR_MAP["surface"])
snake = Player(SNAKE_START, COLOUR_MAP["snake"], SQUARE_SIZE)
apple = Apple(COLOUR_MAP["apple"], SQUARE_SIZE, 1, snake)

done = False
font = pg.font.SysFont("courier new", 50)

while not done:
    for event in pg.event.get():  # User did something
        if event.type == pg.QUIT: 
            done = True

    pg.draw.rect(screen, BLACK, (0,0,w,h))
    arena.display()
    apple.display()

    snake.get_key(event)
    snake.update()
    snake.food_check(apple)
    snake.collision_check()
    snake.display()
    if snake.alive == False:
        print(snake.points)
        done = True

    text = font.render(str(snake.points), True, [255,255,255])
    screen.blit(text, (500, 400))
    pg.display.update()
    clock.tick(FPS)
"""