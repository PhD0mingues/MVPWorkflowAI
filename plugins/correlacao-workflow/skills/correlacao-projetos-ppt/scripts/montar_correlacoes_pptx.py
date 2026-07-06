#!/usr/bin/env python3
"""
Monta o PPT de resultado da skill correlacao-projetos-ppt no template visual
oficial da Advisia (o mesmo estilo de `correlacoes_eletrodomesticos.pptx`).

Uso:
    python3 montar_correlacoes_pptx.py dados.json saida.pptx

Onde dados.json tem o formato:
{
  "titulo": "Correlações entre Projetos",
  "subtitulo": "Leitura orientada ao mercado de design e publicidade de eletrodomésticos",
  "rodape_data": "Workflows AI — 03/07/2026",
  "clusters": [
    {
      "nome": "O aroma como atributo de design",
      "itens": ["6 - Cheiro", "3 - Geladeira", "4 - Forno", "1 - Cigarro"],
      "explicacao": "texto da correlação..."
    },
    ...
  ]
}

Não adivinhe conteúdo aqui — este script só aplica o estilo visual (cores,
fontes, posições). Os clusters, nomes e explicações vêm do raciocínio feito
nos Passos 3 e 4 do SKILL.md.
"""
import json
import sys

from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor

NAVY = RGBColor(0x1F, 0x1F, 0x4A)
GOLD = RGBColor(0xC9, 0x9A, 0x2E)
GRAY = RGBColor(0x33, 0x33, 0x33)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
FONT = "Georgia"

SIDEBAR_W = Emu(2926080)
SLIDE_W = Emu(12192000)
SLIDE_H = Emu(6858000)
CONTENT_X = Emu(3291840)
CONTENT_W = Emu(8229600)


def add_textbox(slide, x, y, w, h, text, size, bold, color, align="l"):
    box = slide.shapes.add_textbox(x, y, w, h)
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = {"l": 1, "ctr": 2}.get(align, 1)
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.name = color and FONT or FONT
    run.font.color.rgb = color
    return box


def add_sidebar(slide, color):
    rect = slide.shapes.add_shape(1, Emu(0), Emu(0), SIDEBAR_W, SLIDE_H)  # 1 = MSO_SHAPE.RECTANGLE
    rect.fill.solid()
    rect.fill.fore_color.rgb = color
    rect.line.fill.background()
    rect.shadow.inherit = False
    return rect


def build_title_slide(prs, titulo, subtitulo, rodape_data):
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # layout em branco
    add_sidebar(slide, NAVY)
    add_textbox(slide, CONTENT_X, Emu(2377440), CONTENT_W, Emu(1097280),
                titulo, 40, True, NAVY)
    add_textbox(slide, CONTENT_X, Emu(3291840), CONTENT_W, Emu(731520),
                subtitulo, 18, False, GRAY)
    add_textbox(slide, CONTENT_X, Emu(3840480), CONTENT_W, Emu(548640),
                rodape_data, 14, True, GOLD)
    return slide


def build_cluster_slide(prs, nome, itens, explicacao):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_sidebar(slide, GOLD)

    # lista de itens do cluster, empilhados na sidebar (0.5" cada, a partir de 0.7")
    y = 640080
    for item in itens:
        add_textbox(slide, Emu(274320), Emu(y), Emu(2377440), Emu(457200),
                    item, 16, True, WHITE)
        y += 457200

    add_textbox(slide, CONTENT_X, Emu(640080), CONTENT_W, Emu(914400),
                nome, 28, True, NAVY)
    add_textbox(slide, CONTENT_X, Emu(1737360), CONTENT_W, Emu(4389120),
                explicacao, 16, False, GRAY)
    return slide


def main():
    if len(sys.argv) != 3:
        print("Uso: python3 montar_correlacoes_pptx.py dados.json saida.pptx", file=sys.stderr)
        sys.exit(1)

    with open(sys.argv[1], encoding="utf-8") as f:
        dados = json.load(f)

    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H

    build_title_slide(
        prs,
        dados.get("titulo", "Correlações entre Projetos"),
        dados.get("subtitulo", ""),
        dados.get("rodape_data", ""),
    )

    for cluster in dados.get("clusters", []):
        build_cluster_slide(
            prs,
            cluster["nome"],
            cluster.get("itens", []),
            cluster.get("explicacao", ""),
        )

    prs.save(sys.argv[2])
    print(f"PPT salvo em {sys.argv[2]}")


if __name__ == "__main__":
    main()
