# %% [markdown]
# # Full Wave Rectifier – simulation and figures
# Bridge rectifier (4 x 1N4007) + 1000 µF filter + green LED with 1 kΩ series resistor.
# Everything below is a model (ideal transformer, constant diode drop), so the numbers are
# *simulated / calculated*, not measured. Change the parameters in the next cell to match your board.

# %% Imports and parameters
import os
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle, Arc
from PIL import Image

plt.rcParams['font.family'] = 'DejaVu Sans'
OUT = 'figures'; os.makedirs(OUT, exist_ok=True)

f   = 50                    # mains frequency (Hz)
Vrms = 12                   # transformer secondary (V rms)  -> check with a multimeter
Vm  = Vrms*np.sqrt(2)       # peak secondary voltage
VD  = 0.7                   # silicon diode drop (V)
VF  = 2.0                   # green LED forward drop (V)
R   = 1000.0                # LED series resistor (ohm)    -> check the colour bands
C_BUILT = 1000e-6           # filter capacitor as built (F)
Vp  = Vm - 2*VD             # peak of the rectified output (two diodes conduct)
print(f'Vm = {Vm:.2f} V, Vp = {Vp:.2f} V')

# %% Simulation of the rectifier
def run(C, R=R, T=0.2, dt=2e-6):
    """Return time, secondary voltage, and output voltage.
    C=None gives the unfiltered output."""
    t = np.arange(0, T, dt)
    vs = Vm*np.sin(2*np.pi*f*t)
    rect = np.clip(np.abs(vs) - 2*VD, 0, None)
    if C is None:
        return t, vs, rect
    vc = 0.0; out = np.empty_like(t)
    for k, r in enumerate(rect):
        if r > vc:                       # diodes conduct, capacitor charges
            vc = r
        else:                            # diodes off, capacitor feeds the LED + R branch
            vc -= max(0.0, vc - VF)/R*dt/C
        out[k] = vc
    return t, vs, out

# %% Table values (unfiltered and filtered)
t, vs, u = run(None)
m = (t >= 0.04) & (t < 0.08)             # two full cycles
vdc = u[m].mean(); vrms = np.sqrt((u[m]**2).mean())
gamma = np.sqrt((vrms/vdc)**2 - 1)
iavg = (np.clip(u[m] - VF, 0, None)/R).mean()
print(f'UNFILTERED: Vdc={vdc:.2f} V  Vrms={vrms:.2f} V  ripple factor={gamma:.3f}  Iavg={iavg*1e3:.2f} mA')

print('\nC(uF)  Vdc    Vr(pp)  gamma_sim(%)  gamma_formula(%)  Idc(mA)')
for C in (100e-6, 220e-6, 470e-6, 1000e-6):
    t, vs, o = run(C, T=0.4); m = t > 0.3
    vdc_c = o[m].mean(); vpp = o[m].max() - o[m].min()
    g_sim = np.sqrt(((o[m]-vdc_c)**2).mean())/vdc_c*100
    I = (vdc_c - VF)/R
    g_form = 1/(4*np.sqrt(3)*f*C*(vdc_c/I))*100
    print(f'{C*1e6:5.0f}  {vdc_c:5.2f}  {vpp:5.2f}   {g_sim:6.2f}        {g_form:6.2f}          {I*1e3:5.2f}')

# %% Figure 7 – circuit diagram
INK = '#1b1b1b'
def wire(ax, *pts, lw=2.6):
    ax.plot(*zip(*pts), c=INK, lw=lw, solid_capstyle='round', solid_joinstyle='round')
def dot(ax, p): ax.plot(*p, 'o', c=INK, ms=7)
def diode(ax, a, b, label, off):
    a = np.array(a, float); b = np.array(b, float)
    m = (a+b)/2; d = (b-a)/np.linalg.norm(b-a); n = np.array([-d[1], d[0]])
    s, w = 0.42, 0.36; p1, p2 = m - d*s, m + d*s
    ax.plot(*zip(a, p1), c=INK, lw=2.6); ax.plot(*zip(p2, b), c=INK, lw=2.6)
    ax.add_patch(Polygon([p1+n*w, p1-n*w, p2], closed=True, fc='white', ec=INK, lw=2.6))
    ax.plot(*zip(p2+n*w, p2-n*w), c=INK, lw=3.2)
    ax.text(m[0]+off[0], m[1]+off[1], label, fontsize=12, fontweight='bold', ha='center', va='center')
def coil(ax, x, y0, y1, n, side):
    ys = np.linspace(y0, y1, n+1)
    for i in range(n):
        ax.add_patch(Arc((x, (ys[i]+ys[i+1])/2), 0.5, ys[i+1]-ys[i],
                         theta1=-90 if side > 0 else 90, theta2=90 if side > 0 else 270, ec=INK, lw=2.6))

