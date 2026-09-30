

"""
- so today we're gonnna study pie chart in python
"""

# Pie Chart

import numpy as np
import matplotlib.pyplot as plt

xpoints = np.array([80.0, 40.0, 20.0, 10.0])
my_color = ["#5128e7", "#2998e7", "r", "g"]
my_labels = ["PYTHON", "CSS", "JAVACRIPT", "C#"]
my_explode = [0.1, 0, 0, 0]


plt.pie(xpoints, labels = my_labels, colors = my_color, explode = my_explode, shadow = True)
plt.legend(title = "MY SKILLS", fontsize = 20)
plt.suptitle("RATING OF MY SKILLS", fontsize = 10)

plt.show()