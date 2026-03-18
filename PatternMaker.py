import adsk.core, adsk.fusion, math, traceback, os, sys
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
from translations import t, key, select_language


_handlers = []
_app = adsk.core.Application.get()
_ui = _app.userInterface
_preview_flags = {'wall': False, 'cyl': False, 'multi': False}


# ==========================================
# 1. UNIVERSAL DRAWING ENGINE
# ==========================================
def draw_shape(sketch, shape_type, cx, cy, r, slot_len, is_rotated, slot_horizontal, rect_h_scale):
    try:
        x, y = cx, cy
        curves = sketch.sketchCurves
        lines = curves.sketchLines
        arcs = curves.sketchArcs

        if r < 0.01: r = 0.01

        if shape_type == 'Hexagon':
            for i in range(6):
                a1, a2 = math.radians(i*60+30), math.radians((i+1)*60+30)
                lines.addByTwoPoints(adsk.core.Point3D.create(x + r*math.cos(a1), y + r*math.sin(a1), 0),
                                     adsk.core.Point3D.create(x + r*math.cos(a2), y + r*math.sin(a2), 0))

        elif shape_type == 'Circle':
            curves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(x, y, 0), r)

        elif shape_type == 'Rect / Square':
            w = r * 2
            h = w * (rect_h_scale / 100.0)
            w_draw = h if is_rotated else w
            h_draw = w if is_rotated else h
            lines.addTwoPointRectangle(
                adsk.core.Point3D.create(x - w_draw/2, y - h_draw/2, 0),
                adsk.core.Point3D.create(x + w_draw/2, y + h_draw/2, 0))

        elif shape_type == 'Slot':
            actual_horizontal = not slot_horizontal if is_rotated else slot_horizontal
            if slot_len < 0.01: slot_len = 0.01

            if actual_horizontal:
                p_left_c, p_right_c = adsk.core.Point3D.create(x - slot_len/2, y, 0), adsk.core.Point3D.create(x + slot_len/2, y, 0)
                p_tl, p_tr = adsk.core.Point3D.create(x - slot_len/2, y + r, 0), adsk.core.Point3D.create(x + slot_len/2, y + r, 0)
                p_bl, p_br = adsk.core.Point3D.create(x - slot_len/2, y - r, 0), adsk.core.Point3D.create(x + slot_len/2, y - r, 0)
                arcs.addByCenterStartEnd(p_right_c, p_br, p_tr); arcs.addByCenterStartEnd(p_left_c, p_tl, p_bl)
                lines.addByTwoPoints(p_tl, p_tr); lines.addByTwoPoints(p_bl, p_br)
            else:
                p_bot_c, p_top_c = adsk.core.Point3D.create(x, y - slot_len/2, 0), adsk.core.Point3D.create(x, y + slot_len/2, 0)
                p_tr, p_tl = adsk.core.Point3D.create(x + r, y + slot_len/2, 0), adsk.core.Point3D.create(x - r, y + slot_len/2, 0)
                p_br, p_bl = adsk.core.Point3D.create(x + r, y - slot_len/2, 0), adsk.core.Point3D.create(x - r, y - slot_len/2, 0)
                arcs.addByCenterStartEnd(p_top_c, p_tr, p_tl); arcs.addByCenterStartEnd(p_bot_c, p_bl, p_br)
                lines.addByTwoPoints(p_tl, p_bl); lines.addByTwoPoints(p_tr, p_br)
    except: pass