fig, ax = plt.subplots(figsize=(11.2, 7.2), dpi=100)
ax.set_xlim(-1.2, 18.0); ax.set_ylim(-0.6, 8.2); ax.axis('off'); ax.set_aspect('equal')
ax.add_patch(Circle((0.9, 4), 0.55, fc='white', ec=INK, lw=2.6))
xs = np.linspace(0.65, 1.15, 50); ax.plot(xs, 4+0.2*np.sin((xs-0.65)/0.5*2*np.pi), c=INK, lw=2)
ax.text(0.2, 4.0, '230 V\n50 Hz', ha='right', va='center', fontsize=11, color='#555')
wire(ax, (0.9, 4.55), (0.9, 5.5), (2.0, 5.5)); wire(ax, (0.9, 3.45), (0.9, 2.5), (2.0, 2.5))
coil(ax, 2.0, 2.5, 5.5, 5, +1); coil(ax, 3.3, 2.5, 5.5, 5, -1)
for x in (2.55, 2.75): wire(ax, (x, 2.3), (x, 5.7), lw=2.2)
ax.text(2.65, 6.2, 'T1\n230 V / 12 V', ha='center', fontsize=11, fontweight='bold')
wire(ax, (3.3, 5.5), (3.9, 5.5), (3.9, 6.9), (6.5, 6.9), (6.5, 6.4))
wire(ax, (3.3, 2.5), (3.9, 2.5), (3.9, 1.5), (6.5, 1.5), (6.5, 1.7))
P, Q, N, POS = (6.5, 6.4), (6.5, 1.7), (4.4, 4.05), (8.6, 4.05)
diode(ax, P, POS, 'D1', (0.55, 0.5)); diode(ax, Q, POS, 'D2', (0.55, -0.5))
diode(ax, N, P, 'D3', (-0.55, 0.5)); diode(ax, N, Q, 'D4', (-0.55, -0.5))
for p in (P, Q, N, POS): dot(ax, p)
ax.text(6.5, 7.3, 'P', ha='center', fontsize=13, color='#666'); ax.text(6.5, 1.0, 'Q', ha='center', fontsize=13, color='#666')
wire(ax, N, (4.4, 0.2), (13.4, 0.2))
ax.plot([4.2, 4.6], [1.5, 1.5], c='white', lw=3.5, zorder=3)                       # wire hop
ax.add_patch(Arc((4.4, 1.5), 0.4, 0.4, theta1=0, theta2=180, ec=INK, lw=2.6, zorder=4))
wire(ax, POS, (13.4, 4.05))
cx = 10.0                                                                          # filter capacitor
wire(ax, (cx, 4.05), (cx, 2.55)); wire(ax, (cx, 1.75), (cx, 0.2))
wire(ax, (cx-0.55, 2.55), (cx+0.55, 2.55), lw=4); wire(ax, (cx-0.55, 1.75), (cx+0.55, 1.75), lw=4)
dot(ax, (cx, 4.05)); dot(ax, (cx, 0.2))
ax.text(cx-0.45, 2.95, '+', fontsize=15, fontweight='bold', color='#1f5fa8')
ax.text(cx+0.2, 3.35, 'C1\n1000 µF\n25 V', ha='left', va='center', fontsize=10.5, fontweight='bold')
lx = 12.1                                                                          # LED + resistor branch
wire(ax, (lx, 4.05), (lx, 3.5))
zz = [(lx, 3.5)] + [(lx+(0.2 if i % 2 == 0 else -0.2), 3.5-0.17*(i+0.5)) for i in range(6)] + [(lx, 2.45)]
wire(ax, *zz); wire(ax, (lx, 2.45), (lx, 2.2))
ax.add_patch(Polygon([(lx-0.33, 2.2), (lx+0.33, 2.2), (lx, 1.55)], closed=True, fc='white', ec=INK, lw=2.6))
wire(ax, (lx-0.33, 1.55), (lx+0.33, 1.55), lw=3.2); wire(ax, (lx, 1.55), (lx, 0.2))
for dy in (0.0, 0.28):
    ax.annotate('', xy=(lx+0.95, 2.45-dy), xytext=(lx+0.45, 1.95-dy), arrowprops=dict(arrowstyle='-|>', color='#2e8b3a', lw=2))
dot(ax, (lx, 4.05)); dot(ax, (lx, 0.2))
ax.text(lx+0.45, 3.0, 'R\n1 kΩ', ha='left', va='center', fontsize=11, fontweight='bold')
ax.text(lx+0.55, 0.85, 'Green LED', ha='left', va='center', fontsize=11, fontweight='bold', color='#2e8b3a')
for y, lab, col in ((4.05, 'DC+  (orange jumper)', '#c75a00'), (0.2, 'DC−  (brown jumper)', '#6b4a2b')):
    ax.add_patch(Circle((13.4, y), 0.14, fc='white', ec=INK, lw=2.4, zorder=5))
    ax.text(13.7, y, lab, fontsize=11, fontweight='bold', color=col, va='center')
