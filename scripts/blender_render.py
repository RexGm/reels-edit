"""Tek bir JSON tarifinden alfa kanallı 3D öğe render eder (Blender 4.2+ / 5.x).

Çalıştırma:
    blender -b --factory-startup -P blender_render.py -- tarif.json
    (macOS: /Applications/Blender.app/Contents/MacOS/Blender)

Tarif alanları (hepsi isteğe bağlı, "scene" hariç):
{
  "scene": "text3d" | "orbit" | "card" | "phone" | "keycap" | "svg",
  "output": "library/3d/proof-red",     # klasör; içine frames/, <ad>.webm|mov, poster.png, meta.json yazılır
  "name": "proof-red",
  "width": 1080, "height": 1920, "fps": 30, "duration": 3.0,   # duration 0 = tek kare PNG
  "engine": "eevee" | "cycles", "samples": 64,
  "format": "webm" | "mov" | "png",      # webm = VP9 alfa, mov = ProRes 4444 alfa, png = sadece kareler
  "material": "red" | "gold" | "chrome" | "silver" | "white" | "black" | "glass" | "#RRGGBB",
  "camera": {"move": "static" | "push" | "orbit", "distance": 8, "lens": 50, "tilt": 0},
  "animation": "rise" | "drop" | "spin" | "float" | "fly" | "turn" | "press" | "none",
  "frame_fill": 0.8,                     # öğenin kare genişliğini doldurma oranı

  # text3d
  "text": "PROOF", "font": "/yol/Anton-Regular.ttf", "extrude": 0.12, "bevel": 0.02, "italic_skew": 0.0,
  # orbit
  "count": 7, "radius": 2.2, "sphere_size": 0.28, "turns": 0.5, "ring": true, "tilt_deg": 72,
  "split_depth": false,                  # true: ön ve arka yarıyı ayrı render eder (kişinin arkasından geçsin diye)
  # card / phone
  "image": "/yol/gorsel.png", "video": "/yol/ekran.mp4", "card_width": 3.0,
  # keycap
  "label": "⌘", "label_color": "#1A1A1A",
  # svg
  "svg": "/yol/ikon.svg"
}
Sonuç klasöründeki meta.json, scripts/library.py add için hazır bilgiyi içerir.
"""
import json
import math
import os
import shutil
import subprocess
import sys

import bpy

# ---------------------------------------------------------------- yardımcılar

def argv_spec():
    argv = sys.argv
    if "--" not in argv:
        sys.exit("Kullanım: blender -b -P blender_render.py -- tarif.json")
    path = argv[argv.index("--") + 1]
    with open(path) as f:
        spec = json.load(f)
    spec["_spec_path"] = os.path.abspath(path)
    return spec


def srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(srgb_to_linear(int(h[i:i + 2], 16) / 255) for i in (0, 2, 4))


def set_input(node, names, value):
    """Principled BSDF giriş adları sürümden sürüme değişiyor; ilk bulunanı ayarla."""
    for n in names if isinstance(names, (list, tuple)) else [names]:
        if n in node.inputs:
            node.inputs[n].default_value = value
            return True
    return False


PRESETS = {
    "red":    dict(color=(0.62, 0.012, 0.03), metallic=0.0, roughness=0.32, coat=0.6),
    "gold":   dict(color=(1.0, 0.70, 0.30), metallic=1.0, roughness=0.22),
    "chrome": dict(color=(0.96, 0.96, 0.97), metallic=1.0, roughness=0.12),
    "silver": dict(color=(0.90, 0.90, 0.92), metallic=1.0, roughness=0.35),
    "white":  dict(color=(0.85, 0.85, 0.83), metallic=0.0, roughness=0.35, coat=0.3),
    "black":  dict(color=(0.01, 0.01, 0.012), metallic=0.0, roughness=0.25, coat=0.8),
    "glass":  dict(color=(0.95, 0.97, 1.0), metallic=0.0, roughness=0.04, transmission=1.0),
}


