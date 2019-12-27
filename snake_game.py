import pygame as pg
import sys
import random
import queue

# TODO: queue for keypress, scene stuff

""" ######################
         PREAMBLE
    ###################### """

""" Constants """
SQUARE_SIZE = 20 # pixels
SQUARES_PER_ARENA_SIDE = 20 # squares
MARGIN = 2 # pixels
SNAKE_START_SIZE = 3
SNAKE_START = (int(SQUARES_PER_ARENA_SIDE/2), int(SQUARES_PER_ARENA_SIDE/2))

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
GREY = (211, 211, 211)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
COLOUR_MAP = {"snake": GREEN, "apple": RED, "wall": BLACK, "surface": GREY }

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

    def index_coords(self):
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
        self.size = SNAKE_START_SIZE
        self.length = square_length
        self.direction = "right"
        self.direction_queue = queue.Queue(4)
        self.points = 0
        self.growing = False
        self.alive = True
        self.squares = []
        for xi in range(self.size): # horizontal initial orientation
            self.squares.append(Square((SNAKE_START[0] - xi, SNAKE_START[1]), self.colour, self.length))

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
        #_collide(walls) TODO
            
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
    
    def get_key(self):
        for event in pg.event.get():
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
        self.square.xi, self.square.yi = _x, _y # this line for ongoing updates
       
    def display(self):
        self.square.display()


""" Game/Scene management and control """
class Director:
    """Represents the main object of the game.
 
    The Director object keeps the game on, and takes care of updating it,
    drawing it and propagate events.
 
    This object must be used with Scene objects that are defined later."""
 
    def __init__(self):
        self.screen = pygame.display.set_mode((640, 480))
        pygame.display.set_caption("Snake")
        self.scene = None
        self.quit = False
        self.clock = pygame.time.Clock()
 
    def loop(self):
        "Main game loop."
 
        while not self.quit:
            time = self.clock.tick(60)
 
            # Exit events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.quit()
 
            # Detect events
            self.scene.on_event()
 
            # Update scene
            self.scene.on_update()
 
            # Draw the screen
            self.scene.on_draw(self.screen)
            pygame.display.flip()
 
    def change_scene(self, scene):
        "Changes the current scene."
        self.scene = scene
 
    def quit(self):
        self.quit_flag = True
        

""" Temporary Standin Control Loop """
pg.init()
clock = pg.time.Clock()
FPS = 10
w, h = 780, 780
screen_size = [w, h]
screen = pg.display.set_mode(screen_size)

# Testing
arena = Arena(SQUARES_PER_ARENA_SIDE, SQUARE_SIZE, COLOUR_MAP["surface"])
snake = Player(SNAKE_START, COLOUR_MAP["snake"], SQUARE_SIZE)
apple = Apple(COLOUR_MAP["apple"], SQUARE_SIZE, 1, snake)

done = False
font = pg.font.SysFont("courier new", 50)

while not done:
    for event in pg.event.get():  # User did something
        if event.type == pg.QUIT:  # If user clicked close
            done = True

    pg.draw.rect(screen, BLACK, (0,0,w,h))
    arena.display()
    apple.display()

    snake.get_key()
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