#!/usr/bin/env python3
"""Buddy Pods project art: ten pairs of pastel fruit, each pod joined to its buddy.

Writes assets/img/buddy-pods/pod-pairs.svg. Shapes are drawn at a base radius of
34 and scaled up with a transform, so stems and leaves stay in proportion.
"""
import io, math, os, random

random.seed(11)

W, H = 3000, 720
PAIRS = 10
BASE_R = 34
R = 75                      # rendered fruit radius
S = R / BASE_R              # scale factor applied per fruit
TOP_Y, BOT_Y = 190, 512
TETHER = "#c9c2d4"
ARROW  = "#b3aac9"
BACKDROP = None             # None = transparent; e.g. "#fdfcfa" for a warm panel

# ── fruit vocabulary: six silhouettes, recoloured into twenty distinct fruits ──
def leaf(x, y, flip=1, col="#a9c9a2", tilt=0):
    d = (f'M {x} {y} C {x+flip*7} {y-13}, {x+flip*22} {y-15}, {x+flip*25} {y-6} '
         f'C {x+flip*20} {y+3}, {x+flip*7} {y+4}, {x} {y} Z')
    rot = f' transform="rotate({tilt} {x} {y})"' if tilt else ''
    return f'<path d="{d}" fill="{col}" opacity=".9"{rot}/>'

def stem(x, y, h=11):
    return (f'<path d="M {x} {y} q 2 -{h*0.6} 1 -{h}" stroke="#9a8a72" '
            f'stroke-width="3.4" fill="none" stroke-linecap="round"/>')

def shine(cx, cy, rx=9, ry=6, rot=-25, op=.45):
    return (f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="#fff" '
            f'opacity="{op}" transform="rotate({rot} {cx} {cy})"/>')

def s_round(cx, cy, body, lf, tilt, crease=None):
    g = [f'<circle cx="{cx}" cy="{cy}" r="{BASE_R}" fill="{body}"/>']
    if crease:
        g.append(f'<path d="M {cx} {cy-BASE_R+3} q -3 {BASE_R} 0 {2*BASE_R-6}" '
                 f'stroke="{crease}" stroke-width="2.2" fill="none" opacity=".75"/>')
    g += [shine(cx-13, cy-14), stem(cx, cy-BASE_R+4), leaf(cx+1, cy-BASE_R-4, 1, lf, tilt)]
    return "".join(g)

def s_striped(cx, cy, body, lf, tilt, stripe):
    g = [f'<circle cx="{cx}" cy="{cy}" r="{BASE_R}" fill="{body}"/>']
    for k in (-1, 0, 1):
        g.append(f'<path d="M {cx+k*13} {cy-BASE_R+6} q 4 {BASE_R} 0 {2*BASE_R-12}" '
                 f'stroke="{stripe}" stroke-width="2" fill="none" opacity=".8"/>')
    g += [shine(cx-14, cy-15), stem(cx, cy-BASE_R+4), leaf(cx+1, cy-BASE_R-4, 1, lf, tilt)]
    return "".join(g)

def s_ellipse(cx, cy, body, lf, tilt, tip, a=34, b=24, lean=20):
    """Lemon: a pointed lens leaning right-end-down, leaf springing from the right tip."""
    d = (f'M {cx-a} {cy} Q {cx-a*0.72} {cy-b}, {cx} {cy-b} '
         f'Q {cx+a*0.72} {cy-b}, {cx+a} {cy} '
         f'Q {cx+a*0.72} {cy+b}, {cx} {cy+b} '
         f'Q {cx-a*0.72} {cy+b}, {cx-a} {cy} Z')
    return "".join([
        f'<g transform="rotate({lean + tilt*0.25} {cx} {cy})">',
        f'<path d="{d}" fill="{body}"/>',
        f'<circle cx="{cx+a+2}" cy="{cy}" r="4" fill="{body}"/>',   # blossom nub, lower tip
        shine(cx-4, cy-8, 9, 5.5),
        leaf(cx+a, cy-2, 1, lf, -52),            # springing from the right-hand tip
        '</g>'])


