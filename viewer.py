"""Viewer application."""
import argparse
import asyncio
import json
import logging
import os
import websockets

import pygame

logging.basicConfig(level=logging.DEBUG)
logger_websockets = logging.getLogger("websockets")
logger_websockets.setLevel(logging.WARN)

logger = logging.getLogger("Viewer")
logger.setLevel(logging.DEBUG)

BLOCK_SIDE = 30
BLOCK_SIZE = BLOCK_SIDE, BLOCK_SIDE

COLORS = {
    "white": (255, 255, 255),
    "red": (255, 0, 0),
    "pink": (255, 105, 180),
    "blue": (135, 206, 235),
    "orange": (255, 165, 0),
    "yellow": (255, 255, 0),
    "grey": (120, 120, 120),
    "green": (0, 240, 0),
}


async def messages_handler(websocket_path, queue):
    """Handles server side messages, putting them into a queue."""
    async with websockets.connect(websocket_path) as websocket:
        await websocket.send(json.dumps({"cmd": "join"}))

        while True:
            update = await websocket.recv()
            queue.put_nowait(update)


def scale(pos):
    """Scale positions according to gfx."""
    x, y = pos
    return int(x * BLOCK_SIDE / SCALE), int(y * BLOCK_SIDE / SCALE)


def draw_info(surface, text, pos, color=(0, 0, 0), background=None):
    """Creates text based surfaces for information display."""
    myfont = pygame.font.Font(None, int(24 / SCALE))
    textsurface = myfont.render(text, True, color, background)

    x, y = pos
    if x > surface.get_width():
        pos = surface.get_width() - (textsurface.get_width() + 10), y
    if y > surface.get_height():
        pos = x, surface.get_height() - textsurface.get_height()

    if background:
        surface.blit(background, pos)
    else:
        erase = pygame.Surface(textsurface.get_size())
        erase.fill(COLORS["grey"])

    surface.blit(textsurface, pos)
    return textsurface.get_width(), textsurface.get_height()


async def main_loop(queue):
    """Processes events from server and display's."""
    win = pygame.display.set_mode((600, 1000))
    pygame.display.set_caption("Tetris")

    logging.info("Waiting for map information from server")
    state = await queue.get()  # first state message includes map information
    logging.debug("Initial game status: %s", state)
    newgame_json = json.loads(state)

    win.fill((0, 0, 0))

    for x, y in newgame_json["grid"]:
        pygame.draw.rect(
            win,
            COLORS["blue"],
            (x * BLOCK_SIDE, y * BLOCK_SIDE, BLOCK_SIDE, BLOCK_SIDE),
            0,
        )

    game_speed = newgame_json["game_speed"]

    while True:
        pygame.display.update()

        pygame.event.pump()
        if pygame.key.get_pressed()[pygame.K_ESCAPE]:
            asyncio.get_event_loop().stop()

        try:
            state = json.loads(queue.get_nowait())
            print(state)

            if "game_speed" in state:
                game_speed = state["game_speed"]

            win.fill((0, 0, 0))

            if "highscores" in state:
                draw_info(win, "HIGHSCORES", scale((5,5)), COLORS["white"])
                for idx, player in enumerate(state["highscores"]):
                    draw_info(win, f"{player[0]: <{20}} {player[1]}", scale((5,6 + idx)), COLORS["white"])
                continue

            for x, y in newgame_json["grid"]:
                pygame.draw.rect(
                    win,
                    COLORS["blue"],
                    (x * BLOCK_SIDE, y * BLOCK_SIDE, BLOCK_SIDE, BLOCK_SIDE),
                    0,
                )

            for x, y in state["game"]:
                pygame.draw.rect(
                    win,
                    COLORS["red"],
                    (x * BLOCK_SIDE, y * BLOCK_SIDE, BLOCK_SIDE, BLOCK_SIDE),
                    0,
                )

            if state["piece"]:
                for x, y in state["piece"]:
                    pygame.draw.rect(
                        win,
                        COLORS["green"],
                        (x * BLOCK_SIDE, y * BLOCK_SIDE, BLOCK_SIDE, BLOCK_SIDE),
                        0,
                    )

            yy = 0
            for next_piece in state["next_pieces"]:
                for x, y in next_piece:
                    pygame.draw.rect(
                        win,
                        COLORS["pink"],
                        (
                            (x + 11) * BLOCK_SIDE,
                            (y + 1 + yy) * BLOCK_SIDE,
                            BLOCK_SIDE,
                            BLOCK_SIDE,
                        ),
                        0,
                    )
                yy += 5

        except asyncio.queues.QueueEmpty:
            await asyncio.sleep(1.0 / game_speed)
            continue


if __name__ == "__main__":
    SERVER = os.environ.get("SERVER", "localhost")
    PORT = os.environ.get("PORT", "8000")

    parser = argparse.ArgumentParser()
    parser.add_argument("--server", help="IP address of the server", default=SERVER)
    parser.add_argument(
        "--scale", help="reduce size of window by x times", type=int, default=1
    )
    parser.add_argument("--port", help="TCP port", type=int, default=PORT)
    arguments = parser.parse_args()
    SCALE = arguments.scale

    LOOP = asyncio.get_event_loop()
    pygame.font.init()
    q = asyncio.Queue()
    PROGRAM_ICON = pygame.image.load("data/tetris_block.png")
    pygame.display.set_icon(PROGRAM_ICON)

    ws_path = f"ws://{arguments.server}:{arguments.port}/viewer"

    try:
        LOOP.run_until_complete(
            asyncio.gather(messages_handler(ws_path, q), main_loop(q))
        )
    except RuntimeError as err:
        logger.error(err)
    finally:
        LOOP.stop()
