
# Creating Test DataSets using sklearn.datasets.make_moon
from sklearn.datasets import make_moons
from matplotlib import pyplot as plt 
from matplotlib import style
 
X, y = make_moons(n_samples = 1000, noise = 0.1)
plt.scatter(X[:, 0], X[:, 1], s = 40, color ='g')
plt.xlabel("X")
plt.ylabel("Y")
 
plt.show()
plt.clf()