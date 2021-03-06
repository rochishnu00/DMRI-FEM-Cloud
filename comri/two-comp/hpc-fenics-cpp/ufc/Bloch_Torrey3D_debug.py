#!/usr/bin/env python
from ufl import *
set_level(DEBUG)
# Copyright (C) 2017 Van-Dang Nguyen (vdnguyen@kth.se)

# This file is part of FEniCS
#
# FEniCS is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

Ve = FiniteElement("CG", tetrahedron, 1)
TH = MixedElement([Ve, Ve, Ve, Ve])

v = TestFunction(TH)
v0r, v0i, v1r, v1i = v[0], v[1], v[2], v[3]

w = TrialFunction(TH);
u0r, u0i, u1r, u1i = w[0], w[1], w[2], w[3]

u_0= Coefficient(TH)
u0r_0, u0i_0, u1r_0, u1i_0  = u_0[0], u_0[1], u_0[2], u_0[3]

V_DG = FiniteElement("DG", tetrahedron, 0)
phase = Coefficient(V_DG)

GX = Coefficient(Ve)
ft_a = Coefficient(TH)
ft = ft_a[0];

gnorm = Coefficient(Ve)
K = Coefficient(Ve)
theta = Coefficient(Ve)
dt = Coefficient(Ve)

kappa = Coefficient(Ve)


def interface_cond(kappa, u0rm, u1rm, v0r, v1r, u0im, u1im, v0i, v1i):
    F_bcr = kappa*(u0rm-u1rm)*(v0r-v1r)
    F_bci = kappa*(u0im-u1im)*(v0i-v1i)
    return F_bcr + F_bci


def FuncF(ft, gnorm, GX, ur, ui, vr, vi, K):
    Fr = ft*gnorm*GX*ui*vr - K*inner(grad(ur), grad(vr))
    Fi = - ft*gnorm*GX*ur*vi - K*inner(grad(ui), grad(vi))
    return Fr + Fi

def ThetaMethod_L(ft, gnorm, GX,  u0r,  u0i, v0r, v0i, u1r,  u1i, v1r, v1i, dt, K, theta, u0r_0, u0i_0, u1r_0, u1i_0):
    L0 = (1-phase)*(u0r_0/dt*v0r + u0i_0/dt*v0i+(1-theta)*FuncF(ft, gnorm, GX, u0r_0, u0i_0, v0r, v0i, K))*dx
    L1 =     phase*(u1r_0/dt*v1r + u1i_0/dt*v1i+(1-theta)*FuncF(ft, gnorm, GX, u1r_0, u1i_0, v1r, v1i, K))*dx
    L_bc = avg((1-theta)*interface_cond(kappa, u0r_0, u1r_0, v0r, v1r, u0i_0, u1i_0, v0i, v1i))*abs(jump(phase))*dS;
    return L0+L1-L_bc


def ThetaMethod_a(ft, gnorm, GX, u0r, u0i, v0r, v0i, u1r, u1i, v1r, v1i, dt, K, theta):
    a0 = (1-phase)*(u0r/dt*v0r   + u0i/dt*v0i  -theta*FuncF(ft, gnorm, GX, u0r , u0i , v0r, v0i, K))*dx
    a1 =     phase*(u1r/dt*v1r   + u1i/dt*v1i  -theta*FuncF(ft, gnorm, GX, u1r , u1i , v1r, v1i, K))*dx
    a_bc = avg(  (theta*interface_cond(kappa, u0r  , u1r  , v0r, v1r, u0i  , u1i  , v0i, v1i)))*abs(jump(phase))*dS;
    return a0+a1+a_bc
    

a = ThetaMethod_a(ft, gnorm, GX, u0r, u0i, v0r, v0i, u1r, u1i, v1r, v1i, dt, K, theta)
L = ThetaMethod_L(ft, gnorm, GX, u0r, u0i, v0r, v0i, u1r, u1i, v1r, v1i, dt, K, theta, u0r_0, u0i_0, u1r_0, u1i_0)


kappa_e = Coefficient(Ve)
L_bc =  kappa_e*(u1r_bc*v1r   + u1i_bc*v1i)*    phase*ds; # u1r_0, u1i_0                                                                                                          
L_bc += kappa_e*(u0r_bc*v0r   + u0i_bc*v0i)*(1-phase)*ds; # u0r_0, u0i_0 
L += L_bc;