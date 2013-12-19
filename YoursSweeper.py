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

T_SIZE = 30
MARGIN = 5 # Margin between each tile

screen = pygame.display.set_mode((285, 315))
pygame.display.set_caption("YoursSweeper")

def opening_click_button(mouse_pos):
    '''Handle clicks during opening screen'''
    if 80 <= mouse_pos[0] <= 200:
        if 178 <= mouse_pos[1] < 210:
            return Game((8, 8), 10)
        elif 210 <= mouse_pos[1] < 244:
            return Game((16, 16), 40)
        elif 244 <= mouse_pos[1] <= 276:
            return Game((16, 31), 99)
    
    return False

def opening_screen():
    '''Display opening screen. Return a game instance or False if quitting'''
    opening_img = pygame.image.load('openingscreen.png')
    screen.blit(opening_img, (0, 0))
    pygame.display.flip()

    while True:
        for event in pygame.event.get(): # User did something
            if event.type == pygame.QUIT: # If user clicked close
                return False # Flag that we are done so we exit this loop
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if opening_click_button(mouse_pos):
                    return opening_click_button(mouse_pos)

def init_visible_grid(grid_size):
    '''Initialize grid representing matrix visible to player'''
    visible_grid = []
    for row in range(grid_size[0]):
        visible_grid.append([-2 for c in range(grid_size[1])])
    return visible_grid

