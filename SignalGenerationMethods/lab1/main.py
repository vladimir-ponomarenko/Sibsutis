import numpy as np
import matplotlib.pyplot as plt

sigma = 1.0
N = 8000

hi = np.random.normal(0, sigma**2, N)   
hq = np.random.normal(0, sigma, N)        

h = hi + 1j * hq

plt.figure(figsize=(10,4))

plt.subplot(1,3,1)
plt.hist(np.abs(h), bins=80, density=True)
plt.title('|h|')

plt.subplot(1,3,2)
plt.hist(np.angle(h), bins=80, density=True)
plt.title('arg(h)')

acf = np.correlate(h, h, mode= 'full') / N
lags  = np.arange(-N+1, N)

plt.subplot(1,3,3)
plt.plot(lags, np.abs(acf))
plt.title('Autocorr h')

plt.tight_layout()
plt.show()