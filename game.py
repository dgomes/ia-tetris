import logging
import random
from common import Dimensions

from shape import SHAPES
from collections import Counter

logger = logging.getLogger("Game")
logger.setLevel(logging.DEBUG)

class Game:

    def __init__(self, x=10, y=30) -> None:
        logger.info("Game")
        self.dimensions = Dimensions(x, y)
        self.current_piece = None

        self._bottom = [(i, y) for i in range(x)] #bottom
        self._lateral = [(0, i) for i in range(y)]  #left
        self._lateral.extend([(x-1, i) for i in range(y)])    #right

        self.grid = self._bottom + self._lateral

        self.game = []
        self.score = 0

    def clear_rows(self):
        lines = 0

        for item,count in Counter(y for _,y in self.game).most_common():
            if count == len(self._bottom) - 2:
                self.game = [(x,y) for (x,y) in self.game if y!=item]   #remove row
                self.game = [(x,y+1) if y<item else (x,y) for (x,y) in self.game]   #drop blocks above
                logger.debug("Clear line %s", item)

        self.score += lines ** 2

    def loop(self, key):
        if self.current_piece is None:
            self.current_piece = random.choice(SHAPES)
            logger.debug("New piece: %s", self.current_piece)
            self.current_piece.set_pos((self.dimensions.x-self.current_piece.dimensions.x)/2, 0)
            if not self.valid(self.current_piece):
                print("GAME OVER")
                print(self.current_piece)
                exit()
            

        self.current_piece.y += 1

        if self.valid(self.current_piece):
            if key == 'space':
                self.speed = 1
            elif key == 'w':
                self.current_piece.rotate()
                if not self.valid(self.current_piece):
                    self.current_piece.rotate(-1)
            elif key == 'a':
                shift = -1
            elif key == 'd':
                shift = +1

            if key in ['a','d']:
                self.current_piece.translate(shift,0)
                if self.collide_lateral(self.current_piece):
                    logger.debug("Hitting the wall")
                    self.current_piece.translate(-shift,0)            
            
        else:
            self.current_piece.y -= 1
            self.game.extend(self.current_piece.positions)

            self.clear_rows()

            self.current_piece = None
    
    def valid(self, piece):
        return not any([piece_part in self.grid for piece_part in self.current_piece.positions]) and\
            not any([piece_part in self.game for piece_part in self.current_piece.positions])

    def collide_lateral(self, piece):
        return any([piece_part in self._lateral for piece_part in self.current_piece.positions])