def s_pear(cx, cy, body, lf, tilt):
    d = (f'M {cx} {cy-BASE_R+2} c 13 0 16 13 11 21 c 11 6 16 15 16 23 '
         f'c 0 14 -13 21 -27 21 c -14 0 -27 -7 -27 -21 c 0 -8 5 -17 16 -23 '
         f'c -5 -8 -2 -21 11 -21 Z')
    return "".join([f'<path d="{d}" fill="{body}"/>', shine(cx-12, cy+9, 8, 5.5),
                    stem(cx, cy-BASE_R+3), leaf(cx+1, cy-BASE_R-5, 1, lf, tilt)])

def s_cluster(cx, cy, body, lf, tilt):
    g = []
    for dx, dy in [(-1,-16),(1,-16),(-2,0),(0,0),(2,0),(-1,16),(1,16),(0,31)]:
        gx, gy = cx+dx*12.5, cy+dy*0.86-6
        g.append(f'<circle cx="{gx}" cy="{gy}" r="12.5" fill="{body}"/>')
        g.append(f'<ellipse cx="{gx-3.6}" cy="{gy-4}" rx="3.4" ry="2.4" fill="#fff" '
                 f'opacity=".38" transform="rotate(-25 {gx-3.6} {gy-4})"/>')
    g += [stem(cx, cy-30, 9), leaf(cx+1, cy-36, 1, lf, tilt)]
    return "".join(g)

def _arc_pt(cx, cy, r, deg):
    a = math.radians(deg)
    return cx + r*math.cos(a), cy + r*math.sin(a)


def _one_banana(cx, cy, R=30, t=6.0, a0=22, a1=158):
    """A banana is a thick circular arc: belly down, tips up, round caps."""
    Ro, Ri = R+t, R-t
    x0, y0 = _arc_pt(cx, cy, Ro, a0); x1, y1 = _arc_pt(cx, cy, Ro, a1)
    x2, y2 = _arc_pt(cx, cy, Ri, a1); x3, y3 = _arc_pt(cx, cy, Ri, a0)
    return (f'M {x0:.1f} {y0:.1f} A {Ro} {Ro} 0 0 1 {x1:.1f} {y1:.1f} '
            f'A {t} {t} 0 0 1 {x2:.1f} {y2:.1f} '
            f'A {Ri} {Ri} 0 0 0 {x3:.1f} {y3:.1f} '
            f'A {t} {t} 0 0 1 {x0:.1f} {y0:.1f} Z')


def s_banana(cx, cy, body, lf, tilt, n=5, fan=13, R=30, t=6.0):
    """Five bananas pivoted about their shared stem end, fanning apart."""
    cy = cy - 22                      # lift so the bunch sits centred in its slot
    px, py = _arc_pt(cx, cy, R, 158)  # the joined end
    edge = "#e9d287"
    g = []
    for i in sorted(range(n), key=lambda i: -abs(i-(n-1)/2)):   # outer ones behind
        a = (i-(n-1)/2)*fan
        depth = abs(i-(n-1)/2)/max((n-1)/2, 1e-9)
        g.append(f'<g transform="rotate({a + tilt*0.25:.1f} {px:.1f} {py:.1f})">'
                 f'<path d="{_one_banana(cx, cy, R, t)}" fill="{edge if depth > 0.55 else body}"/></g>')
    g.append(f'<ellipse cx="{px:.1f}" cy="{py:.1f}" rx="7" ry="5" fill="#d8c48c" '
             f'transform="rotate(-20 {px:.1f} {py:.1f})"/>')
    g.append(f'<path d="M {px:.1f} {py-3:.1f} q -3 -8 -1 -13" stroke="#9a8a72" '
             f'stroke-width="3.6" fill="none" stroke-linecap="round"/>')
    return "".join(g)


