# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from collections import Counter
import math

N_SAMPLES_TO_USE = 2500
N_CLUSTERS_TO_CHECK = range(1, 16)
RANDOM_STATE = 42

(x_train, y_train), (x_test, y_test) = tf.keras.datasets.cifar10.load_data()

all_images = np.concatenate((x_train, x_test), axis=0)
all_labels = np.concatenate((y_train, y_test), axis=0).flatten()

np.random.seed(RANDOM_STATE)
indices = np.random.choice(len(all_images), N_SAMPLES_TO_USE, replace=False)
X_subset = all_images[indices]
y_subset = all_labels[indices]

print(f"Используется {N_SAMPLES_TO_USE} изображений из CIFAR-10.")
print(f"Размерность исходных данных (изображений): {X_subset.shape}")

# 1. Выравнивание изображений в векторы (N, 32, 32, 3) -> (N, 3072)
X_flat = X_subset.reshape(N_SAMPLES_TO_USE, -1)
print(f"Размерность выровненных данных: {X_flat.shape}")

# 2. Масштабирование данных
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_flat.astype(float))

print("Данные выровнены и масштабированы (StandardScaler).")
print("-" * 30)

# 3 Определение оптимального количества кластеров
print("3.2 Определение оптимального количества кластеров")

wcss = []
print(f"Проверка количества кластеров от {min(N_CLUSTERS_TO_CHECK)} до {max(N_CLUSTERS_TO_CHECK)}...")
for i in N_CLUSTERS_TO_CHECK:
    kmeans = KMeans(n_clusters=i,
                    init='k-means++',
                    n_init=10,
                    max_iter=300,
                    random_state=RANDOM_STATE)
    kmeans.fit(X_scaled)
    wcss.append(kmeans.inertia_)
    print(f"  K={i}, WCSS={kmeans.inertia_:.2f}")

plt.figure(figsize=(10, 6))
plt.plot(N_CLUSTERS_TO_CHECK, wcss, marker='o')
plt.title('CIFAR-10 (на основе пикселей)')
plt.xlabel('Количество кластеров (K)')
plt.ylabel('WCSS (Within-Cluster Sum of Squares)')
plt.grid(True)
plt.show()


OPTIMAL_K = 10
print(f"\nПредполагаемое оптимальное количество кластеров (выбрано): K = {OPTIMAL_K}")
print("-" * 30)

# Обучение модели кластеризации для оптимального количества кластеров
print(f"3.3 Обучение модели K-Means с K = {OPTIMAL_K}")

kmeans_final = KMeans(n_clusters=OPTIMAL_K,
                      init='k-means++',
                      n_init=10,
                      max_iter=300,
                      random_state=RANDOM_STATE)
y_kmeans = kmeans_final.fit_predict(X_scaled)

print(f"Модель K-Means обучена. Каждому из {N_SAMPLES_TO_USE} объектов присвоен кластер.")
print("-" * 30)

print("3.4 Визуализация результатов кластеризации")

print("Применение PCA для понижения размерности до 2 для визуализации...")
pca = PCA(n_components=2, random_state=RANDOM_STATE)
X_pca = pca.fit_transform(X_scaled)

centroids_pca = pca.transform(kmeans_final.cluster_centers_)

print("Построение графика кластеров в 2D (PCA)...")
plt.figure(figsize=(12, 8))
scatter_colors = plt.cm.get_cmap('viridis', OPTIMAL_K)

for i in range(OPTIMAL_K):
    plt.scatter(X_pca[y_kmeans == i, 0], X_pca[y_kmeans == i, 1],
                s=50,
                c=[scatter_colors(i / OPTIMAL_K)],
                label=f'Кластер {i+1}')

plt.scatter(centroids_pca[:, 0], centroids_pca[:, 1],
            s=200,
            c='red', marker='X', label='Центроиды')

plt.title(f'Кластеры CIFAR-10 (K={OPTIMAL_K}) в пространстве PCA')
plt.xlabel('Первая главная компонента (PCA1)')
plt.ylabel('Вторая главная компонента (PCA2)')
plt.legend()
plt.grid(True)
plt.show()

print("\n Примеры изображений по кластерам")

cifar10_classes = ['airplane', 'automobile', 'bird', 'cat', 'deer',
                   'dog', 'frog', 'horse', 'ship', 'truck']

def plot_images_grid(images, titles, grid_dims):
    """Отображает сетку изображений."""
    n_rows, n_cols = grid_dims
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(n_cols * 1.5, n_rows * 1.5))
    axes = axes.flatten()
    for img, title, ax in zip(images, titles, axes):
        ax.imshow(img)
        ax.set_title(title, fontsize=8)
        ax.axis('off')
    for i in range(len(images), len(axes)):
        axes[i].axis('off')
    plt.tight_layout()
    plt.show()

n_examples_per_cluster = 9
for i in range(OPTIMAL_K):
    cluster_indices = np.where(y_kmeans == i)[0]
    print(f"\nКластер {i+1} (количество изображений: {len(cluster_indices)}):")

    if len(cluster_indices) > 0:
        examples_indices = np.random.choice(cluster_indices,
                                             min(n_examples_per_cluster, len(cluster_indices)),
                                             replace=False)

        example_images = X_subset[examples_indices]
        example_true_labels = y_subset[examples_indices]
        example_titles = [f"True: {cifar10_classes[label]}" for label in example_true_labels]

        grid_cols = math.ceil(math.sqrt(len(example_images)))
        grid_rows = math.ceil(len(example_images) / grid_cols)

        plot_images_grid(example_images, example_titles, (grid_rows, grid_cols))
    else:
        print("  В этом кластере нет изображений.")

print("\n Распределение истинных меток CIFAR-10 по найденным кластерам")

cluster_label_counts = {}

for cluster_id in range(OPTIMAL_K):
    indices_in_cluster = np.where(y_kmeans == cluster_id)[0]
    true_labels_in_cluster = y_subset[indices_in_cluster]
    cluster_label_counts[cluster_id] = Counter(true_labels_in_cluster)

for cluster_id in range(OPTIMAL_K):
    print(f"\nКластер {cluster_id+1}:")
    if cluster_id in cluster_label_counts and cluster_label_counts[cluster_id]:
        sorted_labels = cluster_label_counts[cluster_id].most_common()
        total_in_cluster = sum(cluster_label_counts[cluster_id].values())
        print(f"  Всего объектов: {total_in_cluster}")
        for label_idx, count in sorted_labels:
            label_name = cifar10_classes[label_idx]
            percentage = (count / total_in_cluster) * 100
            print(f"  - {label_name}: {count} ({percentage:.1f}%)")
    else:
        print("  (пустой кластер)")
