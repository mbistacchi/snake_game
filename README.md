# snake_game
OOP implimentation of the classic game, including scene management. Pygame for displaying. Includes player control, and automated pathfinding snakes using Breadth First Search and A* - enter 1, 2, or 3 when prompted for user input to select these options respectively (lazy I know).

TODO: 

BUGS: Fix bugs in pathfinding - algorithms correct but there are edge cases how they interact with the game (seems to be when on the perimeter of the game arena.

FEATURES: Difficulty config (speed, configurable walls).

CODING: Type hinting (would have saved a lot of pain originally); and tidy up Objects and how they pass to one-another - originally envisaged for scalability, it's ended up not the most elegant or scalable, although assets were useful for my Game of Life implementation in this Github profile. Way pathfinding snakes interact with the game world is definitely a layer of complexity more than needed.