def s_strawberry(cx, cy, body, lf, tilt, w=32, shoulder=-36):
    """Rounded shoulders tapering to a soft point, seeds, and a five-petal calyx."""
    top = cy - 16
    d = (f'M {cx-w} {top} C {cx-w} {cy+shoulder}, {cx+w} {cy+shoulder}, {cx+w} {top} '
         f'C {cx+w} {cy+8}, {cx+w*0.42} {cy+28}, {cx} {cy+34} '
         f'C {cx-w*0.42} {cy+28}, {cx-w} {cy+8}, {cx-w} {top} Z')
    g = [f'<path d="{d}" fill="{body}"/>']
    for n, yy, sp in [(4, top+4, 15), (4, top+16, 13), (3, top+28, 11), (2, top+38, 8)]:
        for k in range(n):
            sx = cx + (k-(n-1)/2)*sp
            g.append(f'<ellipse cx="{sx:.1f}" cy="{yy}" rx="2.1" ry="3" fill="#fff" '
                     f'opacity=".62" transform="rotate(-12 {sx:.1f} {yy})"/>')
    for i in range(5):
        a = (i-2)*37.5 + tilt*0.3
        g.append(f'<ellipse cx="{cx}" cy="{top-9}" rx="15" ry="6" fill="{lf}" '
                 f'transform="rotate({a} {cx} {top-2})" opacity=".95"/>')
    g.append(stem(cx, top-14, 11))
    return "".join(g)


def s_citrus_slice(cx, cy, body, lf, tilt, rind=None, pith="#eef4e4", n=9, gap=6.0):
    """A cut citrus: rind ring, pith ring, then wedges with the pith left showing
    through as the membranes. `body` is the flesh, `rind` the peel."""
    rind = rind or lf
    g = [f'<circle cx="{cx}" cy="{cy}" r="{BASE_R}" fill="{rind}"/>',
         f'<circle cx="{cx}" cy="{cy}" r="{BASE_R-4.5}" fill="{pith}"/>']
    rf = BASE_R - 7
    for i in range(n):
        a0 = tilt - 8 + i*360/n + gap/2
        a1 = tilt - 8 + (i+1)*360/n - gap/2
        x0 = cx + rf*math.cos(math.radians(a0)); y0 = cy + rf*math.sin(math.radians(a0))
        x1 = cx + rf*math.cos(math.radians(a1)); y1 = cy + rf*math.sin(math.radians(a1))
        g.append(f'<path d="M {cx} {cy} L {x0:.1f} {y0:.1f} '
                 f'A {rf} {rf} 0 0 1 {x1:.1f} {y1:.1f} Z" fill="{body}"/>')
    g.append(f'<circle cx="{cx}" cy="{cy}" r="3" fill="{pith}"/>')
    return "".join(g)


def s_cherries(cx, cy, body, lf, tilt, pair=None):
    """Two cherries on a shared stem, with a leaf at the fork. The only paired
    fruit in the set — appropriate on a page about buddies."""
    pair = pair or body
    return "".join([
        f'<path d="M {cx+2} {cy-32} C {cx-8} {cy-20}, {cx-16} {cy-6}, {cx-17} {cy+6}" '
        f'stroke="#9a8a72" stroke-width="3.4" fill="none" stroke-linecap="round"/>',
        f'<path d="M {cx+2} {cy-32} C {cx+10} {cy-20}, {cx+17} {cy-8}, {cx+18} {cy+2}" '
        f'stroke="#9a8a72" stroke-width="3.4" fill="none" stroke-linecap="round"/>',
        leaf(cx+4, cy-32, 1, lf, -30 + tilt*0.3),
        f'<circle cx="{cx-17}" cy="{cy+16}" r="17" fill="{body}"/>',
        f'<circle cx="{cx+18}" cy="{cy+12}" r="15" fill="{pair}"/>',
        f'<ellipse cx="{cx-23}" cy="{cy+10}" rx="5" ry="3.4" fill="#fff" opacity=".4" '
        f'transform="rotate(-25 {cx-23} {cy+10})"/>'])


def s_kiwi_slice(cx, cy, body, lf, tilt, core="#f2f6e8", seeds=14):
    """A cut kiwi: brown rind, green flesh, pale core, and a ring of dark seeds."""
    g = [f'<circle cx="{cx}" cy="{cy}" r="{BASE_R}" fill="{lf}"/>',
         f'<circle cx="{cx}" cy="{cy}" r="{BASE_R-5}" fill="{body}"/>',
         f'<ellipse cx="{cx}" cy="{cy}" rx="9" ry="11" fill="{core}"/>']
    rr = BASE_R - 11
    for i in range(seeds):
        a = tilt + i*360/seeds
        sx = cx + rr*math.cos(math.radians(a)); sy = cy + rr*math.sin(math.radians(a))
        g.append(f'<ellipse cx="{sx:.1f}" cy="{sy:.1f}" rx="1.9" ry="3" fill="#4a4636" '
                 f'opacity=".72" transform="rotate({a+90:.0f} {sx:.1f} {sy:.1f})"/>')
    return "".join(g)


