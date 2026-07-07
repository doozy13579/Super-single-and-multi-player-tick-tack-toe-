import tkinter as tk
from tkinter import simpledialog, messagebox
import random
import functools

def setup_game():
    # EN: Initializes the main window, asks for game mode and player names.
    # AR: بيجهز الويندو الرئيسية ويسأل تختار سينجل ولا مالتي بلاير واسماء اللاعبين.
    root = tk.Tk()
    root.withdraw()
    
    mode = simpledialog.askstring("Game Mode", "Type '1' for Single Player, '2' for Multiplayer:", parent=root)
    if mode not in ["1", "2"]:
        mode = "2"
    
    p1 = simpledialog.askstring("Player 1", "Enter Player 1's name:", parent=root) or "Player 1"
    if mode == "2":
        p2 = simpledialog.askstring("Player 2", "Enter Player 2's name:", parent=root) or "Player 2"
    else:
        p2 = "AI"
    
    root.deiconify()
    root.title("Ultimate Tic Tac Toe")   # EN: Sets window title / AR: بيحط عنوان للويندو
    root.configure(bg="#2c3e50")         # EN: Sets background color / AR: بيغير لون الخلفية
    
    return root, mode, p1, p2

def create_ui(root, mode, player1, player2):
    # EN: Builds the full game UI (labels, buttons, boards, score tracking).
    # AR: بيبني واجهة اللعبة بالكامل (ليبلز، زرار، البوردات، و متابعة السكور).
    current_player = tk.StringVar(value="X")  # EN: Current player symbol / AR: رمز اللاعب الحالي
    active_board = None                       # EN: Active mini-board / AR: البورد اللي لازم يتلعب فيها
    big_board = [["" for _ in range(3)] for _ in range(3)]  # EN: Main 3x3 board / AR: البورد الكبيرة
    boards = {}                               # EN: Dictionary holding mini-boards / AR: معجم فيه كل البوردات الصغيرة
    scores = {player1: 0, player2: 0}         # EN: Tracks both players’ scores / AR: بيسجل السكور بتاع اللاعبين
    game_over = False

    def update_score_display():
        # EN: Returns formatted string showing players' scores.
        # AR: بيرجع سترينج جاهز للعرض فيه سكور كل لاعب.
        return f"{player1}: {scores[player1]}  |  {player2}: {scores[player2]}"

    # EN: Main container + scrolling setup
    # AR: الفريم الرئيسي ومعاه نظام الاسكرول
    main_frame = tk.Frame(root, bg="#2c3e50")
    main_frame.pack(fill="both", expand=True)
    
    canvas = tk.Canvas(main_frame, bg="#2c3e50", highlightthickness=0)
    scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="#2c3e50")
    
    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    def on_mousewheel(event):
        # EN: Allows scrolling with the mouse wheel.
        # AR: يخلي العجلة تشتغل عشان تعمل سكرول.
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    canvas.bind_all("<MouseWheel>", on_mousewheel)

    # EN: Header with title label
    # AR: هيدر فيه عنوان اللعبة
    header_frame = tk.Frame(scrollable_frame, bg="#34495e", height=80)
    header_frame.pack(fill="x", pady=(0, 10))
    header_frame.pack_propagate(False)
    
    title_label = tk.Label(header_frame, text="ULTIMATE TIC TAC TOE", font=("Arial", 18, "bold"), 
                          fg="#ecf0f1", bg="#34495e")
    title_label.pack(pady=10)

    # EN: Top bar (turn indicator + scores)
    # AR: بار فوق فيه دور مين والسكور
    top_bar = tk.Frame(scrollable_frame, bg="#34495e", pady=8)
    top_bar.pack(fill="x")
    
    turn_label = tk.Label(top_bar, text=f"{player1}'s Turn (X)", font=("Arial", 14, "bold"), 
                         fg="#ecf0f1", bg="#34495e")
    turn_label.pack(side="left", padx=20)
    
    score_label = tk.Label(top_bar, text=update_score_display(), font=("Arial", 12), 
                          fg="#f39c12", bg="#34495e")
    score_label.pack(side="right", padx=20)

    # EN: Control buttons (new round, reset scores, hint)
    # AR: ازرار تحكم (جولة جديدة، تصفير السكور، تلميح)
    controls = tk.Frame(scrollable_frame, bg="#2c3e50", pady=10)
    controls.pack(fill="x")
    
    def reset_all_scores():
        # EN: Reset both players' scores to 0.
        # AR: بيرجع السكور للصفر.
        scores[player1] = 0
        scores[player2] = 0
        score_label.config(text=update_score_display())
    
    button_style = {"font": ("Arial", 10, "bold"), "bg": "#3498db", "fg": "white", 
                   "activebackground": "#2980b9", "relief": "raised", "bd": 2}
    
    restart_btn = tk.Button(controls, text="New Round", command=lambda: reset_game(False), **button_style)
    restart_btn.pack(side="left", padx=15)
    
    reset_scores_btn = tk.Button(controls, text="Reset Scores", command=reset_all_scores, **button_style)
    reset_scores_btn.pack(side="left", padx=5)
    
    hint_label = tk.Label(controls, text="Active board highlighted in blue", bg="#2c3e50", 
                         fg="#bdc3c7", font=("Arial", 10, "italic"))
    hint_label.pack(side="right", padx=15)

    # EN: Main container for all mini-boards
    # AR: الفريم الكبير اللي شايل البوردات الصغيرة
    board_frame = tk.Frame(scrollable_frame, bg="#2c3e50", padx=10, pady=10)
    board_frame.pack()

    def check_board_status(board_key):
        # EN: Checks if mini-board is finished (won or full).
        # AR: بيتأكد لو البورد الصغيرة خلصت (فيها فايز او مليانة).
        br, bc = board_key
        board = boards[(br, bc)]
        if board["winner"] is not None:
            return True
        for r in range(3):
            for c in range(3):
                if board["cells"][r][c]["text"] == "":
                    return False
        return True

    def get_board_state(br, bc):
        # EN: Returns the state (X/O/empty) of a mini-board.
        # AR: بيرجع حالة البورد الصغيرة (X/O/فاضية).
        cells = boards[(br, bc)]["cells"]
        return [[cells[r][c]["text"] for c in range(3)] for r in range(3)]

    def check_mini_win(br, bc):
        # EN: Checks if X or O has won in a mini-board.
        # AR: بيتأكد لو X أو O كسبوا في بورد صغيرة.
        B = get_board_state(br, bc)
        for r in range(3):
            if B[r][0] == B[r][1] == B[r][2] != "":
                return True
        for c in range(3):
            if B[0][c] == B[1][c] == B[2][c] != "":
                return True
        if B[0][0] == B[1][1] == B[2][2] != "":
            return True
        if B[0][2] == B[1][1] == B[2][0] != "":
            return True
        return False

    def check_main_win():
        # EN: Checks if someone has won the main (ultimate) board.
        # AR: بيتأكد لو حد كسب البورد الكبيرة.
        B = big_board
        for r in range(3):
            if B[r][0] == B[r][1] == B[r][2] != "":
                return True
        for c in range(3):
            if B[0][c] == B[1][c] == B[2][c] != "":
                return True
        if B[0][0] == B[1][1] == B[2][2] != "":
            return True
        if B[0][2] == B[1][1] == B[2][0] != "":
            return True
        return False

    def is_game_complete():
        # EN: Checks if the whole ultimate board is filled.
        # AR: بيتأكد لو البورد الكبيرة خلصت كلها.
        for r in range(3):
            for c in range(3):
                if big_board[r][c] == "" and not check_board_status((r,c)):
                    return False
        return True

    def update_player_display():
        # EN: Updates label showing whose turn it is.
        # AR: يغير الليبل لدور اللاعب الحالي.
        turn_label.config(text=f"{player1 if current_player.get() == 'X' else player2}'s Turn ({current_player.get()})")

    def create_cell_button(br, bc, r, c):
        # EN: Creates a button (cell) inside a mini-board.
        # AR: بيعمل زرار خانة جوه بورد صغيرة.
        btn = tk.Button(boards[(br, bc)]["frame"], text="", font=("Arial", 16, "bold"),
                        width=2, height=1, relief="raised", bd=2, bg="#ecf0f1", 
                        activebackground="#d6dbdf", fg="#2c3e50")
        btn.grid(row=r, column=c, padx=3, pady=3)
        btn.config(command=functools.partial(process_move, br, bc, r, c))
        
        def on_enter(e):
            # EN: Hover effect (light blue highlight).
            # AR: لما تعدي بالماوس عليه بينور ازرق فاتح.
            if btn["text"] == "":
                btn.config(bg="#d6eaf8")
        
        def on_leave(e):
            # EN: Reset color when mouse leaves.
            # AR: يرجع اللون زي ما كان لما الماوس يبعد.
            if btn["text"] == "":
                btn.config(bg="#ecf0f1")
                
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        return btn

    def mark_winner(br, bc, symbol):
        # EN: Marks a mini-board as won by X or O.
        # AR: يعلم البورد الصغيرة انها اتكسبت بواسطة X أو O.
        boards[(br, bc)]["winner"] = symbol
        boards[(br, bc)]["frame"].config(bg="#7f8c8d")
        for r in range(3):
            for c in range(3):
                color = "#e74c3c" if symbol == "X" else "#3498db"
                boards[(br, bc)]["cells"][r][c].config(bg="#bdc3c7", fg=color, state="disabled")

    def highlight_current_board():
        # EN: Highlights which board is currently playable.
        # AR: بينور البورد اللي ينفع تلعب فيها دلوقتي.
        for (br, bc), b in boards.items():
            if b["winner"] is None:
                b["frame"].config(bg="#34495e", relief="raised")
        
        a = active_board
        if a is None:
            for (br, bc), b in boards.items():
                if b["winner"] is None and not check_board_status((br, bc)):
                    b["frame"].config(bg="#3498db", relief="sunken")
        else:
            br, bc = a
            if boards[(br, bc)]["winner"] is None:
                boards[(br, bc)]["frame"].config(bg="#3498db", relief="sunken")

    def get_empty_cells(br, bc):
        # EN: Returns all empty cells in a mini-board.
        # AR: بيرجع كل الخانات الفاضية في البورد الصغيرة.
        return [(r,c) for r in range(3) for c in range(3) if boards[(br, bc)]["cells"][r][c]["text"] == ""]

    def get_available_boards():
        # EN: Returns all boards that can currently be played in.
        # AR: بيرجع البوردات اللي ينفع تلعب فيها دلوقتي.
        a = active_board
        if a is None:
            return [(br,bc) for (br,bc) in boards.keys() if not check_board_status((br,bc))]
        if not check_board_status(a):
            return [a]
        return [(br,bc) for (br,bc) in boards.keys() if not check_board_status((br,bc))]
 
    def computer_move():
        # EN: AI chooses a random valid move.
        # AR: الكمبيوتر يختار حركة عشوائية من الحركات الصحيحة.
        me = "O"
        opp = "X"
        available_boards = get_available_boards()
        if not available_boards:
            return
        
        possible_moves = []
        for br,bc in available_boards:
            for (sr,sc) in get_empty_cells(br,bc):
                possible_moves.append((br,bc,sr,sc))
        
        if not possible_moves:
            return
        
        selected_move = random.choice(possible_moves)
        process_move(selected_move[0], selected_move[1], selected_move[2], selected_move[3])

    def process_move(br, bc, sr, sc):
        # EN: Executes a move, checks wins, updates turn.
        # AR: بينفذ الحركة، يشوف لو حد كسب، ويغير الدور.
        nonlocal game_over, active_board
        
        if game_over:
            return
        
        a = active_board
        if a is not None and a != (br, bc):
            if not check_board_status(a):
                return
        
        board = boards[(br, bc)]
        btn = board["cells"][sr][sc]
        
        if btn["text"] != "" or board["winner"] is not None:
            return
        
        sym = current_player.get()
        color = "#e74c3c" if sym == "X" else "#3498db"
        btn.config(text=sym, fg=color)
        
        if check_mini_win(br, bc):
            mark_winner(br, bc, sym)
            big_board[br][bc] = sym
        
        if 0 <= sr < 3 and 0 <= sc < 3 and not check_board_status((sr, sc)):
            active_board = (sr, sc)
        else:
            active_board = None
        
        highlight_current_board()
        
        if check_main_win():
            winner_name = player1 if sym == "X" else player2
            scores[winner_name] += 1
            score_label.config(text=update_score_display())
            messagebox.showinfo("Victory", f"{winner_name} wins the Ultimate Board!")
            reset_game(False)
            return
        
        if is_game_complete():
            messagebox.showinfo("Draw", "The Ultimate Board is a draw.")
            reset_game(False)
            return
        
        current_player.set("O" if sym == "X" else "X")
        update_player_display()
        
        if mode == "1" and current_player.get() == "O" and not game_over:
            root.after(300, computer_move)

    def reset_game(reset_scores_flag=False):
        # EN: Resets the board for a new round.
        # AR: بيرجع اللعبة من الاول لجولة جديدة.
        nonlocal big_board, game_over, active_board
        game_over = False
        
        for (br,bc), b in boards.items():
            b["winner"] = None
            for r in range(3):
                for c in range(3):
                    cell = b["cells"][r][c]
                    cell.config(text="", bg="#ecf0f1", state="normal")
            big_board[br][bc] = ""
            b["frame"].config(bg="#34495e", relief="raised")
        
        active_board = None
        current_player.set("X")
        update_player_display()
        highlight_current_board()
        
        if reset_scores_flag:
            reset_all_scores()

    # EN: Build 9 mini-boards (each 3x3)
    # AR: يبني ٩ بوردات صغيرة (كل واحدة ٣x٣)
    for br in range(3):
        for bc in range(3):
            frame = tk.Frame(board_frame, bg="#34495e", bd=3, relief="raised", padx=8, pady=8)
            frame.grid(row=br, column=bc, padx=5, pady=5)
            boards[(br,bc)] = {"frame": frame, "cells": [], "winner": None}
            
            rows = []
            for r in range(3):
                row = []
                for c in range(3):
                    btn = create_cell_button(br, bc, r, c)
                    row.append(btn)
                rows.append(row)
            
            boards[(br,bc)]["cells"] = rows

    reset_game(False)
    root.geometry("800x400")

def main():
    # EN: Starts the program (setup → UI → mainloop).
    # AR: بداية تشغيل البرنامج (تحضير → واجهة → لوب).
    root, mode, player1, player2 = setup_game()
    create_ui(root, mode, player1, player2)
    root.mainloop()

if __name__ == "__main__":
    main()
 
