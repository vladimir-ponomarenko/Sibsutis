import numpy as np
import matplotlib.pyplot as plt

A = [1, 0.7, 0.5] 
f = [1, 3, 5]     
phi = [0, 0, 0]  
A0 = 0.5        
t = np.linspace(0, 2, 500)  

signals = []
for i in range(len(f)):
    signals.append(A[i] * np.sin(2 * np.pi * f[i] * t ))

x = A0 + sum(signals)

spectrum = np.fft.fft(x)
frequencies = np.fft.fftfreq(x.size, d=t[1] - t[0])

plt.figure(figsize=(12, 6))

plt.subplot(2, 1, 1) 
for i in range(len(signals)):
    plt.plot(t, signals[i], label=f'Сигнал {i+1} (f = {f[i]} Гц)')

plt.plot(t, x, linewidth=2, label='Результирующий сигнал')

plt.subplot(2, 1, 2)  
plt.stem(frequencies, np.abs(spectrum), use_line_collection=True)
plt.title('Спектр сигнала')
plt.xlabel('Частота (Гц)')
plt.ylabel('Амплитуда')
plt.xlim(-10, 10) 
plt.tight_layout() 
plt.show()