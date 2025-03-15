import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import seaborn as sns
from tensorflow.keras.datasets import cifar10
import warnings
warnings.filterwarnings('ignore')

# 1. Загрузка набора данных CIFAR-10
print("Загрузка набора данных CIFAR-10...")
(X_train_images, y_train), (X_test_images, y_test) = cifar10.load_data()

def extract_features(images):
    n_samples = len(images)
    features = np.zeros((n_samples, 6))
    for i, img in enumerate(images):
        features[i, 0] = np.mean(img[:, :, 0])  # Среднее по каналу R
        features[i, 1] = np.mean(img[:, :, 1])  # Среднее по каналу G
        features[i, 2] = np.mean(img[:, :, 2])  # Среднее по каналу B
        features[i, 3] = np.std(img[:, :, 0])   # Стандартное отклонение по каналу R
        features[i, 4] = np.std(img[:, :, 1])   # Стандартное отклонение по каналу G
        features[i, 5] = np.std(img[:, :, 2])   # Стандартное отклонение по каналу B
    return features

X_train_features = extract_features(X_train_images)
X_test_features = extract_features(X_test_images)

feature_names = ['mean_red', 'mean_green', 'mean_blue', 'std_red', 'std_green', 'std_blue']
df_train = pd.DataFrame(X_train_features, columns=feature_names)
df_test = pd.DataFrame(X_test_features, columns=feature_names)

df_train['label'] = y_train
df_test['label'] = y_test

df_all = pd.concat([df_train, df_test], axis=0, ignore_index=True)

def get_dominant_color(row):
    values = [row['mean_red'], row['mean_green'], row['mean_blue']]
    max_idx = values.index(max(values))
    return ['red', 'green', 'blue'][max_idx]

df_all['dominant_color'] = df_all.apply(get_dominant_color, axis=1)

df_all['brightness'] = (df_all['mean_red'] + df_all['mean_green'] + df_all['mean_blue']) / 3

np.random.seed(42)
mask = np.random.rand(len(df_all)) < 0.1
df_all.loc[mask, 'std_red'] = np.nan

print("Размер датасета:", df_all.shape)
print("\nПервые 5 строк датасета:")
print(df_all.head())

# 2. Визуализация данных
print("\n2. Визуализация данных")

# Визуализация распределения признаков
plt.figure(figsize=(15, 10))
for i, feature in enumerate(feature_names):
    plt.subplot(2, 3, i+1)
    sns.histplot(df_all[feature].dropna(), kde=True)
    plt.title(f'Распределение {feature}')
plt.tight_layout()
plt.savefig('feature_distributions.png')
plt.close()

# Визуализация корреляции между признаками
plt.figure(figsize=(10, 8))
numeric_cols = [col for col in df_all.columns if df_all[col].dtype != 'object' and col != 'label']
correlation = df_all[numeric_cols].corr()
sns.heatmap(correlation, annot=True, cmap='coolwarm', linewidths=0.5)
plt.title('Корреляционная матрица числовых признаков')
plt.savefig('correlation_matrix.png')
plt.close()

print("\nКоличество пропущенных значений в каждом столбце:")
print(df_all.isnull().sum())

# 3. Подготовка данных для обучения модели
X = df_all.drop(['brightness', 'label'], axis=1)
y = df_all['brightness']

# 4. Определение числовых и категориальных признаков
numeric_features = ['mean_red', 'mean_green', 'mean_blue', 'std_red', 'std_green', 'std_blue']
categorical_features = ['dominant_color']

# 5. Создание преобразователей для числовых и категориальных признаков
numeric_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='mean')),
    ('scaler', StandardScaler())
])

categorical_transformer = Pipeline(steps=[
    ('onehot', OneHotEncoder(drop='first', sparse_output=False))
])

preprocessor = ColumnTransformer(
    transformers=[
        ('num', numeric_transformer, numeric_features),
        ('cat', categorical_transformer, categorical_features)
    ])

# Создание полного пайплайна с моделью линейной регрессии
pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('model', LinearRegression())
])

# 6. Разделение на обучающую и тестовую выборки
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("Размер обучающей выборки:", X_train.shape)
print("Размер тестовой выборки:", X_test.shape)

# 7. Обучение модели с использованием пайплайна
print("\n7. Обучение модели с использованием пайплайна")
pipeline.fit(X_train, y_train)

# 8. Оценка результатов
print("\n8. Оценка результатов")
y_pred = pipeline.predict(X_test)

mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"Среднеквадратичная ошибка (MSE): {mse:.4f}")
print(f"Коэффициент детерминации (R²): {r2:.4f}")

# 9. Визуализация результатов предсказания
plt.figure(figsize=(10, 6))
plt.scatter(y_test, y_pred, alpha=0.5)
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--')
plt.xlabel('Реальные значения')
plt.ylabel('Предсказанные значения')
plt.title('Сравнение реальных и предсказанных значений яркости')
plt.savefig('prediction_results.png')
plt.close()

# 10. Получение преобразованных данных в виде DataFrame
transformed_data = preprocessor.fit_transform(X_train)

transformed_feature_names = []

transformed_feature_names.extend(numeric_features)

ohe = preprocessor.named_transformers_['cat'].named_steps['onehot']
cat_features = ohe.get_feature_names_out(categorical_features)
transformed_feature_names.extend(cat_features)

transformed_df = pd.DataFrame(
    transformed_data,
    columns=numeric_features + [f for f in cat_features]
)

print("\nПреобразованные данные (первые 5 строк):")
print(transformed_df.head())

# 11. Сохранение результатов
transformed_df.to_csv('transformed_data.csv', index=False)
print("\nПреобразованные данные сохранены в файл transformed_data.csv")

print("\nВыполнение пайплайна завершено!")

plt.figure(figsize=(10, 6))
coef = pipeline.named_steps['model'].coef_
feature_names = numeric_features.copy()
feature_names.extend([f.split('_')[-1] for f in cat_features])
indices = np.argsort(np.abs(coef))
plt.barh(range(len(coef)), coef[indices])
plt.yticks(range(len(coef)), [feature_names[i] for i in indices])
plt.xlabel('Коэффициент')
plt.title('Важность признаков')
plt.savefig('feature_importance.png')
plt.close()
