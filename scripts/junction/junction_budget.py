# -*- coding: utf-8 -*-
"""Junction dissipation and artificial-interface energy flux for PH13.

Answers referee #4.4 / #2.4:
  * D_junction(r_j) = 2 nu int_{Omega_junction} S:S dA with the production mask
  * f_junction = D_junction / D_mask
  * the flux of [(1/2)|u|^2 + p]u - 2 nu S.u across the ARTIFICIAL interfaces
    created by excising the junction disks.

The flux is what the previous "power balance off the disks" omitted.  If it is
not negligible, agreement of P and D away from the disks is NOT a verification
of the global energy budget.

Paper units: u = stored ux/uy (lid speed already 1), x = stored X/Y in [-1,1],
nu = 2/Re, p = (rho-1)/(3 U_lid^2) with U_lid = 0.05.  The identity is

    div [ (1/2)|u|^2 u + p u - 2 nu S.u ] = -2 nu S:S = -2 phi,

with phi = (1/Re)(2u_x^2+2v_y^2+(u_y+v_x)^2) and D_mask = 2 sum(phi) dx^2.
Junctions of the tangential upper lid are at (+/-1, 0) for every superellipse.
"""
from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
N_LIST = (1.25, 2.0, 4.0, 8.0)
RE_LIST = (100.0, 1000.0)
RADII = (0.05, 0.10, 0.15)       # r_j / L_c, with L_c = 2
U_LID = 0.05


def grad_valid(fluid):
    v = np.zeros_like(fluid, dtype=bool)
    v[1:-1, 1:-1] = (fluid[1:-1, 1:-1] & fluid[:-2, 1:-1] & fluid[2:, 1:-1]
                     & fluid[1:-1, :-2] & fluid[1:-1, 2:])
    return v


def nearest_valid(arr, valid):
    _, idx = ndimage.distance_transform_edt(~valid, return_indices=True)
    return arr[idx[0], idx[1]]


def interpolate(field, X, Y, xq, yq):
    nx, ny = X.shape
    xi = ((xq - X[0, 0]) / (X[0, 1] - X[0, 0]))
    yi = ((yq - Y[0, 0]) / (Y[1, 0] - Y[0, 0]))
    return ndimage.map_coordinates(field, [yi, xi], order=1, mode="nearest")


def load_case(path):
    with np.load(path) as z:
        out = dict(n=float(z["n"]), Re=float(z["Re"]), N=int(z["N"]),
                   ux=np.asarray(z["ux"], float), uy=np.asarray(z["uy"], float),
                   rho=np.asarray(z["rho"], float),
                   fluid=np.asarray(z["fluid"]).astype(bool),
                   X=np.asarray(z["X"], float), Y=np.asarray(z["Y"], float),
                   dx=float(abs(z["X"][0, 1] - z["X"][0, 0])),
                   cid=str(z["case_id"]))
    return out


