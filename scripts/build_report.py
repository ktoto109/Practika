"""Сборка отчёта по учебной практике для проекта Sarro Orbital Mining."""

import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "static" / "design" / "report_assets"
ASSETS.mkdir(parents=True, exist_ok=True)
TEMP = Path(os.environ.get("TEMP", str(ROOT)))
REPORT_PATH = ROOT / "Otchet_Sarro.docx"

FONT_REGULAR = "C:/Windows/Fonts/arial.ttf"
FONT_BOLD = "C:/Windows/Fonts/arialbd.ttf"


# ---------------------------------------------------------------------------
# Диаграммы
# ---------------------------------------------------------------------------

def font(size: int, bold: bool = False):
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REGULAR, size)


def draw_arrow(draw, points, label=None, label_xy=None, color="black"):
    draw.line(points, fill=color, width=3)
    x1, y1 = points[-2]
    x2, y2 = points[-1]
    dx, dy = x2 - x1, y2 - y1
    length = max((dx * dx + dy * dy) ** 0.5, 1)
    ux, uy = dx / length, dy / length
    px, py = -uy, ux
    size = 16
    p1 = (x2, y2)
    p2 = (x2 - ux * size + px * size * 0.55, y2 - uy * size + py * size * 0.55)
    p3 = (x2 - ux * size - px * size * 0.55, y2 - uy * size - py * size * 0.55)
    draw.polygon([p1, p2, p3], fill=color)
    if label and label_xy:
        draw.text(label_xy, label, font=font(20), fill=color)


def entity(draw, x, y, w, title, fields):
    header_h = 50
    row_h = 30
    h = header_h + row_h * len(fields) + 18
    draw.rectangle([x, y, x + w, y + h], fill="white", outline="black", width=3)
    draw.rectangle([x, y, x + w, y + header_h], fill="#E6E6E6", outline="black", width=3)
    draw.text((x + 14, y + 11), title, font=font(26, True), fill="black")
    yy = y + header_h + 8
    for field in fields:
        draw.text((x + 14, yy), field, font=font(20), fill="black")
        yy += row_h
    return x, y, w, h


def make_er_diagram():
    image = Image.new("RGB", (1800, 980), "white")
    d = ImageDraw.Draw(image)

    user = entity(d, 60, 60, 360, "User", [
        "id (PK)", "username", "email", "password", "is_staff", "is_superuser",
    ])
    profile = entity(d, 60, 430, 360, "Profile", [
        "id (PK)", "user_id (FK)", "balance",
    ])
    order = entity(d, 650, 60, 460, "Order", [
        "id (PK)", "user_id (FK)", "asteroid_id (FK)",
        "code", "status", "created_at",
    ])
    asteroid = entity(d, 650, 410, 460, "Asteroid", [
        "id (PK)", "title", "description", "price", "distance",
        "image", "spectral_class_id (FK)", "status", "is_sold", "created_at",
    ])
    spectral = entity(d, 1280, 60, 420, "SpectralClass", ["id (PK)", "name"])
    composition = entity(d, 1280, 410, 420, "Composition", ["id (PK)", "name"])
    link = entity(d, 1280, 660, 420, "AsteroidComposition", [
        "id (PK)", "asteroid_id (FK)", "composition_id (FK)",
    ])

    draw_arrow(d, [(420, 220), (650, 220)], "1:N", (515, 185))
    draw_arrow(d, [(880, 330), (880, 410)], "1:N", (900, 355))
    draw_arrow(d, [(240, 330), (240, 430)], "1:1", (260, 370))
    draw_arrow(d, [(1490, 200), (1490, 330), (1120, 330), (1120, 410)], "1:N", (1370, 300))
    draw_arrow(d, [(1110, 620), (1280, 700)], "1:N", (1150, 640))
    draw_arrow(d, [(1490, 550), (1490, 660)], "1:N", (1510, 595))

    image.save(ASSETS / "er_diagram.png")


