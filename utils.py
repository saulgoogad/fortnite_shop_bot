import io
import requests
from PIL import Image, ImageDraw, ImageFont

FONT_PATH = "fonts/DejaVuSans-Bold.ttf"

def download_image(url):
    try:
        r = requests.get(url)
        r.raise_for_status()
        return Image.open(io.BytesIO(r.content)).convert("RGBA")
    except Exception:
        return Image.new("RGBA", (64,64), (200,200,200,255))

def wrap_text(text, font, max_width):
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        if font.getsize(test_line)[0] <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines

def generate_shop_image(shop_data):
    categories = shop_data  # список категорий с товарами

    width = 1000
    padding = 20
    category_spacing = 40
    item_spacing = 10
    icon_size = 64
    text_color = (0, 0, 0)
    bg_color = (255, 255, 255)
    title_font = ImageFont.truetype(FONT_PATH, 36)
    item_font = ImageFont.truetype(FONT_PATH, 20)
    price_font = ImageFont.truetype(FONT_PATH, 18)

    # Вычисляем высоту: грубо, чтобы уместить все
    height = padding
    for cat in categories:
        height += title_font.getsize(cat['name'])[1] + category_spacing
        # каждый предмет занимает высоту icon_size + text + item_spacing
        height += len(cat['entries']) * (icon_size + item_spacing)

    image = Image.new("RGBA", (width, height), bg_color)
    draw = ImageDraw.Draw(image)

    y = padding

    for cat in categories:
        draw.text((padding, y), cat['name'], font=title_font, fill=text_color)
        y += title_font.getsize(cat['name'])[1] + 10

        for entry in cat['entries']:
            item = entry['items'][0]
            name = item['name']
            price = entry['finalPrice']
            img_url = item['images']['icon']

            icon = download_image(img_url).resize((icon_size, icon_size))

            image.paste(icon, (padding, y), icon)

            # текст с переносом, если длинное название
            max_text_width = width - padding * 2 - icon_size - 100
            lines = wrap_text(name, item_font, max_text_width)

            text_x = padding + icon_size + 10
            text_y = y
            for line in lines:
                draw.text((text_x, text_y), line, font=item_font, fill=text_color)
                text_y += item_font.getsize(line)[1] + 2

            # цена справа
            price_text = f"{price} V-Bucks"
            price_size = price_font.getsize(price_text)
            price_x = width - padding - price_size[0]
            price_y = y + (icon_size - price_size[1]) // 2
            draw.text((price_x, price_y), price_text, font=price_font, fill=text_color)

            y += icon_size + item_spacing

        y += category_spacing - item_spacing  # дополнительный отступ после категории

    # Сохраняем в BytesIO
    bio = io.BytesIO()
    image.convert("RGB").save(bio, format="JPEG", quality=90)
    bio.seek(0)
    return bio
