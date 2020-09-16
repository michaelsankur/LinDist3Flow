import numpy as np
def compute_NR3FT_vectorized(X, g_SB, b_SB, G_KVL, b_KVL, H, g, b, nnode, nline, H_reg, G_reg):
    FTSUBV = (g_SB @ X) - b_SB
    #FTKVL = np.zeros((2*3*nline, 1))
    # for j in range(2*3*nline):
    #     r = (X.T @ (H_reg[j, :, :] @ X)) + (G_KVL[j, :] @ X) - b_KVL[j]
    #     FTKVL[j, :] = r
    FTKVL = (G_KVL @ X) - b_KVL

    FTKCL = np.zeros((2*3*(nnode-1), 1))

    for i in range(2*3*(nnode-1)):
        r = (X.T @ (H[i, :, :] @ X)) \
        + (g[i, 0,:] @ X) \
        + b[i, 0,0]
        FTKCL[i, :] = r


    FTVR = np.zeros((2*3, 1))
    for i in range(2*3):
        r = X.T @ (H[i, :, :] @ X)
        FTVR[i, :] = r

    FTVR2 = G_reg @ X

    FT = np.r_[FTSUBV, FTKVL, FTKCL, FTVR, FTVR2]



    return FT