"""
Paleta y estilos de la aplicación (tema oscuro moderno).

Se mantienen los nombres originales (BACKGROUND, COMPONENT, TEXT, FONT, STYLE)
para no romper ningún import ya existente, y se añaden nuevos tokens y
diccionarios de estilo listos para usar en los widgets de tkinter.
"""

import tkinter as tk
from tkinter import ttk

# ---------------------------------------------------------------------------
# Paleta de colores
# ---------------------------------------------------------------------------

BACKGROUND   = '#121212'   # Fondo general de la ventana
SURFACE      = '#1B1B1F'   # Fondo de las tarjetas / secciones
SURFACE_ALT  = '#242429'   # Fondo de inputs y elementos "hundidos"
BORDER       = '#33333A'   # Bordes sutiles entre secciones

COMPONENT    = SURFACE     # Alias retrocompatible: el código antiguo usa style.COMPONENT

TEXT         = '#F2F2F2'   # Texto principal
TEXT_MUTED   = '#9A9AA2'   # Texto secundario / ayudas

ACCENT       = '#4FC3F7'   # Azul de acento (antes '#84C9FB')
ACCENT_DARK  = '#2D9CDB'

SUCCESS      = '#4CAF50'   # Iniciar / confirmar
SUCCESS_DARK = '#3C9142'

DANGER       = '#E5484D'   # Detener / peligro
DANGER_DARK  = '#C7383C'

INFO         = ACCENT

# ---------------------------------------------------------------------------
# Tipografías
# ---------------------------------------------------------------------------

FONT_FAMILY   = 'Segoe UI'

FONT_TITLE    = (FONT_FAMILY, 16, 'bold')   # Título de pantalla
FONT_SECTION  = (FONT_FAMILY, 10, 'bold')   # Título de sección (LabelFrame)
FONT_LABEL    = (FONT_FAMILY, 10)           # Texto y etiquetas normales
FONT_BUTTON   = (FONT_FAMILY, 10, 'bold')   # Botones

FONT          = FONT_LABEL   # Alias retrocompatible: el código antiguo usa style.FONT

PAD = 10  # Espaciado estándar entre secciones/widgets

# ---------------------------------------------------------------------------
# Diccionarios de estilo (para pasar como **kwargs a los widgets tk clásicos)
# ---------------------------------------------------------------------------

STYLE = {
    "font": FONT_LABEL,
    "bg": SURFACE,
    "fg": TEXT,
}

# Igual que STYLE pero pensado para colocarse directamente sobre el fondo
# de la ventana (no sobre una tarjeta/sección)
STYLE_ON_BG = {
    "font": FONT_LABEL,
    "bg": BACKGROUND,
    "fg": TEXT,
}

STYLE_TITLE = {
    "font": FONT_TITLE,
    "bg": BACKGROUND,
    "fg": TEXT,
}

STYLE_SECTION_TITLE = {
    "font": FONT_SECTION,
    "bg": BACKGROUND,
    "fg": ACCENT,
}

STYLE_MUTED = {
    "font": FONT_LABEL,
    "bg": SURFACE,
    "fg": TEXT_MUTED,
}

STYLE_MUTED_ON_BG = {
    "font": FONT_LABEL,
    "bg": BACKGROUND,
    "fg": TEXT_MUTED,
}

STYLE_ENTRY = {
    "font": FONT_LABEL,
    "bg": SURFACE_ALT,
    "fg": TEXT,
    "insertbackground": TEXT,       # color del cursor de texto
    "relief": "flat",
    "highlightthickness": 1,
    "highlightbackground": BORDER,
    "highlightcolor": ACCENT,
}

# tk.LabelFrame no admite "font"/"fg" dentro de un mismo dict tan limpiamente
# como Label, así que se define aparte con las claves que sí acepta.
STYLE_LABELFRAME = {
    "bg": BACKGROUND,
    "fg": ACCENT,
    "font": FONT_SECTION,
    "bd": 1,
    "relief": "flat",
    "highlightbackground": BORDER,
    "highlightthickness": 1,
    "labelanchor": "n",
    "padx": PAD,
    "pady": PAD,
}


def _estilo_boton(bg, bg_hover, fg=TEXT):
    return {
        "font": FONT_BUTTON,
        "bg": bg,
        "fg": fg,
        "activebackground": bg_hover,
        "activeforeground": fg,
        "relief": "flat",
        "bd": 0,
        "padx": 16,
        "pady": 8,
        "cursor": "hand2",
    }


STYLE_BOTON           = _estilo_boton(SURFACE_ALT, BORDER, fg=TEXT)
STYLE_BOTON_PRIMARIO  = _estilo_boton(ACCENT, ACCENT_DARK, fg='#0A0A0A')
STYLE_BOTON_EXITO     = _estilo_boton(SUCCESS, SUCCESS_DARK, fg='#0A0A0A')
STYLE_BOTON_PELIGRO   = _estilo_boton(DANGER, DANGER_DARK, fg='#FFFFFF')


def aplicar_tema_ttk():
    """
    Configura los widgets ttk (Progressbar, etc.) para que combinen con el
    tema oscuro. Es seguro llamarla varias veces; sólo debe llamarse una vez
    que exista una instancia de tk.Tk/Toplevel.
    """
    estilo = ttk.Style()
    try:
        estilo.theme_use('clam')  # Tema base que permite personalizar colores
    except tk.TclError:
        pass

    estilo.configure(
        'Moderna.Horizontal.TProgressbar',
        troughcolor=SURFACE_ALT,
        background=ACCENT,
        bordercolor=SURFACE_ALT,
        lightcolor=ACCENT,
        darkcolor=ACCENT,
        thickness=14,
    )

    return estilo
