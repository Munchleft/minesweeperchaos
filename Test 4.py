import tkinter as tk
import random
import time
# Các biến toàn cục
BOMB_RATIO = 0.3  # Tỉ lệ bom
SPREAD_DELAY = 10  # Độ trễ hiệu ứng lan màu
buttons = {}
field = []
first_click = True
game_over = False
win = False
start_time = None
attempts = 0
score = 0
rows = 0
columns = 0
button_size = 30
root = None
stats_frame = None  # Khung thống kê

# Cửa sổ khởi động (mới)
def start_window():
    temp = tk.Tk()
    temp.title("Start Game")
    tk.Label(temp, text="Minesweeper Chaos", font=("Arial", 16)).pack(pady=10)
    tk.Button(temp, text="Run", font=("Arial", 14), command=lambda: [temp.destroy(), setup_game()]).pack(pady=20)
    temp.mainloop()


# Thiết lập màn hình game (mới : tạo tkinter tạm thời để đo kịch thước màn hình, sau đó tắt )
def setup_screen():
    global root, rows, columns
    temp_root = tk.Tk()
    screen_width = temp_root.winfo_screenwidth()
    screen_height = temp_root.winfo_screenheight()
    temp_root.destroy()

    usable_height = int(screen_height * 5 / 7)
    usable_width = int(screen_width* 15/16)   # Con chua tinh duoc ti le
    columns = usable_width // button_size
    rows = usable_height // button_size

    root.attributes('-fullscreen', True)

# Tạo bản đồ 0-1
def create_field(rows, columns):
    total = rows * columns
    bombs = int(total * BOMB_RATIO)
    tiles = [1] * bombs + [0] * (total - bombs)
    random.shuffle(tiles)
    result = []
    for i in range(rows):
        result.append(tiles[i * columns:(i + 1) * columns])
    return result

# Màu nền ngẫu nhiên xanh (mói : dựa vào rgb để random màu xanh cho đa dạng hơn, không dùng darkgreen seagreen lightgreen)
def random_green_color():
    g = random.randint(100, 255)
    r = random.randint(0, 100)
    b = random.randint(0, 100)
    return f'#{r:02x}{g:02x}{b:02x}'

# Màu chữ ngẫu nhiên (của con bị lỗi)
def random_text_color():
    return random.choice(['blue', 'darkgreen', 'purple', 'brown', 'black'])

# Tạo tất cả các nút (con thay hình vuông với nút)
def create_buttons(rows, columns):
    for hang in range(rows):
        for cot in range(columns):
            color = random_green_color()
            btn = tk.Button(root, bg=color, width=2, height=1,
                            font=('Courier', 14, 'bold'))
            btn.grid(row=hang, column=cot, sticky="nsew")
            btn.config(command=lambda hang=hang, cot=cot: on_click(hang, cot))
            btn.bind("<Button-3>", lambda e, hang=hang, cot=cot: on_right_click(hang, cot))
            buttons[(hang, cot)] = btn

# Khu vực thống kê (mới)
def create_stats_area():
    global stats_frame
    stats_frame = tk.Frame(root, height=100)
    stats_frame.grid(row=rows, column=0, columnspan=columns, sticky="we")
    update_stats()

# Cập nhật thống kê (mới: time,attempts(số lượt thử),điểm , note cái lỗi code đang có, nút thử lại và nút quit)
def update_stats():
    for widget in stats_frame.winfo_children():
        widget.destroy()
    elapsed = int(time.time() - start_time) if start_time else 0
    tk.Label(stats_frame, text=f"Time: {elapsed}s", font=("courier", 14)).pack(side="left", padx=30)
    tk.Label(stats_frame, text="BUG: IF YOU LOSE,WAIT FOR THE SCREEN TO SPREAD EVERYTHING BEFORE REPLAY", font=("courier", 14,"bold")).pack(side="left", pady=20, padx = 30)
    tk.Label(stats_frame, text=f"Attempts: {attempts}", font=("courier", 14, )).pack(side="left", padx=30)
    tk.Label(stats_frame, text=f"Score: {score}", font=("courier", 14)).pack(side="left", padx=30)
    tk.Button(stats_frame, text="Retry", command=replay, font=("courier", 14)).pack(side="right", padx=20)
    tk.Button(stats_frame, text="Quit", command=quit_game, font=("courier", 14)).pack(side="right", padx=20)

# Lấy danh sách ô lân cận (điều chỉnh để ko liệt kê dài ra nữa)
def adjacent(hang, cot):
    adj = []
    for d_hang in [-1, 0, 1]:
        for d_cot in [-1, 0, 1]:
            if not (d_hang == 0 and d_cot == 0):
                adj.append((hang + d_hang, cot + d_cot))
    random.shuffle(adj)
    return adj

