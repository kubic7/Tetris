# -*- coding: cp1250 -*-
import random, time, pygame, sys, os
from pygame.locals import *
pygame.init()

FPS = 25
fpsClock = pygame.time.Clock()
WINDOWWIDTH = pygame.display.Info().current_w
WINDOWHEIGHT = pygame.display.Info().current_h
BOXSIDE = 20
BOARDWIDTH = 20
BOARDHEIGHT = 28
BLANK = "-"

NEXTLEVELEACH = 5

XMARGIN = int((WINDOWWIDTH - BOARDWIDTH * BOXSIDE) / 2)
TOPMARGIN = WINDOWHEIGHT - (BOARDHEIGHT * BOXSIDE) - 5

pygame.font.init()
font = pygame.font.Font("font.ttf", WINDOWWIDTH/30)
icon = pygame.image.load("logo.png")
icon = pygame.transform.scale(icon, (32, 32))                   #Nastavování ikony a názvu okna + font & window Surface
pygame.display.set_icon(icon)
window = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), FULLSCREEN)
pygame.display.set_caption("Tetris")



#               R    G    B
WHITE       = (255, 255, 255)
GRAY        = (185, 185, 185)
BLACK       = (  0,   0,   0)
RED         = (155,   0,   0)
LIGHTRED    = (255,  20,  20)
GREEN       = (  0, 155,   0)
LIGHTGREEN  = ( 20, 255,  20)
BLUE        = ( 20,  20, 120)
LIGHTBLUE   = (  30,   30, 255)
YELLOW      = (155, 155,   0)
LIGHTYELLOW = (255, 255,   0)
COLORS      = (     BLUE,      GREEN,      RED,      YELLOW)
LIGHTCOLORS = (LIGHTBLUE, LIGHTGREEN, LIGHTRED, LIGHTYELLOW)
TEXTCOLOR = GRAY

SHAPEWIDTH = 4
SHAPEHEIGHT = 4
SHAPES = {
    "J":((
            "--O-",
            "--O-",
            "-OO-",
            "----"),
         (
            "----",
            "O---",
            "OOO-",
            "----"),
        (
            "-OO-",
            "-O--",
            "-O--",
            "----"),
        (
            "----",
            "OOO-",
            "--O-",
            "----"),
         ),
    
        
    "L":((
            "-O--",
            "-O--",
            "-OO-",
            "----"),
        (
            "----",
            "-OOO",
            "-O--",
            "----"),
         (
            "-OO-",
            "--O-",
            "--O-",
            "----"),
         (
            "----",
            "---O",
            "-OOO",
            "----")
        ),

    
    "T":((
            "----",
            "-O--",
            "OOO-",
            "----"),
         (
             "-O--",
             "-OO-",
             "-O--",
             "----"),
         (
             "----",
             "OOO-",
             "-O--",
             "----"),
         (
             "--O-",
             "-OO-",
             "--O-",
             "----")
         ),
    
    "O":[[
            "----",
            "-OO-",
            "-OO-",
            "----"]
         ],

    "I":((
            "-O--",
            "-O--",
            "-O--",
            "-O--"),
         (
            "----",
            "OOOO",
            "----",
            "----")
         ),
    
    "Z":((
            "--O-",
            "-OO-",
            "-O--",
            "----"),
         (
            "----",
            "OO--",
            "-OO-",
            "----"),
        ),
    
    "S":((
            "-O--",
            "-OO-",
            "--O-",
            "----"),
         (
            "----",
            "--OO",
            "-OO-",
            "----")
        )}



def get_new_piece():
    shape = random.choice(SHAPES.keys())    #Náhodný výběr tvaru
    piece = {"shape":SHAPES[shape],
             "rotation":random.randint(0, len(SHAPES[shape])-1),
             "x":int((BOARDWIDTH-SHAPEWIDTH)/2),
             "y":-SHAPEHEIGHT+1,             # + 1 proto aby při zobrazování nového kousku koukala dolní řádka
             "color_index":random.randint(0, len(COLORS)-1)
             }
    return(piece)

