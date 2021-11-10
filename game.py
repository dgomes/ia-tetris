from asyncio.queues import Queue
import logging
import random
import asyncio
from common import Dimensions
from copy import deepcopy
from shape import SHAPES
from collections import Counter

logger = logging.getLogger("Game")
logger.setLevel(logging.DEBUG)

GAME_SPEED = 10
SPEED_STEP = 10  # points


class Game:
    def __init__(self, x=10, y=30) -> None:
        logger.info("Game")
        self.dimensions = Dimensions(x, y)
        self.current_piece = None
        self.next_pieces = [deepcopy(random.choice(SHAPES)) for _ in range(3)]

        self._bottom = [(i, y) for i in range(x)]  # bottom
        self._lateral = [(0, i) for i in range(y)]  # left
        self._lateral.extend([(x - 1, i) for i in range(y)])  # right

        self.grid = self._bottom + self._lateral

        self.game = []
        self.score = 0
        self.speed = 1
        self.game_speed = 10
        self._lastkeypress = None

        self.running = True

    def info(self):
        return {
            "dimensions": self.dimensions,
            "grid": self.grid,
            "piece": self.current_piece.positions if self.current_piece else None,
            "next_pieces": [n.positions for n in self.next_pieces],
            "game_speed": self.game_speed,
        }

    def clear_rows(self):
        lines = 0

        for item, count in sorted(Counter(y for _, y in self.game).most_common()):
            if count == len(self._bottom) - 2:
                self.game = [
                    (x, y + 1) if y < item else (x, y)
                    for (x, y) in self.game
                    if y != item
                ]  # remove row and drop lines
                lines += 1
                logger.debug("Clear line %s", item)

        self.score += lines ** 2

        self.game_speed = GAME_SPEED + self.score // SPEED_STEP

        most_common = Counter(y for _, y in self.game).most_common(1)
        if most_common != []:
            (_, count) = most_common[0]
            assert count != len(self._bottom) - 2, f"please create an issue https://github.com/dgomes/ia-tetris/issues sharing:\n {self.game}"

    def keypress(self, key):
        """Update locally last key pressed."""
        self._lastkeypress = key

    async def loop(self):
        logger.info("Loop - score: %s - speed: %s", self.score, self.game_speed)
        await asyncio.sleep(1.0 / self.game_speed)
        if self.current_piece is None:
            self.current_piece = self.next_pieces.pop(0)
            self.next_pieces.append(deepcopy(random.choice(SHAPES)))

            logger.debug("New piece: %s", self.current_piece)
            self.current_piece.set_pos(
                (self.dimensions.x - self.current_piece.dimensions.x) / 2, 0
            )
            if not self.valid(self.current_piece):
                logger.info("GAME OVER")
                self.running = False

        self.current_piece.y += 1

        if self.valid(self.current_piece):
            if self._lastkeypress == "s":
                while self.valid(self.current_piece):
                    self.current_piece.y += 1
                self.current_piece.y -= 1
            elif self._lastkeypress == "w":
                self.current_piece.rotate()
                if not self.valid(self.current_piece):
                    self.current_piece.rotate(-1)
            elif self._lastkeypress == "a":
                shift = -1
            elif self._lastkeypress == "d":
                shift = +1

            if self._lastkeypress in ["a", "d"]:
                self.current_piece.translate(shift, 0)
                if self.collide_lateral(self.current_piece):
                    logger.debug("Hitting the wall")
                    self.current_piece.translate(-shift, 0)
                elif not self.valid(self.current_piece):
                    self.current_piece.translate(-shift, 0)

        else:
            self.current_piece.y -= 1
            self.game.extend(self.current_piece.positions)

            self.clear_rows()

            self.current_piece = None

        self._lastkeypress = None

        return {
            "game": self.game,
            "piece": self.current_piece.positions if self.current_piece else None,
            "next_pieces": [n.positions for n in self.next_pieces],
            "game_speed": self.game_speed,
            "score": self.score,
        }

    def valid(self, piece):
        return not any(
            [piece_part in self.grid for piece_part in piece.positions]
        ) and not any([piece_part in self.game for piece_part in piece.positions])

    def collide_lateral(self, piece):
        return any([piece_part in self._lateral for piece_part in piece.positions])
