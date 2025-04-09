import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.datasets import load_iris
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score

print("--- Загрузка и подготовка данных (Iris dataset) ---")
iris = load_iris()

feature_indices = [2, 3]
feature_names = [iris.feature_names[i] for i in feature_indices]

dataset = pd.DataFrame(iris.data[:, feature_indices], columns=feature_names)
print("Первые 5 строк выбранных признаков датасета Iris:")
print(dataset.head())

X_original = dataset.values
y_true_labels = iris.target

print(f"\nРазмерность выбранных данных: {X_original.shape}")
print(f"Используемые признаки: {feature_names}")

scaler = StandardScaler()
X = scaler.fit_transform(X_original)
print("Данные масштабированы с помощью StandardScaler.")


# Определение оптимального количества кластеров
print("\n--- Определение оптимального количества кластеров (Elbow Method) ---")
wcss = []
k_range = range(1, 11)

for i in k_range:
    kmeans_elbow = KMeans(n_clusters=i, init='k-means++', n_init=10, random_state=42, max_iter=300)
    kmeans_elbow.fit(X)
    wcss.append(kmeans_elbow.inertia_)

plt.figure(figsize=(10, 6))
plt.plot(k_range, wcss, marker='o', linestyle='--')
plt.title('Iris dataset')
plt.xlabel('Количество кластеров (k)')
plt.ylabel('WCSS (Within-Cluster Sum of Squares)')
plt.xticks(k_range)
plt.grid(True)
plt.show()

# Обучение модели кластеризации для оптимального количества кластеров
optimal_k = 3
print(f"\n--- Обучение модели K-Means для k={optimal_k} кластеров ---")

kmeans = KMeans(n_clusters=optimal_k, init='k-means++', n_init=10, random_state=42, max_iter=300)
y_kmeans = kmeans.fit_predict(X)

print(f"Метки кластеров получены для {len(y_kmeans)} объектов.")
print(f"Координаты центроидов кластеров (в масштабированном 2D пространстве):")
print(kmeans.cluster_centers_)


print("\n--- Визуализация результатов кластеризации ---")

plt.figure(figsize=(10, 7))
colors = ['red', 'blue', 'green']

for i in range(optimal_k):
    plt.scatter(X[y_kmeans == i, 0], X[y_kmeans == i, 1],
                s=100, c=colors[i], label=f'Кластер {i+1}', alpha=0.7)

plt.scatter(kmeans.cluster_centers_[:, 0], kmeans.cluster_centers_[:, 1],
            s=300, c='yellow', marker='X', label='Центроиды')

plt.title(f'Кластеры Ирисов (k={optimal_k})')
plt.xlabel(f'Масштабированная {feature_names[0]}')
plt.ylabel(f'Масштабированная {feature_names[1]}')
plt.legend()
plt.grid(True)
plt.show()

print("\n--- Оценка качества кластеризации (сравнение с истинными видами Ирисов) ---")
ari_score = adjusted_rand_score(y_true_labels, y_kmeans)
nmi_score = normalized_mutual_info_score(y_true_labels, y_kmeans)

print(f"Adjusted Rand Index (ARI): {ari_score:.4f}")
print(f"Normalized Mutual Information (NMI): {nmi_score:.4f}")


print("\n--- Визуализация с истинными метками для сравнения ---")
plt.figure(figsize=(10, 7))
target_names = iris.target_names
colors_true = ['purple', 'orange', 'brown']

for i, target_name in enumerate(target_names):
     plt.scatter(X[y_true_labels == i, 0], X[y_true_labels == i, 1],
                 s=100, c=colors_true[i], label=target_name, alpha=0.7)

plt.title('Истинные классы Ирисов')
plt.xlabel(f'Масштабированная {feature_names[0]}')
plt.ylabel(f'Масштабированная {feature_names[1]}')
plt.legend()
plt.grid(True)
plt.show()


print("\n--- Распределение истинных меток Iris по найденным кластерам ---")
analysis_df = pd.DataFrame({'True_Label': y_true_labels, 'Cluster': y_kmeans})
analysis_df['True_Label_Name'] = analysis_df['True_Label'].apply(lambda x: iris.target_names[x])

distribution = analysis_df.groupby(['Cluster', 'True_Label_Name']).size().unstack(fill_value=0)
print(distribution)

total_samples = len(y_true_labels)
correctly_clustered = 0
print("\nСостав кластеров:")
for i in range(optimal_k):
    cluster_data = analysis_df[analysis_df['Cluster'] == i]
    print(f"\nКластер {i+1} (Всего объектов: {len(cluster_data)}):")
    counts = cluster_data['True_Label_Name'].value_counts()
    print(counts)
    if not counts.empty:
      majority_class_count = counts.iloc[0]
      correctly_clustered += majority_class_count

purity = correctly_clustered / total_samples
print(f"\nПримерная чистота кластеризации (Purity): {purity:.4f}")
print("(Purity показывает долю объектов, которые принадлежат к самому частому классу в их кластере)")
