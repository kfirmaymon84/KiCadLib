import pcbnew
import wx
import os


TEXT_CLASSES = ("FP_TEXT", "PCB_TEXT", "PCB_TEXT_BOX", "FP_TEXTBOX")


def _get_angle(item):
    try:
        return item.GetTextAngle().AsDegrees()
    except AttributeError:
        return item.GetTextAngleDegrees()


def _set_angle(item, degrees):
    try:
        item.SetTextAngle(pcbnew.EDA_ANGLE(degrees, pcbnew.DEGREES_T))
    except AttributeError:
        item.SetTextAngleDegrees(degrees)


def _get_size(item):
    sz = item.GetTextSize()
    return pcbnew.ToMM(sz.x), pcbnew.ToMM(sz.y)


def _set_size(item, w_mm, h_mm):
    item.SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(w_mm), pcbnew.FromMM(h_mm)))


def _get_thickness(item):
    return pcbnew.ToMM(item.GetTextThickness())


def _set_thickness(item, mm):
    item.SetTextThickness(pcbnew.FromMM(mm))


def _circle_of(item):
    """Return (cx, cy, r) in mm for a fab circle, else None.

    The radius includes half the stroke width so it matches the drawn edge.
    """
    try:
        if item.GetShape() != pcbnew.SHAPE_T_CIRCLE:
            return None
    except AttributeError:
        return None
    center = item.GetCenter()
    try:
        r_iu = item.GetRadius()
    except AttributeError:
        # Fall back to half the bounding-box width
        r_iu = item.GetBoundingBox().GetWidth() / 2
    try:
        r_iu += item.GetWidth() / 2
    except AttributeError:
        pass
    return pcbnew.ToMM(center.x), pcbnew.ToMM(center.y), pcbnew.ToMM(r_iu)


def _fab_outline_boxes(shape_items):
    """Reconstruct candidate outline bounding boxes from fab-layer shapes.

    Fab outlines (including nested rectangles) are usually drawn as separate
    line segments, so an individual segment's bounding box is a thin sliver
    that never encloses the centered text. Group segments that share corners
    into connected components and merge each component's bbox back into a full
    rectangle. Closed rect / poly / arc shapes already have a meaningful bbox
    and are kept as-is. Circles are excluded here — they are treated as
    obstacles (see _circle_of) rather than outline candidates.
    """
    boxes = []
    segments = []
    for it in shape_items:
        try:
            stype = it.GetShape()
        except AttributeError:
            stype = None
        if stype == pcbnew.SHAPE_T_SEGMENT:
            segments.append(it)
        elif stype == pcbnew.SHAPE_T_CIRCLE:
            continue  # obstacle, not an outline
        else:
            boxes.append(it.GetBoundingBox())

    if segments:
        tol = pcbnew.FromMM(0.02)

        def corner_key(pt):
            return (round(pt.x / tol), round(pt.y / tol))

        parent = list(range(len(segments)))

        def find(a):
            while parent[a] != a:
                parent[a] = parent[parent[a]]
                a = parent[a]
            return a

        def union(a, b):
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[ra] = rb

        corner_to_segs = {}
        for i, seg in enumerate(segments):
            for pt in (seg.GetStart(), seg.GetEnd()):
                corner_to_segs.setdefault(corner_key(pt), []).append(i)
        for idxs in corner_to_segs.values():
            for j in idxs[1:]:
                union(idxs[0], j)

        comp_bbox = {}
        for i, seg in enumerate(segments):
            root = find(i)
            bb = seg.GetBoundingBox()
            if root in comp_bbox:
                comp_bbox[root].Merge(bb)
            else:
                comp_bbox[root] = bb
        boxes.extend(comp_bbox.values())

    return boxes


def _bbox_contains(bb, pos):
    return (bb.GetLeft() <= pos.x <= bb.GetRight()
            and bb.GetTop() <= pos.y <= bb.GetBottom())


def _bbox_area(bb):
    return bb.GetWidth() * bb.GetHeight()


class FabToolboxDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title="Fab Layers Toolbox", size=(300, 160))

        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        auto_btn = wx.Button(panel, label="Auto Orient F.Fab / B.Fab")
        auto_btn.SetToolTip("180°→0°, 90°→270° on F.Fab and B.Fab; disables Keep Upright")
        vbox.Add(auto_btn, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)
        auto_btn.Bind(wx.EVT_BUTTON, self._on_auto_orient)

        fit_btn = wx.Button(panel, label="Fit Text to Fab Outline")
        fit_btn.SetToolTip("Scale each ${REFERENCE} text to fill the footprint's Fab outline")
        vbox.Add(fit_btn, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 6)
        fit_btn.Bind(wx.EVT_BUTTON, self._on_fit_text)

        vbox.Add(wx.StaticLine(panel), 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)

        btn_sizer = wx.StdDialogButtonSizer()
        close_btn = wx.Button(panel, wx.ID_CANCEL, "Close")
        btn_sizer.AddButton(close_btn)
        btn_sizer.Realize()
        vbox.Add(btn_sizer, 0, wx.ALIGN_CENTER | wx.ALL, 10)

        panel.SetSizer(vbox)
        self.SetClientSize(panel.GetBestSize())

    def _on_auto_orient(self, event):
        board = pcbnew.GetBoard()
        changed = 0
        FAB_LAYERS = {"F.Fab", "B.Fab"}
        REMAP = {180.0: 0.0, 90.0: 270.0}

        for fp in board.GetFootprints():
            for item in list(fp.GraphicalItems()) + [fp.Reference(), fp.Value()]:
                if item is None:
                    continue
                if item.GetClass() not in TEXT_CLASSES:
                    continue
                if item.GetLayerName() not in FAB_LAYERS:
                    continue
                a = round(_get_angle(item) % 360, 2)
                if a in REMAP:
                    _set_angle(item, REMAP[a])
                    changed += 1
                try:
                    item.SetKeepUpright(False)
                except AttributeError:
                    pass
            try:
                fp.SetModified()
            except AttributeError:
                pass

        board.SetModified()
        pcbnew.Refresh()
        wx.MessageBox(
            f"Auto Orient complete.\n{changed} text item(s) reoriented on F.Fab / B.Fab.",
            "Done", wx.OK | wx.ICON_INFORMATION
        )

    def _on_fit_text(self, event):
        board = pcbnew.GetBoard()
        # Fixed clearance (mm, per side) kept between the text and the fab
        # outline. Using an absolute gap instead of a percentage lets the text
        # grow as large as possible while never touching the rectangle, and
        # behaves consistently across large and small footprints.
        CLEARANCE_MM = 0.15
        FAB_LAYER_NAMES = {"F.Fab", "B.Fab"}

        for fp in board.GetFootprints():
            # Collect fab outline shape items per layer using layer name
            # (avoids pcbnew.F_Fab constant which may differ across versions)
            fab_items_by_layer = {"F.Fab": [], "B.Fab": []}
            text_items_by_layer = {"F.Fab": [], "B.Fab": []}

            for item in fp.GraphicalItems():
                lyr_name = item.GetLayerName()
                if lyr_name not in FAB_LAYER_NAMES:
                    continue
                if item.GetClass() in TEXT_CLASSES:
                    # The "${REFERENCE}" text variable item (fp_text on the fab
                    # layer) is the one we resize — not the Reference property
                    # itself, which normally lives on silkscreen.
                    try:
                        raw_text = item.GetText()
                    except AttributeError:
                        raw_text = ""
                    if raw_text == "${REFERENCE}":
                        text_items_by_layer[lyr_name].append(item)
                    continue
                fab_items_by_layer[lyr_name].append(item)

            # Reconstruct full outline boxes (segments grouped into rectangles)
            fab_boxes_by_layer = {
                lyr: [bb for bb in _fab_outline_boxes(items) if _bbox_area(bb) > 0]
                for lyr, items in fab_items_by_layer.items()
            }
            # Circles inside the fab outline are obstacles the text must avoid.
            fab_circles_by_layer = {
                lyr: [c for c in (_circle_of(it) for it in items) if c and c[2] > 0]
                for lyr, items in fab_items_by_layer.items()
            }

            if not any(fab_boxes_by_layer.values()) and not any(fab_circles_by_layer.values()):
                continue

            for lyr_name, items in text_items_by_layer.items():
                boxes = fab_boxes_by_layer[lyr_name]
                circles = fab_circles_by_layer[lyr_name]
                if not items:
                    continue
                if not boxes:
                    # No rectangular outline — a lone circle IS the outline, so
                    # use its bounding box and don't treat it as an obstacle.
                    boxes = [it.GetBoundingBox() for it in fab_items_by_layer[lyr_name]
                             if _circle_of(it)]
                    boxes = [bb for bb in boxes if _bbox_area(bb) > 0]
                    if not boxes:
                        continue
                    circles = []

                for item in items:
                    # Constrain to the smallest reconstructed outline that
                    # actually encloses the text (handles nested rectangles,
                    # e.g. an inner + outer box). Falls back to the largest
                    # outline if none contain the text position.
                    pos = item.GetPosition()
                    containing = [bb for bb in boxes if _bbox_contains(bb, pos)]
                    if containing:
                        chosen = min(containing, key=_bbox_area)
                    else:
                        chosen = max(boxes, key=_bbox_area)

                    avail_w = max(pcbnew.ToMM(chosen.GetWidth()) - 2 * CLEARANCE_MM, 0.01)
                    avail_h = max(pcbnew.ToMM(chosen.GetHeight()) - 2 * CLEARANCE_MM, 0.01)

                    # Keep the (centered-on-anchor) text clear of any circle
                    # that sits inside the chosen outline. For each circle we
                    # shrink whichever axis leaves the larger usable area, so
                    # the text stops before the circle instead of overlapping.
                    px = pcbnew.ToMM(pos.x)
                    py = pcbnew.ToMM(pos.y)
                    for cx, cy, r in circles:
                        if not _bbox_contains(chosen, pcbnew.VECTOR2I(
                                pcbnew.FromMM(cx), pcbnew.FromMM(cy))):
                            continue
                        reach = r + CLEARANCE_MM
                        w_lim = 2 * (abs(cx - px) - reach)
                        h_lim = 2 * (abs(cy - py) - reach)
                        if w_lim <= 0 and h_lim <= 0:
                            continue  # circle covers the anchor; can't avoid it
                        area_w = min(avail_w, w_lim) * avail_h if w_lim > 0 else -1
                        area_h = avail_w * min(avail_h, h_lim) if h_lim > 0 else -1
                        if area_w >= area_h and w_lim > 0:
                            avail_w = min(avail_w, w_lim)
                        elif h_lim > 0:
                            avail_h = min(avail_h, h_lim)

                    try:
                        text_str = item.GetShownText(False)
                    except TypeError:
                        text_str = item.GetShownText()

                    n_chars = max(len(text_str), 1)
                    cur_w, cur_h = _get_size(item)  # mm

                    text_w = cur_w * n_chars
                    text_h = cur_h

                    angle = round(_get_angle(item) % 360)
                    if angle in (90, 270):
                        text_w, text_h = text_h, text_w

                    if text_w <= 0 or text_h <= 0:
                        continue

                    scale = min(avail_w / text_w, avail_h / text_h)
                    new_size = _snap_size(cur_h * scale)
                    size_scale = new_size / cur_h if cur_h > 0 else 1.0

                    cur_thickness = _get_thickness(item)
                    raw_thickness = cur_thickness * size_scale
                    thickness_hi = max(0.05, 0.3 * new_size)
                    new_thickness = _snap_size(raw_thickness, step=0.05, lo=0.05, hi=thickness_hi)

                    _set_size(item, new_size, new_size)
                    _set_thickness(item, new_thickness)

            try:
                fp.SetModified()
            except AttributeError:
                pass

        board.SetModified()
        pcbnew.Refresh()


def _snap_size(mm, step=0.1, lo=0.3, hi=3.0):
    """Round to nearest step, then clamp to [lo, hi]."""
    snapped = round(round(mm / step) * step, 10)
    return max(lo, min(hi, snapped))


class FabLayersToolboxPlugin(pcbnew.ActionPlugin):
    def defaults(self):
        self.name = "Fab Layers Toolbox"
        self.category = "Modify PCB"
        self.description = "Auto-orient and fit ${REFERENCE} text on F.Fab / B.Fab layers"
        self.show_toolbar_button = True
        self.icon_file_name = os.path.join(os.path.dirname(__file__), "icon.png")
        self.dark_icon_file_name = self.icon_file_name

    def Run(self):
        frame = wx.FindWindowByName("PcbFrame")
        dlg = FabToolboxDialog(frame)
        dlg.ShowModal()
        dlg.Destroy()