def compute(c, rj):
    ux, uy, X, Y, dx = c["ux"], c["uy"], c["X"], c["Y"], c["dx"]
    re = c["Re"]
    nu = 2.0 / re
    valid = grad_valid(c["fluid"])
    gx = np.full(ux.shape, np.nan); gy = np.full(ux.shape, np.nan)
    vx = np.full(ux.shape, np.nan); vy = np.full(ux.shape, np.nan)
    gx[1:-1, 1:-1] = (ux[1:-1, 2:] - ux[1:-1, :-2]) / (2 * dx)
    vx[1:-1, 1:-1] = (uy[1:-1, 2:] - uy[1:-1, :-2]) / (2 * dx)
    gy[1:-1, 1:-1] = (ux[2:, 1:-1] - ux[:-2, 1:-1]) / (2 * dx)
    vy[1:-1, 1:-1] = (uy[2:, 1:-1] - uy[:-2, 1:-1]) / (2 * dx)
    phi = np.where(valid, (2*gx**2 + 2*vy**2 + (gy+vx)**2)/re, 0.0)
    cell = dx * dx
    D = 2.0 * float(np.sum(phi)) * cell

    disk = np.zeros_like(valid)
    for xj in (-1.0, 1.0):
        disk |= (np.hypot(X - xj, Y) <= rj)
    Dd = 2.0 * float(np.sum(np.where(valid & disk, phi, 0.0))) * cell
    Do = D - Dd

    # flux through the artificial circular interfaces (normal points into disk)
    vg = valid & (c["rho"] > 0.5)
    ux_f, uy_f = nearest_valid(ux, vg), nearest_valid(uy, vg)
    gx_f, gy_f, vx_f, vy_f = [nearest_valid(a, vg) for a in (gx, gy, vx, vy)]
    p_fld = np.where(vg, (c["rho"] - 1.0) / (3.0 * U_LID**2), 0.0)
    p_fld = nearest_valid(p_fld, vg)

    # F = (1/2|u|^2 + p)u - 2nu S.u
    Sux = gx_f * ux_f + 0.5 * (gy_f + vx_f) * uy_f
    Suy = 0.5 * (gy_f + vx_f) * ux_f + vy_f * uy_f
    Fx = np.where(vg, (0.5*(ux_f**2+uy_f**2) + p_fld)*ux_f - 2*nu*Sux, 0.0)
    Fy = np.where(vg, (0.5*(ux_f**2+uy_f**2) + p_fld)*uy_f - 2*nu*Suy, 0.0)

    Fx_i, Fy_i = interpolate(Fx, X, Y, X, Y), interpolate(Fy, X, Y, X, Y)
    theta = np.linspace(0.0, 2*np.pi, 720, endpoint=False)
    flux_total = 0.0
    for xj in (-1.0, 1.0):
        xq, yq = xj + rj*np.cos(theta), rj*np.sin(theta)
        fx = interpolate(Fx_i, X, Y, xq, yq)
        fy = interpolate(Fy_i, X, Y, xq, yq)
        # only the arc lying in fluid counts
        inside = interpolate(np.asarray(c["fluid"], float), X, Y, xq, yq) > 0.5
        er_x, er_y = np.cos(theta), np.sin(theta)
        # outward normal of Omega' points INTO the disk: n = -e_r
        fn = -(fx*er_x + fy*er_y)
        flux_total += float(np.sum(np.where(inside, fn, 0.0)) * rj * (2*np.pi/720))
    # NOTE: the interface flux below is reported as an UNVERIFIED diagnostic.
    # See identity_check(): the archived (rho, u) pair does not satisfy the
    # discrete momentum/energy identity, so this quadrature must not be used
    # to claim closure of the energy budget.
    return dict(D=D, D_junction=Dd, f_junction=Dd/D, D_offdisk=Do,
                interface_flux_unverified=flux_total,
                flux_over_Doffdisk_unverified=flux_total/Do)