def switch_rotation(rotate, piece):
    new_rotation = piece["rotation"]
    if rotate == 1:
        if new_rotation < len(piece["shape"])-1:
            new_rotation += 1
        elif new_rotation == len(piece["shape"])-1:
            new_rotation = 0
    elif rotate == -1:
        if new_rotation > 0:
            new_rotation -= 1
        elif new_rotation == 0:
            new_rotation = len(piece["shape"])-1
    return(new_rotation)
            
def draw_square(left, top, color, lighter_color):       #color je okraj čtverce lighter_color
    pygame.draw.rect(window, color, (XMARGIN + left*BOXSIDE, TOPMARGIN + top*BOXSIDE, BOXSIDE, BOXSIDE))
    pygame.draw.rect(window, lighter_color, ((XMARGIN + left*BOXSIDE + 3), (TOPMARGIN + top*BOXSIDE + 3), (BOXSIDE - 6), (BOXSIDE - 6)))
     
def draw_piece(piece):
    shape = piece["shape"][piece["rotation"]]

    for y in range(SHAPEHEIGHT):
        for x in range(SHAPEWIDTH):
            if shape[y][x] == "O" and piece["y"]+y >= 0:
                draw_square((x + piece["x"]), (y + piece["y"]), COLORS[piece["color_index"]], LIGHTCOLORS[piece["color_index"]])

def draw_next_piece(piece):
    shape = piece["shape"][piece["rotation"]]

    for y in range(SHAPEHEIGHT):
        for x in range(SHAPEWIDTH):
            if shape[y][x] == "O":
                draw_square((x + piece["x"]), (y + piece["y"]), COLORS[piece["color_index"]], LIGHTCOLORS[piece["color_index"]])
    
def copy_piece(piece):
    copy_piece = {}
    for key in piece.keys():
        copy_piece[key] = piece[key]
    return(copy_piece)

def draw_board(board, falling_piece):
    pygame.draw.rect(window, GRAY, (XMARGIN-5, TOPMARGIN-5, BOARDWIDTH*BOXSIDE + 10, BOARDHEIGHT*BOXSIDE + 10), 5)
    for y in range(BOARDHEIGHT):
        for x in range(BOARDWIDTH):
            if board[y][x] != BLANK:
                draw_square(x, y, COLORS[int(board[y][x])], LIGHTCOLORS[int(board[y][x])])
    draw_piece(falling_piece)

def game_over():
    global highscore
    over_font = pygame.font.Font("font.ttf", WINDOWWIDTH/15)
    if score > highscore:
        highscore = score
        new_highscore = over_font.render("New highscore!: " + str(score), True, TEXTCOLOR)
        new_highscore_rect = new_highscore.get_rect()
        new_highscore_rect.centery = WINDOWHEIGHT/2
        new_highscore_rect.centerx = WINDOWWIDTH/2
        window.blit(new_highscore, new_highscore_rect)
        game_over_text = font.render("Game over", True, TEXTCOLOR)
        game_over_rect = game_over_text.get_rect()
        game_over_rect.centerx = WINDOWWIDTH/2
        game_over_rect.bottom = new_highscore_rect.top
        window.blit(game_over_text, game_over_rect)
    else:

        score_text = over_font.render("Your Score: " + str(score), True, TEXTCOLOR)
        score_rect = score_text.get_rect()
        score_rect.centery = WINDOWHEIGHT/2
        score_rect.centerx = WINDOWWIDTH/2
        window.blit(score_text, score_rect)
        game_over_text = font.render("Game over", True, TEXTCOLOR)
        game_over_rect = game_over_text.get_rect()
        game_over_rect.centerx = WINDOWWIDTH/2
        game_over_rect.bottom = score_rect.top
        window.blit(game_over_text, game_over_rect)
        highscore_text = font.render("Highscore: " + str(highscore), True, TEXTCOLOR)
        highscore_rect = highscore_text.get_rect()
        highscore_rect.top = score_rect.bottom
        highscore_rect.centerx = WINDOWWIDTH/2
        window.blit(highscore_text, highscore_rect)
    new_game_text = font.render("Press N for new game", True, (255, 255, 255))
    new_game_rect = new_game_text.get_rect()
    new_game_rect.bottom = WINDOWHEIGHT
    new_game_rect.centerx = WINDOWWIDTH/2
    window.blit(new_game_text, new_game_rect)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                f = open("highscore", "w")
                f.write(str(highscore))
                f.close()
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_n or event.key == K_SPACE):
                running = False
        pygame.display.update()
        fpsClock.tick(FPS)