def s_apple(cx, cy, body, lf, tilt, crease=None):
    """Two lobes with a dimple at the top where the stem sits, and a soft waist."""
    r = BASE_R
    d = (f'M {cx} {cy-r+8} C {cx+8} {cy-r-2}, {cx+r} {cy-r+4}, {cx+r} {cy-2} '
         f'C {cx+r} {cy+r-8}, {cx+r-16} {cy+r+2}, {cx} {cy+r-4} '
         f'C {cx-r+16} {cy+r+2}, {cx-r} {cy+r-8}, {cx-r} {cy-2} '
         f'C {cx-r} {cy-r+4}, {cx-8} {cy-r-2}, {cx} {cy-r+8} Z')
    g = [f'<path d="{d}" fill="{body}"/>']
    if crease:
        g.append(f'<path d="M {cx-4} {cy+r-6} q 4 -14 2 -26" stroke="{crease}" '
                 f'stroke-width="2" fill="none" opacity=".5"/>')
    g += [shine(cx-14, cy-12, 9, 6),
          stem(cx, cy-r+9, 13),
          leaf(cx+2, cy-r-2, 1, lf, tilt)]
    return "".join(g)


def s_persimmon(cx, cy, body, lf, tilt):
    g = [f'<ellipse cx="{cx}" cy="{cy+3}" rx="{BASE_R}" ry="{BASE_R-6}" fill="{body}"/>',
         shine(cx-13, cy-6)]
    for a in (0, 60, 120):                       # chunkier calyx than a single leaf
        g.append(f'<ellipse cx="{cx}" cy="{cy-BASE_R+8}" rx="17" ry="7.5" fill="{lf}" '
                 f'transform="rotate({a+tilt} {cx} {cy-BASE_R+8})" opacity=".93"/>')
    g.append(stem(cx, cy-BASE_R+2, 9))
    return "".join(g)

GREEN, DEEP = "#a9c9a2", "#9dbf95"
TOP = [
    ("momo",      lambda c,y,t: s_round(c,y,"#f6c3bd",GREEN,t,"#e8a8a2")),
    ("ichigo",    lambda c,y,t: s_strawberry(c,y,"#f09a98","#8fbb86",t)),
    ("meron",     lambda c,y,t: s_striped(c,y,"#cfe0b6",DEEP,t,"#b6cfa2")),
    ("budou",     lambda c,y,t: s_cluster(c,y,"#c7b5dd",GREEN,t)),
    ("mikan",     lambda c,y,t: s_round(c,y,"#f8cb92",GREEN,t)),
    ("remon",     lambda c,y,t: s_ellipse(c,y,"#f5e5a5",GREEN,t,"#e6d189")),
    ("ringo",     lambda c,y,t: s_apple(c,y,"#eda6a6",GREEN,t,"#dc9090")),
    ("nashi",     lambda c,y,t: s_pear(c,y,"#dde5c2",DEEP,t)),
    ("sumomo",    lambda c,y,t: s_round(c,y,"#dfa7b5",GREEN,t,"#cf94a4")),
    ("kaki",      lambda c,y,t: s_persimmon(c,y,"#f3b489",DEEP,t)),
]
BOTTOM = [
    ("buruberi",  lambda c,y,t: s_cluster(c,y,"#a9bfe0",GREEN,t)),
    ("kiui",      lambda c,y,t: s_kiwi_slice(c,y,"#c6da9d","#b3a07c",t)),
    ("yuzu",      lambda c,y,t: s_ellipse(c,y,"#f0dc9a",DEEP,t,"#ddc77f")),
    ("ichijiku",  lambda c,y,t: s_round(c,y,"#c3a8c8",DEEP,t)),
    ("raimu",     lambda c,y,t: s_citrus_slice(c,y,"#c9e0a6","#aecb8f",t)),
    ("suguri",    lambda c,y,t: s_cluster(c,y,"#eda8a8",GREEN,t)),
    ("youmanashi",lambda c,y,t: s_pear(c,y,"#e9e3ae",DEEP,t)),
    ("kurokaki",  lambda c,y,t: s_persimmon(c,y,"#eaa070",DEEP,t)),
    ("sakuranbo", lambda c,y,t: s_cherries(c,y,"#e8919b","#8fbb86",t,pair="#df8391")),
    ("shiromomo", lambda c,y,t: s_round(c,y,"#f7dcd2",GREEN,t,"#e8c3b8")),
]

