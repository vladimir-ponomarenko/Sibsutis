import numpy as np
import matplotlib.pyplot as plt


# Пономаренко Владимир ИА-231

# ЗАДАНИЕ:
# Сложение гармонических колебаний колебания c различными ча-
# стотами и начальными фазами
# Суммированием гармонических колебаний определенных частот и началь-
# ных фаз можно получить заданный периодический сигнал x(t) произвольной
# формы
# x(t) = сумма от n=0 до N (An * np.cos(2 * np.pi * f0 n t + phin) )
# Выполните сложение колебаний и получите график колебания
# x(t) = π/4cos(2πft −π/2 ) + 4/3π cos(2π3f*t − π/2)
# Выберите значение частоты и интервал времени для отображения 4-5 пери-
# одов полученного колебания.
# Получите график колебания, заданного выражением
# x(t) = сумма от n=0 до 5( 4/((2n-1)*π)cos(2π(2n-1)ft-π/2) )
# Выберите значение частоты и интервал времени для отображения 4-5 пе-
# риодов полученного колебания. Постройте графики колебаний с последующим
# увеличением числа слагаемых в сумме.


f = 1 
t = np.linspace(0, 2, 200) 

x = 4/np.pi * np.cos(2 * np.pi * f * t - np.pi / 2) + 4/(3*np.pi) * np.cos(2 * np.pi * 3 * f * t - np.pi / 2)

plt.figure(figsize=(10, 4))
plt.plot(t, x)
plt.title("График колебания: 4/π*cos(2πft - π/2) + 4/3π cos(2π3ft - π/2)")
plt.xlabel("Время (с)")
plt.ylabel("Амплитуда")
plt.grid(True)
plt.show()


f = 1
t = np.linspace(0, 2, 200)

plt.figure(figsize=(10, 4))
for N in range(1, 6):
    x = 0
    for n in range(N):
        x += 4 / ((2 * (n + 1) - 1) * np.pi) * np.cos(2 * np.pi * (2 * (n + 1) - 1) * f * t - np.pi / 2)
    plt.plot(t, x, label=f"N = {N}")

plt.title("Сложение гармонических колебаний")
plt.xlabel("Время (с)")
plt.ylabel("Амплитуда")
plt.legend()
plt.grid(True)
plt.show()
