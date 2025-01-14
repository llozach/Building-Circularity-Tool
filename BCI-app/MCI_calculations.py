#######################################################################################################################
# Material Circularity Indicator
# https://www.ellenmacarthurfoundation.org/assets/downloads/EMF_Material_Circularity_Indicator_2020.pdf
#######################################################################################################################

#%% Define MCI mathematical model
def LFI(V, W, M, W_f, W_c):
    return((V+W) / (2*M + (W_f-W_c)/2) )

def X(L, L_av, U, U_av, M, M_av):
    return((L*U*M) / (L_av*U_av*M_av))

def F(X):
    return(0.9/X)

def MCI(lfi, f):
    return(max(0, 1-lfi*f))