# ==========================================
# 2. PM: WALL (FLAT MODULE)
# ==========================================
def execute_wall_engine(inputs):
    face_in = inputs.itemById('face_select')
    if face_in.selectionCount == 0: return

    design = adsk.fusion.Design.cast(_app.activeProduct); rootComp = design.rootComponent
    face_sel = face_in.selection(0).entity

    radius = inputs.itemById('radius').value; spacing = inputs.itemById('spacing').value; margin = inputs.itemById('margin').value
    slot_len = inputs.itemById('slot_len').value if inputs.itemById('slot_len').isVisible else 0
    shape_type = key(inputs.itemById('shape_type').selectedItem.name)
    slot_horizontal = True if (inputs.itemById('slot_orient').isVisible and key(inputs.itemById('slot_orient').selectedItem.name) == 'Horizontal') else False
    rect_h_scale = inputs.itemById('rect_h_scale').valueOne if inputs.itemById('rect_h_scale').isVisible else 100
    is_interlock = inputs.itemById('interlock').value if inputs.itemById('interlock').isVisible else False

    if shape_type == 'Hexagon': grid_type = 'Staggered (Brick)'
    else: grid_type = key(inputs.itemById('grid_type').selectedItem.name)
    is_staggered_grid = ('Staggered' in grid_type)

    def prepare_base(sketch):
        curves = adsk.core.ObjectCollection.create()
        for edge in face_sel.edges:
            proj = sketch.project(edge)
            for p in proj: curves.add(p)
        bbox = sketch.boundingBox
        center = adsk.core.Point3D.create((bbox.minPoint.x + bbox.maxPoint.x)/2, (bbox.minPoint.y + bbox.maxPoint.y)/2, 0)
        if margin > 0: sketch.offset(curves, center, margin)
        return bbox

    sk1 = rootComp.sketches.add(face_sel); prepare_base(sk1)
    sk2 = rootComp.sketches.add(face_sel); bbox = prepare_base(sk2)
    sk2.isComputeDeferred = True

    r = radius

    ui_shift = key(inputs.itemById('shift_dir').selectedItem.name) if inputs.itemById('shift_dir').isVisible else 'Rows (Horizontal)'
    actual_shift_dir = ui_shift

    if shape_type == 'Hexagon':
        dx = math.sqrt(3) * r + spacing
        dy = 1.5 * r + (spacing * math.sqrt(3) / 2)
        is_staggered_grid = True
        actual_shift_dir = 'Rows (Horizontal)'
    else:
        w_shape, h_shape = r * 2, r * 2
        if shape_type == 'Rect / Square':
            h_shape = w_shape * (rect_h_scale / 100.0)
        elif shape_type == 'Slot':
            w_shape = (slot_len + r * 2) if slot_horizontal else (r * 2)
            h_shape = (r * 2) if slot_horizontal else (slot_len + r * 2)
        dx = w_shape + spacing
        dy = h_shape + spacing
        if is_interlock:
            if h_shape >= w_shape:
                dx = (w_shape * 2) + (spacing * 2); dy = (h_shape / 2.0) + spacing
                actual_shift_dir = 'Rows (Horizontal)'
            else:
                dx = (w_shape / 2.0) + spacing; dy = (h_shape * 2) + (spacing * 2)
                actual_shift_dir = 'Columns (Vertical)'

    cols, rows = int((bbox.maxPoint.x - bbox.minPoint.x) / dx) + 2, int((bbox.maxPoint.y - bbox.minPoint.y) / dy) + 2
    for r_idx in range(-1, rows + 1):
        for c_idx in range(-1, cols + 1):
            xs = (dx / 2.0) if (is_staggered_grid and actual_shift_dir == 'Rows (Horizontal)' and r_idx % 2 != 0) else 0
            ys = (dy / 2.0) if (is_staggered_grid and actual_shift_dir == 'Columns (Vertical)' and c_idx % 2 != 0) else 0
            is_shape_rot = (shape_type == 'Hexagon')
            draw_shape(sk2, shape_type, bbox.minPoint.x + (c_idx * dx) + xs, bbox.minPoint.y + (r_idx * dy) + ys, r, slot_len, is_shape_rot, slot_horizontal, rect_h_scale)
    sk2.isComputeDeferred = False


class WallPreview(adsk.core.CommandEventHandler):
    def __init__(self): super().__init__()
    def notify(self, args):
        if _preview_flags['wall']:
            try: execute_wall_engine(args.firingEvent.sender.commandInputs)
            except: pass

class WallExecute(adsk.core.CommandEventHandler):
    def __init__(self): super().__init__()
    def notify(self, args):
        try: execute_wall_engine(args.firingEvent.sender.commandInputs)
        except: _ui.messageBox(traceback.format_exc())

