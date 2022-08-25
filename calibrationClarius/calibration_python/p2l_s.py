# -*- coding: utf-8 -*-
"""
Created on Fri Aug 12 12:48:46 2022

@author: chene
"""


# for numpy
import numpy as np
import numpy.matlib

from AOPA_Major import AOPA_Major

def p2l_s(X, Y, D, tol):
    """
    Computes the Procrustean point-line registration between X and Y+nD with
    anisotropic Scaling,


    where X is a mxn matrix, m is typically 3
          Y is a mxn matrix denoting line origin, same dimension as X
          D is a mxn normalized matrix denoting line direction

          R is a mxm rotation matrix,
          A is a mxm diagonal scaling matrix, and
          t is a mx1 translation vector
          Q is a mxn fiducial on line that is closest to X after registration
          fre is the fiducial registration error
          
    based on the Majorization Principle
    """
    [m,n] = X.shape
    err = np.Infinity
    E_old = 1000000 * np.ones((m,n))
    e = np.ones((1,n))
    # intialization
    Q = Y
    # normalize the line orientation just in case
    Dir = D/np.linalg.norm(D, ord=2,axis=0,keepdims=True)
    while err > tol:
        [R, t, A] = AOPA_Major(X, Q, tol)
        E  = Q-np.matmul(R,np.matmul(A,X))-np.matmul(t,e)
        # project point to line
        Q = Y+Dir*np.matlib.repmat(np.einsum('ij,ij->j',np.matmul(R,np.matmul(A,X))+np.matmul(t,e)-Y,Dir),m,1)       
        err = np.linalg.norm(E-E_old)
        E_old = E
    E = Q - np.matmul(R, np.matmul(A,X)) - np.matmul(t,e)
    fre = np.sum(np.linalg.norm(E,ord=1,axis=0,keepdims=True))/X.shape[1]
    return[R,t,A,Q,fre]
