import tkinter as tk
from tkinter import ttk, simpledialog
import pygetwindow as gw
import pywinauto
import time
import threading

# Начальные значения для интервалов времени и команд
commands = {
    '!work': {'interval': 300, 'additional': ['!dep all']},
    '!collect': {'interval': 900, 'additional': ['!dep all']}
}
running = False  # Флаг, указывающий на активность фарминга
target_window = None  # Переменная для хранения выбранного окна

def send_message(message):
    """Отправляем сообщение в указанное окно."""
    try:
        # Проверяем, выбрано ли окно
        if target_window is None:
            raise Exception("Окно не выбрано")

        # Используем pywinauto для активации окна и ввода текста
        app = pywinauto.Application().connect(handle=target_window)
        window = app.window(handle=target_window)
        window.set_focus()
        window.type_keys(message + '{ENTER}')
        print(f'{message} отправлено в окно с handle {target_window}')
    except Exception as e:
        print(f'Ошибка при отправке сообщения: {e}')
    time.sleep(0.5)  # Небольшая задержка для корректной отправки сообщений

def afk_farm():
    """Функция для выполнения команд по расписанию."""
    global running
    last_times = {cmd: time.time() for cmd in commands}

    while running:
        current_time = time.time()
        for cmd, data in commands.items():
            if current_time - last_times[cmd] >= data['interval']:
                send_message(cmd)
                for add_cmd in data['additional']:
                    send_message(add_cmd)
                last_times[cmd] = current_time

        update_timers(current_time, last_times)
        time.sleep(1)

def start_farming():
    """Запуск процесса фарминга в отдельном потоке."""
    global running
    running = True
    threading.Thread(target=afk_farm, daemon=True).start()
    switch_to_farming_screen()

def stop_farming():
    """Остановить процесс фарминга."""
    global running
    running = False

def switch_to_farming_screen():
    """Переключение на экран фарминга."""
    hide_all_frames()
    farming_frame.pack()

def switch_to_main_menu():
    """Переключение на главное меню."""
    hide_all_frames()
    main_frame.pack()

def open_settings():
    """Открыть меню настроек."""
    hide_all_frames()
    settings_frame.pack()

def open_command_settings():
    """Открыть меню редактирования команд."""
    hide_all_frames()
    command_settings_frame.pack()

def select_target_window():
    """Выбрать целевое окно для отправки сообщений."""
    global target_window
    selected_title = window_combobox.get()

    if selected_title:
        windows = gw.getWindowsWithTitle(selected_title)
        if windows:
            target_window = windows[0]._hWnd  # Используем _hWnd вместо hwnd
            print(f'Вы выбрали окно: {selected_title} с handle {target_window}')
        else:
            print("Окно не найдено.")
    else:
        print("Окно не выбрано.")

def add_new_command():
    """Добавить новую команду."""
    cmd = simpledialog.askstring("Новая команда", "Введите основную команду:")
    if cmd:
        commands[cmd] = {'interval': 60, 'additional': []}
        edit_command(cmd)

def edit_command(cmd):
    """Редактировать существующую команду."""
    def save_command():
        commands[cmd]['additional'] = additional_commands.get().split(';')
        commands[cmd]['interval'] = int(interval_entry.get())
        edit_command_window.destroy()
        update_command_list()

    def delete_command():
        if cmd in commands:
            del commands[cmd]
        edit_command_window.destroy()
        update_command_list()

    edit_command_window = tk.Toplevel(root)
    edit_command_window.title(f"Редактирование команды: {cmd}")

    tk.Label(edit_command_window, text="Основная команда:").pack(pady=5)
    tk.Label(edit_command_window, text=cmd).pack(pady=5)

    tk.Label(edit_command_window, text="Дополнительные команды (через ;):").pack(pady=5)
    additional_commands = tk.Entry(edit_command_window)
    additional_commands.insert(0, ";".join(commands[cmd]['additional']))
    additional_commands.pack(pady=5)

    tk.Label(edit_command_window, text="Интервал (секунды):").pack(pady=5)
    interval_entry = tk.Entry(edit_command_window)
    interval_entry.insert(0, str(commands[cmd]['interval']))
    interval_entry.pack(pady=5)

    tk.Button(edit_command_window, text="Сохранить", command=save_command).pack(pady=5)
    tk.Button(edit_command_window, text="Удалить команду", command=delete_command).pack(pady=5)

