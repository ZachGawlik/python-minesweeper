'''YoursSweeper, a basic Minesweeper clone'''
import __future__
import pygame
from pygame.locals import *
import random
import numpy as np
import webbrowser
import os.path


BLACK  = (   0,   0,   0)
WHITE  = ( 255, 255, 255)
RED    = ( 255,   0,   0)
GREY   = ( 100, 100, 100)
L_GREY = ( 200, 200, 200)
L_BLUE = ( 150, 150, 250)

MARGIN = 5 # Margin between each tile
T_SIZE = 25

pygame.font.init()
T_FONT = pygame.font.Font(None, T_SIZE)
T2_FONT = pygame.font.Font(None, T_SIZE*2)

EASY = ((8, 8), 10)
MEDIUM = ((16, 16), 40)
HARD = ((16, 31), 99)


def create_base_file():
    highscore_file = open('highscore.txt', 'w')
    highscore_file.writelines([
        'Easy \n'
        'N/A: 999 seconds\n'
        'Medium \n'
        'N/A: 999 seconds\n'
        'Hard \n'
        'N/A: 999 seconds\n'
         ])
    highscore_file.close()


def opening_click_button(mouse_pos):
    '''Handle clicks during opening screen.'''
    if 80 <= mouse_pos[0] <= 200:
        if 155 <= mouse_pos[1] < 184:
            return Game(*EASY)
        elif 184 <= mouse_pos[1] < 212:
            return Game(*MEDIUM)
        elif 212 <= mouse_pos[1] <= 240:
            return Game(*HARD)
    
    if mouse_pos[1] > 250:
        webbrowser.open_new_tab('http://en.wikipedia.org/wiki/'
                                'Minesweeper_(game)#Overview)')
    return False


def load_png(file_name):
    return pygame.image.load(file_name).convert_alpha()


def opening_screen(screen):
    '''Display opening screen. Return a game instance or False if quitting.'''
    OPENING_IMG = pygame.image.load('openingscreen.png')
    scaled_opening_img = pygame.transform.scale(OPENING_IMG, 
                                                easy_game.total_screen_size)
    screen.blit(scaled_opening_img, (0, 0))
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                return False
            if event.type == MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if opening_click_button(mouse_pos):
                    return opening_click_button(mouse_pos)


def grid_ndindex(grid):
    '''Generate all indices for a nonempty 2d array.'''
    return np.ndindex(len(grid), len(grid[0]))


def adjacents(grid, row, col):
    '''Generate valid indices adjacent to given index. Include given index.'''
    for r, c in np.ndindex(3, 3):
        if 0 <= row-1+r < len(grid) and 0 <= col-1+c < len(grid[0]):
            yield row-1+r, col-1+c


def count_adjacent_mines(grid, row, col):
    '''Count mines surrounding the given index on the grid.'''
    return (sum((1 for r, c in adjacents(grid, row, col) if grid[r][c] == -1)))


def count_flags(grid):
    '''Count flags placed by user.'''
    return sum((1 for r, c in grid_ndindex(grid) if grid[r][c] == -4))


def init_visible_grid(grid_size):
    '''Initialize the grid visible to player. Set all tiles to covered.'''
    visible_grid = []
    for row in range(grid_size[0]):
        visible_grid.append([-2 for c in range(grid_size[1])])
    return visible_grid