ax.text(13.7, 2.1, 'free ends = bare male pins\n(output terminals, left\nunconnected)', fontsize=10, color='#555', va='center')
ax.text(5.2, 4.05, '−', fontsize=22, color='#1f5fa8', ha='right', va='center', fontweight='bold')
ax.text(8.8, 4.55, '+', fontsize=22, color='#1f5fa8', ha='left', va='center', fontweight='bold')
fig.savefig(f'{OUT}/fig7_circuit.png', bbox_inches='tight', dpi=170, facecolor='white'); plt.show()

# %% Figure 10 – output waveform with and without the filter
G, RD, OR, BL = '#2e7d32', '#c8102e', '#e07b00', '#1565c0'
cols = {100: OR, 220: BL, 470: RD, 1000: G}
t, vs, u = run(None, T=0.08); tm = t*1e3
sims = {C: run(C*1e-6, T=0.08)[2] for C in (100, 220, 470, 1000)}
fig, (a1, a2) = plt.subplots(2, 1, figsize=(7.6, 6.2), dpi=180)
a1.plot(tm, vs, c='#b0b0b0', lw=1.1, label='Transformer secondary')
a1.plot(tm, u, c='#555', lw=1.3, ls='--', label='Without filter')
a1.plot(tm, sims[1000], c=G, lw=2.4, label='With C1 = 1000 µF (as built)')
a1.set(ylabel='Voltage (V)', xlim=(-2, 80)); a1.set_title('(a) Full view', loc='left', fontsize=10)
a1.legend(loc='lower right', fontsize=8); a1.grid(alpha=.25)
for C in (100, 220, 470):
    a2.plot(tm, sims[C], c=cols[C], lw=1.2, ls='--', label=f'{C} µF (simulated, for comparison)')
a2.plot(tm, sims[1000], c=G, lw=2.6, label='1000 µF (as built)')
a2.set(xlim=(30, 80), ylim=(14.0, 15.9), xlabel='Time (ms)', ylabel='Output voltage (V)')
a2.set_title('(b) Zoomed view of the ripple', loc='left', fontsize=10); a2.grid(alpha=.25); a2.legend(loc='lower left', fontsize=7.5, ncol=2)
mm = (tm >= 40) & (tm <= 60); vmax, vmin = sims[1000][mm].max(), sims[1000][mm].min()
a2.annotate(f'ripple (1000 µF): V$_{{r(pp)}}$ ≈ {vmax-vmin:.2f} V', xy=(54.5, vmin), xytext=(56, 15.78), fontsize=8.5, arrowprops=dict(arrowstyle='->'))
for a in (a1, a2): a.spines[['top', 'right']].set_visible(False)
plt.tight_layout(); fig.savefig(f'{OUT}/fig10_waveform.png', dpi=180, facecolor='white'); plt.show()

# %% Figure 11 – ripple factor vs capacitance
Cs = np.logspace(np.log10(47e-6), np.log10(4700e-6), 60)
def ripple_pct(C, Rser):
    I = (Vp - VF)/Rser; Vr = I/(2*f*C); Vdc = Vp - Vr/2
    return Vr/(2*np.sqrt(3)*Vdc)*100
fig, ax = plt.subplots(figsize=(7.6, 4.2), dpi=180)
for Rser, c, l in ((470, RD, 'R = 470 Ω'), (1000, G, 'R = 1 kΩ (as built)'), (2200, BL, 'R = 2.2 kΩ')):
    ax.loglog(Cs*1e6, ripple_pct(Cs, Rser), c=c, lw=2.4 if Rser == 1000 else 1.6, label=l)
g0 = ripple_pct(C_BUILT, R)
ax.plot(1000, g0, 'o', c='k', ms=8, zorder=5)
ax.annotate(f'built circuit\n(1000 µF, 1 kΩ)\nγ ≈ {g0:.2f} %', xy=(1000, g0), xytext=(1400, 2.2), fontsize=8.5, arrowprops=dict(arrowstyle='->'))
ax.set(xlabel='Filter capacitance C (µF)', ylabel='Ripple factor γ (%)'); ax.grid(alpha=.3, which='both')
ax.legend(fontsize=8.5, title='Series resistor with LED', title_fontsize=8.5); ax.spines[['top', 'right']].set_visible(False)
plt.tight_layout(); fig.savefig(f'{OUT}/fig11_ripple_vs_C.png', dpi=180, facecolor='white'); plt.show()

# %% Figure 12 – average output voltage vs load current (small-ripple approximation)
I = np.linspace(0, 60e-3, 100)
fig, ax = plt.subplots(figsize=(7.6, 4.2), dpi=180)
for C in (100, 220, 470, 1000):
    ax.plot(I*1e3, Vp - I/(4*f*C*1e-6), c=cols[C], lw=2.4 if C == 1000 else 1.6, label=f'C = {C} µF')