def make_material(name, kind="white"):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    if isinstance(kind, str) and kind.startswith("#"):
        p = dict(color=hex_rgb(kind), metallic=0.0, roughness=0.32, coat=0.4)
    else:
        p = PRESETS.get(kind, PRESETS["white"])
    set_input(bsdf, "Base Color", (*p["color"], 1.0))
    set_input(bsdf, "Metallic", p.get("metallic", 0.0))
    set_input(bsdf, "Roughness", p.get("roughness", 0.4))
    if p.get("coat"):
        set_input(bsdf, ["Coat Weight", "Clearcoat"], p["coat"])
    if p.get("transmission"):
        set_input(bsdf, ["Transmission Weight", "Transmission"], p["transmission"])
        set_input(bsdf, "IOR", 1.45)
    return mat


def image_material(name, path, movie=False, frames=1):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    tex = nt.nodes.new("ShaderNodeTexImage")
    img = bpy.data.images.load(path)
    if movie:
        img.source = "MOVIE"
        tex.image_user.frame_duration = frames
        tex.image_user.use_auto_refresh = True
    tex.image = img
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    # ekran/görsel parlak görünsün: emission'a da bağla
    if "Emission Color" in bsdf.inputs:
        nt.links.new(tex.outputs["Color"], bsdf.inputs["Emission Color"])
        set_input(bsdf, "Emission Strength", 0.6)
    set_input(bsdf, "Roughness", 0.3)
    return mat, img


def kf(obj, path, frame, value=None):
    if value is not None:
        setattr(obj, path, value) if not isinstance(value, (list, tuple)) else setattr(obj, path, value)
    obj.keyframe_insert(data_path=path, frame=frame)


def ease_out(t):
    return 1 - (1 - t) ** 3


# ---------------------------------------------------------------- sahne

