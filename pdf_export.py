from reportlab.platypus import SimpleDocTemplate, Preformatted
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os


from reportlab.platypus import SimpleDocTemplate, Preformatted, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os


def export_pdf(title, songs, filename):

    doc = SimpleDocTemplate(filename)
    styles = getSampleStyleSheet()

    # UTF-8 font
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "C:\\Windows\\Fonts\\DejaVuSans.ttf",
        "C:\\Windows\\Fonts\\arial.ttf"
    ]

    font_name = "Helvetica"

    for path in font_paths:
        if os.path.exists(path):
            pdfmetrics.registerFont(TTFont("MyFont", path))
            font_name = "MyFont"
            break

    style = styles["Code"]
    style.fontName = font_name
    style.fontSize = 10

    story = []

    for i, song in enumerate(songs):

        content = f"{song['artist']} - {song['title']}\n\n{song['content']}"

        story.append(Preformatted(content, style))

        if i != len(songs) - 1:
            story.append(PageBreak())

    doc.build(story)



    # font_paths = [
    #     "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
    #     "/Library/Fonts/DejaVu Sans.ttf",                    # Mac
    #     "C:\\Windows\\Fonts\\DejaVuSans.ttf",              # Windows
    #     "C:\\Windows\\Fonts\\arial.ttf"                    # fallback Windows
    # ]