class WallInputChanged(adsk.core.InputChangedEventHandler):
    def __init__(self): super().__init__()
    def notify(self, args):
        try:
            inputs = args.inputs; changed_id = args.input.id
            _preview_flags['wall'] = (changed_id == 'preview_btn')
            shape = key(inputs.itemById('shape_type').selectedItem.name)
            inputs.itemById('slot_len').isVisible = inputs.itemById('slot_orient').isVisible = (shape == 'Slot')
            inputs.itemById('rect_h_scale').isVisible = (shape == 'Rect / Square')
            grid = inputs.itemById('grid_type'); shift = inputs.itemById('shift_dir')
            if shape == 'Hexagon': grid.listItems.item(1).isSelected = True; grid.isEnabled = shift.isVisible = False
            else: grid.isEnabled = True; shift.isVisible = ('Staggered' in key(grid.selectedItem.name))
            inputs.itemById('interlock').isVisible = (shift.isVisible and shape != 'Hexagon')
        except: pass

class WallCreated(adsk.core.CommandCreatedEventHandler):
    def __init__(self): super().__init__()
    def notify(self, args):
        cmd = args.command; inputs = cmd.commandInputs
        sel = inputs.addSelectionInput('face_select', t('Face'), t('Planar'))
        sel.addSelectionFilter('PlanarFaces'); sel.setSelectionLimits(1,1)
        shape = inputs.addDropDownCommandInput('shape_type', t('Shape'), 1)
        [shape.listItems.add(t(n), n=='Hexagon') for n in ['Hexagon', 'Circle', 'Rect / Square', 'Slot']]
        grid = inputs.addDropDownCommandInput('grid_type', t('Grid Type'), 1)
        grid.listItems.add(t('Checkerboard'), False); grid.listItems.add(t('Staggered (Brick)'), True)
        shift = inputs.addDropDownCommandInput('shift_dir', t('Shift Direction'), 1)
        shift.listItems.add(t('Rows (Horizontal)'), True); shift.listItems.add(t('Columns (Vertical)'), False); shift.isVisible = False
        interlock = inputs.addBoolValueInput('interlock', t('Vertical Interlocking'), True, '', False); interlock.isVisible = False
        inputs.addValueInput('radius', t('Base Radius (R)'), 'mm', adsk.core.ValueInput.createByReal(0.5))
        inputs.addValueInput('spacing', t('Spacing (mm)'), 'mm', adsk.core.ValueInput.createByReal(0.1))
        inputs.addValueInput('margin', t('Margin (mm)'), 'mm', adsk.core.ValueInput.createByReal(0.5))
        rhs = inputs.addIntegerSliderCommandInput('rect_h_scale', t('Rectangle Height (%)'), 10, 500, False)
        rhs.valueOne = 100; rhs.isVisible = False
        sl = inputs.addValueInput('slot_len', t('Slot Length'), 'mm', adsk.core.ValueInput.createByReal(1.0)); sl.isVisible = False
        so = inputs.addDropDownCommandInput('slot_orient', t('Slot Orientation'), 1)
        so.listItems.add(t('Vertical'), True); so.listItems.add(t('Horizontal'), False); so.isVisible = False
        preview_btn = inputs.addBoolValueInput('preview_btn', t('Generate / Refresh Preview'), False, '', True)
        preview_btn.isFullWidth = True
        onExec = WallExecute(); cmd.execute.add(onExec); _handlers.append(onExec)
        onPrev = WallPreview(); cmd.executePreview.add(onPrev); _handlers.append(onPrev)
        onChg = WallInputChanged(); cmd.inputChanged.add(onChg); _handlers.append(onChg)


