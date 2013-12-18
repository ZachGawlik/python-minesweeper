'''Basic Minesweeper clone'''
import pygame
import random
import numpy

BLACK    = (   0,   0,   0)
WHITE    = ( 255, 255, 255)
RED      = ( 255,   0,   0)
GREEN    = (   0, 255,   0)
GREY     = ( 100, 100, 100)
L_GREY   = ( 200, 200, 200)
L_BLUE   = ( 150, 150, 250)

GRID_SIZE = 10
T_WIDTH = 40
T_HEIGHT = 40
MARGIN = 5 # Margin between each tile

# Set the height and width of the screen dynamically based off grid size
SCREEN_SIZE = (T_WIDTH*GRID_SIZE + MARGIN*(GRID_SIZE+1),
                T_HEIGHT*GRID_SIZE + MARGIN*(GRID_SIZE+1))
CENTER = (SCREEN_SIZE[0]//2, SCREEN_SIZE[1]//2)
screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption("YoursSweeper")

FLAG_IMAGE = pygame.image.load('flag.png').convert_alpha()
MINE_IMAGE = pygame.image.load('mine.png').convert_alpha()

def init_visible_grid():
    '''Initialize grid representing matrix visible to player'''
    visible_grid = []
    for row in range(GRID_SIZE):
        visible_grid.append([-2 for i in range(GRID_SIZE)])
    return visible_grid

def init_grid(mine_count=10):
    '''Initialize mine grid. Reset board and place new mines randomly'''
    grid = []
    for row in range(GRID_SIZE):
        grid.append([0 for i in range(GRID_SIZE)])
    
    # Place mines randomly
    mine_locs = random.sample(xrange(pow(GRID_SIZE, 2)), mine_count)
    for mine_loc in mine_locs:
        grid[mine_loc//GRID_SIZE][mine_loc%GRID_SIZE] = -1
    
    # Set all non-mine cell's value to the number of adjacent mines
    for r, c in numpy.ndindex((GRID_SIZE, GRID_SIZE)):
        if grid[r][c] != -1:
            grid[r][c] = count_surrounding_mines(grid, r, c)

    return grid

def count_surrounding_mines(grid, row, col):
    count = 0
    for r in range(row-1, row+2):
        for c in range(col-1, col+2):
            if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE:
                count = count + 1 if grid[r][c] == -1 else count
    return count

def draw_visible_grid(visible_grid):
    '''Draw the grid representation of what is shown to the player.
       -2: a covered tile, unclicked.
       -1: a mine that has been clicked
       -4: a flag placed by the player on an unclicked tile
        0: a clicked tile with no adjacent mines'''
    font = pygame.font.Font(None, T_HEIGHT)
    for r, c in numpy.ndindex((GRID_SIZE, GRID_SIZE)):
        color_dict = {-2: L_GREY, -1: RED, 0: GREY, -4: L_GREY}
        color = color_dict.get(visible_grid[r][c], WHITE)

        pygame.draw.rect(screen, color,
            [get_tl_xy_coords(r, c), (T_WIDTH, T_HEIGHT)])

        if visible_grid[r][c] == -4:
            flag_rect = FLAG_IMAGE.get_rect()
            flag_rect.center = get_center_xy_coords(r, c)
            screen.blit(FLAG_IMAGE, flag_rect)

        elif visible_grid[r][c] == -1:
            mine_rect = MINE_IMAGE.get_rect()
            mine_rect.center = get_center_xy_coords(r, c)
            screen.blit(MINE_IMAGE, mine_rect)

        elif visible_grid[r][c] > 0:
            value_text = font.render(str(grid[r][c]), True, RED)
            value_rect = value_text.get_rect()
            value_rect.center = get_center_xy_coords(r, c)
            screen.blit(value_text, value_rect)

def reveal_square(row, col):
    '''Uncover value of cell. If the cell has 0 adjacent mines, uncover
       the values of all adjacent cells'''
    if visible_grid[row][col] == -4: return False

    if grid[row][col] == 0:
        visible_grid[row][col] = 0
        for r in range(row-1, row+2):
            for c in range(col-1, col+2):
                if (0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE and 
                    visible_grid[r][c] <= -2):
                    reveal_square(r, c)
    else:
        visible_grid[row][col] = grid[row][col]
        return grid[row][col] == -1

def game_won(visible_grid):
    uncovered_tiles = 0
    for r, c in numpy.ndindex((GRID_SIZE, GRID_SIZE)):
        if visible_grid[r][c] >= 0:
            uncovered_tiles += 1

    return pow(GRID_SIZE, 2) - uncovered_tiles == MINE_COUNT

def get_grid_coords(x, y):
    '''Convert screen x/y coordinates to grid coordinates: row/col'''
    return y // (T_HEIGHT + MARGIN), x // (T_WIDTH + MARGIN)

def get_tl_xy_coords(row, col):
    '''Convert grid coordinates to x/y coordinates. Top left of tile'''
    return ((MARGIN+T_WIDTH)*col+MARGIN, (MARGIN+T_HEIGHT)*row+MARGIN)

def get_center_xy_coords(row, col):
    '''Convert grid coordinates to x/y coordinates. Center of tile'''
    return ((MARGIN+T_WIDTH)*col+MARGIN + T_WIDTH/2, 
            (MARGIN+T_HEIGHT)*row+MARGIN + T_HEIGHT/2)


pygame.init()
hit_mine = False
done = False
grid = init_grid()
visible_grid = init_visible_grid()
GRID_SIZE = 10
MINE_COUNT = 10
# ---- MAIN PROGRAM LOOP ----
while not done:
    # Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if hit_mine or game_won(visible_grid):
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                grid = init_grid()
                visible_grid = init_visible_grid()
                hit_mine = False
        else:
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                hit_mine = reveal_square(*get_grid_coords(*pos))
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                pos = pygame.mouse.get_pos()
                row, col = get_grid_coords(*pos)

                # Set/unset flag
                if col < GRID_SIZE and row < GRID_SIZE:
                    if visible_grid[row][col] == -2:
                            visible_grid[row][col] = -4
                    elif visible_grid[row][col] == -4:
                            visible_grid[row][col] = -2

    # Displaying board
    screen.fill(BLACK)
    draw_visible_grid(visible_grid)

    if hit_mine or game_won(visible_grid):
        font = pygame.font.Font(None, 60)
        if hit_mine:
            end_game_text = font.render('Game over!', True, L_BLUE, BLACK) 
        else:
            end_game_text = font.render('You won!', True, L_BLUE, BLACK)
        end_game_rect = end_game_text.get_rect()
        end_game_rect.center = CENTER
        screen.blit(end_game_text, end_game_rect)

        continue_text = font.render('Hit space to play again', True, 
            L_BLUE, BLACK)
        continue_rect = continue_text.get_rect()
        continue_rect.center = (CENTER[0], CENTER[1] + 40)
        screen.blit(continue_text, continue_rect)

    pygame.display.flip()

pygame.quit()