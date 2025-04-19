import tkinter as tk
import math
import sys

# Скрытие консоли на Windows
if sys.platform.startswith("win"):
    try:
        import ctypes
        whnd = ctypes.windll.kernel32.GetConsoleWindow()
        if whnd:
            ctypes.windll.user32.ShowWindow(whnd, 0)  # 0 = SW_HIDE
    except Exception:
        pass

# Функция линейной интерполяции между двумя цветами (RGB)
def interpolate_color(c1, c2, factor):
    return (
        int(c1[0] + (c2[0] - c1[0]) * factor),
        int(c1[1] + (c2[1] - c1[1]) * factor),
        int(c1[2] + (c2[2] - c1[2]) * factor)
    )

# Преобразование RGB в hex-строку
def rgb_to_hex(rgb):
    return "#%02x%02x%02x" % rgb

# Контрольные точки градиента (от красного к красному)
gradient_stops = [
    (0.0, (255, 0, 0)),
    (1/7, (255, 165, 0)),
    (2/7, (255, 255, 0)),
    (3/7, (0, 255, 0)),
    (4/7, (0, 0, 255)),
    (5/7, (75, 0, 130)),
    (6/7, (238, 130, 238)),
    (1.0, (255, 0, 0))
]

def get_gradient_color(frac):
    """Возвращает цвет по градиенту для значения frac от 0 до 1."""
    for i in range(len(gradient_stops) - 1):
        start_frac, start_color = gradient_stops[i]
        end_frac, end_color = gradient_stops[i+1]
        if start_frac <= frac < end_frac or (frac == 1.0 and i == len(gradient_stops) - 2):
            local_frac = (frac - start_frac) / (end_frac - start_frac)
            interpolated = interpolate_color(start_color, end_color, local_frac)
            return rgb_to_hex(interpolated)
    return rgb_to_hex(gradient_stops[-1][1])

# Настройка главного окна
root = tk.Tk()
root.overrideredirect(True)           # Убираем стандартные рамки и заголовок
root.attributes("-topmost", True)       # Окно всегда поверх остальных
transparent_color = "magenta"           # Этот цвет будет прозрачным
root.config(bg=transparent_color)
root.wm_attributes("-transparentcolor", transparent_color)
root.geometry("400x400")

canvas = tk.Canvas(root, width=400, height=400,
                   bg=transparent_color, highlightthickness=0)
canvas.pack()

# Отрисовка радужного градиентного пончика
bbox = (50, 50, 350, 350)   # Область внешнего круга
step = 2                    # Шаг в градусах (чем меньше — тем плавнее)
for angle in range(0, 360, step):
    frac = angle / 360.0
    color = get_gradient_color(frac)
    canvas.create_arc(bbox, start=angle, extent=step,
                      fill=color, outline=color, style=tk.PIESLICE)

# Отрисовка прозрачного внутреннего отверстия пончика
canvas.create_oval(125, 125, 275, 275,
                   fill=transparent_color, outline=transparent_color)

# ---------------------------
# Параметры для глаз
eye_radius = 20        # Номинальный радиус белой области глаза
pupil_radius = 8       # Номинальный радиус зрачка
max_offset = eye_radius - pupil_radius  # Максимальное смещение зрачка

# Центры глаз (левый и правый) внутри отверстия пончика
left_eye_center = (175, 200)
right_eye_center = (225, 200)

# Рисуем белые области глаз с чёрной окантовкой
left_eye = canvas.create_oval(
    left_eye_center[0] - eye_radius, left_eye_center[1] - eye_radius,
    left_eye_center[0] + eye_radius, left_eye_center[1] + eye_radius,
    fill="white", outline="black", width=2
)
right_eye = canvas.create_oval(
    right_eye_center[0] - eye_radius, right_eye_center[1] - eye_radius,
    right_eye_center[0] + eye_radius, right_eye_center[1] + eye_radius,
    fill="white", outline="black", width=2
)

# Данные для зрачков (начальное положение – в центре глаз)
eyes = [
    {'center': left_eye_center, 'pupil_id': None, 'offset_x': 0.0, 'offset_y': 0.0},
    {'center': right_eye_center, 'pupil_id': None, 'offset_x': 0.0, 'offset_y': 0.0}
]

eyes[0]['pupil_id'] = canvas.create_oval(
    left_eye_center[0] - pupil_radius, left_eye_center[1] - pupil_radius,
    left_eye_center[0] + pupil_radius, left_eye_center[1] + pupil_radius,
    fill="black"
)
eyes[1]['pupil_id'] = canvas.create_oval(
    right_eye_center[0] - pupil_radius, right_eye_center[1] - pupil_radius,
    right_eye_center[0] + pupil_radius, right_eye_center[1] + pupil_radius,
    fill="black"
)