def place(fn, cx, cy, tilt):
    """Draw a base-radius fruit, scaled about its own centre."""
    return (f'<g transform="translate({cx} {cy}) scale({S:.4f}) translate({-cx} {-cy})">'
            f'{fn(cx, cy, tilt)}</g>')

STYLE_BLOCK = """
<style>
  .pod { cursor: pointer; }
  .pod:focus { outline: none; }
  .pod:focus-visible .hit { stroke: %(arrow)s; stroke-width: 2.5; }
  @keyframes pod-shake {
    0%%, 100%% { transform: rotate(0deg)    translateY(0); }
    12%%       { transform: rotate(-7deg)   translateY(-5px); }
    26%%       { transform: rotate(6deg)    translateY(0); }
    40%%       { transform: rotate(-5deg)   translateY(-4px); }
    54%%       { transform: rotate(4deg)    translateY(0); }
    70%%       { transform: rotate(-2.5deg) translateY(-2px); }
    86%%       { transform: rotate(1.5deg)  translateY(0); }
  }
  .pod.shaking { animation: pod-shake 720ms cubic-bezier(.36,.07,.19,.97); }
  .pod-link { transition: opacity 220ms ease, stroke-width 220ms ease; }
  .pod-link.lit { opacity: .95; stroke-width: 3.4; }
  .smoothie { display: none; }
  .smoothie.show { display: block; }
  .smoothie .veil { cursor: pointer; }
  .cup-cap {
    font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
    font-size: 30px; letter-spacing: 3px; fill: rgba(6, 29, 73, 0.42);
    pointer-events: none;
  }
  @keyframes cup-in {
    0%%   { transform: scale(.18) translateY(70px); opacity: 0; }
    62%%  { transform: scale(1.07) translateY(0);   opacity: 1; }
    100%% { transform: scale(1)    translateY(0);   opacity: 1; }
  }
  .smoothie.show .cup { animation: cup-in 620ms cubic-bezier(.22,1.1,.36,1) both; }
  .smoothie.show .veil, .smoothie.show .cup-cap { animation: veil-in 300ms ease both; }
  @keyframes veil-in { from { opacity: 0; } to { opacity: .93; } }
  @keyframes veil-in-text { from { opacity: 0; } to { opacity: 1; } }
  .smoothie.show .cup-cap { animation: veil-in-text 420ms 260ms ease both; }
  @media (prefers-reduced-motion: reduce) {
    .pod.shaking { animation: none; }
    .pod-link { transition: none; }
    .smoothie.show .cup { animation: none; }
  }
</style>
"""