def identity_check():
    """Check whether div F = -2 phi holds for the archived macroscopic fields.

    This is a precondition for using the interface quadrature as a budget.
    It FAILS on the archived fields, hence the flux column is labelled
    'unverified' and no closure claim is made.
    """
    path = ROOT / "05_dataset" / "data_all190" / "se_n4p0_Re1000_N128.npz"
    c = load_case(path)
    ux, uy, rho, dx, re = c["ux"], c["uy"], c["rho"], c["dx"], c["Re"]
    nu = 2.0 / re
    valid = grad_valid(c["fluid"])
    gx = np.full(ux.shape, np.nan); gy = np.full(ux.shape, np.nan)
    vx = np.full(ux.shape, np.nan); vy = np.full(ux.shape, np.nan)
    gx[1:-1,1:-1] = (ux[1:-1,2:]-ux[1:-1,:-2])/(2*dx)
    vx[1:-1,1:-1] = (uy[1:-1,2:]-uy[1:-1,:-2])/(2*dx)
    gy[1:-1,1:-1] = (ux[2:,1:-1]-ux[:-2,1:-1])/(2*dx)
    vy[1:-1,1:-1] = (uy[2:,1:-1]-uy[:-2,1:-1])/(2*dx)
    phi = np.where(valid, (2*gx**2+2*vy**2+(gy+vx)**2)/re, 0.0)
    vg = valid & (rho > 0.5)
    uxf, uyf, gxf, gyf, vxf, vyf = [nearest_valid(a, vg) for a in (ux,uy,gx,gy,vx,vy)]
    p = nearest_valid(np.where(vg, (rho-1.0)/(3.0*U_LID**2), 0.0), vg)
    Sux = gxf*uxf + 0.5*(gyf+vxf)*uyf
    Suy = 0.5*(gyf+vxf)*uxf + vyf*uyf
    Fx = (0.5*(uxf**2+uyf**2)+p)*uxf - 2*nu*Sux
    Fy = (0.5*(uxf**2+uyf**2)+p)*uyf - 2*nu*Suy
    Ax = 0.5*(uxf**2+uyf**2)*uxf - 2*nu*Sux
    Ay = 0.5*(uxf**2+uyf**2)*uyf - 2*nu*Suy
    Bx, By = p*uxf, p*uyf
    def div(a, b):
        da = np.zeros_like(a); db = np.zeros_like(b)
        da[:,1:-1] = (a[:,2:]-a[:,:-2])/(2*dx)
        db[1:-1,:] = (b[2:,:]-b[:-2,:])/(2*dx)
        return da + db
    core = vg.copy(); core[:2,:]=False; core[-2:,:]=False
    core[:,:2]=False; core[:,-2:]=False
    IA = float(np.sum(div(Ax,Ay)[core])*dx*dx)
    IB = float(np.sum(div(Bx,By)[core])*dx*dx)
    Iphi = float(np.sum(2*phi[core])*dx*dx)
    ratio = (IA+IB)/(-Iphi)
    required_p_scale = (-Iphi-IA)/IB
    print("\n=== discrete identity check on n=4, Re=1000, N=128 ===")
    print("  integral div[A] = %+.6f ; integral div[p u] = %+.6f ; integral 2 phi = %+.6f"
          % (IA, IB, Iphi))
    print("  (div F)/(-2 phi) = %+.3f  (expected +1)" % ratio)
    print("  pressure scale required for closure = %+.4f  (expected +1)" % required_p_scale)
    print("  => archived (rho,u) fields DO NOT satisfy the budget identity;")
    print("     interface flux cannot certify global closure.")
    return dict(int_div_A=IA, int_div_pu=IB, int_2phi=Iphi,
                ratio=ratio, required_pressure_scale=required_p_scale)


def main():
    check = identity_check()
    (OUT / "identity_check.csv").write_text(
        "quantity,value\n" + "\n".join("%s,%.10g" % kv for kv in check.items()),
        encoding="utf-8")
    d128 = ROOT / "05_dataset" / "data_all190"
    d256 = [ROOT / "05_dataset" / "data_conv256", ROOT / "05_dataset" / "data_conv256_lowRe"]
    paths = {}
    for p in d128.glob("*.npz"):
        with np.load(p) as z:
            key = (round(float(z["n"]),4), round(float(z["Re"]),1), 128)
        paths[key] = p
    for d in d256:
        for p in d.glob("*.npz"):
            with np.load(p) as z:
                if "N" not in z.files or int(z["N"]) != 256:
                    continue
                key = (round(float(z["n"]),4), round(float(z["Re"]),1), 256)
            paths[key] = p

    rows = []
    for n in N_LIST:
        for Re in RE_LIST:
            for N in (128, 256):
                p = paths.get((n, Re, N))
                if p is None:
                    continue
                c = load_case(p)
                for rj in RADII:
                    r = compute(c, rj * 2.0)   # rj is r_j/L_c, L_c = 2
                    rows.append(dict(case_id=c["cid"], n=n, Re=Re, N=N,
                                     r_over_Lc=rj, r_physical=rj*2.0, **r))
                print("done", n, Re, N)

    with (OUT / "junction_budget.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print("\n=== D_junction / D_mask and artificial-interface flux ===")
    print("   n    Re    N   r_j/Lc   f_junction   D_offdisk   (flux/D_offdisk, UNVERIFIED)")
    for r in rows:
        print("  %5.2f %6.0f %4d   %5.2f      %.4f      %9.5f      %+8.4f" %
              (r["n"], r["Re"], r["N"], r["r_over_Lc"], r["f_junction"],
               r["D_offdisk"], r["flux_over_Doffdisk_unverified"]))


if __name__ == "__main__":
    main()
