# -*- coding: utf-8 -*-
"""
Created on Fri Aug 12 12:47:32 2022

@author: chene
"""

# for numpy
import numpy as np
import numpy.matlib
import math

def AOPA_Major(X, Y, tol):
    """
    Computes the Procrustean fiducial registration between X and Y with
    anisotropic Scaling:
        
        Y = R * A * X + t
        
    where X is a mxn matrix, m is typically 3
          Y is a mxn matrix, same dimension as X
          
          R is a mxm rotation matrix,
          A is a mxm diagonal scaling matrix, and
          t is a mx1 translation vector
          
    based on the Majorization Principle
    """
    [m,n] = X.shape
    II = np.identity(n) - np.ones((n,n))/n
    # demean X, and Y
    # and also normalize X (by row) after demean, in matlab:
    # mX = normr(X*II); mY = Y*II
    mX = np.nan_to_num(np.matmul(X,II)/np.linalg.norm(np.matmul(X,II), ord=2, axis=1, keepdims=True))
    mY = np.matmul(Y,II)
    
    # estimate the initial rotation
    # B = mY*mX'; [U,~,V] = svd( B ); 
    B = np.matmul(mY, mX.transpose())
    u, s, vh = np.linalg.svd(B)
    
    # check for flip
    # D   = eye(m); D(m,m) = det(U*V'); R = U*D*V';
    D = np.identity(m)
    D[m-1,m-1] = np.linalg.det(np.matmul(u,vh))
    R = np.matmul(u, np.matmul(D,vh))
    
    # loop
    # err = +Inf; E_old = 10000*ones(m,n);
    err = np.Infinity
    E_old = 1000000 * np.ones((m,n))
    while err > tol:
        # [U,~,V] = svd( B*diag(diag(R'*B)) ); 
        u, s, vh = np.linalg.svd( np.matmul(B, np.diag(np.diag(np.matmul(R.transpose(),B)))) )
        # R = U*[1 0 0; 0 1 0; 0 0 det(U*V')]*V';
        D[m-1,m-1] = np.linalg.det(np.matmul(u,vh))
        R = np.matmul(u, np.matmul(D,vh))
        # E = R*mX-mY;
        E = np.matmul(R,mX) - mY
        # err = norm( E-E_old,'fro' ); E_old = E;
        err = np.linalg.norm(E-E_old)
        E_old = E
    # after rotation is computed, compute the scale
    # B = Y*II*X'; A = diag( diag(B'*R)./diag(X*II*X') ); 
    B = np.matmul(Y, np.matmul(II, X.transpose()))
    A = np.diag( np.divide( np.diag( np.matmul(B.transpose(), R)), np.diag( np.matmul(X, np.matmul(II, X.transpose()))) ) )
    if (math.isnan(A[2,2])):
        # special case for ultrasound calibration, where z=0
        A[2,2] = .5 * (A[0,0] + A[1,1]) # artificially assign a number to the scale in z-axis
    # calculate translation
    # t = mean( Y-R*A*X, 2); 
    t = np.mean( Y - np.matmul(R, np.matmul(A,X)), 1)
    t = np.reshape(t,[m,1])
    return[R,t,A]