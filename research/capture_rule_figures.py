"""Capture selected official rulebook figures requested by the researcher.

Input PDFs are locally downloaded from the documented publisher links and are
not committed. Captures exclude rulebook prose; explanations are original.
"""
from pathlib import Path
import fitz
ROOT=Path(__file__).resolve().parents[1]
CAPTURES=[
 ('dragon_castle_rules.pdf',5,(.608,.14,.807,.39),'dragon_rule_tiles.png'),
 ('dragon_castle_rules.pdf',5,(.04,.54,.61,.69),'dragon_rule_groups.png'),
 ('azul_rules.pdf',0,(.05,.70,.17,.975),'azul_rule_board.png'),
 ('azul_rules.pdf',0,(.847,.45,.974,.68),'azul_rule_tiling.png'),
]
for name,page,area,out in CAPTURES:
    doc=fitz.open(ROOT/'research'/name);p=doc[page];w,h=p.rect.width,p.rect.height
    r=fitz.Rect(area[0]*w,area[1]*h,area[2]*w,area[3]*h)
    p.get_pixmap(matrix=fitz.Matrix(3,3),clip=r).save(ROOT/'assets'/out)
