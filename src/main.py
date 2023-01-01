import pygame
import sys
import os

import time

from const import *
from game import Game
from square import Square
from move import Move
from piece import Pawn
from stockfish import Stockfish

class Main:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Chess')
        self.game = Game()
        self.stockfish = Stockfish(path = os.path.join(f'stockfish/stockfish.exe'), depth = 20)
        #self.texture = os.path.join(f'assets/images/imgs-{size}px/{self.color}_{self.name}.png')

    def mainloop(self):

        screen = self.screen
        game = self.game
        board = self.game.board
        dragger = self.game.dragger
        stockfish = self.stockfish

        while True:
            game.show_bg(screen)
            game.show_last_move(screen)
            game.show_moves(screen)
            game.show_pieces(screen)
            game.show_hover(screen)
            

            if dragger.dragging:
                dragger.update_blit(screen)

            if game.checkmate:
                game.show_game_over(screen)

            if game.next_player == 'black':
                
                pygame.display.update()
                best_move = stockfish.get_best_move()
                stockfish.make_moves_from_current_position([best_move])
                ai_initial = Square(8 - int(best_move[1]), ord(best_move[0]) - 97)
                piece = board.squares[8 - int(best_move[1])][ord(best_move[0]) - 97].piece
                ai_final = Square(8 - int(best_move[3]), ord(best_move[2]) - 97, piece)
                ai_move = Move(ai_initial, ai_final)
                board.calc_moves(piece, 8 - int(best_move[1]), ord(best_move[0]) - 97)
                board.move(ai_move)
                game.next_turn()

                if board.in_checkmate('white'):
                    game.checkmate = True
                
            for event in pygame.event.get():
                
                # click
                if event.type == pygame.MOUSEBUTTONDOWN:
                    dragger.update_mouse(event.pos)
                    
                    clicked_row = dragger.mouseY // SQSIZE
                    clicked_col = dragger.mouseX // SQSIZE
                    
                    if board.squares[clicked_row][clicked_col].has_piece():
                        piece = board.squares[clicked_row][clicked_col].piece

                        if piece.color == game.next_player:
                            board.calc_moves(piece, clicked_row, clicked_col)
                            dragger.save_initial(event.pos)
                            dragger.drag_piece(piece)

                            game.show_bg(screen)
                            game.show_last_move(screen)
                            game.show_moves(screen)
                            game.show_pieces(screen)

                # mouse motion
                elif event.type == pygame.MOUSEMOTION:
                    motion_col = event.pos[0] // SQSIZE
                    motion_row = event.pos[1] // SQSIZE

                    game.set_hover(motion_row, motion_col)
                    if dragger.dragging:
                        dragger.update_mouse(event.pos)
                        game.show_bg(screen)
                        game.show_last_move(screen)
                        game.show_moves(screen)
                        game.show_pieces(screen)
                        game.show_hover(screen)
                        dragger.update_blit(screen)

                    if game.checkmate:
                        game.show_game_over(screen)

                # click release
                elif event.type == pygame.MOUSEBUTTONUP:

                    if dragger.dragging:
                        dragger.update_mouse(event.pos)
                        
                        released_row = dragger.mouseY // SQSIZE
                        released_col = dragger.mouseX // SQSIZE

                        # create possible move
                        piece = board.squares[clicked_row][clicked_col].piece
                        initial = Square(dragger.initial_row, dragger.initial_col)
                        final = Square(released_row, released_col, piece)
                        move = Move(initial, final)


                        en_passant = False
                        if isinstance(piece, Pawn):
                            en_passant = board.squares[released_row-piece.dir][released_col].has_enemy_piece(piece.color)

                        # valid move ?
                        if board.valid_move(dragger.piece, move):
                            captured =  (board.squares[released_row][released_col].has_piece() or en_passant)

                            board.move(move)
                            stockfish.make_moves_from_current_position([board.get_move()])
                            
                            game.play_sound(captured)
                            game.show_bg(screen)
                            game.show_last_move(screen)
                            game.show_pieces(screen)
                            game.next_turn()

                            
                    dragger.undrag_piece()

                # key press
                elif event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_t:
                        game.change_theme()

                    if event.key == pygame.K_r:
                        game.reset()

                        screen = self.screen
                        game = self.game
                        board = self.game.board
                        dragger = self.game.dragger
                        stockfish.set_fen_position("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")

                # quit application
                elif event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            
            pygame.display.update()
        

main = Main()
main.mainloop()