def box(draw, x, y, w, h, text, fill="white", rounded=False, size=22):
    if rounded:
        draw.rounded_rectangle([x, y, x + w, y + h], radius=28, fill=fill, outline="black", width=3)
    else:
        draw.rectangle([x, y, x + w, y + h], fill=fill, outline="black", width=3)
    lines = text.split("\n")
    f = font(size)
    heights = [draw.textbbox((0, 0), line, font=f)[3] for line in lines]
    total = sum(heights) + (len(lines) - 1) * 6
    yy = y + (h - total) / 2 - 2
    for line, line_h in zip(lines, heights):
        bbox = draw.textbbox((0, 0), line, font=f)
        tw = bbox[2] - bbox[0]
        draw.text((x + (w - tw) / 2, yy), line, font=f, fill="black")
        yy += line_h + 6


def diamond(draw, cx, cy, w, h, text):
    points = [(cx, cy - h / 2), (cx + w / 2, cy), (cx, cy + h / 2), (cx - w / 2, cy)]
    draw.polygon(points, fill="white", outline="black", width=3)
    f = font(22)
    bbox = draw.multiline_textbbox((0, 0), text, font=f, spacing=6, align="center")
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.multiline_text((cx - tw / 2, cy - th / 2 - 2), text, font=f, fill="black", spacing=6, align="center")


def make_flow_diagram():
    image = Image.new("RGB", (1600, 1080), "white")
    d = ImageDraw.Draw(image)

    box(d, 650, 30, 300, 60, "Начало", rounded=True, size=24)
    box(d, 600, 140, 400, 60, "Ввод email и пароля", size=22)
    diamond(d, 800, 300, 260, 120, "Поля\nзаполнены?")
    box(d, 110, 270, 380, 60, "Показать ошибку", size=20)
    diamond(d, 800, 480, 260, 120, "Email\nсвободен?")
    box(d, 110, 450, 380, 60, "Ошибка: email занят", size=20)
    box(d, 600, 610, 400, 60, "Создать User и Profile", size=21)
    box(d, 600, 720, 400, 60, "Вход в систему", size=22)
    box(d, 600, 830, 400, 60, "Главная страница", size=22)
    box(d, 650, 950, 300, 60, "Конец", rounded=True, size=24)

    draw_arrow(d, [(800, 90), (800, 140)])
    draw_arrow(d, [(800, 200), (800, 240)])
    draw_arrow(d, [(670, 300), (490, 300)], "нет", (550, 265))
    draw_arrow(d, [(300, 330), (300, 380), (600, 380), (600, 170)], "вернуться", (320, 350))
    draw_arrow(d, [(800, 360), (800, 420)], "да", (815, 382))
    draw_arrow(d, [(670, 480), (490, 480)], "нет", (550, 445))
    draw_arrow(d, [(300, 510), (300, 570), (600, 570), (600, 170)], "вернуться", (320, 530))
    draw_arrow(d, [(800, 540), (800, 610)], "да", (815, 565))
    draw_arrow(d, [(800, 670), (800, 720)])
    draw_arrow(d, [(800, 780), (800, 830)])
    draw_arrow(d, [(800, 890), (800, 950)])

    image.save(ASSETS / "flow_diagram.png")


# ---------------------------------------------------------------------------
# Изображения
# ---------------------------------------------------------------------------

def prepare_image(source, target, width, crop=None):
    image = Image.open(source).convert("RGB")
    if crop:
        image = image.crop(crop)
    ratio = width / image.width
    image = image.resize((width, max(1, int(image.height * ratio))), Image.LANCZOS)
    image.save(target, "JPEG", quality=88, optimize=True)


def prepare_assets():
    make_er_diagram()
    make_flow_diagram()

    sources = {
        "design_general.jpg": (ROOT / "static/design/01_general.png", 1500, None),
        "design_catalog.jpg": (ROOT / "static/design/02_catalog.png", 1500, None),
        "design_profile.jpg": (ROOT / "static/design/06_profile.png", 1400, None),
        "design_admin.jpg": (ROOT / "static/design/07_admin.png", 1400, None),
        "design_mobile.jpg": (ROOT / "static/design/22_general-375px.png", 480, (0, 0, 750, 1900)),
        "impl_general.jpg": (TEMP / "report_general.png", 1500, None),
        "impl_catalog.jpg": (ROOT / "static/design/preview_catalog_images.png", 1500, None),
        "impl_card.jpg": (TEMP / "report_card.png", 1500, None),
        "impl_login.jpg": (TEMP / "report_login.png", 1500, None),
        "impl_register.jpg": (TEMP / "report_register.png", 1500, None),
        "impl_profile.jpg": (ROOT / "static/design/preview_profile.png", 1400, None),
        "impl_admin.jpg": (ROOT / "static/design/preview_admin.png", 1500, None),
        "impl_admin_form.jpg": (ROOT / "static/design/preview_admin_form.png", 1500, (560, 170, 1840, 1340)),
    }
    for target, (source, width, crop) in sources.items():
        prepare_image(source, ASSETS / target, width, crop)


