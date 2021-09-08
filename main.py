from game import Game
import pygame
import logging

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("Tetris")
logger.setLevel(logging.DEBUG)

pygame.font.init()

def draw_window(surface, game):
    surface.fill((0,0,0))
 
    for x, y in game.game:
        pygame.draw.rect(surface, (250,0,0), (x*30, y*30, 30, 30), 0)

    for x, y in game.grid:
        pygame.draw.rect(surface, (0,0,230), (x*30, y*30, 30, 30), 0)

    if game.current_piece:
        for x, y in game.current_piece.positions:
            pygame.draw.rect(surface, (0,250,0), (x*30, y*30, 30, 30), 0)
    
    pygame.display.update()


def main_menu():
    game = Game()
    clock = pygame.time.Clock()

    win.fill((0,0,0))

    run = True
    while run:
        clock.tick(2)
        draw_window(win, game)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
 
            if event.type == pygame.KEYDOWN:
                game.loop(event.unicode)
                
        game.loop(' ')

    pygame.quit()
 
 
win = pygame.display.set_mode((600, 1000))
pygame.display.set_caption('Tetris')
 
main_menu()  # start game