def setup_scene(spec):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.resolution_x = int(spec.get("width", 1080))
    sc.render.resolution_y = int(spec.get("height", 1920))
    sc.render.resolution_percentage = 100
    fps = int(spec.get("fps", 30))
    sc.render.fps = fps
    dur = float(spec.get("duration", 3.0))
    sc.frame_start = 1
    sc.frame_end = max(1, int(round(dur * fps))) if dur > 0 else 1
    sc.render.film_transparent = True
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA"
    for vt in ("AgX", "Filmic", "Standard"):
        try:
            sc.view_settings.view_transform = vt
            break
        except TypeError:
            continue

    engine = spec.get("engine", "eevee")
    if engine == "cycles":
        sc.render.engine = "CYCLES"
        sc.cycles.samples = int(spec.get("samples", 64))
        try:
            sc.cycles.use_denoising = True
        except AttributeError:
            pass
        try:  # macOS Metal / NVIDIA varsa GPU
            prefs = bpy.context.preferences.addons["cycles"].preferences
            for dev in ("METAL", "OPTIX", "CUDA", "HIP"):
                try:
                    prefs.compute_device_type = dev
                    prefs.get_devices()
                    if any(d.type != "CPU" for d in prefs.devices):
                        for d in prefs.devices:
                            d.use = True
                        sc.cycles.device = "GPU"
                        break
                except TypeError:
                    continue
        except Exception:
            pass
    else:
        for name in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
            try:
                sc.render.engine = name
                break
            except TypeError:
                continue
        try:
            sc.eevee.taa_render_samples = int(spec.get("samples", 64))
        except AttributeError:
            pass

    # dünya: koyu, hafif yansıma veren ortam
    world = bpy.data.worlds.new("World")
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    # film_transparent arka planı gizler ama metal ve cam bu ortamı yansıtır:
    # üstten aydınlık, alttan koyu bir gradyan krom/altın küreleri canlı gösterir.
    nt = world.node_tree
    coord = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.35
    ramp.color_ramp.elements[0].color = (0.015, 0.015, 0.02, 1)
    ramp.color_ramp.elements[1].position = 0.75
    ramp.color_ramp.elements[1].color = (0.9, 0.9, 0.95, 1)
    maprange = nt.nodes.new("ShaderNodeMapRange")
    maprange.inputs["From Min"].default_value = -1.0
    maprange.inputs["From Max"].default_value = 1.0
    nt.links.new(coord.outputs["Generated"], sep.inputs[0])
    nt.links.new(sep.outputs["Z"], maprange.inputs["Value"])
    nt.links.new(maprange.outputs["Result"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = float(spec.get("env_strength", 0.8))
    sc.world = world
    return sc


def add_lights():
    def area(name, loc, color, energy, size):
        data = bpy.data.lights.new(name, "AREA")
        data.color, data.energy, data.size = color, energy, size
        obj = bpy.data.objects.new(name, data)
        obj.location = loc
        bpy.context.collection.objects.link(obj)
        c = obj.constraints.new("TRACK_TO")
        c.target = target_empty()
        return obj
    area("key", (3.5, -5, 4.5), (1.0, 0.88, 0.75), 900, 4)
    area("rim", (-4.5, 3.5, 3), (0.65, 0.78, 1.0), 700, 3)
    area("fill", (-3, -5, -1), (1.0, 1.0, 1.0), 180, 6)
    # sadece yansımalarda görünen parlak şeritler (metal ve cam için)
    for i, x in enumerate((-2.5, 2.5)):
        bpy.ops.mesh.primitive_plane_add(size=1, location=(x, -6, 1.5 + i))
        strip = bpy.context.active_object
        strip.scale = (0.4, 1, 3)
        strip.rotation_euler = (math.radians(90), 0, math.radians(15 if x < 0 else -15))
        m = bpy.data.materials.new(f"strip{i}")
        m.use_nodes = True
        nodes = m.node_tree.nodes
        nodes.clear()
        em = nodes.new("ShaderNodeEmission")
        em.inputs["Strength"].default_value = 4
        out = nodes.new("ShaderNodeOutputMaterial")
        m.node_tree.links.new(em.outputs[0], out.inputs[0])
        strip.data.materials.append(m)
        try:
            strip.visible_camera = False
            strip.visible_shadow = False
        except AttributeError:
            pass


_TARGET = None


def target_empty():
    global _TARGET
    if _TARGET is None:
        _TARGET = bpy.data.objects.new("target", None)
        bpy.context.collection.objects.link(_TARGET)
    return _TARGET


def add_camera(spec, sc):
    cam_spec = spec.get("camera", {})
    d = float(cam_spec.get("distance", 8))
    tilt = math.radians(float(cam_spec.get("tilt", 0)))
    data = bpy.data.cameras.new("cam")
    data.lens = float(cam_spec.get("lens", 50))
    data.sensor_fit = "HORIZONTAL"
    data.sensor_width = 36
    cam = bpy.data.objects.new("cam", data)
    bpy.context.collection.objects.link(cam)
    sc.camera = cam
    rig = bpy.data.objects.new("cam_rig", None)  # orbit için dönen kök
    bpy.context.collection.objects.link(rig)
    cam.parent = rig
    cam.location = (0, -d * math.cos(tilt), d * math.sin(tilt))
    c = cam.constraints.new("TRACK_TO")
    c.target = target_empty()
    c.track_axis, c.up_axis = "TRACK_NEGATIVE_Z", "UP_Y"

    move, f0, f1 = cam_spec.get("move", "static"), sc.frame_start, sc.frame_end
    if move == "push" and f1 > f0:
        start = (0, -d * 1.3 * math.cos(tilt), d * 1.3 * math.sin(tilt))
        for f in range(f0, f1 + 1, 2):
            t = ease_out((f - f0) / (f1 - f0))
            cam.location = tuple(s + (e - s) * t for s, e in zip(start, (0, -d * math.cos(tilt), d * math.sin(tilt))))
            cam.keyframe_insert("location", frame=f)
    elif move == "orbit" and f1 > f0:
        for f in range(f0, f1 + 1, 2):
            t = (f - f0) / (f1 - f0)
            rig.rotation_euler = (0, 0, math.radians(-25 + 50 * t))
            rig.keyframe_insert("rotation_euler", frame=f)
    return cam, d


def visible_width(cam, d):
    return cam.data.sensor_width * d / cam.data.lens


def fit_object(obj, cam, d, fill):
    bpy.context.view_layer.update()
    w = max(obj.dimensions.x, 1e-4)
    h = max(obj.dimensions.z, obj.dimensions.y, 1e-4)
    vw = visible_width(cam, d)
    sc = bpy.context.scene
    vh = vw * sc.render.resolution_y / sc.render.resolution_x
    s = min(vw * fill / w, vh * 0.6 / h)
    obj.scale = tuple(v * s for v in obj.scale)
    bpy.context.view_layer.update()


def animate(obj, kind, sc):
    f0, f1 = sc.frame_start, sc.frame_end
    if f1 <= f0 or kind in (None, "none"):
        return
    n = f1 - f0
    base_loc, base_rot = tuple(obj.location), tuple(obj.rotation_euler)
    intro = max(2, int(n * 0.35))
    for f in range(f0, f1 + 1):
        t = (f - f0) / n
        ti = min(1.0, (f - f0) / intro)
        loc, rot = list(base_loc), list(base_rot)
        if kind == "rise":
            e = ease_out(ti)
            loc[2] = base_loc[2] - 1.2 * (1 - e)
            rot[0] = base_rot[0] + math.radians(80) * (1 - e)
        elif kind == "drop":
            # düşüş + iki sönümlü sekme
            if ti < 1:
                loc[2] = base_loc[2] + 4 * (1 - ti) ** 2
            else:
                tb = (f - f0 - intro) / max(1, n - intro)
                loc[2] = base_loc[2] + 0.35 * abs(math.sin(tb * math.pi * 3)) * math.exp(-5 * tb)
        elif kind == "spin":
            rot[2] = base_rot[2] + math.radians(360) * ease_out(t)
        elif kind == "turn":
            rot[2] = base_rot[2] + math.radians(-25 + 50 * t)
        elif kind == "float":
            loc[2] = base_loc[2] + 0.08 * math.sin(t * math.pi * 2)
            rot[2] = base_rot[2] + math.radians(6) * math.sin(t * math.pi * 2)
        elif kind == "fly":
            e = ease_out(ti)
            loc[0] = base_loc[0] + 6 * (1 - e)
            loc[2] = base_loc[2] + 2 * (1 - e)
            rot[1] = base_rot[1] + math.radians(-160) * (1 - e)
            rot[2] = base_rot[2] + math.radians(40) * (1 - e)
        elif kind == "press":
            mid = 0.5
            k = max(0.0, 1 - abs(t - mid) / 0.12)
            loc[2] = base_loc[2] - 0.12 * k
        obj.location, obj.rotation_euler = loc, rot
        obj.keyframe_insert("location", frame=f)
        obj.keyframe_insert("rotation_euler", frame=f)


# ---------------------------------------------------------------- sahne türleri

def scene_text3d(spec, cam, d, sc):
    curve = bpy.data.curves.new("text", "FONT")
    curve.body = spec.get("text", "TEXT")
    curve.align_x, curve.align_y = "CENTER", "CENTER"
    curve.extrude = float(spec.get("extrude", 0.12))
    curve.bevel_depth = float(spec.get("bevel", 0.02))
    curve.bevel_resolution = 3
    curve.shear = float(spec.get("italic_skew", 0.0))
    if spec.get("font") and os.path.exists(spec["font"]):
        curve.font = bpy.data.fonts.load(spec["font"])
    obj = bpy.data.objects.new("text", curve)
    bpy.context.collection.objects.link(obj)
    obj.rotation_euler = (math.radians(90), 0, 0)
    obj.data.materials.append(make_material("text", spec.get("material", "red")))
    fit_object(obj, cam, d, float(spec.get("frame_fill", 0.8)))
    animate(obj, spec.get("animation", "rise"), sc)
    return [obj]


def scene_orbit(spec, cam, d, sc):
    # eğim (tilt_root) ve dönüş (root) ayrı katman: yoksa dönüş eğik düzlemi savurur
    tilt_root = bpy.data.objects.new("orbit_tilt", None)
    bpy.context.collection.objects.link(tilt_root)
    tilt = math.radians(float(spec.get("tilt_deg", 72)))
    tilt_root.rotation_euler = (tilt, 0, 0)
    root = bpy.data.objects.new("orbit_root", None)
    bpy.context.collection.objects.link(root)
    root.parent = tilt_root
    n, r = int(spec.get("count", 7)), float(spec.get("radius", 2.2))
    size = float(spec.get("sphere_size", 0.28))
    mat = make_material("orbit", spec.get("material", "chrome"))
    for i in range(n):
        a = 2 * math.pi * i / n
        bpy.ops.mesh.primitive_uv_sphere_add(radius=size, segments=48, ring_count=24, location=(r * math.cos(a), r * math.sin(a), 0))
        s = bpy.context.active_object
        bpy.ops.object.shade_smooth()
        s.data.materials.append(mat)
        s.parent = root
        s["orbit_sphere"] = 1
    if spec.get("ring", True):
        # halka simetrik, dönmesine gerek yok: eğim katmanına bağlı iki sabit yarı (ön/arka)
        import bmesh
        ring_mat = make_material("ring", "white")
        for half in ("front", "back"):
            bpy.ops.mesh.primitive_torus_add(major_radius=r, minor_radius=0.006, major_segments=192, minor_segments=8)
            ring = bpy.context.active_object
            bm = bmesh.new()
            bm.from_mesh(ring.data)
            drop = [v for v in bm.verts if (v.co.y > 0.0005 if half == "front" else v.co.y < -0.0005)]
            bmesh.ops.delete(bm, geom=drop, context="VERTS")
            bm.to_mesh(ring.data)
            bm.free()
            ring.data.materials.append(ring_mat)
            ring.parent = tilt_root
            ring["ring_half"] = half
    f0, f1 = sc.frame_start, sc.frame_end
    turns = float(spec.get("turns", 0.5))
    if f1 > f0:
        for f in range(f0, f1 + 1):
            t = (f - f0) / (f1 - f0)
            root.rotation_euler = (0, 0, 2 * math.pi * turns * t)
            root.keyframe_insert("rotation_euler", frame=f)
    return [tilt_root]


def scene_card(spec, cam, d, sc):
    w = float(spec.get("card_width", 3.0))
    aspect = 1.414
    mat = make_material("card", "white")
    if spec.get("image") and os.path.exists(spec["image"]):
        mat, img = image_material("card", spec["image"])
        if img.size[0]:
            aspect = img.size[1] / img.size[0]
    bpy.ops.mesh.primitive_plane_add(size=1)
    card = bpy.context.active_object
    card.scale = (w, w * aspect, 1)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    card.rotation_euler = (math.radians(90), 0, 0)
    mod = card.modifiers.new("thick", "SOLIDIFY")
    mod.thickness = 0.02
    card.data.materials.append(mat)
    fit_object(card, cam, d, float(spec.get("frame_fill", 0.6)))
    animate(card, spec.get("animation", "fly"), sc)
    return [card]


def scene_phone(spec, cam, d, sc):
    body_w, body_h, depth = 1.5, 3.1, 0.12
    bpy.ops.mesh.primitive_cube_add(size=1)
    body = bpy.context.active_object
    body.scale = (body_w, depth, body_h)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bev = body.modifiers.new("round", "BEVEL")
    bev.width, bev.segments = 0.16, 10
    body.data.materials.append(make_material("body", spec.get("material", "black")))
    bpy.ops.object.shade_smooth()

    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, -depth / 2 - 0.002, 0))
    screen = bpy.context.active_object
    screen.scale = (body_w * 0.92, body_h * 0.95, 1)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    screen.rotation_euler = (math.radians(90), 0, 0)
    if spec.get("video") and os.path.exists(spec["video"]):
        m, _ = image_material("screen", spec["video"], movie=True, frames=sc.frame_end)
    elif spec.get("image") and os.path.exists(spec["image"]):
        m, _ = image_material("screen", spec["image"])
    else:
        m = make_material("screen", "#111418")
    screen.data.materials.append(m)
    screen.parent = body

    fit_object(body, cam, d, float(spec.get("frame_fill", 0.45)))
    animate(body, spec.get("animation", "turn"), sc)
    return [body]