def update_command_list():
    """Обновить список команд."""
    for widget in command_list_frame.winfo_children():
        widget.destroy()

    for cmd in commands:
        tk.Button(command_list_frame, text=cmd, command=lambda c=cmd: edit_command(c)).pack(fill='x')

def update_timers(current_time, last_times):
    """Обновить таймеры на экране."""
    for widget in farming_frame.winfo_children():
        widget.destroy()

    tk.Label(farming_frame, text="SekyndaAfk фарминг...", font=("Arial", 18)).pack(pady=10)

    for cmd, data in commands.items():
        time_left = max(0, data['interval'] - (current_time - last_times[cmd]))
        tk.Label(farming_frame, text=f"До следующего {cmd}: {int(time_left)} секунд").pack(pady=5)

    tk.Button(farming_frame, text="Главное меню", command=lambda: [stop_farming(), switch_to_main_menu()]).pack(pady=5, fill='x')

def open_time_settings():
    """Открыть меню редактирования времени."""
    hide_all_frames()
    time_settings_frame.pack()
    update_time_settings()

def save_time_settings():
    """Сохранить настройки времени."""
    for cmd, data in commands.items():
        interval_entry = time_entries[cmd]
        commands[cmd]['interval'] = int(interval_entry.get())
    switch_to_main_menu()

def update_time_settings():
    """Обновить список команд и их времени в настройках времени."""
    for widget in time_settings_list_frame.winfo_children():
        widget.destroy()

    global time_entries
    time_entries = {}
    
    for cmd, data in commands.items():
        tk.Label(time_settings_list_frame, text=f"Команда: {cmd}").pack(pady=5)
        interval_entry = tk.Entry(time_settings_list_frame)
        interval_entry.insert(0, str(data['interval']))
        interval_entry.pack(pady=5)
        time_entries[cmd] = interval_entry

def change_theme(theme):
    """Изменить тему интерфейса."""
    theme_colors = {
        'blue': ('#0078d4', '#005a9e'),
        'red': ('#e57373', '#c62828'),
        'green': ('#81c784', '#388e3c'),
        'orange': ('#ffb74d', '#f57c00'),
        'pink': ('#f48fb1', '#d81b60'),
        'purple': ('#9575cd', '#512da8'),
        'yellow': ('#fff176', '#fbc02d'),
        'gray': ('#bdbdbd', '#757575')
    }
    
    bg_color, button_color = theme_colors.get(theme, ('#f0f0f0', '#0078d4'))
    
    root.configure(bg=bg_color)
    style.configure('TButton',
                    background=button_color,
                    foreground='#000000')
    style.map('TButton',
              background=[('active', button_color)])
    main_frame.configure(style='TFrame', background=bg_color)
    settings_frame.configure(style='TFrame', background=bg_color)
    farming_frame.configure(style='TFrame', background=bg_color)
    theme_frame.configure(style='TFrame', background=bg_color)
    command_settings_frame.configure(style='TFrame', background=bg_color)
    time_settings_frame.configure(style='TFrame', background=bg_color)

def hide_all_frames():
    """Скрыть все панели."""
    main_frame.pack_forget()
    settings_frame.pack_forget()
    command_settings_frame.pack_forget()
    time_settings_frame.pack_forget()
    farming_frame.pack_forget()
    theme_frame.pack_forget()

# Создание главного окна
root = tk.Tk()
root.title("SekyndaAfk")
root.geometry("450x400")  # Размер окна

# Настройка стиля
style = ttk.Style()
style.configure("TButton",
                padding=6,
                relief="flat",
                background="#0078d4",
                foreground="#000000",
                font=("Arial", 12))