def add_to_board(board, piece):
    shape = piece["shape"][piece["rotation"]]
    for y in range(len(shape)):
        for x in range(len(shape[y])):
            if shape[y][x] == "O" and piece["y"]>-3:
                board[piece["y"]+y][piece["x"]+x] = piece["color_index"]
    return(board)


def delete_lines(board, score):
    new_board = []
    for line_index in range(len(board)):
        if board[line_index].count(BLANK) > 0:
            new_board.append(board[line_index])
        else:
            score += 1
    for i in range(BOARDHEIGHT-len(new_board)):
        new_board = [list((BLANK*BOARDWIDTH))] + new_board
    return(new_board, score)

    
def print_status(score, level):
    score_text = font.render("SCORE: " + str(score), True, TEXTCOLOR)
    score_rect = score_text.get_rect()
    score_rect.top = 0
    score_rect.right = WINDOWWIDTH
    window.blit(score_text, score_rect)
    level_text = font.render("LEVEL: " + str(level), True, TEXTCOLOR)
    level_rect = level_text.get_rect()
    level_rect.top = score_rect.bottom
    level_rect.right = WINDOWWIDTH
    window.blit(level_text, level_rect)
    

def calculate_level():
    global next_level, level, MOVESIDEFREQ, MOVEDOWNFREQ, NORMALMOVEDOWNFREQ, FASTMOVEDOWNFREQ
    koeficient = 0.9
    if score >= next_level:
        next_level += NEXTLEVELEACH
        level += 1
        MOVESIDEFREQ *= koeficient
        MOVEDOWNFREQ *= koeficient
        NORMALMOVEDOWNFREQ *= koeficient
        FASTMOVEDOWNFREQ *= koeficient

def get_new_board():                #Board bude seznam řádků znaků a to buď BLANK ("-") nebo indexu barvy (číslo), jsou 4 typy barev
    board = []
    for y in range(BOARDHEIGHT):
        board.append(list((BLANK*BOARDWIDTH)))
    return(board)

def show_next_piece(next_piece):
    next_piece_text = font.render("Next: ", True, TEXTCOLOR)
    next_piece_rect = next_piece_text.get_rect()
    next_piece_rect.top = int(3*(WINDOWWIDTH/30.))
    next_piece_rect.right = int(WINDOWWIDTH*0.96)
    window.blit(next_piece_text, next_piece_rect)
    next_piece["x"] = BOARDWIDTH + ((XMARGIN-BOXSIDE-(SHAPEWIDTH*BOXSIDE))/BOXSIDE)
    next_piece["y"] = -(TOPMARGIN/BOXSIDE)+((5*(WINDOWWIDTH/30))/BOXSIDE)
    draw_next_piece(next_piece)

    
def is_on_board(piece):
    shape = piece["shape"][piece["rotation"]]
    for y in range(len(shape)):
        for x in range(len(shape[y])):
            
            if shape[y][x] == "O":
                if not ((piece["y"] + y) < BOARDHEIGHT and (piece["x"] + x) >= 0 and (piece["x"] + x) < BOARDWIDTH):
                    return(False)
    return(True)

