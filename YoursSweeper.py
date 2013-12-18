'''Basic Minesweeper clone'''
import pygame
from pygame.locals import *
import random
import itertools as it

BLACK    = (   0,   0,   0)
WHITE    = ( 255, 255, 255)
RED      = ( 255,   0,   0)
GREEN    = (   0, 255,   0)
GREY     = ( 100, 100, 100)
L_GREY   = ( 200, 200, 200)
L_BLUE   = ( 150, 150, 250)

# TODO: remove GRID_SIZE dependency
GRID_SIZE = 10
T_SIZE = 30
MARGIN = 5 # Margin between each tile

# Set the height and width of the screen dynamically based off grid size
SCREEN_SIZE = (T_SIZE*GRID_SIZE + MARGIN*(GRID_SIZE+1),
                T_SIZE*GRID_SIZE + MARGIN*(GRID_SIZE+1))
CENTER = (SCREEN_SIZE[0]//2, SCREEN_SIZE[1]//2)
screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption("YoursSweeper")

FLAG_IMAGE = pygame.image.load('flag.png').convert_alpha()
FLAG_IMAGE = pygame.transform.scale(FLAG_IMAGE, (T_SIZE, T_SIZE))
MINE_IMAGE = pygame.image.load('mine.png').convert_alpha()
MINE_IMAGE = pygame.transform.scale(MINE_IMAGE, (T_SIZE, T_SIZE))

def init_visible_grid(grid_size=10):
    '''Initialize grid representing matrix visible to player'''
    visible_grid = []
    for row in range(grid_size):
        visible_grid.append([-2 for i in range(grid_size)])
    return visible_grid

def init_grid(grid_size=10, mine_count=10):
    '''Initialize mine grid. Reset board and place new mines randomly
       -1: represents a mine
       0-8: represents number of miens adjacent to this cell'''
    grid = []
    for row in range(grid_size):
        grid.append([0 for i in range(grid_size)])
    
    # Place mines randomly
    mine_locs = random.sample(xrange(pow(grid_size, 2)), mine_count)
    for mine_loc in mine_locs:
        grid[mine_loc//grid_size][mine_loc%grid_size] = -1
    
    # Set all non-mine cell's value to the number of adjacent mines
    for r, c in it.product(range(grid_size), repeat=2):
        if grid[r][c] != -1:
            grid[r][c] = count_surrounding_mines(grid, r, c)

    return grid

def count_surrounding_mines(grid, row, col):
    count = 0
    for r in range(row-1, row+2):
        for c in range(col-1, col+2):
            if 0 <= r < len(grid) and 0 <= c < len(grid[0]):
                count = count + 1 if grid[r][c] == -1 else count
    return count

def draw_visible_grid(visible_grid):
    '''Draw the grid representation of what is shown to the player.
       -2: a covered tile, unclicked.
       -1: a mine that has been clicked
       -4: a flag placed by the player on an unclicked tile
        0: a clicked tile with no adjacent mines'''
    font = pygame.font.Font(None, T_SIZE)
    for r, c in it.product(range(len(visible_grid)), repeat=2):
        color_dict = {-2: L_GREY, -1: RED, 0: GREY, -4: L_GREY}
        color = color_dict.get(visible_grid[r][c], WHITE)

        pygame.draw.rect(screen, color,
            [get_tl_xy_coords(r, c), (T_SIZE, T_SIZE)])

        if visible_grid[r][c] == -4:
            flag_rect = FLAG_IMAGE.get_rect()
            flag_rect.center = get_center_xy_coords(r, c)
            screen.blit(FLAG_IMAGE, flag_rect)

        elif visible_grid[r][c] == -1:
            mine_rect = MINE_IMAGE.get_rect()
            mine_rect.center = get_center_xy_coords(r, c)
            screen.blit(MINE_IMAGE, mine_rect)

        elif visible_grid[r][c] > 0:
            value_text = font.render(str(visible_grid[r][c]), True, RED)
            value_rect = value_text.get_rect()
            value_rect.center = get_center_xy_coords(r, c)
            screen.blit(value_text, value_rect)

def get_grid_coords(x, y):
    '''Convert screen x/y coordinates to grid coordinates: row/col'''
    return y // (T_SIZE + MARGIN), x // (T_SIZE + MARGIN)

def get_tl_xy_coords(row, col):
    '''Convert grid coordinates to x/y coordinates. Top left of tile'''
    return ((MARGIN+T_SIZE)*col+MARGIN, (MARGIN+T_SIZE)*row+MARGIN)

def get_center_xy_coords(row, col):
    '''Convert grid coordinates to x/y coordinates. Center of tile'''
    return ((MARGIN+T_SIZE)*col+MARGIN + T_SIZE/2, 
            (MARGIN+T_SIZE)*row+MARGIN + T_SIZE/2)



class Game(object):
    def __init__(self, grid_size=10, mine_amt=10):
        self.reset(grid_size, mine_amt)

    def reset(self, grid_size, mine_amt):
        self.grid_size = grid_size
        self.mine_amt = mine_amt
        self.grid = init_grid(self.grid_size, self.mine_amt)
        self.visible_grid = init_visible_grid(self.grid_size)

        self.ticks = 0
        self.hit_mine = False
        self.done = False

    def all_clicked(self):
        uncovered_tiles = 0
        for r, c in it.product(range(self.grid_size), repeat=2):
            if self.visible_grid[r][c] >= 0:
                uncovered_tiles += 1

        return pow(self.grid_size, 2) - uncovered_tiles == self.mine_amt

    def all_mines_flagged(self):
        '''Check for win by flagging all mines correctly and no other tiles'''
        for r, c in it.product(range(self.grid_size), repeat=2):
            if (self.grid[r][c] == -1 and self.visible_grid[r][c] != -4 or
                self.visible_grid[r][c] == -4 and self.grid[r][c] != -1):
                return False
        return True

    def game_won(self):
        '''Determine if current game has been won'''
        return self.all_clicked() or self.all_mines_flagged()

    def reveal_square(self, row, col):
        '''Uncover value of cell. If the cell has 0 adjacent mines, uncover
           the values of all adjacent cells'''
        if self.grid[row][col] == 0:
            self.visible_grid[row][col] = 0
            for r, c in it.product(range(row-1, row+2), range(col-1, col+2)):
                if (0 <= r < self.grid_size and 0 <= c < self.grid_size and
                    self.visible_grid[r][c] <= -2):
                    self.reveal_square(r, c)
        else:
            if self.visible_grid[row][col] == -4: return False

            self.visible_grid[row][col] = self.grid[row][col]
            return self.visible_grid[row][col] == -1


    def process_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                return True
            if self.hit_mine or self.game_won():
                if event.type == KEYDOWN and event.key == K_SPACE:
                    self.reset(self.grid_size, self.mine_amt)
            else:
                if event.type == MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    self.hit_mine = self.reveal_square(*get_grid_coords(*pos))
                elif event.type == KEYDOWN and event.key == K_SPACE:
                    pos = pygame.mouse.get_pos()
                    row, col = get_grid_coords(*pos)

                    # Set/unset flag
                    if col < self.grid_size and row < self.grid_size:
                        if self.visible_grid[row][col] == -2:
                                self.visible_grid[row][col] = -4
                        elif self.visible_grid[row][col] == -4:
                                self.visible_grid[row][col] = -2

    def run_logic(self):
        if not self.hit_mine and not self.game_won():
            self.ticks += 1

    def display_frame(self):
        screen.fill(BLACK)
        draw_visible_grid(self.visible_grid)

        if self.hit_mine or self.game_won():
            draw_visible_grid(self.grid)
            font = pygame.font.Font(None, T_SIZE*2)
            if self.hit_mine:
                end_game_text = font.render('Game over!', True, L_BLUE, BLACK) 
            else:
                end_game_text = font.render('You won!' + str(self.ticks), 
                    True, L_BLUE, BLACK)
            end_game_rect = end_game_text.get_rect()
            end_game_rect.center = CENTER
            screen.blit(end_game_text, end_game_rect)

            font = pygame.font.Font(None, T_SIZE)
            continue_text = font.render('Hit space to play again', True, 
                L_BLUE, BLACK)
            continue_rect = continue_text.get_rect()
            continue_rect.center = (CENTER[0], CENTER[1] + T_SIZE)
            screen.blit(continue_text, continue_rect)

        pygame.display.flip()


def main():
    pygame.init()
    done = False
    clock = pygame.time.Clock()
    game = Game()

    while not done:
        done = game.process_events()
        game.run_logic()
        game.display_frame()
        clock.tick(10)

    pygame.quit()


if __name__ == '__main__':
    main()