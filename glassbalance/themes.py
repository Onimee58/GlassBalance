"""Application styles with persistent user-selectable appearance."""
from __future__ import annotations
from PySide6.QtGui import QColor, QGuiApplication


def effective_theme(preference: str) -> str:
    if preference == "Light": return "light"
    if preference == "System":
        scheme=QGuiApplication.styleHints().colorScheme()
        from PySide6.QtCore import Qt
        return "light" if scheme == Qt.ColorScheme.Light else "dark"
    return "dark"


def theme_background(mode: str) -> str:
    return "#e8f0f7" if mode=="light" else "#091221"


def stylesheet(dark_css: str, mode: str, accent: str) -> str:
    color=QColor(accent)
    if not color.isValid(): color=QColor("#81e0ce")
    # Use a contrasting control foreground for arbitrary custom accent colors.
    foreground="#071825" if color.lightness()>130 else "#ffffff"
    css=dark_css.replace("#81e0ce",color.name()).replace("#082a32",foreground)
    if mode == "light":
        mapping={
          "#ecf2fa":"#1b3044", "#091221":"#e8f0f7", "#edf3f9":"#1b3044",
          "#fbfdff":"#172b3b", "#fafcff":"#142c43", "#a4b8cd":"#50667a",
          "#9fb5c8":"#4f667a", "#a0b6c8":"#435c70", "#94acbe":"#52677b",
          "#e8f2fc":"#244057", "#edf7ff":"#18344d", "#f3f6fc":"#18344d",
          "#344a61":"#bacbd9", "#1b2a3e":"#f7fbff", "#526479":"#cad9e6",
          "#17283d":"#f7fbff", "#95b2bf":"#567081", "#99e5be":"#17634b",
          "#ffb5b9":"#a93441", "#ffbabf":"#ac3643", "#a2ebd3":"#166b58",
          "#b3fff2":"#176b63", "#687f94":"#71899b", "#78dace":"#177b76",
          "rgba(18, 32, 51, 222)":"rgba(255,255,255,230)",
          "rgba(18, 32, 51, 218)":"rgba(255,255,255,225)",
          "rgba(22, 44, 64, 230)":"rgba(228,244,243,235)",
          "rgba(10, 21, 37, 188)":"rgba(255,255,255,235)",
          "rgba(23, 42, 60, 190)":"rgba(224,235,245,230)",
          "rgba(96, 132, 166, 30)":"rgba(189,208,224,120)",
          "rgba(68, 169, 164, 37)":"rgba(87,169,156,90)",
          "rgba(111, 161, 189, 35)":"rgba(105,150,180,60)",
        }
        for a,b in mapping.items(): css=css.replace(a,b)
        css+='\nQFrame#sidebar { background-color: #e8f0f7; }\nQTableWidget { background-color: #ffffff; color: #1b3044; }\nQDialog { background-color: #f7fbff; }\n'
    return css