SCRIPT_BLOCK = """
<script>
(function () {
  var self = document.currentScript;
  var svg = null;
  if (self) { svg = self.ownerSVGElement || self.closest('svg'); }
  if (!svg) { svg = document.querySelector('svg'); }
  if (!svg) { svg = document.documentElement; }
  var pods  = svg.querySelectorAll('.pod');
  var links = svg.querySelectorAll('.pod-link');
  var PERM = %(perm)s;                       // top index maps to bottom index
  var INV  = {};
  PERM.forEach(function (b, t) { INV[b] = t; });

  var smoothies = svg.querySelectorAll('.smoothie');
  var openTimer = null;

  function hideDrink() {
    if (openTimer) { clearTimeout(openTimer); openTimer = null; }
    smoothies.forEach(function (m) { m.classList.remove('show'); });
  }

  function showDrink(topIndex) {
    var m = svg.querySelector('.smoothie[data-pair="' + topIndex + '"]');
    if (!m) { return; }
    m.classList.remove('show');
    void svg.getBoundingClientRect();
    m.classList.add('show');
  }

  smoothies.forEach(function (m) {
    m.addEventListener('click', hideDrink);
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') { hideDrink(); }
  });

  function clear() {
    pods.forEach(function (p) { p.classList.remove('shaking'); });
    links.forEach(function (l) { l.classList.remove('lit'); });
    smoothies.forEach(function (m) { m.classList.remove('show'); });
  }

  function find(row, i) {
    return svg.querySelector('.pod[data-row="' + row + '"][data-i="' + i + '"]');
  }

  function activate(pod) {
    var row = pod.getAttribute('data-row');
    var i   = +pod.getAttribute('data-i');
    var top = row === 't' ? i : INV[i];
    var bot = row === 't' ? PERM[i] : i;
    clear();
    // force a reflow so re-clicking the same pair restarts the animation
    void svg.getBoundingClientRect();
    [find('t', top), find('b', bot)].forEach(function (el) {
      if (el) el.classList.add('shaking');
    });
    var link = svg.querySelector('.pod-link[data-a="' + top + '"][data-b="' + bot + '"]');
    if (link) { link.classList.add('lit'); }
    // let the shake read before the glass arrives
    if (openTimer) { clearTimeout(openTimer); }
    openTimer = setTimeout(function () { showDrink(top); }, 480);
  }

  pods.forEach(function (pod) {
    pod.addEventListener('click', function () { activate(pod); });
    pod.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); activate(pod); }
    });
    pod.addEventListener('animationend', function () { pod.classList.remove('shaking'); });
  });
})();
</script>
"""

# ── smoothie: the blend of a pod pair, shown when either fruit is clicked ──
GLASS_S = 2.3
GLASS_CX, GLASS_CY = 1500, 340
GLASS_TX = GLASS_CX - 110*GLASS_S
GLASS_TY = GLASS_CY - 117*GLASS_S


def _hex(h):
    return tuple(int(h[i:i+2], 16) for i in (1, 3, 5))


def _mix(a, b, t=0.5):
    A, B = _hex(a), _hex(b)
    return "#%02x%02x%02x" % tuple(round(A[i] + (B[i]-A[i])*t) for i in range(3))


def smoothie(idx, ca, cb, label, cx=110, cy=140):
    """One glass, blended from the pair's two fruit colours. Pre-rendered per pair
    rather than built in JS, so the script stays free of markup characters."""
    tw, bw, h = 76, 54, 150
    lip, base = cy - h/2, cy + h/2
    lt = lip + 26
    body = (f'M {cx-tw} {lip} L {cx-bw} {base-14} Q {cx-bw} {base} {cx-bw+14} {base} '
            f'L {cx+bw-14} {base} Q {cx+bw} {base} {cx+bw} {base-14} L {cx+tw} {lip} Z')
    liq = (f'M {cx-tw+10} {lt} L {cx-bw+3} {base-14} Q {cx-bw+3} {base-4} {cx-bw+15} {base-4} '
           f'L {cx+bw-15} {base-4} Q {cx+bw-3} {base-4} {cx+bw-3} {base-14} L {cx+tw-10} {lt} Z')
    mid = _mix(ca, cb, .5)
    light = _mix(mid, "#ffffff", .35)
    return (
        f'<g class="smoothie" data-pair="{idx}">'
        f'<rect class="veil" x="0" y="0" width="{W}" height="{H}" fill="#ffffff" opacity=".93"/>'
        f'<g class="cup" style="transform-origin:{GLASS_CX}px {GLASS_CY}px">'
        f'<g transform="translate({GLASS_TX:.1f} {GLASS_TY:.1f}) scale({GLASS_S})">'
        f'<defs>'
        f'<linearGradient id="lg{idx}" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0%" stop-color="{ca}"/>'
        f'<stop offset="48%" stop-color="{mid}"/>'
        f'<stop offset="100%" stop-color="{cb}"/>'
        f'</linearGradient>'
        f'<clipPath id="cp{idx}"><path d="{liq}"/></clipPath>'
        f'</defs>'
        f'<path d="{body}" fill="#eef2f6" opacity=".55"/>'
        f'<path d="{liq}" fill="url(#lg{idx})"/>'
        f'<g clip-path="url(#cp{idx})">'
        f'<circle cx="{cx-22}" cy="{lt+52}" r="7" fill="#fff" opacity=".28"/>'
        f'<circle cx="{cx+16}" cy="{lt+80}" r="5" fill="#fff" opacity=".22"/>'
        f'<circle cx="{cx-4}" cy="{lt+104}" r="4" fill="#fff" opacity=".2"/>'
        f'</g>'
        f'<ellipse cx="{cx}" cy="{lt}" rx="{tw-10}" ry="9" fill="{light}"/>'
        f'<path d="M {cx+18} {lt-2} L {cx+44} {lip-46}" stroke="#d9b9c6" stroke-width="11" '
        f'stroke-linecap="round" opacity=".92"/>'
        f'<path d="M {cx-tw+16} {lip+16} L {cx-bw+12} {base-26}" stroke="#fff" stroke-width="7" '
        f'stroke-linecap="round" opacity=".4"/>'
        f'<path d="{body}" fill="none" stroke="#c9d3dd" stroke-width="2.5" opacity=".8"/>'
        f'</g></g>'
        f'<text class="cup-cap" x="{GLASS_CX}" y="642" text-anchor="middle">{label}</text>'
        f'</g>')


