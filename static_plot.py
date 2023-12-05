import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Sample data
np.random.seed(0)
df = pd.DataFrame({
    'X': np.random.rand(10),
    'Y': np.random.rand(10),
    'Z': np.random.rand(10) * 1000
})

# Create bubble plot
plt.scatter('X', 'Y', s='Z', data=df)
plt.xlabel('X Axis Label')
plt.ylabel('Y Axis Label')
plt.title('Bubble Plot Example')
plt.show()


import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