# ==========================================
# 3. PM: CYLINDER (CIRCUMFERENTIAL MODULE)
# ==========================================
def execute_cylinder_engine(inputs):
    face_in = inputs.itemById('face_select')
    if face_in.selectionCount == 0: return
    design = adsk.fusion.Design.cast(_app.activeProduct); rootComp = design.rootComponent
    face_sel = face_in.selection(0).entity
    cyl = face_sel.geometry; axis, R = cyl.axis, cyl.radius; C = 2 * math.pi * R
    density = inputs.itemById('density').valueOne; spacing = inputs.itemById('spacing').value; margin = inputs.itemById('margin').value
    slot_len = inputs.itemById('slot_len').value if inputs.itemById('slot_len').isVisible else 0
    shape_type = key(inputs.itemById('shape_type').selectedItem.name)
    slot_horizontal = (key(inputs.itemById('slot_orient').selectedItem.name) == 'Horizontal') if inputs.itemById('slot_orient').isVisible else False
    rect_h_scale = inputs.itemById('rect_h_scale').valueOne if inputs.itemById('rect_h_scale').isVisible else 100
    is_interlock = inputs.itemById('interlock').value if inputs.itemById('interlock').isVisible else False
    if shape_type == 'Hexagon': grid_type, shift_dir = 'Staggered (Brick)', 'Rows (Horizontal)'
    else: grid_type = key(inputs.itemById('grid_type').selectedItem.name); shift_dir = key(inputs.itemById('shift_dir').selectedItem.name) if inputs.itemById('shift_dir').isVisible else 'Rows (Horizontal)'
    is_staggered_grid = ('Staggered' in grid_type)
    if is_staggered_grid and density % 2 != 0: density += 1
    dx = C / density
    if shape_type == 'Hexagon': r = (dx - spacing)/math.sqrt(3); dy = 1.5*r + (spacing*math.sqrt(3)/2)
    else:
        eff_dx = (dx / 2.0) if is_interlock else dx
        r = (eff_dx - slot_len - spacing)/2.0 if (shape_type == 'Slot' and slot_horizontal) else (eff_dx - spacing)/2.0
        if r < 0.01: r = 0.01
        h_shape = (r*2)*(rect_h_scale/100.0) if shape_type == 'Rect / Square' else ((r*2) if slot_horizontal else slot_len + r*2) if shape_type == 'Slot' else r*2
        dy = (h_shape + spacing) / 2.0 if is_interlock else (h_shape + spacing)
    bbox = face_sel.boundingBox
    cyl_height = (bbox.maxPoint.x - bbox.minPoint.x) if abs(axis.x) > 0.5 else (bbox.maxPoint.y - bbox.minPoint.y) if abs(axis.y) > 0.5 else (bbox.maxPoint.z - bbox.minPoint.z)
    planes = rootComp.constructionPlanes; planeInput = planes.createInput()
    pt_on_face = face_sel.pointOnFace
    planeInput.setByTangentAtPoint(face_sel, pt_on_face)
    tangentPlane = planes.add(planeInput)
    sk2 = rootComp.sketches.add(tangentPlane); sk2.isComputeDeferred = True
    pt_axis = adsk.core.Point3D.create(pt_on_face.x + axis.x, pt_on_face.y + axis.y, pt_on_face.z + axis.z)
    orig_2d, axis_2d = sk2.modelToSketchSpace(pt_on_face), sk2.modelToSketchSpace(pt_axis)
    is_rotated = abs(axis_2d.x - orig_2d.x) > abs(axis_2d.y - orig_2d.y)
    mid_3d = adsk.core.Point3D.create((bbox.minPoint.x+bbox.maxPoint.x)/2, (bbox.minPoint.y+bbox.maxPoint.y)/2, (bbox.minPoint.z+bbox.maxPoint.z)/2)
    mid_2d = sk2.modelToSketchSpace(mid_3d)
    rows = int((cyl_height - (2 * margin)) / dy)
    if rows < 1: rows = 1
    start_cz = -((rows - 1) * dy) / 2.0
    for r_idx in range(rows):
        for c_idx in range(density):
            xs = (dx / 2.0) if (is_staggered_grid and shift_dir == 'Rows (Horizontal)' and r_idx % 2 != 0) else 0
            ys = (dy / 2.0) if (is_staggered_grid and shift_dir == 'Columns (Vertical)' and c_idx % 2 != 0) else 0
            cx = -C/2.0 + (c_idx + 0.5) * dx + xs
            if cx >= C/2.0: cx -= C
            if cx < -C/2.0: cx += C
            cz = start_cz + r_idx * dy + ys
            if is_rotated: draw_shape(sk2, shape_type, mid_2d.x + cz, mid_2d.y + cx, r, slot_len, not is_rotated, slot_horizontal, rect_h_scale)
            else: draw_shape(sk2, shape_type, mid_2d.x + cx, mid_2d.y + cz, r, slot_len, is_rotated, slot_horizontal, rect_h_scale)
    sk2.isComputeDeferred = False