import re as _re
_src = io.open(__file__, encoding="utf-8").read()

def _colours(label):
    blk = _src[_src.index(label + " = ["):_src.index("]", _src.index(label + " = ["))]
    return [c for _, c in _re.findall(r'\("([^"]+)",\s*lambda[^:]*:\s*s_\w+\(c,y,"(#[0-9a-fA-F]{6})"', blk)]

TOP_COLOURS, BOTTOM_COLOURS = _colours("TOP"), _colours("BOTTOM")
assert len(TOP_COLOURS) == PAIRS and len(BOTTOM_COLOURS) == PAIRS, "colour table mismatch"

SLOTS = PAIRS + 1                       # ten fruit columns plus one ellipsis slot
ELLIPSIS_AT = PAIRS - 1                 # sits between the 9th and 10th column
MARGIN = 130
SP = (W - 2*MARGIN) / (SLOTS - 1)
POD_NUMBERS = list(range(1, PAIRS)) + [30]   # 1..9, then the last one is pod 30
LABEL = "#a7a3b4"

xs, ex = [], None                       # x for each fruit column; ex for the ellipsis
slot = 0
for i in range(PAIRS):
    if i == ELLIPSIS_AT:
        ex = MARGIN + slot*SP
        slot += 1
    xs.append(MARGIN + slot*SP)
    slot += 1

out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" height="100%" '
       f'role="img" aria-label="Ten numbered pairs of pastel fruit in two rows, each pod in the top '
       f'row paired with the one below it, with a line from every pod to its buddy in the other row, '
       f'trailing off into an ellipsis before pod 30.">',
       (f'<rect width="{W}" height="{H}" fill="{BACKDROP}"/>' if BACKDROP else '')]

# ── buddy links: every pod is paired with a pod in the other row ──
# A derangement, so no fruit is simply joined to the one directly below it.
while True:
    perm = list(range(PAIRS))
    random.shuffle(perm)
    if all(i != perm[i] for i in range(PAIRS)):
        break

TOP_CLEAR = R + 20          # below the deepest top-row fruit
BOT_CLEAR = 128             # above the tallest bottom-row leaf
BAND_TOP = TOP_Y + TOP_CLEAR
BAND_BOT = BOT_Y - BOT_CLEAR

# Connector geometry: a cubic with both control points on the midline between
# the endpoints — D3's linkVertical form. That gives vertical tangents at both
# ends and a symmetric curve, so every link is the same shape stretched.
# Tension is varied by span length so short hops turn early and long spans stay
# vertical longer, which fans the ten links apart without breaking the family.
out.append(STYLE_BLOCK % {"arrow": ARROW})

