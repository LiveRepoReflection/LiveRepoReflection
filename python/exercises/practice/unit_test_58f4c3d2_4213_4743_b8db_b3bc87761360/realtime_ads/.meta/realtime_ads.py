import math

# Global parameters for the LinUCB algorithm
d = 2  # Dimension of context vectors (default)
k = 2  # Number of ads (default)
alpha = 0.1  # Exploration parameter

# Global lists to hold the inverse matrix (A_inv) and vector (b) for each ad
A_inv = []
b = []

def _initialize():
    global A_inv, b, d, k
    A_inv = [[_identity_matrix(d) for _ in range(1)][0] for _ in range(k)]
    # Initialize each A_inv as identity matrix and each b as zero vector
    A_inv = [_identity_matrix(d) for _ in range(k)]
    b = [[0.0 for _ in range(d)] for _ in range(k)]

def _identity_matrix(n):
    return [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]

def _dot(u, v):
    return sum(x*y for x, y in zip(u, v))

def _mat_vec(M, v):
    return [ _dot(row, v) for row in M]

def _outer(u, v):
    return [[x*y for y in v] for x in u]

def choose_ad(context_vector):
    global A_inv, b, d, k, alpha
    # If not initialized, initialize with the dimension from the context_vector if necessary.
    if len(A_inv) == 0 or len(b) == 0:
        # Update global dimension if needed.
        d = len(context_vector)
        _initialize()
    best_ad = 0
    best_score = -float("inf")
    for i in range(k):
        # theta = A_inv * b
        theta = _mat_vec(A_inv[i], b[i])
        exploitation = _dot(context_vector, theta)
        # exploration term: sqrt( x^T A_inv x)
        A_inv_x = _mat_vec(A_inv[i], context_vector)
        exploration = alpha * math.sqrt(max(_dot(context_vector, A_inv_x), 0.0))
        score = exploitation + exploration
        if score > best_score:
            best_score = score
            best_ad = i
    return best_ad

def update(context_vector, chosen_ad, reward):
    global A_inv, b, d, k
    # Verify initialization
    if len(A_inv) == 0 or len(b) == 0:
        d = len(context_vector)
        _initialize()
    # Update b for the chosen ad: b = b + reward * context_vector
    b[chosen_ad] = [bi + reward * ci for bi, ci in zip(b[chosen_ad], context_vector)]
    # Update A_inv for the chosen ad using Sherman-Morrison formula
    # Let u = context_vector (as column vector)
    u = context_vector
    # v = A_inv * u
    v = _mat_vec(A_inv[chosen_ad], u)
    denom = 1.0 + _dot(u, v)
    # Compute outer product of v with itself
    outer_vv = _outer(v, v)
    # Update A_inv: A_inv = A_inv - outer_vv/denom
    new_A_inv = []
    for i in range(d):
        new_row = []
        for j in range(d):
            new_row.append(A_inv[chosen_ad][i][j] - outer_vv[i][j] / denom)
        new_A_inv.append(new_row)
    A_inv[chosen_ad] = new_A_inv