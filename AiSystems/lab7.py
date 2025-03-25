import numpy as np
import matplotlib.pyplot as plt
from keras.datasets import cifar10
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, FunctionTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import statsmodels.api as sm


def backward_elimination(X, y, sl=0.05):
    """Backward Elimination для отбора признаков."""
    X = sm.add_constant(X)
    num_vars = X.shape[1]
    selected_cols = list(range(num_vars))

    for i in range(num_vars):
        model = sm.OLS(y, X).fit()
        max_p_value = max(model.pvalues)
        if max_p_value > sl:
            remove_idx = np.argmax(model.pvalues)
            X = np.delete(X, remove_idx, axis=1)
            selected_cols.pop(remove_idx)
        else:
            break

    return selected_cols, model


def select_features(X, selected_cols):
    """Выбирает указанные столбцы из матрицы X (удаляя константу)."""
    cols_without_const = [col - 1 for col in selected_cols if col != 0]
    return X[:, cols_without_const]


# ---------- Загрузка и подготовка данных ----------
(X_train_full, y_train_full), (X_test_full, y_test_full) = cifar10.load_data()

n_train_samples = 1000
n_test_samples = 200
X_train = X_train_full[:n_train_samples]
X_test = X_test_full[:n_test_samples]

X_train_gray = X_train.mean(axis=3)
X_test_gray = X_test.mean(axis=3)
y_train = X_train_gray.mean(axis=(1, 2))
y_test = X_test_gray.mean(axis=(1, 2))
X_train_flat = X_train_gray.reshape(n_train_samples, -1)
X_test_flat = X_test_gray.reshape(n_test_samples, -1)

X_train_flat, X_temp, y_train, y_temp = train_test_split(
    X_train_flat, y_train, test_size=0.3, random_state=42
X_val_flat, X_test_flat, y_val, y_test = train_test_split(
    X_temp, y_temp, test_size=0.5, random_state=42
)

# ---------- Backward Elimination ----------
selected_cols, final_model = backward_elimination(X_train_flat, y_train)
print(final_model.summary())
# print(f"Отобранные признаки (индексы): {selected_cols}")


# ---------- Создание пайплайнов ----------

# Пайплайн для модели со всеми признаками (для сравнения)
pipeline_full = Pipeline([
    ('imputer', SimpleImputer(strategy='mean')),
    ('scaler', StandardScaler()),
    ('regressor', LinearRegression())
])

# Пайплайн для модели с отобранными признаками
pipeline_be = Pipeline([
    ('imputer', SimpleImputer(strategy='mean')),
    ('scaler', StandardScaler()),
    ('selector', FunctionTransformer(select_features, kw_args={'selected_cols': selected_cols})),
    ('regressor', LinearRegression())
])


# ---------- Обучение моделей ----------
pipeline_full.fit(X_train_flat, y_train)
pipeline_be.fit(X_train_flat, y_train)

# ---------- Предсказание и оценка ----------
y_pred_val_full = pipeline_full.predict(X_val_flat)
y_pred_val_be = pipeline_be.predict(X_val_flat)
y_pred_test_full = pipeline_full.predict(X_test_flat)
y_pred_test_be = pipeline_be.predict(X_test_flat)

mse_val_full = mean_squared_error(y_val, y_pred_val_full)
mse_val_be = mean_squared_error(y_val, y_pred_val_be)
mse_test_full = mean_squared_error(y_test, y_pred_test_full)
mse_test_be = mean_squared_error(y_test, y_pred_test_be)

print(f"MSE (Full, Validation): {mse_val_full:.4f}")
print(f"MSE (BE, Validation): {mse_val_be:.4f}")
print(f"MSE (Full, Test): {mse_test_full:.4f}")
print(f"MSE (BE, Test): {mse_test_be:.4f}")


# ---------- Графики ----------

plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)
plt.scatter(y_val, y_pred_val_full, color='blue', label='Full Model')
plt.plot([y_val.min(), y_val.max()], [y_val.min(), y_val.max()], 'k--', label='Ideal')
plt.title('Full Model (Validation)')
plt.xlabel('True')
plt.ylabel('Predicted')
plt.legend()

plt.subplot(1, 2, 2)
plt.scatter(y_val, y_pred_val_be, color='red', label='BE Model')
plt.plot([y_val.min(), y_val.max()], [y_val.min(), y_val.max()], 'k--', label='Ideal')
plt.title('BE Model (Validation)')
plt.xlabel('True')
plt.ylabel('Predicted')
plt.legend()
plt.tight_layout()
plt.show()

plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)
plt.scatter(y_test, y_pred_test_full, color='blue', label='Full Model')
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'k--', label='Ideal')
plt.title('Full Model (Test)')
plt.xlabel('True')
plt.ylabel('Predicted')
plt.legend()

plt.subplot(1, 2, 2)
plt.scatter(y_test, y_pred_test_be, color='red', label='BE Model')
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'k--', label='Ideal')
plt.title('BE Model (Test)')
plt.xlabel('True')
plt.ylabel('Predicted')
plt.legend()
plt.tight_layout()
plt.show()