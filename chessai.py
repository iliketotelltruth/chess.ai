import chess
import chess.engine
import pygame
import sys


# --- 初始化 ---
pygame.init()
square_size = 80
board_size = square_size * 8
screen = pygame.display.set_mode((board_size, board_size))
pygame.display.set_caption("Chess Game")
font = pygame.font.SysFont("Arial", 24)
clock = pygame.time.Clock()
colors = [(240, 217, 181), (181, 136, 99)]
highlight_color = (0, 0, 255)
piece_images = {}
def load_piece_images():
    piece_map = {
        'r': 6, 'n': 7, 'b': 8, 'q': 9, 'k': 10, 'p': 11,
        'R': 0, 'N': 1, 'B': 2, 'Q': 3, 'K': 4, 'P': 5,
    }
    for symbol, num in piece_map.items():
        try:
            image = pygame.image.load(f"assets/{num}.png")
            piece_images[symbol] = pygame.transform.scale(image, (square_size, square_size))
        except pygame.error as e:
            print(f"Error loading image for {symbol}: {e}")
          
def get_ai_best_move(board, depth=2, time_limit=2.0):
    stockfish_path = r"C:\Users\k2006\OneDrive\Desktop\stockfish\stockfish-windows-x86-64-avx2.exe"
    try:
        with chess.engine.SimpleEngine.popen_uci(stockfish_path) as engine:
            result = engine.play(board, chess.engine.Limit(time=time_limit, depth=depth))
            return result.move
    except Exception as e:
        print(f"Error with Stockfish engine: {e}")
        return None

