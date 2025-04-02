import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import mean_squared_error, r2_score


print("Библиотеки успешно импортированы.")

print("\n--- Загрузка и подготовка данных ---")
try:
    dataset = sns.load_dataset('mpg')
    print("Датасет 'mpg' успешно загружен.")

    print("\nПервые 5 строк датасета:")
    print(dataset.head())
    print("\nИнформация о датасете:")
    dataset.info()

    print("\nПропущенные значения по столбцам:")
    print(dataset.isnull().sum())

    dataset.dropna(subset=['horsepower'], inplace=True)
    print(f"\nУдалены строки с пропущенными значениями в 'horsepower'. Новый размер датасета: {dataset.shape}")

    X = dataset[['horsepower']].values
    y = dataset['mpg'].values

    print(f"\nМатрица признаков X (первые 5): \n{X[:5]}")
    print(f"\nЗависимая переменная y (первые 5): \n{y[:5]}")
    print(f"\nРазмер X: {X.shape}, Размер y: {y.shape}")

except Exception as e:
    print(f"\nОшибка при загрузке или обработке данных: {e}")
    print("Убедитесь, что библиотека seaborn установлена (`pip install seaborn`) и есть доступ к интернету для скачивания датасета.")
    exit()

print("\n--- Визуализация исходных данных ---")
plt.figure(figsize=(10, 6))
plt.scatter(X, y, color='red', alpha=0.6)
plt.title('Зависимость MPG от мощности (Horsepower)')
plt.xlabel('Мощность (Horsepower)')
plt.ylabel('Расход топлива (MPG)')
plt.grid(True)
plt.show()
print("График исходных данных показан.")

print("\n--- Анализ моделей с разной степенью полинома ---")

degrees = [1, 2, 4, 10]

X_grid = np.arange(min(X), max(X), 0.1)
X_grid = X_grid.reshape((len(X_grid), 1))

plt.figure(figsize=(12, 8))
plt.scatter(X, y, color='red', label='Исходные данные', alpha=0.6)

results = {}

for degree in degrees:
    print(f"\n--- Обучение и визуализация для степени полинома = {degree} ---")

    poly_reg = PolynomialFeatures(degree=degree)
    X_poly = poly_reg.fit_transform(X)
    # print(f"Размер X_poly (degree={degree}): {X_poly.shape}")

    lin_reg = LinearRegression()
    lin_reg.fit(X_poly, y)
    print(f"Модель для степени {degree} обучена.")

    y_pred = lin_reg.predict(X_poly)
    mse = mean_squared_error(y, y_pred)
    r2 = r2_score(y, y_pred)
    results[degree] = {'mse': mse, 'r2': r2}
    print(f"Оценка модели (degree={degree}): MSE = {mse:.2f}, R^2 = {r2:.4f}")


    X_grid_poly = poly_reg.transform(X_grid)
    y_grid_pred = lin_reg.predict(X_grid_poly)

    plt.plot(X_grid, y_grid_pred, label=f'Полином степени {degree} (R^2={r2:.3f})')


plt.title('Полиномиальная регрессия: MPG vs Horsepower (разные степени)')
plt.xlabel('Мощность (Horsepower)')
plt.ylabel('Расход топлива (MPG)')
plt.legend()
plt.grid(True)
plt.ylim(bottom=0)
plt.show()

print("\n--- Сводка по метрикам качества ---")
print("Степень | MSE     | R^2")
print("--------|---------|-------")
for degree, metrics in results.items():
    print(f"{degree:<7} | {metrics['mse']:<7.2f} | {metrics['r2']:.4f}")

