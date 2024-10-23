import string
import numpy as np
import sys
from numpy.linalg import matrix_power

file = open('matrix.txt')

mat_orig = []
for line in file:
	mat_orig.append(line.split())

dim = len(mat_orig)

for p in np.linspace(0.1,1.0, 20):
	# print(p)
	mp = {}
	mp['1'] = 1.0
	mp['0'] = 0.0
	mp['p'] = p
	mp['q'] = 1.0 - mp['p']
	mat = mat_orig.copy()

	mat = [[mp.get(x) for x in l] for l in mat]

	mat = np.array(mat)

	E = np.full((dim,dim),1.0)
	#let's regularize the last column of mat by making it random reflective, instead of absorbing
	for i in range(dim):
		mat[i][dim-1] = 1.0/float(dim)
	A = matrix_power(mat,1000000)
	np.set_printoptions(threshold=sys.maxsize)
	Dmat = np.full((dim,dim),0.0) 
	for i in range(dim):
		Dmat[i][i] = 1.0/A[i][i];
	Z = np.linalg.inv(np.identity(dim)-mat+A)
	Z0 = np.diag(np.diag(Z))
	F = np.matmul(Dmat,np.identity(dim)-Z+np.matmul(Z0,E))
	print("{} {}".format(p,F[dim-1][0]))