# ---------------------------------------------------------------------------
# Документ
# ---------------------------------------------------------------------------

def set_run_font(run, name="Times New Roman", size=13, bold=False, italic=False, color=None):
    run.font.name = name
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    if color:
        run.font.color.rgb = RGBColor(*color)
    rpr = run._element.get_or_add_rPr()
    fonts = rpr.get_or_add_rFonts()
    for attr in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        fonts.set(qn(attr), name)


def body(doc, text, bold=False, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=13, first_indent=1.25,
         space_after=0, line_spacing=1.5):
    p = doc.add_paragraph()
    p.paragraph_format.alignment = align
    p.paragraph_format.first_line_indent = Cm(first_indent)
    p.paragraph_format.line_spacing = line_spacing
    p.paragraph_format.space_after = Pt(space_after)
    run = p.add_run(text)
    set_run_font(run, size=size, bold=bold)
    return p


def body_mixed(doc, parts, align=WD_ALIGN_PARAGRAPH.JUSTIFY):
    p = doc.add_paragraph()
    p.paragraph_format.alignment = align
    p.paragraph_format.first_line_indent = Cm(1.25)
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_after = Pt(0)
    for text, bold in parts:
        run = p.add_run(text)
        set_run_font(run, size=13, bold=bold)
    return p


def caption(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(12)
    run = p.add_run(text)
    set_run_font(run, size=12)


def figure(doc, filename, caption_text, width_cm=15.5):
    p = doc.add_paragraph()
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(str(ASSETS / filename), width=Cm(width_cm))
    caption(doc, caption_text)


def listing(doc, title, code):
    cap = doc.add_paragraph()
    cap.paragraph_format.first_line_indent = Cm(0)
    cap.paragraph_format.space_before = Pt(6)
    cap.paragraph_format.space_after = Pt(2)
    cap.paragraph_format.keep_with_next = True
    run = cap.add_run(title)
    set_run_font(run, size=11, italic=True)

    p = doc.add_paragraph()
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.left_indent = Cm(0.5)
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.space_after = Pt(10)
    p.paragraph_format.keep_together = True
    pPr = p._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), "F2F2F2")
    pPr.append(shd)

    lines = code.strip("\n").split("\n")
    for index, line in enumerate(lines):
        run = p.add_run(line)
        set_run_font(run, name="Consolas", size=9)
        if index < len(lines) - 1:
            run.add_break()


def add_adaptive_table(doc):
    cap = doc.add_paragraph()
    cap.paragraph_format.first_line_indent = Cm(0)
    cap.paragraph_format.line_spacing = 1.0
    cap.paragraph_format.space_before = Pt(12)
    cap.paragraph_format.space_after = Pt(4)
    run = cap.add_run("Таблица 1 – Адаптивные разрешения")
    set_run_font(run, size=12, italic=True)

    rows = [
        ("Разрешение", "Особенности вёрстки"),
        ("375 px", "Мобильная версия: одна колонка, фильтры над каталогом, кнопки на всю ширину."),
        ("960 px", "Планшет: две колонки каталога, фильтры слева."),
        ("1200 px", "Ноутбук: три колонки каталога, уменьшенные отступы."),
        ("1920 px", "Десктоп: базовый макет, ширина контента до 1720 px."),
        ("2560 px", "Широкий экран: контент ограничен по ширине, увеличены боковые поля."),
    ]
    table = doc.add_table(rows=len(rows), cols=2)
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    table.columns[0].width = Cm(4.2)
    table.columns[1].width = Cm(11.3)
    for row_index, (left, right) in enumerate(rows):
        cells = table.rows[row_index].cells
        for cell, text in zip(cells, (left, right)):
            cell.width = Cm(4.2) if cell is cells[0] else Cm(11.3)
            paragraph = cell.paragraphs[0]
            paragraph.paragraph_format.first_line_indent = Cm(0)
            paragraph.paragraph_format.line_spacing = 1.0
            paragraph.paragraph_format.space_after = Pt(0)
            run = paragraph.add_run(text)
            set_run_font(run, size=12, bold=(row_index == 0))
            if row_index == 0:
                shading = OxmlElement("w:shd")
                shading.set(qn("w:val"), "clear")
                shading.set(qn("w:color"), "auto")
                shading.set(qn("w:fill"), "E6E6E6")
                cell._tc.get_or_add_tcPr().append(shading)