def colliding(board, piece):
    global spam
    shape = piece["shape"][piece["rotation"]]
    respond = 1
    for y in range(len(shape)):
        for x in range(len(shape[y])):
            if shape[y][x] == "O" and piece["y"]+ y >= 0 and board[piece["y"]+y][piece["x"]+x] != BLANK:
                if piece["y"] < 0:
                    spam = False
                return(True)
    return(False)

def is_valid_position(board, piece, adx = 0, ady = 0, adrot = False):
    copy_p = copy_piece(piece)
    if adrot != False:
        copy_p["rotation"] = adrot
    copy_p["x"] += adx
    copy_p["y"] += ady
    if is_on_board(copy_p) and not colliding(board, copy_p):
        
        return(True)

    
    return(False)




if "highscore" not in os.listdir(os.getcwd()):
    f = open("highscore", "w")
    highscore = 0
else:
    f = open("highscore", "r")
    highscore = int(f.read())
    f.close()

while True:           
    board = get_new_board()
    falling_piece = get_new_piece()
    score = 0
    level = 0
    next_piece = get_new_piece()
    last_move_down = time.time()
    last_move_left = time.time()
    last_move_right = time.time()
    last_fast_move_down = time.time()
    next_level = NEXTLEVELEACH
    MOVESIDEFREQ = 0.15
    MOVEDOWNFREQ = 0.1
    NORMALMOVEDOWNFREQ = 0.3
    FASTMOVEDOWNFREQ = 0.05
    moveleft = False
    moveright = False
    fast_move_down = False
    rotate = 0
    running = True
    spam = True
    while running:
        window.fill(BLACK)
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                f = open("highscore", "w")
                f.write(str(highscore))
                f.close()
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_DOWN:
                    rotate -= 1
                if event.key == K_UP:
                    rotate += 1
                if event.key == K_LEFT:
                    moveleft = True
                if event.key == K_RIGHT:
                    moveright = True
                if event.key == K_SPACE:
                    fast_move_down = True
            if event.type == KEYUP:
                if event.key == K_LEFT:
                    moveleft = False
                if event.key == K_RIGHT:
                    moveright = False
                if event.key == K_SPACE:
                    fast_move_down = False
        if time.time()-last_move_down > NORMALMOVEDOWNFREQ:
            last_move_down = time.time()
            if is_valid_position(board, falling_piece, 0, 1):
                falling_piece["y"] += 1
            else:
                board = add_to_board(board, falling_piece)
                falling_piece = next_piece
                next_piece = get_new_piece()
                if not is_valid_position(board, falling_piece, 0, 1):
                    running = False

        if moveleft and time.time()-last_move_left > MOVESIDEFREQ:
            if is_valid_position(board, falling_piece, -1, 0):
                falling_piece["x"] -= 1
                last_move_left = time.time()

        if moveright and time.time()-last_move_right > MOVESIDEFREQ:
            if is_valid_position(board, falling_piece, 1, 0):
                falling_piece["x"] += 1
                last_move_right = time.time()
                
        if fast_move_down and time.time()-last_fast_move_down > FASTMOVEDOWNFREQ:
            last_fast_move_down = time.time()
            if is_valid_position(board, falling_piece, 0, 1):
                falling_piece["y"] += 1
            else:
                board = add_to_board(board, falling_piece)
                falling_piece = next_piece
                next_piece = get_new_piece()
                if not is_valid_position(board, falling_piece, 0, 1):
                    running = False

        if rotate:
            rotation = switch_rotation(rotate, falling_piece)
            c = copy_piece(falling_piece)
            c["rotation"] = switch_rotation(rotate, falling_piece)
            if is_on_board(c):
                if is_valid_position(board, falling_piece, 0, 0, rotation):
                    falling_piece["rotation"] = rotation
            rotate = 0

        if spam == False:
            running = False
        calculate_level()
        board, score = delete_lines(board, score)
        draw_board(board, falling_piece)
        copied_piece = copy_piece(next_piece)
        show_next_piece(copied_piece)
        print_status(score, level)
        pygame.display.update()
        fpsClock.tick(FPS)
    game_over()
