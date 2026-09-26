

import numpy as np
import matplotlib.pyplot as plt

y = ([80, 50, 30, 20])
x = np.array(["Python", "C", "JavaScript", "CSS"])

font1 = {"family" : "serif", "color" : "r"}
font2 = {"family" : "arial", "color" : "b"}

plt.suptitle("MY SKILLS BAR GRAPH", fontdict = font1,  size = 30)
plt.ylabel("LEVEL OF PERCENT", fontdict = font2, size = 20)
plt.xlabel("PROGRAMMING LANGUAGE", fontdict = font2, size = 20)
plt.bar(x, y)
plt.show()