def add_page_number(section):
    section.different_first_page_header_footer = True
    footer = section.footer
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    set_run_font(run, size=12)
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = "PAGE"
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.append(begin)
    run._r.append(instr)
    run._r.append(end)


def add_toc(doc):
    title = doc.add_paragraph()
    title.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.paragraph_format.first_line_indent = Cm(0)
    title.paragraph_format.space_after = Pt(12)
    run = title.add_run("ОГЛАВЛЕНИЕ")
    set_run_font(run, size=16, bold=True)

    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.line_spacing = 1.0
    run = p.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = 'TOC \\o "1-2" \\h \\z \\u'
    separate = OxmlElement("w:fldChar")
    separate.set(qn("w:fldCharType"), "separate")
    text = OxmlElement("w:t")
    text.text = "Оглавление обновится при открытии документа."
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.append(begin)
    run._r.append(instr)
    run._r.append(separate)
    run._r.append(text)
    run._r.append(end)

    settings = doc.settings.element
    update = OxmlElement("w:updateFields")
    update.set(qn("w:val"), "true")
    settings.append(update)


def setup_styles(doc):
    normal = doc.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(13)
    normal.paragraph_format.line_spacing = 1.5
    normal.paragraph_format.first_line_indent = Cm(1.25)
    normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    normal.paragraph_format.space_after = Pt(0)
    rpr = normal.element.get_or_add_rPr()
    fonts = rpr.get_or_add_rFonts()
    for attr in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        fonts.set(qn(attr), "Times New Roman")

    h1 = doc.styles["Heading 1"]
    h1.font.name = "Times New Roman"
    h1.font.size = Pt(16)
    h1.font.bold = True
    h1.font.color.rgb = RGBColor(0, 0, 0)
    h1.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    h1.paragraph_format.first_line_indent = Cm(0)
    h1.paragraph_format.line_spacing = 1.5
    h1.paragraph_format.space_before = Pt(0)
    h1.paragraph_format.space_after = Pt(12)
    h1.paragraph_format.page_break_before = True
    h1.paragraph_format.keep_with_next = True
    rpr = h1.element.get_or_add_rPr()
    fonts = rpr.get_or_add_rFonts()
    for attr in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        fonts.set(qn(attr), "Times New Roman")

    h2 = doc.styles["Heading 2"]
    h2.font.name = "Times New Roman"
    h2.font.size = Pt(14)
    h2.font.bold = True
    h2.font.color.rgb = RGBColor(0, 0, 0)
    h2.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
    h2.paragraph_format.first_line_indent = Cm(0)
    h2.paragraph_format.line_spacing = 1.5
    h2.paragraph_format.space_before = Pt(12)
    h2.paragraph_format.space_after = Pt(6)
    h2.paragraph_format.keep_with_next = True
    rpr = h2.element.get_or_add_rPr()
    fonts = rpr.get_or_add_rFonts()
    for attr in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        fonts.set(qn(attr), "Times New Roman")


def add_heading(doc, text, level=1):
    p = doc.add_heading(text, level=level)
    p.paragraph_format.first_line_indent = Cm(0)
    return p


