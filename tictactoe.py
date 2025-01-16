import copy
import sys
import pygame
import random
import numpy as np
from constants import *

# --- PYGAME SETUP ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('TIC TAC TOE AI')
screen.fill(BG_COLOR)

# Função para exibir a mensagem de início
def show_start_message(screen, font, start_time, countdown_duration):
    current_time = pygame.time.get_ticks()
    if current_time < start_time + countdown_duration * 1000:
        screen.fill(BG_COLOR)
        text = font.render(f"Começando em {countdown_duration - (current_time - start_time) // 1000} segundos...", True, (0, 0, 0))
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(text, text_rect)
        pygame.display.update()
        return True
    return False

# Função para exibir a mensagem de vitória
def show_winner_message(screen, font, winner, display_time=2000):
    screen.fill(BG_COLOR)
    winner_text = f"Jogador {winner} Vencedor!"
    text = font.render(winner_text, True, (0, 0, 0))
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(text, text_rect)

    # Desenhar estrelas ao redor da mensagem
    for i in range(5):
        pygame.draw.circle(screen, (255, 215, 0), (WIDTH // 2 + random.randint(-50, 50), HEIGHT // 2 + random.randint(-50, 50)), 10, 0)
    
    pygame.display.update()
    pygame.time.wait(display_time)

# --- CLASSES ---

class Board:

    def __init__(self):
        self.squares = np.zeros((ROWS, COLS))
        self.marked_sqrs = 0

    def final_state(self, show=False):
        '''
            @return 0 if there is no win yet
            @return 1 if player 1 wins
            @return 2 if player 2 wins
        '''

        # vertical wins
        for col in range(COLS):
            if self.squares[0][col] == self.squares[1][col] == self.squares[2][col] != 0:
                if show:
                    color = CIRC_COLOR if self.squares[0][col] == 2 else CROSS_COLOR
                    iPos = (col * SQSIZE + SQSIZE // 2, 20)
                    fPos = (col * SQSIZE + SQSIZE // 2, HEIGHT - 20)
                    pygame.draw.line(screen, color, iPos, fPos, LINE_WIDTH)
                return self.squares[0][col]

        # horizontal wins
        for row in range(ROWS):
            if self.squares[row][0] == self.squares[row][1] == self.squares[row][2] != 0:
                if show:
                    color = CIRC_COLOR if self.squares[row][0] == 2 else CROSS_COLOR
                    iPos = (20, row * SQSIZE + SQSIZE // 2)
                    fPos = (WIDTH - 20, row * SQSIZE + SQSIZE // 2)
                    pygame.draw.line(screen, color, iPos, fPos, LINE_WIDTH)
                return self.squares[row][0]

        # desc diagonal
        if self.squares[0][0] == self.squares[1][1] == self.squares[2][2] != 0:
            if show:
                color = CIRC_COLOR if self.squares[1][1] == 2 else CROSS_COLOR
                iPos = (20, 20)
                fPos = (WIDTH - 20, HEIGHT - 20)
                pygame.draw.line(screen, color, iPos, fPos, CROSS_WIDTH)
            return self.squares[1][1]

        # asc diagonal
        if self.squares[2][0] == self.squares[1][1] == self.squares[0][2] != 0:
            if show:
                color = CIRC_COLOR if self.squares[1][1] == 2 else CROSS_COLOR
                iPos = (20, HEIGHT - 20)
                fPos = (WIDTH - 20, 20)
                pygame.draw.line(screen, color, iPos, fPos, CROSS_WIDTH)
            return self.squares[1][1]

        # no win yet
        return 0

    def mark_sqr(self, row, col, player):
        self.squares[row][col] = player
        self.marked_sqrs += 1

    def empty_sqr(self, row, col):
        return self.squares[row][col] == 0

    def get_empty_sqrs(self):
        empty_sqrs = []
        for row in range(ROWS):
            for col in range(COLS):
                if self.empty_sqr(row, col):
                    empty_sqrs.append((row, col))
        
        return empty_sqrs

    def isfull(self):
        return self.marked_sqrs == 9

    def isempty(self):
        return self.marked_sqrs == 0

class AI:

    def __init__(self, level=1, player=2):
        self.level = level
        self.player = player

    # --- RANDOM ---

    def rnd(self, board):
        empty_sqrs = board.get_empty_sqrs()
        idx = random.randrange(0, len(empty_sqrs))
        return empty_sqrs[idx]  # (row, col)

    # --- MINIMAX ---

    def minimax(self, board, maximizing):
        # terminal case
        case = board.final_state()

        # player 1 wins
        if case == 1:
            return 1, None  # eval, move

        # player 2 wins
        if case == 2:
            return -1, None

        # draw
        elif board.isfull():
            return 0, None

        if maximizing:
            max_eval = -100
            best_move = None
            empty_sqrs = board.get_empty_sqrs()

            for (row, col) in empty_sqrs:
                temp_board = copy.deepcopy(board)
                temp_board.mark_sqr(row, col, 1)
                eval = self.minimax(temp_board, False)[0]
                if eval > max_eval:
                    max_eval = eval
                    best_move = (row, col)

            return max_eval, best_move

        elif not maximizing:
            min_eval = 100
            best_move = None
            empty_sqrs = board.get_empty_sqrs()

            for (row, col) in empty_sqrs:
                temp_board = copy.deepcopy(board)
                temp_board.mark_sqr(row, col, self.player)
                eval = self.minimax(temp_board, True)[0]
                if eval < min_eval:
                    min_eval = eval
                    best_move = (row, col)

            return min_eval, best_move

    # --- MAIN EVAL ---

    def eval(self, main_board):
        if self.level == 0:
            # random choice
            eval = 'random'
            move = self.rnd(main_board)
        else:
            # minimax algo choice
            eval, move = self.minimax(main_board, False)

        print(f'AI has chosen to mark the square in pos {move} with an eval of: {eval}')

        # Ensure move is not None
        if move is None:
            raise ValueError("AI evaluation did not return a valid move.")

        return move  # (row, col)

class Game:

    def __init__(self):
        self.board = Board()
        self.ai = AI()
        self.player = 1   # 1-cross  # 2-circles
        self.gamemode = 'ai' # pvp or ai
        self.running = True
        self.scores = {1: 0, 2: 0}  # Adicionando pontuação para ambos os jogadores
        self.show_lines()

    # --- DRAW METHODS ---

    def show_lines(self):
        # bg
        screen.fill(BG_COLOR)

        # vertical
        pygame.draw.line(screen, LINE_COLOR, (SQSIZE, 0), (SQSIZE, HEIGHT), LINE_WIDTH)
        pygame.draw.line(screen, LINE_COLOR, (WIDTH - SQSIZE, 0), (WIDTH - SQSIZE, HEIGHT), LINE_WIDTH)

        # horizontal
        pygame.draw.line(screen, LINE_COLOR, (0, SQSIZE), (WIDTH, SQSIZE), LINE_WIDTH)
        pygame.draw.line(screen, LINE_COLOR, (0, HEIGHT - SQSIZE), (WIDTH, HEIGHT - SQSIZE), LINE_WIDTH)

    def draw_fig(self, row, col):
        if self.player == 1:
            # draw cross
            # desc line
            start_desc = (col * SQSIZE + OFFSET, row * SQSIZE + OFFSET)
            end_desc = (col * SQSIZE + SQSIZE - OFFSET, row * SQSIZE + SQSIZE - OFFSET)
            pygame.draw.line(screen, CROSS_COLOR, start_desc, end_desc, CROSS_WIDTH)
            # asc line
            start_asc = (col * SQSIZE + OFFSET, row * SQSIZE + SQSIZE - OFFSET)
            end_asc = (col * SQSIZE + SQSIZE - OFFSET, row * SQSIZE + OFFSET)
            pygame.draw.line(screen, CROSS_COLOR, start_asc, end_asc, CROSS_WIDTH)

        elif self.player == 2:
            # draw circle
            center = (col * SQSIZE + SQSIZE // 2, row * SQSIZE + SQSIZE // 2)
            pygame.draw.circle(screen, CIRC_COLOR, center, RADIUS, CIRC_WIDTH)

    def make_move(self, row, col):
        if self.board.empty_sqr(row, col):
            self.board.mark_sqr(row, col, self.player)
            self.draw_fig(row, col)
            self.player = 1 if self.player == 2 else 2

    def change_gamemode(self):
        self.gamemode = 'ai' if self.gamemode == 'pvp' else 'pvp'

    def isover(self):
        return self.board.final_state() != 0 or self.board.isfull()

    def update_scores(self):
        winner = self.board.final_state()
        if winner:
            self.scores[winner] += 1
        print(f'Scores: {self.scores}')

    def restart(self):
        self.board = Board()
        self.show_lines()
        self.running = True
        self.player = 1

# --- MAIN FUNCTION ---

def main():
    # Inicialização do pygame font
    pygame.font.init()
    font = pygame.font.SysFont('Arial', 40)

    # Tempo de início da contagem regressiva
    countdown_duration = 3  # em segundos
    start_time = pygame.time.get_ticks()

    # Criação do jogo
    game = Game()

    # --- MAINLOOP ---
    while True:
        # pygame events
        for event in pygame.event.get():
            # quit event
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # keydown event
            if event.type == pygame.KEYDOWN:
                # g-gamemode
                if event.key == pygame.K_g:
                    game.change_gamemode()

                # r-restart
                if event.key == pygame.K_r:
                    game.restart()

                # 0-random ai
                if event.key == pygame.K_0:
                    game.ai.level = 0

                # 1-random ai
                if event.key == pygame.K_1:
                    game.ai.level = 1

            # click event
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                row = pos[1] // SQSIZE
                col = pos[0] // SQSIZE
                
                # human mark sqr
                if game.board.empty_sqr(row, col) and game.running:
                    game.make_move(row, col)

                    if game.isover():
                        winner = game.board.final_state()
                        game.update_scores()
                        show_winner_message(screen, font, winner)
                        pygame.display.update()
                        pygame.time.wait(2000)  # Espera 2 segundos antes de reiniciar
                        game.restart()

        # Mostrar a mensagem de início
        if show_start_message(screen, font, start_time, countdown_duration):
            # Espera a contagem regressiva terminar
            continue
        else:
            # Início do jogo
            if game.gamemode == 'ai' and game.player == game.ai.player and game.running:
                pygame.display.update()
                move = game.ai.eval(game.board)
                if move is not None:
                    row, col = move
                    game.make_move(row, col)
                    if game.isover():
                        winner = game.board.final_state()
                        game.update_scores()
                        show_winner_message(screen, font, winner)
                        pygame.display.update()
                        pygame.time.wait(2000)  # Espera 2 segundos antes de reiniciar
                        game.restart()

        pygame.display.update()

if __name__ == '__main__':
    main()
