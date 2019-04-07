import numpy as np
import matplotlib.pyplot as plt

def draw_vec(P, vec, length):
    P1 = P + vec/np.linalg.norm(vec) * length
    coords = np.vstack([P, P1])
    plt.plot(coords[:,0], coords[:,1])

def draw_point(P):
    plt.plot([P[0]], [P[1]], 'o')
    
def draw_line(A, B):
    coords = np.vstack([A, B])
    plt.plot(coords[:,0], coords[:,1])

def draw_segment(A1, B1, A2, B2):
    draw_line(A1, A2)
    draw_line(B1, B2)
    draw_line(A2, B2)

def draw_tri(A, B, C):
    coords = np.vstack([A, B, C])
    plt.fill(coords[:,0], coords[:,1])    