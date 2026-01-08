from PIL import Image, ImageDraw

def draw_icon(size):
    """Рисует минималистичное изображение орла в круге с валькнутом в центре груди."""
    # Создаем RGB изображение с белым/светлым фоном
    img = Image.new("RGB", (size, size), (255, 255, 255))  # Белый фон
    draw = ImageDraw.Draw(img)
    
    # Вычисляем размеры с отступами (5% от размера с каждой стороны)
    padding = int(size * 0.05)
    circle_size = size - (padding * 2)
    
    # Координаты для круга (центрированный)
    center_x = size // 2
    center_y = size // 2
    radius = circle_size // 2
    
    # Рисуем круг (граница)
    circle_coords = [
        center_x - radius,
        center_y - radius,
        center_x + radius,
        center_y + radius
    ]
    
    # Темно-синий/черный цвет для круга
    circle_color = (30, 30, 60)
    draw.ellipse(circle_coords, outline=circle_color, width=max(2, size // 64))
    
    # Рисуем стилизованного орла
    # Голова орла (вверху)
    head_y = center_y - radius * 0.3
    head_radius = radius * 0.15
    head_coords = [
        center_x - head_radius,
        head_y - head_radius,
        center_x + head_radius,
        head_y + head_radius
    ]
    draw.ellipse(head_coords, fill=circle_color)
    
    # Клюв (треугольник)
    beak_size = head_radius * 0.6
    beak_points = [
        (center_x, head_y + head_radius * 0.3),
        (center_x - beak_size * 0.5, head_y + head_radius * 0.8),
        (center_x + beak_size * 0.5, head_y + head_radius * 0.8)
    ]
    draw.polygon(beak_points, fill=(255, 200, 0))  # Золотистый клюв
    
    # Тело орла (овал)
    body_width = radius * 0.5
    body_height = radius * 0.6
    body_coords = [
        center_x - body_width,
        head_y + head_radius,
        center_x + body_width,
        center_y + radius * 0.2
    ]
    draw.ellipse(body_coords, fill=circle_color)
    
    # Крылья (стилизованные)
    wing_width = radius * 0.4
    wing_height = radius * 0.3
    
    # Левое крыло
    left_wing_coords = [
        center_x - body_width - wing_width * 0.3,
        center_y - radius * 0.1,
        center_x - body_width + wing_width * 0.7,
        center_y + radius * 0.2
    ]
    draw.ellipse(left_wing_coords, fill=circle_color)
    
    # Правое крыло
    right_wing_coords = [
        center_x + body_width - wing_width * 0.7,
        center_y - radius * 0.1,
        center_x + body_width + wing_width * 0.3,
        center_y + radius * 0.2
    ]
    draw.ellipse(right_wing_coords, fill=circle_color)
    
    # Валькнут в центре груди орла
    valknut_center_y = center_y + radius * 0.05
    valknut_size = radius * 0.25
    
    # Валькнут - три переплетенных треугольника
    # Внешний треугольник
    triangle_size = valknut_size
    triangle_points = [
        (center_x, valknut_center_y - triangle_size * 0.87),  # Верхняя точка
        (center_x - triangle_size, valknut_center_y + triangle_size * 0.43),  # Левая нижняя
        (center_x + triangle_size, valknut_center_y + triangle_size * 0.43)  # Правая нижняя
    ]
    draw.polygon(triangle_points, outline=(255, 255, 255), width=max(2, size // 128))
    
    # Внутренние переплетения (упрощенный валькнут)
    inner_size = triangle_size * 0.6
    # Верхний внутренний треугольник
    inner_triangle1 = [
        (center_x, valknut_center_y - inner_size * 0.5),
        (center_x - inner_size * 0.5, valknut_center_y + inner_size * 0.25),
        (center_x + inner_size * 0.5, valknut_center_y + inner_size * 0.25)
    ]
    draw.polygon(inner_triangle1, outline=(255, 255, 255), width=max(1, size // 128))
    
    # Переплетение - линии, соединяющие вершины
    line_width = max(1, size // 128)
    # Линия от верхней точки к левой нижней
    draw.line(
        [(center_x, valknut_center_y - triangle_size * 0.87),
         (center_x - inner_size * 0.5, valknut_center_y + inner_size * 0.25)],
        fill=(255, 255, 255), width=line_width
    )
    # Линия от верхней точки к правой нижней
    draw.line(
        [(center_x, valknut_center_y - triangle_size * 0.87),
         (center_x + inner_size * 0.5, valknut_center_y + inner_size * 0.25)],
        fill=(255, 255, 255), width=line_width
    )
    
    return img

# Размеры иконки
sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
icons = [draw_icon(s) for s, _ in sizes]

# Изображения уже в RGB режиме, просто убеждаемся
rgb_icons = []
for icon in icons:
    # Убеждаемся, что изображение в RGB режиме (не палитра)
    if icon.mode != "RGB":
        rgb_img = icon.convert("RGB")
    else:
        rgb_img = icon
    rgb_icons.append(rgb_img)

# Сохранение с явным указанием формата и цветов
# ВАЖНО: Изображения уже в RGB режиме с красным фоном, что гарантирует
# сохранение цветов и избегает автоматической конвертации в градации серого
try:
    rgb_icons[0].save(
        "app.ico",
        format="ICO",
        sizes=sizes,
        append_images=rgb_icons[1:]
    )
    print("OK: Иконка 'app.ico' создана!")
    print("   Дизайн: минималистичный орел в круге с валькнутом на груди")
    print("   Цвета: белый фон, темно-синий орел, золотистый клюв, белый валькнут")
except Exception as e:
    print(f"ОШИБКА при сохранении: {e}")
    # Альтернативный способ - сохранить каждое изображение отдельно
    print("Попытка альтернативного метода сохранения...")
    rgb_icons[0].save("app.ico", format="ICO")
    print("OK: Иконка 'app.ico' создана (только один размер)")