def init_grid(grid_size, mine_count):
    '''Initialize mine grid: reset board and place new mines randomly.

    -1: represents a mine
    0-8: represents number of mines adjacent to this cell

    '''
    grid = []
    for row in range(grid_size[0]):
        grid.append([0 for c in range(grid_size[1])])
    
    # Place mines randomly
    mine_locs = random.sample(xrange(grid_size[0]*grid_size[1]), mine_count)
    for mine_loc in mine_locs:
        grid[mine_loc//grid_size[1]][mine_loc%grid_size[1]] = -1
    
    # Set all non-mine cell's value to the number of adjacent mines
    for r, c in np.ndindex(*grid_size):
        if grid[r][c] != -1:
            grid[r][c] = count_adjacent_mines(grid, r, c)

    return grid

 
def draw_grid(visible_grid, screen):
    '''Draw the grid representation of what is shown to the player.

    -2: a covered tile, unclicked.
    -1: a mine that has been clicked
    -4: a flag placed by the player on an unclicked tile
     0: a clicked tile with no adjacent mines

    '''
    scaled_flag_img = pygame.transform.scale(FLAG_IMG, (T_SIZE, T_SIZE))
    scaled_mine_img = pygame.transform.scale(MINE_IMG, (T_SIZE, T_SIZE))

    for r, c in grid_ndindex(visible_grid):
        cvalue = visible_grid[r][c]
        tile_color_dict = {-2: L_GREY, -1: RED, 0: GREY, -4: L_GREY}
        tile_color = tile_color_dict.get(cvalue, WHITE)

        pygame.draw.rect(screen, tile_color,
                         [get_tl_xy_coords(r, c), (T_SIZE, T_SIZE)])

        if cvalue == -4:
            flag_rect = scaled_flag_img.get_rect()
            flag_rect.center = get_center_xy_coords(r, c)
            screen.blit(scaled_flag_img, flag_rect)

        elif cvalue == -1:
            mine_rect = scaled_mine_img.get_rect()
            mine_rect.center = get_center_xy_coords(r, c)
            screen.blit(scaled_mine_img, mine_rect)

        elif cvalue > 0:
            text_color = [
                None, (0, 0, 255), (0, 120, 0), (255, 0, 0), (98, 0, 98), 
                (176, 48, 96), (0, 200, 200), BLACK, GREY
                ]

            value_text = T_FONT.render(str(cvalue), True, text_color[cvalue])
            value_rect = value_text.get_rect()
            value_rect.center = get_center_xy_coords(r, c)
            screen.blit(value_text, value_rect)


def draw_buttons(screen):
    '''Draw the buttons for beginner, medium, hard difficulties'''
    beg_text = T_FONT.render('EASY', True, WHITE, (175, 175, 175))
    beg_rect = beg_text.get_rect()
    beg_rect.midleft = (0, screen.get_height() - T_SIZE/2)
    screen.blit(beg_text, beg_rect)

    med_text = T_FONT.render('MED ', True, WHITE, (150, 150, 150))
    med_rect = med_text.get_rect()
    med_rect.midleft = beg_rect.midright
    screen.blit(med_text, med_rect)

    hard_text = T_FONT.render('HARD', True, WHITE, GREY)
    hard_rect = hard_text.get_rect()
    hard_rect.midleft = med_rect.midright
    screen.blit(hard_text, hard_rect)


def get_grid_coords(x, y):
    '''Convert screen x, y coordinates to grid coordinates row, col.'''
    return y // (T_SIZE+MARGIN), x // (T_SIZE+MARGIN)


def get_tl_xy_coords(row, col):
    '''Convert grid coordinates to x, y coordinates for top left of tile.'''
    return ((MARGIN+T_SIZE)*col+MARGIN, (MARGIN+T_SIZE)*row+MARGIN)


def get_center_xy_coords(row, col):
    '''Convert grid coordinates to x, y coordinates for center of tile.'''
    return ((MARGIN+T_SIZE)*col+MARGIN + T_SIZE/2, 
            (MARGIN+T_SIZE)*row+MARGIN + T_SIZE/2)


class Game(object):
    def __init__(self, grid_size, mine_amt):
        if (not os.path.exists('highscore.txt') or 
            os.path.getsize('highscore.txt') == 0):
            create_base_file()

        with open('highscore.txt') as f:
            self.scoredata = f.readlines()

        self.reset(grid_size, mine_amt)
        
    def reset(self, grid_size, mine_amt):
        self.grid_screen_size = (
            T_SIZE*grid_size[0] + MARGIN*(grid_size[0]+1),
            T_SIZE*grid_size[1] + MARGIN*(grid_size[1]+1)
            )
        self.center = (self.grid_screen_size[1]//2, 
                       self.grid_screen_size[0]//2)
        self.total_screen_size = (self.grid_screen_size[1], 
                                  self.grid_screen_size[0] + T_SIZE)
        self.screen = pygame.display.set_mode(self.total_screen_size)

        self.grid_size = grid_size
        self.mine_amt = mine_amt
        self.grid = init_grid(self.grid_size, self.mine_amt)
        self.visible_grid = init_visible_grid(self.grid_size)

        self.clicks = 0
        self.ticks = 0
        self.game_over = False
        self.hit_mine = False
        self.won = False

    def all_clicked(self):
        '''Return if all non-mine tiles have been uncovered.'''
        covered_tiles = 0
        for r, c in grid_ndindex(self.grid):
            if self.visible_grid[r][c] <= -2: # spot flagged or unclicked
                if not self.grid[r][c] == -1: # covered spot is not a mine
                    return False

        return True

    def all_mines_flagged(self):
        '''Return if game won by correctly flagging all mines.'''
        for r, c in grid_ndindex(self.grid):
            if (self.grid[r][c] == -1 and self.visible_grid[r][c] != -4):
                return False

        return count_flags(self.visible_grid) == self.mine_amt

    def flag_cell(self, row, col):
        '''Set/unset flag for the given cell.'''
        if row < self.grid_size[0] and col < self.grid_size[1]:
            if (self.visible_grid[row][col] == -2 and 
                count_flags(self.visible_grid) < self.mine_amt):
                    self.visible_grid[row][col] = -4
            elif self.visible_grid[row][col] == -4:
                    self.visible_grid[row][col] = -2

    def check_won(self):
        '''Determine if current game has been won.'''
        self.won = self.all_clicked() or self.all_mines_flagged()
        self.game_over = self.won or self.game_over 

    def reveal_square(self, row, col, overwrite_flags=False):
        '''Uncover value of cell. Return if a mine is revealed.

        If the cell has no adjacent mines, uncover all adjacent cells.

        '''
        if not (row < self.grid_size[0] and col < self.grid_size[1]):
            return False
        cell_value = self.grid[row][col]

        if self.visible_grid[row][col] == -4 and not overwrite_flags:
            return False

        if self.clicks == 0 and cell_value == -1:  # Prevent first click loss
            self.reset(self.grid_size, self.mine_amt)
            self.reveal_square(row, col)
            return False
        else: 
            self.visible_grid[row][col] = cell_value
            if cell_value == 0:
                for r, c in adjacents(self.grid, row, col):
                    if self.visible_grid[r][c] <= -2:
                        self.reveal_square(r, c, True)
            else:
                return cell_value == -1

    def click_button(self, mouse_pos):
        '''Handle clicks during game over screen.'''
        if mouse_pos[1] >= self.grid_screen_size[0]:
            if 0 <= mouse_pos[0] <= 45:
                self.reset(*EASY)
            elif 45 < mouse_pos[0] <= 80:
                self.reset(*MEDIUM)
            elif 80 < mouse_pos[0] <= 120:
                self.reset(*HARD)

    def process_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                return True
            elif self.game_over:
                if event.type == KEYDOWN and event.key == K_SPACE:
                    self.reset(self.grid_size, self.mine_amt)
                if event.type == MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    self.click_button(pos)
            else: 
                if event.type == MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    self.hit_mine = self.reveal_square(*get_grid_coords(*pos))
                    self.game_over = self.hit_mine or self.game_over
                    self.clicks += 1
                elif event.type == KEYDOWN and event.key == K_SPACE:
                    pos = pygame.mouse.get_pos()
                    self.flag_cell(*get_grid_coords(*pos))

    def getline(self):
        '''Return which line # of highscore file to overwrite for this mode.'''
        mode_to_line = {EASY[0]: 1, MEDIUM[0]: 3, HARD[0]: 5}
        return mode_to_line.get(self.grid_size)

    def new_highscore(self):
        name = raw_input('New high score! What is your name?  ')
        new_entry = '{0}: {1} seconds\n'.format(name, self.ticks//10)
        self.scoredata[self.getline()] = new_entry
        
        for line in self.scoredata:
            print(line.strip())
        print('Return to game window to play again.')

        with open('highscore.txt', 'w') as f:
            f.writelines(self.scoredata)

    def is_highscore(self):
        '''Determine if completed game set a new highscore.'''
        current_line = self.scoredata[self.getline()].strip()
        current_highscore = current_line.split(' ')[-2]
        return self.ticks//10 < int(current_highscore) and self.won

    def run_logic(self):
        self.check_won()
        if not self.game_over:
            self.ticks += 1

        if self.won and self.is_highscore():
            self.display_frame()
            self.new_highscore()

    def display_frame(self):
        self.screen.fill(BLACK)
        draw_grid(self.visible_grid, self.screen)

        time_text = T_FONT.render(
                '{:0>3}'.format(self.ticks//10), True, L_BLUE)
        time_rect = time_text.get_rect()
        time_rect.bottomright = self.total_screen_size
        self.screen.blit(time_text, time_rect)

        remaining_mines = self.mine_amt - count_flags(self.visible_grid)
        mine_count_text = T_FONT.render(str(remaining_mines), True, RED)
        mine_count_rect = mine_count_text.get_rect()
        mine_count_rect.right = time_rect.left - 10
        mine_count_rect.bottom = time_rect.bottom
        self.screen.blit(mine_count_text, mine_count_rect)


        if self.game_over:
            if self.hit_mine:
                draw_grid(self.grid, self.screen)
                img_file, end_file = 'lost.png', 'endtext.png'
            elif self.is_highscore():
                img_file, end_file = 'newhs.png', 'hsinstruct.png'
            else:
                img_file, end_file = 'won.png', 'endtext.png'

            first_ln = load_png(img_file)
            first_ln_rect = first_ln.get_rect()
            first_ln_rect.midbottom = self.center
            self.screen.blit(first_ln, first_ln_rect)

            end_text = load_png(end_file)
            end_text_rect = end_text.get_rect()
            end_text_rect.midtop = self.center
            self.screen.blit(end_text, end_text_rect)
            draw_buttons(screen)

        pygame.display.flip()


easy_game = Game(*EASY)
screen = pygame.display.set_mode(easy_game.total_screen_size)
pygame.display.set_caption('YoursSweeper')
FLAG_IMG = load_png('flag.png')
MINE_IMG = load_png('mine.png')


def main():
    pygame.init()
    done = False
    clock = pygame.time.Clock()
    game = opening_screen(screen)
    
    while game and not done:
        done = game.process_events()
        game.run_logic()
        game.display_frame()
        clock.tick(10)

    pygame.quit()


if __name__ == '__main__':
    main()