y0 = Vp - 13.5e-3/(4*f*C_BUILT)
ax.plot(13.5, y0, 'o', c='k', ms=8, zorder=5)
ax.annotate('built circuit\n(≈ 13.5 mA, 1000 µF)', xy=(13.5, y0), xytext=(24, 15.9), fontsize=8.5, arrowprops=dict(arrowstyle='->'))
ax.set(xlabel='Load current (mA)', ylabel='Average output voltage V$_{dc}$ (V)', ylim=(8, 16.4)); ax.grid(alpha=.3)
ax.legend(fontsize=8.5, loc='lower left'); ax.spines[['top', 'right']].set_visible(False)
plt.tight_layout(); fig.savefig(f'{OUT}/fig12_vdc_vs_I.png', dpi=180, facecolor='white'); plt.show()

# %% Figures 8 and 9 – photos (put your three photos in the photos/ folder first)
PHOTO_TOP, PHOTO_CLOSE, PHOTO_SIDE = 'photos/top_view.jpeg', 'photos/closeup.jpeg', 'photos/side_view.jpeg'
if all(os.path.exists(p) for p in (PHOTO_TOP, PHOTO_CLOSE, PHOTO_SIDE)):
    # Fig 9: close-up + side view
    a, b = Image.open(PHOTO_CLOSE), Image.open(PHOTO_SIDE)
    fig, axs = plt.subplots(1, 2, figsize=(10, 3.9), dpi=150)
    for ax, im, tt in zip(axs, (a, b), ('(a) Close-up: capacitor, diodes and plugged-in output pins', '(b) Side view of the finished board')):
        ax.imshow(im); ax.axis('off'); ax.set_title(tt, fontsize=9.5)
    plt.tight_layout(); fig.savefig(f'{OUT}/fig9_photo_pair.png', dpi=150, facecolor='white'); plt.show()

    # Fig 8: numbered top view. Marker positions are pixel positions in a 1600x900 photo;
    # adjust them if your photo is different.
    im = Image.open(PHOTO_TOP); box = (440, 100, 1140, 880); cr = im.crop(box); ox, oy = box[0], box[1]
    fig = plt.figure(figsize=(10.2, 6.4), dpi=100); ax = fig.add_axes([0, 0, 0.62, 1]); ax.imshow(cr); ax.axis('off')
    marks = {1: (840, 250), 2: (560, 350), 3: (720, 335), 4: (822, 430), 5: (880, 470),
             6: (975, 440), 7: (970, 522), 8: (900, 565), 9: (838, 408), 10: (570, 650)}
    extra = {4: [(815, 515), (945, 415), (945, 525)], 3: [(1020, 370)], 10: [(660, 530)]}
    offs = {1: (0, -70), 2: (-20, -45), 3: (-45, -35), 4: (-55, 0), 5: (12, 52), 6: (55, -40), 7: (60, 5), 8: (35, 38), 9: (-48, -28), 10: (-8, 38)}
    badge = dict(boxstyle='circle,pad=0.25', fc='#ffe600', ec='black', lw=1.2)
    for k, (x, y) in marks.items():
        for (px, py) in [(x, y)] + extra.get(k, []):
            ax.add_patch(Circle((px-ox, py-oy), 26 if k == 1 else 20, fc='none', ec='#ffe600', lw=2.2))
        ax.text(x-ox+offs[k][0], y-oy+offs[k][1], str(k), fontsize=12, fontweight='bold', ha='center', va='center', bbox=badge)
    leg = ['Transformer T1 (230 V / 12 V)', 'Primary leads (orange) to the\nmains plug', 'Secondary leads (green) to the\nbridge inputs P and Q',
           'Bridge diodes D1–D4 (1N4007)', 'Filter capacitor C1, 1000 µF / 25 V', 'Series resistor R', 'Green LED (indicator)',
           'Orange jumper (DC+): end plugged\ninto the board', 'Brown jumper (DC−): end plugged\ninto the board',
           'Free male pins of the two jumper\nleads (output terminals, unconnected)']
    y = 0.955
    for i, tt in enumerate(leg, 1):
        fig.text(0.645, y, str(i), fontsize=11, fontweight='bold', ha='center', va='top', bbox=dict(boxstyle='circle,pad=0.25', fc='#ffe600', ec='black', lw=1))
        fig.text(0.68, y, tt, fontsize=10.5, va='top'); y -= 0.045*(tt.count('\n')+1) + 0.03
    fig.savefig(f'{OUT}/fig8_photo_annotated.png', dpi=170, facecolor='white'); plt.show()
else:
    print('Photos not found in photos/ – skipping Figures 8 and 9.')