class CylPreview(adsk.core.CommandEventHandler):
    def __init__(self): super().__init__()
    def notify(self, args):
        if _preview_flags['cyl']:
            try: execute_cylinder_engine(args.firingEvent.sender.commandInputs)
            except: pass

class CylExecute(adsk.core.CommandEventHandler):
    def __init__(self): super().__init__()
    def notify(self, args):
        try: execute_cylinder_engine(args.firingEvent.sender.commandInputs)
        except: _ui.messageBox(traceback.format_exc())

class CylInputChanged(adsk.core.InputChangedEventHandler):
    def __init__(self): super().__init__()
    def notify(self, args):
        try:
            inputs = args.inputs; changed_id = args.input.id
            _preview_flags['cyl'] = (changed_id == 'preview_btn')
            shape = key(inputs.itemById('shape_type').selectedItem.name)
            inputs.itemById('slot_len').isVisible = inputs.itemById('slot_orient').isVisible = (shape == 'Slot')
            inputs.itemById('rect_h_scale').isVisible = (shape == 'Rect / Square')
            grid = inputs.itemById('grid_type'); shift = inputs.itemById('shift_dir')
            if shape == 'Hexagon': grid.listItems.item(1).isSelected = True; grid.isEnabled = shift.isVisible = False
            else: grid.isEnabled = True; shift.isVisible = ('Staggered' in key(grid.selectedItem.name))
            inputs.itemById('interlock').isVisible = (shift.isVisible and shape != 'Hexagon')
        except: pass

class CylCreated(adsk.core.CommandCreatedEventHandler):
    def __init__(self): super().__init__()
    def notify(self, args):
        cmd = args.command; inputs = cmd.commandInputs
        sel = inputs.addSelectionInput('face_select', t('Cylinder Face'), t('Select'))
        sel.addSelectionFilter('Faces'); sel.setSelectionLimits(1,1)
        shape = inputs.addDropDownCommandInput('shape_type', t('Shape'), 1)
        [shape.listItems.add(t(n), n=='Hexagon') for n in ['Hexagon', 'Circle', 'Rect / Square', 'Slot']]
        grid = inputs.addDropDownCommandInput('grid_type', t('Grid Type'), 1)
        grid.listItems.add(t('Checkerboard'), False); grid.listItems.add(t('Staggered (Brick)'), True)
        shift = inputs.addDropDownCommandInput('shift_dir', t('Shift Direction'), 1)
        shift.listItems.add(t('Rows (Horizontal)'), True); shift.listItems.add(t('Columns (Vertical)'), False); shift.isVisible = False
        interlock = inputs.addBoolValueInput('interlock', t('Vertical Interlocking'), True, '', False); interlock.isVisible = False
        inputs.addIntegerSliderCommandInput('density', t('Density (Columns)'), 2, 200, False).valueOne = 20
        inputs.addValueInput('spacing', t('Spacing (mm)'), 'mm', adsk.core.ValueInput.createByReal(0.1))
        inputs.addValueInput('margin', t('Margin (mm)'), 'mm', adsk.core.ValueInput.createByReal(0.5))
        rhs = inputs.addIntegerSliderCommandInput('rect_h_scale', t('Rectangle Height (%)'), 10, 500, False); rhs.valueOne = 100; rhs.isVisible = False
        sl = inputs.addValueInput('slot_len', t('Slot Length'), 'mm', adsk.core.ValueInput.createByReal(1.0)); sl.isVisible = False
        so = inputs.addDropDownCommandInput('slot_orient', t('Slot Orientation'), 1)
        so.listItems.add(t('Vertical'), True); so.listItems.add(t('Horizontal'), False); so.isVisible = False
        preview_btn = inputs.addBoolValueInput('preview_btn', t('Generate / Refresh Preview'), False, '', True); preview_btn.isFullWidth = True
        onExec = CylExecute(); cmd.execute.add(onExec); _handlers.append(onExec)
        onPrev = CylPreview(); cmd.executePreview.add(onPrev); _handlers.append(onPrev)
        onChg = CylInputChanged(); cmd.inputChanged.add(onChg); _handlers.append(onChg)


