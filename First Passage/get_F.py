import string
import numpy as np
import sys
from numpy.linalg import matrix_power

file = open('matrix.txt')

mat_orig = []
for line in file:
	mat_orig.append(line.split())

dim = len(mat_orig)

divs = 0

for i in range(dim):
	if(mat_orig[i][dim-1]!="x"):
		divs += 1

for p in np.linspace(0.1,1.0, 20):
	# print(p)
	mp = {}
	mp['1'] = 1.0
	mp['0'] = 0.0
	mp['p'] = p
	mp['x'] = 'x'
	mp['q'] = 1.0 - mp['p']
	mat = mat_orig.copy()

	mat = [[mp.get(x) for x in l] for l in mat]
	for i in range(dim):
		if mat[i][dim-3] != 'x':
			mat[i][dim-3] = 1.0/float(divs)
			mat[i][dim-2] = 1.0/float(divs)
			mat[i][dim-1] = 1.0/float(divs)
	for i in range(dim):
		if mat[i][dim-3] == 'x':
			mat[i][dim-3] = 0.0
			mat[i][dim-2] = 0.0
			mat[i][dim-1] = 0.0


	 

	mat = np.array(mat)
	# np.set_printoptions(threshold=sys.maxsize)
	E = np.full((dim,dim),1.0)
	# #let's regularize the last column of mat by making it random reflective, instead of absorbing
	# for i in range(dim):
	# 	mat[i][dim-1] = 1.0/float(dim)
	A = matrix_power(mat,1000000)
	# for i in range(dim):
	# 	print(np.sum(np.transpose(A)[i]))
	np.set_printoptions(threshold=sys.maxsize)
	Dmat = np.full((dim,dim),0.0) 
	for i in range(dim):
		Dmat[i][i] = 1.0/A[i][i];
	Z = np.linalg.inv(np.identity(dim)-mat+A)
	Z0 = np.diag(np.diag(Z))
	F = np.matmul(Dmat,np.identity(dim)-Z+np.matmul(Z0,E))
	print("{} {}".format(p,F[dim-3][0]))