def scene_keycap(spec, cam, d, sc):
    bpy.ops.mesh.primitive_cube_add(size=1)
    key = bpy.context.active_object
    key.scale = (1.0, 1.0, 0.45)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bev = key.modifiers.new("round", "BEVEL")
    bev.width, bev.segments = 0.12, 8
    key.data.materials.append(make_material("key", spec.get("material", "white")))
    bpy.ops.object.shade_smooth()

    curve = bpy.data.curves.new("label", "FONT")
    curve.body = spec.get("label", "⌘")
    curve.align_x, curve.align_y = "CENTER", "CENTER"
    curve.size = 0.5
    curve.extrude = 0.01
    if spec.get("font") and os.path.exists(spec["font"]):
        curve.font = bpy.data.fonts.load(spec["font"])
    label = bpy.data.objects.new("label", curve)
    bpy.context.collection.objects.link(label)
    label.location = (0, 0, 0.226)
    label.data.materials.append(make_material("label", spec.get("label_color", "#1A1A1A")))
    label.parent = key

    cam.location = (0, -d * 0.75, d * 0.66)  # yukarıdan bakış
    fit_object(key, cam, d, float(spec.get("frame_fill", 0.45)))
    animate(key, spec.get("animation", "press"), sc)
    return [key]


def scene_svg(spec, cam, d, sc):
    path = spec.get("svg")
    if not path or not os.path.exists(path):
        sys.exit("svg sahnesi için 'svg' dosyası gerekli")
    before = set(bpy.data.objects)
    try:
        import addon_utils
        addon_utils.enable("io_curve_svg", default_set=True)
    except Exception:
        pass
    bpy.ops.import_curve.svg(filepath=path)
    objs = [o for o in bpy.data.objects if o not in before and o.type == "CURVE"]
    if not objs:
        sys.exit("SVG içinden eğri okunamadı")
    for o in objs:
        o.data.extrude = float(spec.get("extrude", 0.004))
        o.data.bevel_depth = float(spec.get("bevel", 0.0005))
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    icon = bpy.context.active_object
    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")
    icon.location = (0, 0, 0)
    icon.rotation_euler = (math.radians(90), 0, 0)
    icon.data.materials.clear()
    icon.data.materials.append(make_material("icon", spec.get("material", "white")))
    fit_object(icon, cam, d, float(spec.get("frame_fill", 0.5)))
    animate(icon, spec.get("animation", "spin"), sc)
    return [icon]