def draw_board(board, selected_square=None, best_move=None):
    for row in range(8):
        for col in range(8):
            color = colors[(row + col) % 2]
            pygame.draw.rect(screen, color, pygame.Rect(col * square_size, row * square_size, square_size, square_size))
            pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(col * square_size, row * square_size, square_size, square_size), 2)
    if selected_square is not None:
        for move in board.legal_moves:
            if move.from_square == selected_square:
                to_square = move.to_square
                to_row = 7 - (to_square // 8)
                to_col = to_square % 8
                pygame.draw.circle(screen, highlight_color, (to_col * square_size + square_size // 2, to_row * square_size + square_size // 2), 10)
    if best_move:
        to_square = best_move.to_square
        to_row = 7 - (to_square // 8)
        to_col = to_square % 8
        pygame.draw.circle(screen, (255, 0, 0), (to_col * square_size + square_size // 2, to_row * square_size + square_size // 2), 15)  # 高亮顯示最佳步伐
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            symbol = piece.symbol()
            row = 7 - (square // 8)
            col = square % 8
            screen.blit(piece_images[symbol], (col * square_size, row * square_size))
          
def show_text(text, color, position):
    label = font.render(text, True, color)
    screen.blit(label, position)
  
def draw_game_over_message(winner):
    result_text = f"{winner} wins!"
    show_text(result_text, (0, 0, 0), (board_size // 2 - font.size(result_text)[0] // 2, board_size // 2 - 40))
    menu_button = pygame.Rect(board_size // 2 - 75, board_size // 2, 150, 50)
    pygame.draw.rect(screen, (255, 255, 255), menu_button)  # 按鈕背景顏色改為白色
    screen.blit(font.render("Back to Menu", True, (0, 0, 0)), (menu_button.x + 10, menu_button.y + 10))
    pygame.display.flip()
    return menu_button

def run_game(mode, ai_depth, ai_time_limit, player_color):
    board = chess.Board()
    # 根據玩家選擇的顏色調整開始回合
    if player_color == chess.BLACK:
        board.push(chess.Move.from_uci("e2e4"))  # 模擬白方第一步，讓黑方先行
    selected_square = None
    load_piece_images()
    ai_move = None  # Variable to hold AI's move when it's ready
    best_move = None  # Variable to hold AI's best recommended move
    while True:
        draw_board(board, selected_square, best_move)
        if board.is_game_over():
            result = board.result()
            winner = "White" if result == "1-0" else "Black" if result == "0-1" else "Draw"
            menu_button = draw_game_over_message(winner)
            waiting_for_menu = True
            while waiting_for_menu:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if menu_button.collidepoint(event.pos):
                            return  # 返回選單界面
        else:
            turn = "White" if board.turn == chess.WHITE else "Black"
            turn_color = (255, 255, 255) if board.turn == chess.WHITE else (0, 0, 0)
            show_text(f"{turn}'s turn", turn_color, (10, board_size - 40))
            # AI推薦最佳步伐
            if mode == "AI" and board.turn == player_color:
                best_move = get_ai_best_move(board, ai_depth, ai_time_limit)
            # 如果是AI回合，則讓AI下棋
            if mode == "AI" and ((board.turn == chess.WHITE and player_color == chess.BLACK) or
                                 (board.turn == chess.BLACK and player_color == chess.WHITE)) and ai_move is None:
                ai_move = get_ai_best_move(board, ai_depth, ai_time_limit)  # 使用 get_ai_best_move 而非 get_ai_move
            if ai_move:
                board.push(ai_move)
                ai_move = None  # Reset AI move to avoid repeating moves
        pygame.display.flip()
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and not board.is_game_over():
                x, y = pygame.mouse.get_pos()
                col = x // square_size
                row = 7 - (y // square_size)
                clicked_square = row * 8 + col
                if selected_square is None:
                    piece = board.piece_at(clicked_square)
                    if piece and piece.color == board.turn:
                        selected_square = clicked_square
                else:
                    move = chess.Move(selected_square, clicked_square)
                    if move in board.legal_moves:
                        board.push(move)
                        selected_square = None
                        best_move = None  # Reset best move after player move
                        if mode == "AI" and not board.is_game_over():
                            ai_move = get_ai_best_move(board, ai_depth, ai_time_limit)  # 使用 get_ai_best_move 而非 get_ai_move
                    else:
                        selected_square = None

def ai_mode_menu(ai_depth, ai_time_limit):
    white_button = pygame.Rect(100, 200, 200, 50)
    black_button = pygame.Rect(100, 300, 200, 50)
    menu_title = font.render("Choose Your Color", True, (0, 0, 0))
    while True:
        screen.fill((200, 200, 200))
        screen.blit(menu_title, (board_size // 2 - menu_title.get_width() // 2, 50))
        pygame.draw.rect(screen, (255, 255, 255), white_button)  # 按鈕背景顏色改為白色
        pygame.draw.rect(screen, (255, 255, 255), black_button)  # 按鈕背景顏色改為白色
        screen.blit(font.render("White", True, (0, 0, 0)), (white_button.x + 50, white_button.y + 10))
        screen.blit(font.render("Black", True, (0, 0, 0)), (black_button.x + 50, black_button.y + 10))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if white_button.collidepoint(event.pos):
                    run_game("AI", ai_depth, ai_time_limit, chess.WHITE)
                    return
                elif black_button.collidepoint(event.pos):
                    run_game("AI", ai_depth, ai_time_limit, chess.BLACK)
                    return

def main_menu():
    ai_button = pygame.Rect(100, 200, 200, 50)
    two_player_button = pygame.Rect(100, 300, 200, 50)
    menu_title = font.render("Chess Game", True, (0, 0, 0))
    slider_rect = pygame.Rect(100, 400, 300, 20)
    slider_handle = pygame.Rect(100, 395, 20, 30)
    ai_depth = 2
    ai_time_limit = 2.0
    while True:
        screen.fill((200, 200, 200))
        screen.blit(menu_title, (board_size // 2 - menu_title.get_width() // 2, 50))
        pygame.draw.rect(screen, (180, 180, 180), slider_rect)
        pygame.draw.rect(screen, (255, 0, 0), slider_handle)
        screen.blit(font.render(f"ELO Level: {ai_depth * 100 + 1000}", True, (0, 0, 0)), (slider_rect.x + slider_rect.width + 10, 400))
        pygame.draw.rect(screen, (100, 200, 100), ai_button)
        pygame.draw.rect(screen, (100, 100, 200), two_player_button)
        screen.blit(font.render("AI Battle", True, (0, 0, 0)), (ai_button.x + 50, ai_button.y + 10))
        screen.blit(font.render("2 Player", True, (0, 0, 0)), (two_player_button.x + 50, two_player_button.y + 10))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if ai_button.collidepoint(event.pos):
                    ai_mode_menu(ai_depth, ai_time_limit)
                elif two_player_button.collidepoint(event.pos):
                    run_game("2P", 0, 0, None)
                if slider_rect.collidepoint(event.pos):
                    slider_handle.x = max(min(event.pos[0] - 10, slider_rect.right - 10), slider_rect.left)
                    ai_depth = (slider_handle.x - slider_rect.left) // 20
                    ai_time_limit = 1.0 + ai_depth

if __name__ == "__main__":
    main_menu()