def build_document():
    doc = Document()
    section = doc.sections[0]
    section.page_width = Cm(21)
    section.page_height = Cm(29.7)
    section.left_margin = Cm(3)
    section.right_margin = Cm(1.5)
    section.top_margin = Cm(2)
    section.bottom_margin = Cm(2)
    add_page_number(section)
    setup_styles(doc)

    # ---------------------------- Титульный лист ----------------------------
    def title_center(text, size=12, bold=True, after=0, before=0):
        p = doc.add_paragraph()
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.first_line_indent = Cm(0)
        p.paragraph_format.line_spacing = 1.0
        p.paragraph_format.space_after = Pt(after)
        p.paragraph_format.space_before = Pt(before)
        run = p.add_run(text)
        set_run_font(run, size=size, bold=bold)

    def title_left(text, size=13, after=4):
        p = doc.add_paragraph()
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.first_line_indent = Cm(0)
        p.paragraph_format.line_spacing = 1.0
        p.paragraph_format.space_after = Pt(after)
        run = p.add_run(text)
        set_run_font(run, size=size)

    title_center("МИНИСТЕРСТВО НАУКИ И ВЫСШЕГО ОБРАЗОВАНИЯ РОССИЙСКОЙ ФЕДЕРАЦИИ", 11)
    title_center("федеральное государственное бюджетное образовательное учреждение", 12)
    title_center("высшего образования", 12)
    title_center("«УЛЬЯНОВСКИЙ ГОСУДАРСТВЕННЫЙ ТЕХНИЧЕСКИЙ УНИВЕРСИТЕТ»", 12)
    title_center("Факультет среднего профессионального образования –", 12)
    title_center("Колледж экономики и информатики им. А. Н. Афанасьева", 12)

    for _ in range(3):
        doc.add_paragraph()

    title_center("О Т Ч Е Т", 28, after=8)
    title_center("по учебной практике (по профилю специальности)", 13, bold=False)
    title_center('УП.09.01 Учебная практика «Проектирование и разработка веб-приложений»', 13, bold=False)
    title_center("специальность 09.02.07 Информационные системы и программирование", 13, bold=False)
    title_center("Период прохождения практики: с 17.11.2026 г. по 28.11.2026 г.", 13, bold=False)
    title_center("Место прохождения: ФСПО – Колледж экономики и информатики им. А. Н. Афанасьева УлГТУ", 13, bold=False)

    for _ in range(2):
        doc.add_paragraph()

    title_left("Выполнил: Шайхаттаров Руслан")
    title_left("Отделение: очное")
    title_left("Группа: ____________________")
    title_left("Руководитель практики от ФСПО-КЭИ им. А. Н. Афанасьева")
    title_left("________________________ / ____________________ /")
    title_left("М. П.")
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(120)
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("2026")
    set_run_font(run, size=13)

    doc.add_page_break()
    add_toc(doc)

    # ---------------------------- Введение ----------------------------
    add_heading(doc, "ВВЕДЕНИЕ", 1)
    body(doc, "Учебная практика по профилю специальности проходила в ФСПО – Колледже экономики и информатики им. А. Н. Афанасьева УлГТУ. В качестве индивидуального задания разрабатывался веб-сервис Sarro Orbital Mining — учебный магазин астероидов, реализованный на Django по макету Figma.")
    body(doc, "Цель практики — освоить полный цикл разработки веб-приложения: от анализа предметной области и прототипирования до реализации серверной и клиентской частей, тестирования и документирования.")
    body(doc, "Задачи учебной практики:")
    tasks = [
        "Проанализировать предметную область, целевую аудиторию и бизнес-правила сервиса.",
        "Спроектировать ER-диаграмму и бизнес-логику.",
        "Подготовить адаптивные макеты в Figma для разрешений 375, 960, 1200, 1920 и 2560 px.",
        "Создать проект Django, модели, маршрутизацию, шаблоны и стили.",
        "Реализовать каталог с фильтрами, карточку лота, покупку, регистрацию, вход и личный кабинет.",
        "Разработать собственную админ-панель с CRUD лотов, загрузкой фото, заказами и пользователями.",
        "Провести тестирование, обеспечить адаптивность и подготовить README.",
    ]
    for index, task in enumerate(tasks, 1):
        body(doc, f"{index}. {task}")

    # ---------------------------- 1. Аналитическая часть ----------------------------
    add_heading(doc, "1. АНАЛИТИЧЕСКАЯ ЧАСТЬ", 1)
    add_heading(doc, "1.1. Аналитика", 2)
    body(doc, "Sarro Orbital Mining — учебный веб-сервис, в котором пользователь выбирает астероид, изучает его характеристики и оформляет покупку с доставкой на опорную орбиту. Основная аудитория — коллекционеры, частные колонии, добывающие станции и любители научной фантастики. Дополнительная аудитория — студенты и пользователи, интересующиеся космосом.")
    body(doc, "Потребности аудитории: удобный каталог с фильтрами по составу, расстоянию и спектральному классу; подробная карточка лота; понятная цена в крышках; личный кабинет с историей заказов; инструменты администратора для управления ассортиментом.")
    body(doc, "Бизнес-правила: лот имеет название, описание, цену, расстояние, спектральный класс, состав и фотографию. Статусы лота — «В продаже», «Продан» и «Резерв». Проданные лоты скрываются из каталога, резерв остаётся видимым. Фотография обязательна. После покупки создаётся заказ, а лот переводится в статус «Продан».")
    body(doc, "География проекта — Россия и СНГ; интерфейс полностью русскоязычный, с локальной валютой «крышки» и фантастическим антуражем орбитальной корпорации.")

    add_heading(doc, "1.2. ER-диаграмма", 2)
    body(doc, "Для хранения данных спроектированы модели SpectralClass, Composition, Asteroid, Order и Profile; используется стандартная модель User. Asteroid связан с SpectralClass отношением «многие к одному», с Composition — отношением «многие ко многим» через промежуточную таблицу. Order связывает пользователя и астероид, Profile хранит баланс пользователя.")
    figure(doc, "er_diagram.png", "Рисунок 1 – ER-диаграмма базы данных", 15.5)

    add_heading(doc, "1.3. Бизнес-логика", 2)
    body(doc, "Регистрация проходит по шагам: пользователь вводит email и пароль, проверяется заполненность полей, совпадение паролей и занятость email. При успешной проверке создаются User и Profile, после чего выполняется вход в систему. Вход возможен как по логину, так и по email.")
    body(doc, "После авторизации пользователь может открыть каталог, отфильтровать лоты, перейти в карточку и оформить покупку. Покупка создаёт заказ, а лот получает статус «Продан». Администратор управляет лотами через отдельную панель, доступную только staff-пользователям.")
    figure(doc, "flow_diagram.png", "Рисунок 2 – Бизнес-логика регистрации", 15.5)

    # ---------------------------- 2. Работа в Figma ----------------------------
    add_heading(doc, "2. РАБОТА В FIGMA", 1)
    add_heading(doc, "2.1. Прототипирование", 2)
    body(doc, "Макет разработан в Figma и доступен по ссылке: https://www.figma.com/design/GheQyhOECS53cCZH7K0CMW/Untitled?node-id=0-1. Прототипы выполнены для пяти разрешений: 375, 960, 1200, 1920 и 2560 px.")
    body(doc, "В макете представлены страницы General, Catalog, Card, Login, Register, Profile и Admin. Для каждой страницы подготовлены адаптивные варианты: мобильная версия, планшетная, десктопная и широкоформатная. Это позволило заранее определить сетку, отступы, размеры шрифтов и поведение блоков.")
    figure(doc, "design_general.jpg", "Рисунок 3 – прототип главной страницы, 1920 px", 15.5)
    figure(doc, "design_catalog.jpg", "Рисунок 4 – прототип каталога, 1920 px", 15.5)
    figure(doc, "design_profile.jpg", "Рисунок 5 – прототип личного кабинета, 1920 px", 15.0)
    figure(doc, "design_admin.jpg", "Рисунок 6 – прототип админ-панели, 1920 px", 15.0)
    figure(doc, "design_mobile.jpg", "Рисунок 7 – мобильный прототип главной страницы", 7.0)

    add_heading(doc, "2.2. Дизайн", 2)
    body(doc, "Визуальный стиль построен на космической теме: чёрный фон, звёздное небо, пиксельная типографика и синие акцентные рамки. Основные цвета: #000000 — фон, #302BC0 — акцент и обводки, #FFFFFF — основной текст, #ADB0C2 — вторичный текст.")
    body(doc, "Шрифты: Pixelify Sans — заголовки, логотип и крупные числа; WDXL Lubrifont SC — основной текст, навигация, формы и таблицы. Шрифты подключены локально через @font-face, поэтому сайт не зависит от внешних CDN.")
    body(doc, "Интерфейс оформлен блоками с тонкими акцентными рамками, полупрозрачными тёмными панелями и пиксельными кнопками. Для адаптивности использованы медиазапросы и гибкие сетки; стили разделены по страницам и общим компонентам.")
    add_adaptive_table(doc)

    # ---------------------------- 3. Практическая часть ----------------------------
    add_heading(doc, "3. ПРАКТИЧЕСКАЯ ЧАСТЬ", 1)
    add_heading(doc, "3.1. Структура проекта и маршрутизация", 2)
    body(doc, "Проект состоит из Django-проекта djangoproject и приложения SVO_I_Tochka. Шаблоны находятся в templates, статические файлы — в static, загруженные фотографии — в media/asteroids. Стили разделены на base.css, components/auth.css и отдельные файлы pages/*.css; классы оформлены по БЭМ.")
    body(doc, "Маршрутизация описывает публичные страницы, авторизацию, профиль и собственную админ-панель. Для ограничения доступа используются login_required и staff_member_required.")
    listing(doc, "Листинг 1 – Маршрутизация проекта", """
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('catalog/', views.catalog, name='catalog'),
    path('asteroid/<int:pk>/', views.asteroid_detail),
    path('asteroid/<int:pk>/buy/', views.buy_asteroid),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile, name='profile'),
    path('admin-panel/', views.admin_panel),
    path('admin-panel/orders/', views.admin_orders),
]
""")
    figure(doc, "impl_general.jpg", "Рисунок 8 – реализованная главная страница", 15.5)

    add_heading(doc, "3.2. Модели данных", 2)
    body(doc, "Модель Asteroid хранит название, описание, цену, расстояние, фотографию, спектральный класс, состав и статус. Метод save синхронизирует статус и флаг is_sold. Profile связан с User один к одному и хранит баланс. Order содержит номер, статус, покупателя, лот и дату.")
    listing(doc, "Листинг 2 – Фрагмент models.py", """
class Asteroid(models.Model):
    STATUS_CHOICES = [
        ('in_sale', 'В продаже'),
        ('sold', 'Продан'),
        ('reserved', 'Резерв'),
    ]
    title = models.CharField('Название', max_length=200)
    description = models.TextField('Описание')
    price = models.PositiveIntegerField('Цена')
    distance = models.PositiveIntegerField('Расстояние')
    image = models.ImageField(
        'Фотография',
        upload_to='asteroids/',
        blank=True,
        null=True,
    )
    status = models.CharField(
        'Статус',
        max_length=20,
        choices=STATUS_CHOICES,
        default='in_sale',
    )

    def save(self, *args, **kwargs):
        self.is_sold = self.status == 'sold'
        super().save(*args, **kwargs)
""")
    body(doc, "На уровне модели поле фотографии оставлено необязательным для совместимости, но форма AsteroidForm требует загрузку фото при добавлении и не позволяет удалить его при редактировании.")
    body(doc, "Для проекта созданы миграции, а модели зарегистрированы в стандартной админке Django. Это позволяет при необходимости управлять данными через встроенный интерфейс.")

    add_heading(doc, "3.3. Основной функционал", 2)
    body(doc, "Каталог поддерживает фильтрацию по составу, спектральному классу и расстоянию, а также сортировку по цене. Параметры передаются через GET-запрос и сохраняются в форме. Некорректные значения не приводят к ошибке: они игнорируются.")
    listing(doc, "Листинг 3 – Фильтрация каталога", """
selected_compositions = _to_ints(
    request.GET.getlist('composition')
)
selected_classes = _to_ints(
    request.GET.getlist('spectral_class')
)
if selected_compositions:
    asteroids = asteroids.filter(
        compositions__id__in=selected_compositions
    ).distinct()
if selected_classes:
    asteroids = asteroids.filter(
        spectral_class__id__in=selected_classes
    )
if sort_by == 'price_desc':
    asteroids = asteroids.order_by('-price')
""")
    figure(doc, "impl_catalog.jpg", "Рисунок 9 – каталог с фильтрами и фотографиями", 15.5)
    figure(doc, "impl_card.jpg", "Рисунок 10 – карточка лота", 15.5)
    body(doc, "Карточка лота показывает фотографию, название, теги, описание, цену и кнопку покупки. Для проданного лота кнопка меняется на неактивную. Покупка выполняется POST-запросом с CSRF-токеном; после успешной покупки создаётся заказ и обновляется статус лота.")
    figure(doc, "impl_login.jpg", "Рисунок 11 – страница входа", 14.0)
    figure(doc, "impl_register.jpg", "Рисунок 12 – страница регистрации", 14.0)
    body(doc, "Вход возможен по логину или email. Регистрация проверяет совпадение паролей и уникальность email, создаёт пользователя и профиль. Личный кабинет показывает баланс, позволяет изменить имя и email и выводит историю заказов.")
    figure(doc, "impl_profile.jpg", "Рисунок 13 – личный кабинет", 15.0)

    add_heading(doc, "3.4. Админ-панель", 2)
    body(doc, "Собственная админ-панель доступна по адресу /admin-panel/ только staff-пользователям. На главной странице выводятся карточки статистики, поиск по названию или ID, фильтр по статусу, таблица лотов и пагинация. Для лотов реализованы создание, редактирование и удаление, а также загрузка фотографии.")
    body(doc, "Фотография обязательна: без неё форма не сохраняется. При замене фото старый файл удаляется с диска, при удалении лота удаляется и его фотография. Разделы «Заказы» и «Пользователи» позволяют просматривать заказы, менять их статус и открывать карточки пользователей.")
    listing(doc, "Листинг 4 – Замена фотографии лота", """
old_image = asteroid.image if asteroid.image else None
old_image_name = old_image.name if old_image else None
...
new_image_name = asteroid.image.name if asteroid.image else None
if old_image and old_image_name != new_image_name:
    old_image.delete(save=False)
""")
    figure(doc, "impl_admin.jpg", "Рисунок 14 – админ-панель, список лотов", 15.5)
    figure(doc, "impl_admin_form.jpg", "Рисунок 15 – форма добавления лота", 15.5)

    add_heading(doc, "3.5. Тестирование", 2)
    body(doc, "Для проекта написаны автоматические тесты. Проверяются доступность публичных страниц, вход по логину и email, регистрация, обновление профиля, ограничение доступа в админку, добавление лота с обязательным фото, редактирование, замена и удаление изображения, страницы заказов и пользователей.")
    body(doc, "Запуск тестов выполняется командой python manage.py test. Все 10 тестов проходят успешно. Дополнительно проект проверен вручную на разрешениях 1920, 1200, 960 и 375 px: навигация, формы, фильтры, загрузка изображений и адаптивная вёрстка работают корректно.")

    # ---------------------------- Заключение ----------------------------
    add_heading(doc, "ЗАКЛЮЧЕНИЕ", 1)
    body(doc, "В ходе учебной практики был разработан полноценный веб-сервис Sarro Orbital Mining на Django. Выполнен анализ предметной области, спроектированы ER-диаграмма и бизнес-логика, подготовлены адаптивные макеты в Figma, реализованы серверная и клиентская части приложения.")
    body(doc, "Созданы каталог с фильтрами и сортировкой, карточка лота с покупкой, регистрация, вход, личный кабинет с балансом и историей заказов, а также собственная админ-панель с CRUD, статистикой, поиском, пагинацией, обязательными фотографиями, заказами и пользователями.")
    body(doc, "Проект адаптирован под пять разрешений, использует локальные шрифты, БЭМ-классы и раздельные CSS-файлы. Добавлены миграции, README, requirements.txt и автоматические тесты. Полученный результат готов к локальному запуску и дальнейшему развитию: подключению платежей, реальной доставки и расширению админ-панели.")

    doc.save(str(REPORT_PATH))
    return REPORT_PATH


if __name__ == "__main__":
    prepare_assets()
    path = build_document()
    print(path)
    print("size", path.stat().st_size)
