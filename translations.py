# translations.py — PM2 multi-language support
import json
import os

_current_lang = 'en'
_reverse_map = {}
_settings_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pm2_language.json')

TRANSLATIONS = {
    'en': {
        # Menu & commands
        'Pattern Maker': 'Pattern Maker',
        'PM: Wall': 'PM: Wall',
        'wall_tooltip': 'Pattern on a single flat face.',
        'wall_tooltip_desc': (
            'A tool designed for working on flat surfaces.\n\n'
            'Select a face and use the preview to fine-tune proportions. '
            'Great for ventilation grids and simple grates.'
        ),
        'PM: Cylinder': 'PM: Cylinder',
        'cyl_tooltip': 'Pattern wrapped around a cylinder circumference.',
        'cyl_tooltip_desc': (
            'Generates a seamless pattern on cylindrical geometry.\n\n'
            'The script automatically unwraps the cylinder surface and closes '
            'the pattern around its full circumference. Ideal for knurling and textures.'
        ),
        'PM: Multi': 'PM: Multi',
        'multi_tooltip': 'Advanced pattern for multiple connected faces.',
        'multi_tooltip_desc': (
            'Our most advanced engine. Maps multi-face patterns.\n\n'
            'Requires defining a Vertical Axis and a Horizontal Axis and '
            'supports multi-selection of any number of connected faces.'
        ),
        # Input labels
        'Face': 'Face',
        'Planar': 'Planar',
        'Shape': 'Shape',
        'Grid Type': 'Grid Type',
        'Shift Direction': 'Shift Direction',
        'Vertical Interlocking': 'Vertical Interlocking',
        'Base Radius (R)': 'Base Radius (R)',
        'Spacing (mm)': 'Spacing (mm)',
        'Margin (mm)': 'Margin (mm)',
        'Rectangle Height (%)': 'Rectangle Height (%)',
        'Slot Length': 'Slot Length',
        'Slot Orientation': 'Slot Orientation',
        'Generate / Refresh Preview': 'Generate / Refresh Preview',
        'Cylinder Face': 'Cylinder Face',
        'Select': 'Select',
        'Density (Columns)': 'Density (Columns)',
        '1. Vertical Axis (H)': '1. Vertical Axis (H)',
        '2. Horizontal Axis (X)': '2. Horizontal Axis (X)',
        '3. Perimeter Faces': '3. Perimeter Faces',
        'Faces': 'Faces',
        'Alignment (Vertical Axis)': 'Alignment (Vertical Axis)',
        # Dropdown items (also used as comparison keys in engine logic)
        'Hexagon': 'Hexagon',
        'Circle': 'Circle',
        'Rect / Square': 'Rect / Square',
        'Slot': 'Slot',
        'Checkerboard': 'Checkerboard',
        'Staggered (Brick)': 'Staggered (Brick)',
        'Rows (Horizontal)': 'Rows (Horizontal)',
        'Columns (Vertical)': 'Columns (Vertical)',
        'Vertical': 'Vertical',
        'Horizontal': 'Horizontal',
        'Symmetrical (Center)': 'Symmetrical (Center)',
        'From Axis (Start)': 'From Axis (Start)',
    },
    'pl': {
        'Pattern Maker': 'Kreator Wzor\u00f3w',
        'PM: Wall': 'PM: \u015aciana',
        'wall_tooltip': 'Wz\u00f3r na pojedynczej p\u0142askiej powierzchni.',
        'wall_tooltip_desc': (
            'Narz\u0119dzie do pracy na p\u0142askich powierzchniach.\n\n'
            'Wybierz powierzchni\u0119 i u\u017cyj podgl\u0105du, aby dopasowa\u0107 proporcje. '
            'Idealne do kratek wentylacyjnych i prostych siatek.'
        ),
        'PM: Cylinder': 'PM: Cylinder',
        'cyl_tooltip': 'Wz\u00f3r owini\u0119ty wok\u00f3\u0142 obwodu cylindra.',
        'cyl_tooltip_desc': (
            'Generuje bezszwowy wz\u00f3r na geometrii cylindrycznej.\n\n'
            'Skrypt automatycznie rozwija powierzchni\u0119 cylindra i zamyka wz\u00f3r '
            'wok\u00f3\u0142 pe\u0142nego obwodu. Idealny do rade\u0142kowania i tekstur.'
        ),
        'PM: Multi': 'PM: Multi',
        'multi_tooltip': 'Zaawansowany wz\u00f3r dla wielu po\u0142\u0105czonych powierzchni.',
        'multi_tooltip_desc': (
            'Nasz najbardziej zaawansowany silnik. Mapuje wzory na wielu powierzchniach.\n\n'
            'Wymaga zdefiniowania osi pionowej i osi poziomej oraz obs\u0142uguje '
            'wyb\u00f3r wielu po\u0142\u0105czonych powierzchni.'
        ),
        'Face': 'Powierzchnia',
        'Planar': 'P\u0142aska',
        'Shape': 'Kszta\u0142t',
        'Grid Type': 'Typ siatki',
        'Shift Direction': 'Kierunek przesuni\u0119cia',
        'Vertical Interlocking': 'Blokowanie pionowe',
        'Base Radius (R)': 'Promie\u0144 bazowy (R)',
        'Spacing (mm)': 'Odst\u0119p (mm)',
        'Margin (mm)': 'Margines (mm)',
        'Rectangle Height (%)': 'Wysoko\u015b\u0107 prostok\u0105ta (%)',
        'Slot Length': 'D\u0142ugo\u015b\u0107 szczeliny',
        'Slot Orientation': 'Orientacja szczeliny',
        'Generate / Refresh Preview': 'Generuj / Od\u015bwie\u017c podgl\u0105d',
        'Cylinder Face': 'Powierzchnia cylindra',
        'Select': 'Wybierz',
        'Density (Columns)': 'G\u0119sto\u015b\u0107 (kolumny)',
        '1. Vertical Axis (H)': '1. O\u015b pionowa (H)',
        '2. Horizontal Axis (X)': '2. O\u015b pozioma (X)',
        '3. Perimeter Faces': '3. Powierzchnie obwodu',
        'Faces': 'Powierzchnie',
        'Alignment (Vertical Axis)': 'Wyr\u00f3wnanie (o\u015b pionowa)',
        'Hexagon': 'Sze\u015bciok\u0105t',
        'Circle': 'Okr\u0105g',
        'Rect / Square': 'Prostok\u0105t / Kwadrat',
        'Slot': 'Szczelina',
        'Checkerboard': 'Szachownica',
        'Staggered (Brick)': 'Przesuni\u0119ty (Ceg\u0142a)',
        'Rows (Horizontal)': 'Wiersze (Poziomo)',
        'Columns (Vertical)': 'Kolumny (Pionowo)',
        'Vertical': 'Pionowo',
        'Horizontal': 'Poziomo',
        'Symmetrical (Center)': 'Symetryczny (\u015arodek)',
        'From Axis (Start)': 'Od osi (Start)',
    },
    'es': {
        'Pattern Maker': 'Creador de Patrones',
        'PM: Wall': 'PM: Pared',
        'wall_tooltip': 'Patr\u00f3n en una sola cara plana.',
        'wall_tooltip_desc': (
            'Una herramienta dise\u00f1ada para trabajar en superficies planas.\n\n'
            'Seleccione una cara y use la vista previa para ajustar las proporciones. '
            'Ideal para rejillas de ventilaci\u00f3n y rejillas simples.'
        ),
        'PM: Cylinder': 'PM: Cilindro',
        'cyl_tooltip': 'Patr\u00f3n envuelto alrededor de la circunferencia de un cilindro.',
        'cyl_tooltip_desc': (
            'Genera un patr\u00f3n continuo en geometr\u00eda cil\u00edndrica.\n\n'
            'El script desenrolla autom\u00e1ticamente la superficie del cilindro y cierra '
            'el patr\u00f3n alrededor de toda la circunferencia. Ideal para moleteado y texturas.'
        ),
        'PM: Multi': 'PM: Multi',
        'multi_tooltip': 'Patr\u00f3n avanzado para m\u00faltiples caras conectadas.',
        'multi_tooltip_desc': (
            'Nuestro motor m\u00e1s avanzado. Mapea patrones en m\u00faltiples caras.\n\n'
            'Requiere definir un eje vertical y un eje horizontal y admite la selecci\u00f3n '
            'm\u00faltiple de cualquier n\u00famero de caras conectadas.'
        ),
        'Face': 'Cara',
        'Planar': 'Plana',
        'Shape': 'Forma',
        'Grid Type': 'Tipo de cuadr\u00edcula',
        'Shift Direction': 'Direcci\u00f3n de desplazamiento',
        'Vertical Interlocking': 'Entrelazado vertical',
        'Base Radius (R)': 'Radio base (R)',
        'Spacing (mm)': 'Espaciado (mm)',
        'Margin (mm)': 'Margen (mm)',
        'Rectangle Height (%)': 'Altura del rect\u00e1ngulo (%)',
        'Slot Length': 'Longitud de ranura',
        'Slot Orientation': 'Orientaci\u00f3n de ranura',
        'Generate / Refresh Preview': 'Generar / Actualizar vista previa',
        'Cylinder Face': 'Cara del cilindro',
        'Select': 'Seleccionar',
        'Density (Columns)': 'Densidad (columnas)',
        '1. Vertical Axis (H)': '1. Eje vertical (H)',
        '2. Horizontal Axis (X)': '2. Eje horizontal (X)',
        '3. Perimeter Faces': '3. Caras del per\u00edmetro',
        'Faces': 'Caras',
        'Alignment (Vertical Axis)': 'Alineaci\u00f3n (eje vertical)',
        'Hexagon': 'Hex\u00e1gono',
        'Circle': 'C\u00edrculo',
        'Rect / Square': 'Rect / Cuadrado',
        'Slot': 'Ranura',
        'Checkerboard': 'Tablero de ajedrez',
        'Staggered (Brick)': 'Escalonado (Ladrillo)',
        'Rows (Horizontal)': 'Filas (Horizontal)',
        'Columns (Vertical)': 'Columnas (Vertical)',
        'Vertical': 'Vertical',
        'Horizontal': 'Horizontal',
        'Symmetrical (Center)': 'Sim\u00e9trico (Centro)',
        'From Axis (Start)': 'Desde eje (Inicio)',
    },
    'de': {
        'Pattern Maker': 'Mustergenerator',
        'PM: Wall': 'PM: Wand',
        'wall_tooltip': 'Muster auf einer einzelnen flachen Fl\u00e4che.',
        'wall_tooltip_desc': (
            'Ein Werkzeug f\u00fcr die Arbeit an flachen Oberfl\u00e4chen.\n\n'
            'W\u00e4hlen Sie eine Fl\u00e4che und nutzen Sie die Vorschau, um die Proportionen '
            'anzupassen. Ideal f\u00fcr L\u00fcftungsgitter und einfache Gitter.'
        ),
        'PM: Cylinder': 'PM: Zylinder',
        'cyl_tooltip': 'Muster um den Zylinderumfang gewickelt.',
        'cyl_tooltip_desc': (
            'Erzeugt ein nahtloses Muster auf zylindrischer Geometrie.\n\n'
            'Das Skript wickelt die Zylinderoberfl\u00e4che automatisch ab und schlie\u00dft '
            'das Muster um den gesamten Umfang. Ideal f\u00fcr R\u00e4ndelung und Texturen.'
        ),
        'PM: Multi': 'PM: Multi',
        'multi_tooltip': 'Erweitertes Muster f\u00fcr mehrere verbundene Fl\u00e4chen.',
        'multi_tooltip_desc': (
            'Unsere fortschrittlichste Engine. Bildet Muster auf mehreren Fl\u00e4chen ab.\n\n'
            'Erfordert die Definition einer vertikalen Achse und einer horizontalen Achse '
            'und unterst\u00fctzt die Mehrfachauswahl beliebig vieler verbundener Fl\u00e4chen.'
        ),
        'Face': 'Fl\u00e4che',
        'Planar': 'Eben',
        'Shape': 'Form',
        'Grid Type': 'Rastertyp',
        'Shift Direction': 'Versatzrichtung',
        'Vertical Interlocking': 'Vertikale Verzahnung',
        'Base Radius (R)': 'Basisradius (R)',
        'Spacing (mm)': 'Abstand (mm)',
        'Margin (mm)': 'Rand (mm)',
        'Rectangle Height (%)': 'Rechteckh\u00f6he (%)',
        'Slot Length': 'Schlitzl\u00e4nge',
        'Slot Orientation': 'Schlitzausrichtung',
        'Generate / Refresh Preview': 'Generieren / Vorschau aktualisieren',
        'Cylinder Face': 'Zylinderfl\u00e4che',
        'Select': 'Ausw\u00e4hlen',
        'Density (Columns)': 'Dichte (Spalten)',
        '1. Vertical Axis (H)': '1. Vertikale Achse (H)',
        '2. Horizontal Axis (X)': '2. Horizontale Achse (X)',
        '3. Perimeter Faces': '3. Umfangsfl\u00e4chen',
        'Faces': 'Fl\u00e4chen',
        'Alignment (Vertical Axis)': 'Ausrichtung (Vertikale Achse)',
        'Hexagon': 'Sechseck',
        'Circle': 'Kreis',
        'Rect / Square': 'Rect / Quadrat',
        'Slot': 'Schlitz',
        'Checkerboard': 'Schachbrett',
        'Staggered (Brick)': 'Versetzt (Ziegel)',
        'Rows (Horizontal)': 'Zeilen (Horizontal)',
        'Columns (Vertical)': 'Spalten (Vertikal)',
        'Vertical': 'Vertikal',
        'Horizontal': 'Horizontal',
        'Symmetrical (Center)': 'Symmetrisch (Mitte)',
        'From Axis (Start)': 'Von Achse (Start)',
    },
}


