import numpy as np
import matplotlib.pyplot as plt
from keras.datasets import cifar10
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

(X_train_full, y_train_full), (X_test_full, y_test_full) = cifar10.load_data()

n_train_samples = 1000
n_test_samples = 200
X_train = X_train_full[:n_train_samples]
y_train = y_train_full[:n_train_samples]
X_test = X_test_full[:n_test_samples]
y_test = y_test_full[:n_test_samples]

y_train_reg = (y_train == 0).astype(int).ravel()
y_test_reg = (y_test == 0).astype(int).ravel()

X_train_flat = X_train.reshape(n_train_samples, -1)
X_test_flat = X_test.reshape(n_test_samples, -1)

print("Первые 5 меток для регрессии:", y_train_reg[:5])

pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('pca', PCA(n_components=50)),
    ('regressor', LinearRegression())
])

pipeline.fit(X_train_flat, y_train_reg)

y_pred_train = pipeline.predict(X_train_flat)
y_pred_test = pipeline.predict(X_test_flat)

mse_train = mean_squared_error(y_train_reg, y_pred_train)
mse_test = mean_squared_error(y_test_reg, y_pred_test)
print(f"Среднеквадратичная ошибка на обучающей выборке: {mse_train:.2f}")
print(f"Среднеквадратичная ошибка на тестовой выборке: {mse_test:.2f}")

plt.figure(figsize=(10, 5))
plt.scatter(y_train_reg, y_pred_train, color='red', label='Предсказания')
plt.plot([0, 1], [0, 1], color='blue', linestyle='--', label='Идеальная линия')
plt.title('Истинные vs Предсказанные значения (Обучающая выборка)')
plt.xlabel('Истинная метка (0 или 1)')
plt.ylabel('Предсказанная склонность')
plt.legend()
plt.grid(True)
plt.show()

plt.figure(figsize=(10, 5))
plt.scatter(y_test_reg, y_pred_test, color='green', label='Предсказания')
plt.plot([0, 1], [0, 1], color='blue', linestyle='--', label='Идеальная линия')
plt.title('Истинные vs Предсказанные значения (Тестовая выборка)')
plt.xlabel('Истинная метка (0 или 1)')
plt.ylabel('Предсказанная склонность')
plt.legend()
plt.grid(True)
plt.show()

plt.figure(figsize=(10, 3))
for i in range(3):
    plt.subplot(1, 3, i + 1)
    plt.imshow(X_train[i])
    plt.title(f'Склонность: {y_pred_train[i]:.2f}\nИстинная: {y_train_reg[i]}')
    plt.axis('off')
plt.suptitle('Примеры изображений с предсказанной склонностью к классу "самолёт"')
plt.show()
