import numpy as np
import matplotlib.pyplot as plt
from keras.datasets import cifar10
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

# 2. Загрузка CIFAR-10
(X_train_full, y_train_full), (X_test_full, y_test_full) = cifar10.load_data()

n_train_samples = 1000
n_test_samples = 200
X_train = X_train_full[:n_train_samples]
X_test = X_test_full[:n_test_samples]

# 3. Подготовка данных для регрессии
X_train_gray = X_train.mean(axis=3)
X_test_gray = X_test.mean(axis=3)

y_train = X_train_gray.mean(axis=(1, 2))
y_test = X_test_gray.mean(axis=(1, 2))

X_train_flat = X_train_gray.reshape(n_train_samples, -1)
X_test_flat = X_test_gray.reshape(n_test_samples, -1)

print("Первые 5 значений целевой переменной (средняя яркость):")
print(y_train[:5])

# 4. Разделение данных

# 5. Создание универсального пайплайна
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('regressor', LinearRegression())
])

# 6. Обучение модели
pipeline.fit(X_train_flat, y_train)

# 7. Предсказание результатов
y_pred_train = pipeline.predict(X_train_flat)
y_pred_test = pipeline.predict(X_test_flat)

mse_train = mean_squared_error(y_train, y_pred_train)
mse_test = mean_squared_error(y_test, y_pred_test)
print(f"Среднеквадратичная ошибка на обучающей выборке: {mse_train:.2f}")
print(f"Среднеквадратичная ошибка на тестовой выборке: {mse_test:.2f}")

# 8. Визуализация результатов
plt.figure(figsize=(10, 5))
plt.scatter(y_train, y_pred_train, color='red', label='Предсказания')
plt.plot([y_train.min(), y_train.max()], [y_train.min(), y_train.max()],
         color='blue', linestyle='--', label='Идеальная линия')
plt.title('Истинные vs Предсказанные значения (Обучающая выборка)')
plt.xlabel('Истинная средняя яркость')
plt.ylabel('Предсказанная средняя яркость')
plt.legend()
plt.grid(True)
plt.show()

plt.figure(figsize=(10, 5))
plt.scatter(y_test, y_pred_test, color='green', label='Предсказания')
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()],
         color='blue', linestyle='--', label='Идеальная линия')
plt.title('Истинные vs Предсказанные значения (Тестовая выборка)')
plt.xlabel('Истинная средняя яркость')
plt.ylabel('Предсказанная средняя яркость')
plt.legend()
plt.grid(True)
plt.show()

plt.figure(figsize=(10, 3))
for i in range(3):
    plt.subplot(1, 3, i + 1)
    plt.imshow(X_train[i])
    plt.title(f'Яркость: {y_pred_train[i]:.2f}')
    plt.axis('off')
plt.show()