# Добавляем «блик» на зрачки для эффекта блеска
pupil_highlight_radius = 2
for eye in eyes:
    cx, cy = eye["center"]
    hl = canvas.create_oval(
        cx - pupil_radius/2 - pupil_highlight_radius,
        cy - pupil_radius/2 - pupil_highlight_radius,
        cx - pupil_radius/2 + pupil_highlight_radius,
        cy - pupil_radius/2 + pupil_highlight_radius,
        fill="white", outline=""
    )
    eye["highlight_id"] = hl

# Переменная, характеризующая «открытость» глаз:
# 1.0 – полностью открыты, 0.0 – полностью закрыты.
eye_openness = 1.0

def update_eyes():
    global eye_openness
    # Получаем координаты курсора относительно окна
    mouse_x = root.winfo_pointerx() - root.winfo_rootx()
    mouse_y = root.winfo_pointery() - root.winfo_rooty()
    
    # Если курсор внутри отверстия пончика (центр (200,200), радиус 75), target_openness = 0.0 (полное закрытие),
    # иначе target_openness = 1.0 (полностью открыты).
    dx_donut = mouse_x - 200
    dy_donut = mouse_y - 200
    if math.hypot(dx_donut, dy_donut) < 75:
        target_openness = 0.0
    else:
        target_openness = 1.0
        
    # Увеличиваем сглаживание (закрытие происходит быстрее)
    smoothing = 0.2
    eye_openness += smoothing * (target_openness - eye_openness)
    
    # Обновляем форму белых областей глаз: фиксированная ширина, новая высота = 2*eye_radius*eye_openness
    new_left_eye = (left_eye_center[0] - eye_radius,
                    left_eye_center[1] - eye_openness * eye_radius,
                    left_eye_center[0] + eye_radius,
                    left_eye_center[1] + eye_openness * eye_radius)
    new_right_eye = (right_eye_center[0] - eye_radius,
                     right_eye_center[1] - eye_openness * eye_radius,
                     right_eye_center[0] + eye_radius,
                     right_eye_center[1] + eye_openness * eye_radius)
    canvas.coords(left_eye, *new_left_eye)
    canvas.coords(right_eye, *new_right_eye)
    
    # Если глаза почти закрыты, зрачки остаются в центре
    for eye in eyes:
        ex, ey = eye["center"]
        if eye_openness < 0.7:
            desired_offset_x = 0
            desired_offset_y = 0
        else:
            dx = mouse_x - ex
            dy = mouse_y - ey
            dist = math.hypot(dx, dy)
            if dist > 0:
                if dist > max_offset:
                    desired_offset_x = dx / dist * max_offset
                    desired_offset_y = dy / dist * max_offset
                else:
                    desired_offset_x = dx
                    desired_offset_y = dy
            else:
                desired_offset_x, desired_offset_y = 0, 0
        eye["offset_x"] += 0.15 * (desired_offset_x - eye["offset_x"])
        eye["offset_y"] += 0.15 * (desired_offset_y - eye["offset_y"])
        new_cx = ex + eye["offset_x"]
        new_cy = ey + eye["offset_y"]
        effective_pupil_radius = pupil_radius * eye_openness
        canvas.coords(eye["pupil_id"],
                      new_cx - effective_pupil_radius, new_cy - effective_pupil_radius,
                      new_cx + effective_pupil_radius, new_cy + effective_pupil_radius)
        effective_hl_radius = pupil_highlight_radius * eye_openness
        hl_center_x = new_cx - (pupil_radius/2 * eye_openness)
        hl_center_y = new_cy - (pupil_radius/2 * eye_openness)
        canvas.coords(eye["highlight_id"],
                      hl_center_x - effective_hl_radius, hl_center_y - effective_hl_radius,
                      hl_center_x + effective_hl_radius, hl_center_y + effective_hl_radius)
    root.after(20, update_eyes)

update_eyes()

# ---------------------------
# Функции для перетаскивания окна
def start_move(event):
    global offset_x, offset_y
    offset_x = event.x
    offset_y = event.y

def do_move(event):
    x = root.winfo_pointerx() - offset_x
    y = root.winfo_pointery() - offset_y
    root.geometry(f'+{x}+{y}')

canvas.bind("<ButtonPress-1>", start_move)
canvas.bind("<B1-Motion>", do_move)

root.mainloop()