def _build_reverse_map():
    """Build reverse mapping from translated strings back to English keys."""
    global _reverse_map
    _reverse_map = {}
    lang_dict = TRANSLATIONS.get(_current_lang, TRANSLATIONS['en'])
    for eng_key, translated_val in lang_dict.items():
        _reverse_map[translated_val] = eng_key


def t(key_str):
    """Translate an English key to the current language."""
    lang_dict = TRANSLATIONS.get(_current_lang, TRANSLATIONS['en'])
    return lang_dict.get(key_str, key_str)


def key(translated_text):
    """Reverse-translate a displayed/selected string back to its English key."""
    return _reverse_map.get(translated_text, translated_text)


def _load_saved_lang():
    try:
        with open(_settings_path, 'r') as f:
            return json.load(f).get('language', 'en')
    except Exception:
        return 'en'


def _save_lang(lang):
    try:
        with open(_settings_path, 'w') as f:
            json.dump({'language': lang}, f)
    except Exception:
        pass


def select_language(ui):
    """Show language selection dialog. Call once at add-in startup."""
    global _current_lang
    saved = _load_saved_lang()
    default = {'en': '1', 'pl': '2', 'es': '3', 'de': '4'}.get(saved, '1')
    prompt = ('Select language / Wybierz jezyk / Seleccionar idioma / Sprache wahlen:\n\n'
              '1 = English\n'
              '2 = Polski\n'
              '3 = Espanol\n'
              '4 = Deutsch')
    try:
        (val, cancelled) = ui.inputBox(prompt, 'PM2 - Language', default)
        if cancelled:
            _current_lang = saved
        else:
            lang_map = {'1': 'en', '2': 'pl', '3': 'es', '4': 'de'}
            _current_lang = lang_map.get(val.strip(), saved)
            _save_lang(_current_lang)
    except Exception:
        _current_lang = saved
    _build_reverse_map()