# ==========================================
# 4. PM: MULTI (MULTI-FACE MODULE)
# ==========================================
def execute_multi_engine(inputs):
    v_in = inputs.itemById('v_edge'); h_in = inputs.itemById('h_edge'); faces_in = inputs.itemById('faces_select')
    if v_in.selectionCount == 0 or h_in.selectionCount == 0 or faces_in.selectionCount == 0: return
    design = adsk.fusion.Design.cast(_app.activeProduct); root = design.rootComponent
    v_edge = v_in.selection(0).entity; h_edge = h_in.selection(0).entity
    first_face = faces_in.selection(0).entity; test_pt_3d = first_face.pointOnFace
    _, p_start, p_end = v_edge.evaluator.getEndPoints(); h_total = p_start.distanceTo(p_end)
    total_area = sum([faces_in.selection(i).entity.area for i in range(faces_in.selectionCount)])
    C = (total_area / h_total) - 0.001
    planes = root.constructionPlanes; p_input = planes.createInput()
    p_input.setByTwoEdges(v_edge, h_edge)
    target_plane = planes.add(p_input); sk = root.sketches.add(target_plane); sk.isComputeDeferred = True
    p_start_sk = sk.modelToSketchSpace(p_start); p_end_sk = sk.modelToSketchSpace(p_end)
    sk_vec_x = p_end_sk.x - p_start_sk.x; sk_vec_y = p_end_sk.y - p_start_sk.y
    is_rotated = abs(sk_vec_x) > abs(sk_vec_y)
    v_mid_3d = adsk.core.Point3D.create((p_start.x + p_end.x)/2, (p_start.y + p_end.y)/2, (p_start.z + p_end.z)/2)
    v_mid_2d = sk.modelToSketchSpace(v_mid_3d)
    base_cx = v_mid_2d.y if is_rotated else v_mid_2d.x
    base_cy = v_mid_2d.x if is_rotated else v_mid_2d.y
    shape_type = key(inputs.itemById('shape_type').selectedItem.name)
    grid_type = key(inputs.itemById('grid_type').selectedItem.name)
    pattern_align = key(inputs.itemById('pattern_align').selectedItem.name)
    is_staggered_grid = ('Staggered' in grid_type)
    density = inputs.itemById('density').valueOne
    if is_staggered_grid and density % 2 != 0: density += 1
    spacing = inputs.itemById('spacing').value; margin = inputs.itemById('margin').value
    slot_len = inputs.itemById('slot_len').value if inputs.itemById('slot_len').isVisible else 0
    slot_horizontal = (key(inputs.itemById('slot_orient').selectedItem.name) == 'Horizontal') if inputs.itemById('slot_orient').isVisible else False
    rect_h_scale = inputs.itemById('rect_h_scale').valueOne if inputs.itemById('rect_h_scale').isVisible else 100
    is_interlock = inputs.itemById('interlock').value if inputs.itemById('interlock').isVisible else False
    dx = C / density
    if shape_type == 'Hexagon': r = (dx - spacing)/math.sqrt(3); dy = 1.5*r + (spacing*math.sqrt(3)/2)
    else:
        eff_dx = (dx / 2.0) if is_interlock else dx
        r = (eff_dx - slot_len - spacing)/2.0 if (shape_type == 'Slot' and slot_horizontal) else (eff_dx - spacing)/2.0
        if r < 0.01: r = 0.01
        h_shape = (r*2)*(rect_h_scale/100.0) if shape_type == 'Rect / Square' else ((r*2) if slot_horizontal else slot_len + r*2) if shape_type == 'Slot' else r*2
        dy = (h_shape + spacing) / 2.0 if is_interlock else (h_shape + spacing)
    rows = int((h_total - 2*margin) / dy); rows = rows if rows > 0 else 1
    start_cy = base_cy - ((rows - 1) * dy / 2.0)
    test_pt_sk = sk.modelToSketchSpace(test_pt_3d)
    test_x = test_pt_sk.y if is_rotated else test_pt_sk.x
    dir_x = 1.0 if test_x >= base_cx else -1.0
    drawn_pts = set()
    for r_idx in range(rows):
        is_stagg = (is_staggered_grid and r_idx % 2 != 0)
        count = density + 1 if is_stagg else density
        for c_idx in range(count):
            if pattern_align == 'Symmetrical (Center)':
                xs = dx/2.0 if is_stagg else 0
                cx = -C/2.0 + (c_idx * dx) - xs
                if cx > C/2.0 + 0.001: cx -= C
                if cx < -C/2.0 - 0.001: cx += C
            else:
                xs = dx/2.0 if is_stagg else 0
                offset = margin + (c_idx * dx) + xs
                cx = offset if dir_x == 1.0 else -offset
            draw_cx = base_cx + cx; draw_cy = start_cy + (r_idx * dy)
            pt_key = (round(draw_cx, 3), round(draw_cy, 3))
            if pt_key not in drawn_pts:
                draw_shape(sk, shape_type, draw_cx, draw_cy, r, slot_len, is_rotated, slot_horizontal, rect_h_scale)
                drawn_pts.add(pt_key)
    sk.isComputeDeferred = False