def init_grid(grid_size, mine_count):
    '''Initialize mine grid. Reset board and place new mines randomly
       -1: represents a mine
       0-8: represents number of miens adjacent to this cell'''
    grid = []
    for row in range(grid_size[0]):
        grid.append([0 for c in range(grid_size[1])])
    
    # Place mines randomly
    mine_locs = random.sample(xrange(grid_size[0]*grid_size[1]), mine_count)
    for mine_loc in mine_locs:
        grid[mine_loc//grid_size[1]][mine_loc%grid_size[1]] = -1
    
    # Set all non-mine cell's value to the number of adjacent mines
    for r, c in it.product(range(grid_size[0]), range(grid_size[1])):
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

def count_flags(visible_grid):
    '''Count flags placed by user. Use for player's remaining mine count'''
    total_flags = 0
    for r, c in it.product(range(len(visible_grid)), repeat=2):
        if visible_grid[r][c] == -4:
            total_flags += 1
    return total_flags

def draw_buttons(screen):
    '''Draw the buttons for beg, med, hard difficulties'''
    font = pygame.font.Font(None, T_SIZE)
    beg_text = font.render('BEG.', True, WHITE, (175, 175, 175))
    beg_rect = beg_text.get_rect()
    beg_rect.midleft = (0, screen.get_height() - T_SIZE/2)
    screen.blit(beg_text, beg_rect)

    med_text = font.render('MED.', True, WHITE, (150, 150, 150))
    med_rect = med_text.get_rect()
    med_rect.midleft = (75, screen.get_height() - T_SIZE/2)
    screen.blit(med_text, med_rect)

    hard_text = font.render('HARD', True, WHITE, GREY)
    hard_rect = hard_text.get_rect()
    hard_rect.midleft = (150, screen.get_height() - T_SIZE/2)
    screen.blit(hard_text, hard_rect)

def draw_grid(visible_grid, screen, flag_img, mine_img):
    '''Draw the grid representation of what is shown to the player.
       -2: a covered tile, unclicked.
       -1: a mine that has been clicked
       -4: a flag placed by the player on an unclicked tile
        0: a clicked tile with no adjacent mines'''
    font = pygame.font.Font(None, T_SIZE)
    for r, c in it.product(range(len(visible_grid)), 
                            range(len(visible_grid[0]))):
        color_dict = {-2: L_GREY, -1: RED, 0: GREY, -4: L_GREY}
        color = color_dict.get(visible_grid[r][c], WHITE)

        pygame.draw.rect(screen, color,
            [get_tl_xy_coords(r, c), (T_SIZE, T_SIZE)])

        if visible_grid[r][c] == -4:
            flag_rect = flag_img.get_rect()
            flag_rect.center = get_center_xy_coords(r, c)
            screen.blit(flag_img, flag_rect)

        elif visible_grid[r][c] == -1:
            mine_rect = mine_img.get_rect()
            mine_rect.center = get_center_xy_coords(r, c)
            screen.blit(mine_img, mine_rect)

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
    def __init__(self, grid_size, mine_amt):
        self.reset(grid_size, mine_amt)

    def reset(self, grid_size, mine_amt):
        self.grid_screen_size = (T_SIZE*grid_size[0] + MARGIN*(grid_size[0]+1),
                T_SIZE*grid_size[1] + MARGIN*(grid_size[1]+1))
        self.center = (self.grid_screen_size[1]//2, 
                        self.grid_screen_size[0]//2)
        self.total_screen_size = (self.grid_screen_size[1], 
            self.grid_screen_size[0] + T_SIZE)

        self.screen = pygame.display.set_mode(self.total_screen_size)

        flag_img = pygame.image.load('flag.png').convert_alpha()
        self.flag_img = pygame.transform.scale(flag_img, (T_SIZE, T_SIZE))
        mine_img = pygame.image.load('mine.png').convert_alpha()
        self.mine_img = pygame.transform.scale(mine_img, (T_SIZE, T_SIZE))

        self.grid_size = grid_size
        self.mine_amt = mine_amt
        self.grid = init_grid(self.grid_size, self.mine_amt)
        self.visible_grid = init_visible_grid(self.grid_size)

        self.ticks = 0
        self.hit_mine = False
        self.done = False

    def all_clicked(self):
        uncovered_tiles = 0
        for r, c in it.product(range(self.grid_size[0]), 
                                range(self.grid_size[1])):
            if self.visible_grid[r][c] >= 0:
                uncovered_tiles += 1

        return (self.grid_size[0]*self.grid_size[1] - 
                    uncovered_tiles == self.mine_amt)

    def all_mines_flagged(self):
        '''Check for win by flagging all mines correctly and no other tiles'''
        for r, c in it.product(range(self.grid_size[0]), 
                                range(self.grid_size[1])):
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
        if not (row < self.grid_size[0] and col < self.grid_size[1]): 
            return False

        if self.grid[row][col] == 0:
            self.visible_grid[row][col] = 0
            for r, c in it.product(range(row-1, row+2), range(col-1, col+2)):
                if (0 <= r < self.grid_size[0] and 0 <= c < self.grid_size[1]
                    and self.visible_grid[r][c] <= -2):
                    self.reveal_square(r, c)
        else:
            if self.visible_grid[row][col] == -4: return False

            self.visible_grid[row][col] = self.grid[row][col]
            return self.visible_grid[row][col] == -1

    def click_button(self, mouse_pos):
        if mouse_pos[1] >= self.grid_screen_size[0]: #change so it's [1]?
            if 0 <= mouse_pos[0] <= 50:
                self.reset((8, 8), 10)
            elif 75 <= mouse_pos[0] <= 125:
                self.reset((16, 16), 40)
            elif 150 <= mouse_pos[0] <= 200:
                self.reset((16, 31), 99)


    def process_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                return True
            if self.hit_mine or self.game_won():
                if event.type == KEYDOWN and event.key == K_SPACE:
                    self.reset(self.grid_size, self.mine_amt)
                if event.type == MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    self.click_button(pos)
            else: 
                if event.type == MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    self.hit_mine = self.reveal_square(*get_grid_coords(*pos))
                elif event.type == KEYDOWN and event.key == K_SPACE:
                    pos = pygame.mouse.get_pos()
                    row, col = get_grid_coords(*pos)

                    # Set/unset flag
                    if row < self.grid_size[0] and col < self.grid_size[1]:
                        if self.visible_grid[row][col] == -2:
                                self.visible_grid[row][col] = -4
                        elif self.visible_grid[row][col] == -4:
                                self.visible_grid[row][col] = -2

    def run_logic(self):
        if not self.hit_mine and not self.game_won():
            self.ticks += 1

    def display_frame(self):
        self.screen.fill(BLACK)
        draw_buttons(self.screen)
        draw_grid(self.visible_grid, self.screen, self.flag_img, self.mine_img)

        font = pygame.font.Font(None, T_SIZE)
        points_text = font.render(str(self.ticks//10), True, L_BLUE)
        points_rect = points_text.get_rect()
        points_rect.bottomright = self.total_screen_size
        self.screen.blit(points_text, points_rect)

        mines_text = font.render(
            str(self.mine_amt - count_flags(self.visible_grid)), True, RED)
        mines_rect = mines_text.get_rect()
        mines_rect.right = points_rect.left - 10
        mines_rect.bottom = points_rect.bottom
        self.screen.blit(mines_text, mines_rect)


        if self.hit_mine or self.game_won():
            draw_grid(self.grid, self.screen, self.flag_img, self.mine_img)

            font = pygame.font.Font(None, T_SIZE*2)
            if self.hit_mine:
                end_game_text = font.render('Game over!', True, L_BLUE, BLACK) 
            else:
                end_game_text = font.render('You won!', True, L_BLUE, BLACK)
            end_game_rect = end_game_text.get_rect()
            end_game_rect.center = self.center
            self.screen.blit(end_game_text, end_game_rect)

            font = pygame.font.Font(None, T_SIZE)
            continue_text = font.render('Hit space to play again', True, 
                L_BLUE, BLACK)
            continue_rect = continue_text.get_rect()
            continue_rect.center = (self.center[0], self.center[1] + T_SIZE)
            self.screen.blit(continue_text, continue_rect)

            difficulty_text = font.render('Or select a difficulty', True,
                L_BLUE, BLACK)
            difficulty_rect = difficulty_text.get_rect()
            difficulty_rect.center = (self.center[0], 
                                        self.center[1] + 1.6*T_SIZE)
            self.screen.blit(difficulty_text, difficulty_rect)

        pygame.display.flip()


def main():
    pygame.init()
    done = False
    clock = pygame.time.Clock()
    game = opening_screen()
    while game and not done:
        done = game.process_events()
        game.run_logic()
        game.display_frame()
        clock.tick(10)

    pygame.quit()


if __name__ == '__main__':
    main()