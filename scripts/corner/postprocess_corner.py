# -*- coding: utf-8 -*-
"""
06_physics/postprocess_corner.py

Chantier D — post-traitement automatique : attend le npz N=512 CONVERGE
(se_n8p0_Re1000_N512.npz, residual < TOL) puis lance l'analyse de coin
(etude_corner_bnd.py, Richardson 64..512).

Resilience : lance en detache (tache planifiee schtasks) — survit a la
destruction du shell harnais. Poll 30 s, deadline 6 h, puis exit.

Sortie : 05_dataset/data_corner/postanalysis.log
"""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NPZ = ROOT / "05_dataset" / "data_corner" / "se_n8p0_Re1000_N512.npz"
ANALYSE = ROOT / "06_physics" / "etude_corner_bnd.py"
LOGF = ROOT / "05_dataset" / "data_corner" / "postanalysis.log"
TOL = 1.0e-8
DEADLINE_S = 6 * 3600
POLL_S = 30


def log(msg: str) -> None:
    with LOGF.open("a", encoding="utf-8") as f:
        f.write(msg + "\n")


def main() -> int:
    t0 = time.time()
    resid = None
    iters = None
    while time.time() - t0 < DEADLINE_S:
        if NPZ.exists():
            import numpy as np
            with np.load(NPZ) as d:
                resid = float(d["residual_lbm"])
                iters = int(d["iters_lbm"])
            if resid < TOL:
                break
            log(f"[post] npz present mais residual={resid:.3e} >= tol "
                f"(iters={iters}) ; pas d'analyse")
            return 1
        time.sleep(POLL_S)
    else:
        log("[post] deadline 6h depassee sans npz converge ; abandon")
        return 2

    log(f"[post] npz CONVERGE iters={iters} residual={resid:.3e} -> analyse")
    with LOGF.open("a", encoding="utf-8") as f:
        r = subprocess.run([sys.executable, str(ANALYSE)],
                           cwd=str(ROOT / "06_physics"),
                           stdout=f, stderr=subprocess.STDOUT, text=True)
    log(f"[post] analyse terminee rc={r.returncode}")
    return r.returncode


if __name__ == "__main__":
    raise SystemExit(main())