span_order = sorted(range(PAIRS), key=lambda k: abs(xs[perm[k]] - xs[k]))
rank_of = {k: n/(PAIRS-1) for n, k in enumerate(span_order)}

for i in range(PAIRS):
    x0, x1 = xs[i], xs[perm[i]]
    dy = BAND_BOT - BAND_TOP
    t = 0.30 + 0.44*rank_of[i]
    out.append(f'<path class="pod-link" data-a="{i}" data-b="{perm[i]}" '
               f'd="M {x0:.1f} {BAND_TOP:.1f} C {x0:.1f} {BAND_TOP+dy*t:.1f}, '
               f'{x1:.1f} {BAND_BOT-dy*t:.1f}, {x1:.1f} {BAND_BOT:.1f}" '
               f'stroke="{ARROW}" stroke-width="1.9" fill="none" opacity=".48" '
               f'stroke-linecap="round" pointer-events="none"/>')

# ── fruit and pod numbers ──
# Each fruit is wrapped in a .pod group carrying its row and index, plus an
# invisible hit circle so the whole slot is clickable (the shapes have gaps).
inv = {v: k for k, v in enumerate(perm)}

def pod_group(row, i, x, y, inner, buddy_no):
    return (f'<g class="pod" data-row="{row}" data-i="{i}" tabindex="0" role="button" '
            f'style="transform-origin:{x:.1f}px {y}px" '
            f'aria-label="Pod {POD_NUMBERS[i]}, buddy of pod {buddy_no}">'
            f'{inner}'
            f'<circle class="hit" cx="{x:.1f}" cy="{y}" r="{R+16}" fill="none" pointer-events="all"/>'
            f'</g>')

for i in range(PAIRS):
    x = xs[i]
    out.append(pod_group("t", i, x, TOP_Y,
                         place(TOP[i][1], x, TOP_Y, random.uniform(-14, 14)),
                         POD_NUMBERS[perm[i]]))
    out.append(pod_group("b", i, x, BOT_Y,
                         place(BOTTOM[i][1], x, BOT_Y, random.uniform(-14, 14)),
                         POD_NUMBERS[inv[i]]))
    out.append(f'<text x="{x:.1f}" y="{BOT_Y+R+52}" text-anchor="middle" fill="{LABEL}" '
               f'font-family="ui-monospace, SFMono-Regular, Menlo, monospace" font-size="30" '
               f'letter-spacing="2" pointer-events="none">{POD_NUMBERS[i]}</text>')

# ── ellipsis: both rows continue ──
for y in (TOP_Y, BOT_Y):
    for k in (-1, 0, 1):
        out.append(f'<circle cx="{ex + k*30:.1f}" cy="{y}" r="7" fill="{TETHER}" opacity=".75"/>')

# one pre-rendered glass per pairing, layered above the fruit
for i in range(PAIRS):
    ca = TOP_COLOURS[i]
    cb = BOTTOM_COLOURS[perm[i]]
    out.append(smoothie(i, ca, cb, TOP[i][0] + " + " + BOTTOM[perm[i]][0]))

out.append(SCRIPT_BLOCK % {"perm": list(perm)})
out.append('</svg>')

os.makedirs("assets/img/buddy-pods", exist_ok=True)
svg = "\n".join(out)

# Guard: the embedded JS must contain no &, < or > — see the note on SCRIPT_BLOCK.
_js = svg[svg.index("<script>")+8 : svg.index("</script>")]
_bad = [c for c in "&<>" if c in _js]
if _bad:
    raise SystemExit("script contains XML-unsafe characters %s — rewrite to avoid them" % _bad)
io.open("assets/img/buddy-pods/pod-pairs.svg", "w", encoding="utf-8").write(svg)
print("wrote assets/img/buddy-pods/pod-pairs.svg")

# The page embeds this with <object>, which loads it as its own document, so the
# style and behaviour above still run. Nothing needs to be pasted into the HTML.
pod_count = svg.count('class="pod"')
link_count = svg.count('class="pod-link"')
print("  %dK, %d pods, %d links" % (len(svg)//1024, pod_count, link_count))