class MultiPreview(adsk.core.CommandEventHandler):
    def __init__(self): super().__init__()
    def notify(self, args):
        if _preview_flags['multi']:
            try: execute_multi_engine(args.firingEvent.sender.commandInputs)
            except: pass

class MultiExecute(adsk.core.CommandEventHandler):
    def __init__(self): super().__init__()
    def notify(self, args):
        try: execute_multi_engine(args.firingEvent.sender.commandInputs)
        except: _ui.messageBox(traceback.format_exc())

class MultiInputChanged(adsk.core.InputChangedEventHandler):
    def __init__(self): super().__init__()
    def notify(self, args):
        try:
            inputs = args.inputs; changed_id = args.input.id
            _preview_flags['multi'] = (changed_id == 'preview_btn')
            shape = key(inputs.itemById('shape_type').selectedItem.name)
            inputs.itemById('slot_len').isVisible = inputs.itemById('slot_orient').isVisible = (shape == 'Slot')
            inputs.itemById('rect_h_scale').isVisible = (shape == 'Rect / Square')
            grid = inputs.itemById('grid_type')
            if shape == 'Hexagon': grid.listItems.item(1).isSelected = True; grid.isEnabled = False
            else: grid.isEnabled = True
            inputs.itemById('interlock').isVisible = (('Staggered' in key(grid.selectedItem.name)) and shape != 'Hexagon')
        except: pass

class MultiCreated(adsk.core.CommandCreatedEventHandler):
    def __init__(self): super().__init__()
    def notify(self, args):
        cmd = args.command; inputs = cmd.commandInputs
        v = inputs.addSelectionInput('v_edge', t('1. Vertical Axis (H)'), 'H'); v.addSelectionFilter('LinearEdges'); v.setSelectionLimits(1,1)
        h = inputs.addSelectionInput('h_edge', t('2. Horizontal Axis (X)'), 'X'); h.addSelectionFilter('LinearEdges'); h.setSelectionLimits(1,1)
        f = inputs.addSelectionInput('faces_select', t('3. Perimeter Faces'), t('Faces')); f.addSelectionFilter('Faces'); f.setSelectionLimits(1, 0)
        align = inputs.addDropDownCommandInput('pattern_align', t('Alignment (Vertical Axis)'), 1)
        align.listItems.add(t('Symmetrical (Center)'), True); align.listItems.add(t('From Axis (Start)'), False)
        shape = inputs.addDropDownCommandInput('shape_type', t('Shape'), 1)
        [shape.listItems.add(t(n), n=='Hexagon') for n in ['Hexagon', 'Circle', 'Rect / Square', 'Slot']]
        grid = inputs.addDropDownCommandInput('grid_type', t('Grid Type'), 1)
        grid.listItems.add(t('Checkerboard'), False); grid.listItems.add(t('Staggered (Brick)'), True)
        interlock = inputs.addBoolValueInput('interlock', t('Vertical Interlocking'), True, '', False); interlock.isVisible = False
        inputs.addIntegerSliderCommandInput('density', t('Density (Columns)'), 2, 200, False).valueOne = 20
        inputs.addValueInput('spacing', t('Spacing (mm)'), 'mm', adsk.core.ValueInput.createByReal(0.1))
        inputs.addValueInput('margin', t('Margin (mm)'), 'mm', adsk.core.ValueInput.createByReal(0.5))
        rhs = inputs.addIntegerSliderCommandInput('rect_h_scale', t('Rectangle Height (%)'), 10, 500, False); rhs.valueOne = 100; rhs.isVisible = False
        sl = inputs.addValueInput('slot_len', t('Slot Length'), 'mm', adsk.core.ValueInput.createByReal(1.0)); sl.isVisible = False
        so = inputs.addDropDownCommandInput('slot_orient', t('Slot Orientation'), 1)
        so.listItems.add(t('Vertical'), True); so.listItems.add(t('Horizontal'), False); so.isVisible = False
        preview_btn = inputs.addBoolValueInput('preview_btn', t('Generate / Refresh Preview'), False, '', True); preview_btn.isFullWidth = True
        onExec = MultiExecute(); cmd.execute.add(onExec); _handlers.append(onExec)
        onPrev = MultiPreview(); cmd.executePreview.add(onPrev); _handlers.append(onPrev)
        onChg = MultiInputChanged(); cmd.inputChanged.add(onChg); _handlers.append(onChg)