style.configure("TLabel",
                background="#f0f0f0",
                font=("Arial", 12))
style.configure("TFrame",
                background="#f0f0f0")

# Главная панель
main_frame = ttk.Frame(root, padding="10", relief="sunken")
main_frame.pack(fill="both", expand=True)

ttk.Label(main_frame, text="SekyndaAfk", font=("Arial", 18)).pack(pady=10)

# Создаем выпадающий список для выбора окна
window_list = [window.title for window in gw.getAllWindows()]
window_combobox = ttk.Combobox(main_frame, values=window_list)
window_combobox.pack(pady=5, fill='x')
window_combobox.set("Выберите окно...")

ttk.Button(main_frame, text="Начать AFK FARM", command=start_farming).pack(pady=5, fill='x')
ttk.Button(main_frame, text="Выбрать окно", command=select_target_window).pack(pady=5, fill='x')
ttk.Button(main_frame, text="Редактировать настройки", command=open_settings).pack(pady=5, fill='x')
ttk.Button(main_frame, text="Кастомизация", command=lambda: [hide_all_frames(), theme_frame.pack()]).pack(pady=5, fill='x')

# Панель настроек
settings_frame = ttk.Frame(root, padding="10", relief="sunken")

ttk.Label(settings_frame, text="SekyndaAfk", font=("Arial", 18)).pack(pady=10)
ttk.Button(settings_frame, text="Команды", command=open_command_settings).pack(pady=5, fill='x')
ttk.Button(settings_frame, text="Время", command=open_time_settings).pack(pady=5, fill='x')
ttk.Button(settings_frame, text="Главное меню", command=switch_to_main_menu).pack(pady=5, fill='x')

# Панель кастомизации темы
theme_frame = ttk.Frame(root, padding="10", relief="sunken")

ttk.Label(theme_frame, text="Кастомизация", font=("Arial", 18)).pack(pady=10)

themes = ['blue', 'red', 'green', 'orange', 'pink', 'purple', 'yellow', 'gray']
for theme in themes:
    ttk.Button(theme_frame, text=theme.capitalize(), command=lambda t=theme: change_theme(t)).pack(pady=5, fill='x')

ttk.Button(theme_frame, text="Главное меню", command=switch_to_main_menu).pack(pady=5, fill='x')

# Панель редактирования команд
command_settings_frame = ttk.Frame(root, padding="10", relief="sunken")

ttk.Label(command_settings_frame, text="Редактирование команд", font=("Arial", 18)).pack(pady=10)

command_list_frame = ttk.Frame(command_settings_frame)
command_list_frame.pack(pady=5, fill='x')

update_command_list()
ttk.Button(command_settings_frame, text="Добавить команду", command=add_new_command).pack(pady=5, fill='x')
ttk.Button(command_settings_frame, text="Главное меню", command=switch_to_main_menu).pack(pady=5, fill='x')

# Панель редактирования времени
time_settings_frame = ttk.Frame(root, padding="10", relief="sunken")

ttk.Label(time_settings_frame, text="Редактирование времени команд", font=("Arial", 18)).pack(pady=10)

time_settings_list_frame = ttk.Frame(time_settings_frame)
time_settings_list_frame.pack(pady=5, fill='x')

ttk.Button(time_settings_frame, text="Сохранить", command=save_time_settings).pack(pady=5, fill='x')
ttk.Button(time_settings_frame, text="Главное меню", command=switch_to_main_menu).pack(pady=5, fill='x')

# Панель фарминга
farming_frame = ttk.Frame(root, padding="10", relief="sunken")

ttk.Label(farming_frame, text="SekyndaAfk фарминг...", font=("Arial", 18)).pack(pady=10)
ttk.Button(farming_frame, text="Главное меню", command=lambda: [stop_farming(), switch_to_main_menu()]).pack(pady=5, fill='x')

# Запуск главного цикла обработки событий
root.mainloop()