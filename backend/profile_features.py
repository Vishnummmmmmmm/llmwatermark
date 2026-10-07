import sys; sys.path.append('backend')
import re, json, torch, numpy as np
from watermark_detector import WatermarkDetectorPipeline

p = WatermarkDetectorPipeline()
dev = json.load(open('backend/data/dev_data.json', encoding='utf-8'))

for cat in ['clean', 'kgw_token_bias']:
    samps = [s for s in dev if s['watermark_type'] == cat]
    w3, rl, ge, gr = [], [], [], []
    for s in samps:
        f = p.extract_features(s['text'])
        w3.append(float(f[0,7].item()))
        rl.append(int(f[0,9].item()))
        ge.append(float(f[0,6].item()) / 100.0)
        gr.append(float(f[0,5].item()))
    a3 = np.array(w3); ar = np.array(rl); ag = np.array(ge); agr = np.array(gr)
    print(f"{cat} (N={len(samps)}):")
    print(f"  green_ratio:  mean={agr.mean():.3f} med={np.median(agr):.3f} min={agr.min():.3f} max={agr.max():.3f}")
    print(f"  win3_max:     mean={a3.mean():.3f} med={np.median(a3):.3f} min={a3.min():.3f} max={a3.max():.3f}")
    print(f"  max_run_len:  mean={ar.mean():.1f} med={np.median(ar):.0f} min={ar.min()} max={ar.max()}")
    print(f"  green_elev:   mean={ag.mean():.4f} med={np.median(ag):.4f} min={ag.min():.4f} max={ag.max():.4f}")
    # count how many pass each KGW detection rule
    z_pass = 0; gr_pass = 0; combo_pass = 0
    for s in samps:
        f = p.extract_features(s['text'])
        km = int(f[0,4].item())
        cw = [re.sub(r'[^\w]','',w).lower() for w in s['text'].split() if w]
        nw = max(1,len(cw))
        zs = (km - 0.5*nw) / max(1e-6, 0.5*(nw**0.5))
        g_ratio = float(f[0,5].item())
        g_elev = float(f[0,6].item()) / 100.0
        w3v = float(f[0,7].item())
        rlv = int(f[0,9].item())
        if zs >= 1.70: z_pass += 1
        if g_ratio >= 0.58 and nw >= 10: gr_pass += 1
        if g_elev > 0.08 and (w3v >= 0.67 or rlv >= 3): combo_pass += 1
    print(f"  KGW rules fire: z>=1.70: {z_pass}  gr>=0.58: {gr_pass}  combo: {combo_pass}")
    total = len(set(range(len(samps))))  # just count unique
    print()
