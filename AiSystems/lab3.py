import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score
from sklearn.decomposition import PCA
from tensorflow.keras.datasets import cifar10

(x_train, y_train), (x_test, y_test) = cifar10.load_data()

# Размер выборки = 10000 изображений
x_train_flat = x_train[:10000].reshape(10000, -1)
y_train_flat = y_train[:10000].flatten()

x_train_flat = x_train_flat / 255.0

pca = PCA(n_components=50)
x_train_pca = pca.fit_transform(x_train_flat)

df = pd.DataFrame(x_train_pca)
df['label'] = y_train_flat

df.columns = [f'component_{i}' for i in range(x_train_pca.shape[1])] + ['label']

print("Первые 5 строк таблицы:")
print(df.head())

subset_df = df[['component_0', 'component_1', 'component_2', 'label']]
subset_df.columns = ['feature_1', 'feature_2', 'feature_3', 'answer']

subset_df = subset_df[subset_df['answer'] < 3]

sns.pairplot(subset_df, hue='answer', markers=["o", "s", "D"])
plt.show()

X_train, X_test, y_train, y_test = train_test_split(
    x_train_pca, y_train_flat, test_size=0.1, random_state=42
)

# 2.1 Построение классификатора с заданием K пользователем
def build_classifier(K, metric='euclidean'):
    knn = KNeighborsClassifier(n_neighbors=K, metric=metric)
    knn.fit(X_train, y_train)
    return knn

K = 3
classifier = build_classifier(K)
y_pred = classifier.predict(X_test)
print(f"Точность модели при K={K}: {accuracy_score(y_test, y_pred):.2f}")

# 2.2 Вычисление оценки hold-out для различных значений K
hold_out_scores = []
K_values = range(1, 21)
for K in K_values:
    classifier = build_classifier(K)
    y_pred = classifier.predict(X_test)
    hold_out_scores.append(accuracy_score(y_test, y_pred))

plt.plot(K_values, hold_out_scores, marker='o')
plt.title('Hold-out Accuracy vs K')
plt.xlabel('K (Number of Neighbors)')
plt.ylabel('Accuracy')
plt.grid()
plt.show()

# 2.3 Вычисление оценки cross-validation для различных значений K и fold
folds = range(3, 11)
cv_results = {}

for fold in folds:
    cv_scores = []
    for K in K_values:
        knn = KNeighborsClassifier(n_neighbors=K)
        scores = cross_val_score(knn, x_train_pca, y_train_flat, cv=fold, scoring='accuracy')
        cv_scores.append(scores.mean())
    cv_results[fold] = cv_scores

# Визуализация cross-validation Accuracy для различных значений K и fold
plt.figure(figsize=(10, 6))
for fold, scores in cv_results.items():
    plt.plot(K_values, scores, marker='o', label=f'Fold={fold}')
plt.title('Cross-Validation Accuracy vs K for Different Folds')
plt.xlabel('K (Number of Neighbors)')
plt.ylabel('Accuracy')
plt.legend()
plt.grid()
plt.show()

# Визуализация cross-validation оценки
plt.plot(K_values, cv_scores, marker='o', color='orange')
plt.title('Cross-Validation Accuracy vs K')
plt.xlabel('K (Number of Neighbors)')
plt.ylabel('Accuracy')
plt.grid()
plt.show()

# 2.4 Вычисление оптимального значения K
optimal_K_holdout = K_values[np.argmax(hold_out_scores)]
optimal_K_cv = K_values[np.argmax(cv_scores)]

print(f"Оптимальное значение K по hold-out: {optimal_K_holdout}")
print(f"Оптимальное значение K по cross-validation: {optimal_K_cv}")

optimal_classifier = build_classifier(optimal_K_cv)
y_pred_optimal = optimal_classifier.predict(X_test)
print(f"Точность оптимальной модели: {accuracy_score(y_test, y_pred_optimal):.2f}")

metrics = ['euclidean', 'manhattan', 'cosine']
for metric in metrics:
    classifier = build_classifier(K=optimal_K_cv, metric=metric)
    y_pred = classifier.predict(X_test)
    print(f"Точность модели с метрикой {metric}: {accuracy_score(y_test, y_pred):.2f}")

# 1 2 3 4 5
# взять признак, убрать из выборки и обучить модель