SCENES = {"text3d": scene_text3d, "orbit": scene_orbit, "card": scene_card,
          "phone": scene_phone, "keycap": scene_keycap, "svg": scene_svg}


# ---------------------------------------------------------------- render + paketleme

def render_frames(sc, frames_dir):
    os.makedirs(frames_dir, exist_ok=True)
    sc.render.filepath = os.path.join(frames_dir, "")
    if sc.frame_end == sc.frame_start:
        sc.render.filepath = os.path.join(frames_dir, "0001.png")
        bpy.ops.render.render(write_still=True)
    else:
        bpy.ops.render.render(animation=True)


def encode(frames_dir, out_file, fps, fmt):
    ff = shutil.which("ffmpeg")
    if not ff or fmt == "png":
        return None
    src = os.path.join(frames_dir, "%04d.png")
    if fmt == "mov":
        cmd = [ff, "-y", "-v", "error", "-framerate", str(fps), "-i", src,
               "-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le", out_file]
    else:
        cmd = [ff, "-y", "-v", "error", "-framerate", str(fps), "-i", src,
               "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-auto-alt-ref", "0",
               "-b:v", "0", "-crf", "24", out_file]
    subprocess.run(cmd, check=True)
    return out_file


def split_orbit(sc, side):
    """Her küreyi kare kare merkezinin derinliğine göre bütün olarak gizle/göster.
    Kamera -Y tarafında; dünya y < 0 olan küre öndedir."""
    spheres = [o for o in bpy.data.objects if o.get("orbit_sphere")]
    for o in bpy.data.objects:
        if o.get("ring_half"):
            o.hide_render = o["ring_half"] != side
    for f in range(sc.frame_start, sc.frame_end + 1):
        sc.frame_set(f)
        for o in spheres:
            in_front = o.matrix_world.translation.y < 0
            o.hide_render = in_front != (side == "front")
            o.keyframe_insert("hide_render", frame=f)
    sc.frame_set(sc.frame_start)


