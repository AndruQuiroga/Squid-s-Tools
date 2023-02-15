import matplotlib.pyplot as plt
import numpy as np



r1 = np.random.randint(1, 21, 100000)
r2 = np.random.randint(1, 21, 100000)

# get higher of the two
r3 = np.maximum(r1, r2)
plt.hist(r3, bins=20)
plt.show()




