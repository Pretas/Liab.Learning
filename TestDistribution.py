import numpy as np
import matplotlib.pyplot as plt
import math


a = chr(92)


################# My dist. #########################

yr = [5,10,15,20]
s = np.random.choice(yr, 1000, p=[0.1, 0.40, 0.1,0.4])

count, bins, ignored = plt.hist(s, 15, density=True, color='y')
plt.plot(bins, np.ones_like(bins), linewidth=2, color='b')
plt.show()


################# Uniform #########################

# 샘플
s = np.random.uniform(0,30,1000)
# count : 높이(가로*높이 = 확률값 나옴)
# bins : 경계값
count, bins, ignored = plt.hist(s, 15, density=True, color='y')
plt.plot(bins, np.ones_like(bins), linewidth=2, color='b')
plt.show()

s_ = np.array()
for i in s:
    print(math.ceil(i))


################# Normal #########################

muy, sigma = 30, 10 # mean and standard deviation
s =  np.random.normal(muy, sigma, 1000)

count, bins, ignored = plt.hist(s, 100, density=True, color='y')

#plt.plot(bins, linewidth=2, color='b')
plt.plot(bins, 1/(sigma * np.sqrt(2 * np.pi)) * np.exp( - (bins - muy)**2 / (2 * sigma**2) ), linewidth=2, color='b')
plt.show()


################# 베르누이 #########################

s = np.random.binomial(1, 0.4, 1000)

count, bins, ignored = plt.hist(s, 100, density=True, color='y')

#plt.plot(bins, linewidth=2, color='b')
plt.plot(bins, linewidth=2, color='b')
plt.show()



