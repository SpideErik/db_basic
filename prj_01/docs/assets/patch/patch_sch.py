from pathlib import Path
import re

# 1. Описание стилей
STYLES = {
    "bold": {
        "stroke": "#880E4F",
        "stroke-width": "4",
    },
}

# 2. Списки связей для каждого стиля
STYLE_TARGETS = {
    "bold": ["R_WORKS-EMP", "R_HOLDS-EMP", "R_SICK-SICK", "R_OPEN-VAC", "R_FOR-VAC", "R_INTER-INTV", "R_LEAVE-LEAVE", "R_HIST-HIST", "R_RECV-CV", "R_PASS-INTV"],
}


def apply_styles(svg: str) -> str:
    for style_name, element_ids in STYLE_TARGETS.items():
        style = STYLES[style_name]

        for element_id in element_ids:
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


source = Path("sch.svg")
destination = Path("sch_styled.svg")

svg_text = source.read_text(encoding="utf-8")
destination.write_text(
    apply_styles(svg_text),
    encoding="utf-8",
)

print(f"Сохранено: {destination}")