# ==========================================
# MAIN ADD-IN MECHANICS (UI REGISTRATION)
# ==========================================
def run(context):
    try:
        select_language(_ui)

        script_dir = os.path.dirname(os.path.realpath(__file__))

        res_main = os.path.join(script_dir, 'resources')
        res_wall = os.path.join(script_dir, 'resources', 'wall')
        res_cyl = os.path.join(script_dir, 'resources', 'cylinder')
        res_multi = os.path.join(script_dir, 'resources', 'multi')

        panel = _ui.allToolbarPanels.itemById('SolidCreatePanel')

        for cmd_id in ['PM_Wall_Cmd', 'PM_Cyl_Cmd', 'PM_Multi_Cmd']:
            cmd = _ui.commandDefinitions.itemById(cmd_id)
            if cmd: cmd.deleteMe()
        old_drop = panel.controls.itemById('PM_DropDown')
        if old_drop: old_drop.deleteMe()

        cmdWall = _ui.commandDefinitions.addButtonDefinition('PM_Wall_Cmd', t('PM: Wall'), t('wall_tooltip'), res_wall)
        cmdWall.tooltipDescription = t('wall_tooltip_desc')
        onWallCreated = WallCreated(); cmdWall.commandCreated.add(onWallCreated); _handlers.append(onWallCreated)

        cmdCyl = _ui.commandDefinitions.addButtonDefinition('PM_Cyl_Cmd', t('PM: Cylinder'), t('cyl_tooltip'), res_cyl)
        cmdCyl.tooltipDescription = t('cyl_tooltip_desc')
        onCylCreated = CylCreated(); cmdCyl.commandCreated.add(onCylCreated); _handlers.append(onCylCreated)

        cmdMulti = _ui.commandDefinitions.addButtonDefinition('PM_Multi_Cmd', t('PM: Multi'), t('multi_tooltip'), res_multi)
        cmdMulti.tooltipDescription = t('multi_tooltip_desc')
        onMultiCreated = MultiCreated(); cmdMulti.commandCreated.add(onMultiCreated); _handlers.append(onMultiCreated)

        dropControl = panel.controls.addDropDown(t('Pattern Maker'), res_main, 'PM_DropDown')
        dropControl.controls.addCommand(cmdWall)
        dropControl.controls.addCommand(cmdCyl)
        dropControl.controls.addCommand(cmdMulti)

        dropControl.isPromotedByDefault = True
        dropControl.isPromoted = True

    except: _ui.messageBox(traceback.format_exc())

def stop(context):
    try:
        panel = _ui.allToolbarPanels.itemById('SolidCreatePanel')
        dropControl = panel.controls.itemById('PM_DropDown')
        if dropControl: dropControl.deleteMe()
        for cmd_id in ['PM_Wall_Cmd', 'PM_Cyl_Cmd', 'PM_Multi_Cmd']:
            cmd = _ui.commandDefinitions.itemById(cmd_id)
            if cmd: cmd.deleteMe()
    except: pass