def main():
    spec = argv_spec()
    kind = spec.get("scene")
    if kind not in SCENES:
        sys.exit(f"Bilinmeyen sahne: {kind}. Seçenekler: {', '.join(SCENES)}")
    out = os.path.abspath(spec.get("output", f"render_{kind}"))
    name = spec.get("name", os.path.basename(out))
    os.makedirs(out, exist_ok=True)

    sc = setup_scene(spec)
    add_lights()
    cam, d = add_camera(spec, sc)
    SCENES[kind](spec, cam, d, sc)

    fps, fmt = sc.render.fps, spec.get("format", "webm")
    ext = {"webm": "webm", "mov": "mov"}.get(fmt)
    outputs = {}
    passes = [("", None)]
    if kind == "orbit" and spec.get("split_depth"):
        # ön ve arka yarıyı ayrı render et: kişi iki katmanın arasına konur
        passes = [("_front", "front"), ("_back", "back")]
    for suffix, side in passes:
        if side:
            split_orbit(sc, side)
        frames = os.path.join(out, f"frames{suffix}")
        render_frames(sc, frames)
        if ext and sc.frame_end > sc.frame_start:
            outputs[f"video{suffix}"] = encode(frames, os.path.join(out, f"{name}{suffix}.{ext}"), fps, fmt)
        outputs[f"frames{suffix}"] = frames

    # poster: orta kare
    first = outputs.get("frames") or outputs.get("frames_front")
    pngs = sorted(p for p in os.listdir(first) if p.endswith(".png"))
    if pngs:
        shutil.copy(os.path.join(first, pngs[len(pngs) // 2]), os.path.join(out, "poster.png"))

    meta = {
        "name": name, "kind": "3d-render", "scene": kind,
        "width": sc.render.resolution_x, "height": sc.render.resolution_y,
        "fps": fps, "frames": sc.frame_end - sc.frame_start + 1,
        "duration": (sc.frame_end - sc.frame_start + 1) / fps,
        "alpha": True, "outputs": outputs, "poster": os.path.join(out, "poster.png"),
        "spec": {k: v for k, v in spec.items() if not k.startswith("_")},
        "blender": bpy.app.version_string,
    }
    with open(os.path.join(out, "meta.json"), "w") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    print("BLENDER_RENDER_OK", os.path.join(out, "meta.json"))


main()
