import re
import subprocess
from pathlib import Path

# новый стиль линии
line_style = {
    "stroke": "#880E4F",
    "stroke-width": "4",
}


def apply_style(svg: str, targets: list[str], style: dict[str, str]) -> str:
    """Применяем новый стиль к элементам с id из targets

    Args:
        svg (str): исходные данные svg
        targets (list[str]): список id для изменения стиля
        style (dict[str, str]): новый стиль

    Returns:
        str: svg с новыми стилями.
    """
    for element_id in targets:
        # Ищем SVG-элемент с указанным id
        pattern = re.compile(
            r'<(path|line|polyline|polygon)\b'
            r'(?=[^>]*\bid="' + re.escape(element_id) + r'")'
            r'[^>]*>',
            re.DOTALL,
        )
        def update(match):
            tag = match.group(0)

            # Меняем свойства в inline style
            style_match = re.search(
                r'\bstyle="([^"]*)"', tag
            )

            properties = {}
            if style_match:
                for item in style_match.group(1).split(";"):
                    if ":" in item:
                        key, value = item.split(":", 1)
                        properties[key.strip()] = value.strip()

            properties.update(style)

            new_style = ";".join(
                f"{key}:{value}"
                for key, value in properties.items()
            )

            if style_match:
                return tag[:style_match.start(1)] + \
                    new_style + tag[style_match.end(1):]

            return tag[:-1] + f' style="{new_style}">'

        svg = pattern.sub(update, svg)
    return svg


# pattern полного участия
full_pattern = re.compile(r"^(\w+)\s*=N=\s*(\w+)")


def get_patch_ids(text: str) -> list[str]:
    """Поиск id линий полного участия 

    Args:
        text (str): данные puml файла

    Returns:
        list[str]: список id, которые будут в svg файле.
    """
    res = []
    for line in text.splitlines():
        match = full_pattern.search(line.strip())
        if match:
            lab1 = match.group(1)
            lab2 = match.group(2)
            res.append(f'{lab1}-{lab2}')
    return res


def convert_puml(text: str) -> str:
    """Конвертирует текст puml в svg.

    Args:
        text (str): исходный puml

    Returns:
        str: сгенерированный svg
    """

    result = subprocess.run(
        ['plantuml.exe', '-f', 'svg', '-pipe'],
        input=text,                      # Передаем обычную строку
        text=True,                       # Включаем текстовый режим для потоков
        encoding='utf-8',                # Указываем кодировку для авто-кодирования
        capture_output=True,
        check=True
    )

    return result.stdout


def process_puml():
    work_dir = Path(__file__).parent.resolve()
    for puml_path in work_dir.glob('*.puml'):
        print(f'processing: {puml_path}')
        puml_text = puml_path.read_text(encoding='utf8')
        patch_ids = get_patch_ids(puml_text)
        svg_text = convert_puml(puml_text)
        svg_text = apply_style(svg_text, patch_ids, line_style)
        (puml_path.parent / '../img' / puml_path.name).with_suffix('.svg').write_text(svg_text, encoding='utf8')


if __name__ == '__main__':
    process_puml()