# Hiện số ô
def reveal_tile(hang, cot):
    btn = buttons[(hang, cot)]
    if btn['state'] == 'disabled' or btn.cget('text') == 'F':
        return
    bombs = count_adjacent_bombs(hang, cot)
    btn.config(text=str(bombs), fg=random_text_color(), bg='lightgrey', relief='sunken')  # Con bị lỗi màu ở đây.
    btn['state'] = 'disabled'

# Đếm số bom quanh ô
def count_adjacent_bombs(hang, cot):
    count = 0
    for n_hang, n_cot in adjacent(hang, cot):
        if (0 <= n_hang < rows) and (0 <= n_cot < columns):
            if field[n_hang][n_cot] == 1:
                count += 1
    return count

# Mở rộng ____ ô đầu tiên (mới: giống như google thì mở như thế)
def reveal_first(hang, cot):
    revealed = set()
    queue = [(hang, cot)]
    i = random.randint(9,20)
    while len(revealed) < i and queue:
        current_hang, current_cot = queue.pop(0)
        if (0 <= current_hang < rows) and (0 <= current_cot < columns) and ((current_hang, current_cot) not in revealed):
            if field[current_hang][current_cot] == 0:
                revealed.add((current_hang, current_cot))
                queue.extend(adjacent(current_hang, current_cot))
    for current_hang, current_cot in revealed:
        reveal_tile(current_hang, current_cot)

# Khi nhấn trúng bom
def reveal_bomb(hang, cot):
    btn = buttons[(hang, cot)]
    btn.config(bg='red')
    start_spread('red')
    end_game(False)

# Hiệu ứng lan màu
def start_spread(color):
    queue = list(buttons.keys())
    random.shuffle(queue)
    def spread():
        if queue:
            for _ in range(random.randint(3, 10)):
                if queue:
                    hang, cot = queue.pop()
                    if buttons[(hang, cot)]['bg'] not in ['red', 'lightyellow', 'green']:
                        buttons[(hang, cot)].config(bg=color)
            root.after(SPREAD_DELAY, spread)
    spread()

# Kết thúc trò chơi
def end_game(is_win):
    global game_over
    game_over = True
    elapsed = int(time.time() - start_time)
    final_score = score
    result = "Victory!" if is_win else "Game Over!"
    popup = tk.Toplevel(root)
    popup.geometry("300x200")
    popup.attributes('-topmost', True)
    label = tk.Label(popup, text=f"{result}\nTime: {elapsed}s\nScore: {final_score}", font=("Arial", 16))
    label.pack(pady=20)
    button = tk.Button(popup, text="Replay", command=lambda:[popup.destroy(), replay()])
    button.pack()

# Kiểm tra thắng
def check_win():
    all_revealed = True
    for (hang, cot), btn in buttons.items():
        if field[hang][cot] == 0 and btn['state'] != 'disabled':
            all_revealed = False
    if all_revealed:
        global win, attempts
        win = True
        turn_bombs_green()
        start_spread('lightyellow')
        end_game(True)
        attempts = -1
        

# Biến bom thành xanh khi thắng
def turn_bombs_green():
    for (hang, cot), btn in buttons.items():
        if field[hang][cot] == 1:
            btn.config(bg='green')

# Xử lý click trái
def on_click(hang, cot):
    global first_click, start_time, attempts, score
    if game_over:
        return
    if first_click:
        start_time = time.time()
        reveal_first(hang, cot)
        first_click = False
    else:
        if field[hang][cot] == 1:
            reveal_bomb(hang, cot)
        else:
            reveal_tile(hang, cot)
    score = sum(btn['state'] == 'disabled' for btn in buttons.values())
    update_stats()
    check_win()

# Xử lý click phải (cắm/gỡ cờ)
def on_right_click(hang, cot):
    if game_over:
        return
    btn = buttons[(hang, cot)]
    if btn['state'] == 'disabled':
        return
    if btn.cget('text') == 'F':
        btn.config(text="")
    else:
        btn.config(text="F", fg="red", font=("Courier", 14, "bold"))

# Chơi lại
def replay():
    global buttons, field, first_click, game_over, win, start_time, attempts, score
    for widget in root.winfo_children():
        widget.destroy()
    buttons = {}
    field = []
    first_click = True
    game_over = False
    win = False
    start_time = None
    attempts = attempts + 1
    score = 0
    main()

# Thoát game
def quit_game():
    root.destroy()

# Bắt đầu game chính
def main():
    global root, field
    setup_screen()
    field = create_field(rows, columns)
    create_buttons(rows, columns)
    create_stats_area()



# Thiết lập game
def setup_game():
    global root
    root = tk.Tk()
    root.title("Minesweeper Chaos")
    main()
    root.mainloop()

# Bắt đầu từ cửa sổ Run
start_window()
