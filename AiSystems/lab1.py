import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf

# 1. Загрузка датасета CIFAR-10
(x_train, y_train), (x_test, y_test) = tf.keras.datasets.cifar10.load_data()

label_names = ['airplane', 'automobile', 'bird', 'cat', 'deer',
               'dog', 'frog', 'horse', 'ship', 'truck']

# 2.1 Общая информация
print("2.1 Общая информация:")
print(f"  Количество обучающих образцов: {x_train.shape[0]}")
print(f"  Количество тестовых образцов: {x_test.shape[0]}")
print(f"  Размер изображения: {x_train.shape[1]}x{x_train.shape[2]}")
print(f"  Количество каналов: {x_train.shape[3]}")
print(f"  Количество классов: {len(np.unique(y_train))}")
print(f"  Тип данных изображений: {x_train.dtype}")
print(f"  Тип данных меток: {y_train.dtype}")
print(f"  Описание набора данных: CIFAR-10 состоит из 60000 32x32 цветных изображений в 10 классах, по 6000 изображений на класс.  ")
print(f"  Назначение: Классификация изображений.")
print(f"  Возможные модели: Сверточные нейронные сети (CNN), классификаторы на основе деревьев решений, SVM и др.")
print("-" * 30)

# 2.2 Форма набора данных
print("\n2.2 Форма набора данных:")
print(f"  Количество элементов в обучающем наборе: {x_train.size}")
print(f"  Количество элементов в тестовом наборе: {x_test.size}")
num_features = x_train.shape[1] * x_train.shape[2] * x_train.shape[3]
print(f"  Количество признаков (пикселей): {num_features}")
print("  Пропущенные значения: Нет")
print(f"    В обучающем наборе: {np.isnan(x_train).any()}")
print(f"    В тестовом наборе: {np.isnan(x_test).any()}")

for channel in range(3):
    channel_data = x_train[:, :, :, channel]
    print(f"\n  Статистика для канала {channel} (0=Red, 1=Green, 2=Blue):")
    print(f"    Среднее значение признака: {np.mean(channel_data):.2f}")
    print(f"    Стандартное отклонение признака: {np.std(channel_data):.2f}")
    print(f"    Минимальное значение признака: {np.min(channel_data)}")
    print(f"    Максимальное значение признака: {np.max(channel_data)}")

    print(f"    25-й перцентиль: {np.percentile(channel_data, 25):.2f}")
    print(f"    50-й перцентиль (медиана): {np.percentile(channel_data, 50):.2f}")
    print(f"    75-й перцентиль: {np.percentile(channel_data, 75):.2f}")

print("-" * 30)

# 2.3 Графические представления

print("\n2.3 Графические представления:")

# 2.3.1 Гистограммы распределения значений пикселей по каналам
plt.figure(figsize=(12, 4))
for channel in range(3):
    plt.subplot(1, 3, channel + 1)
    plt.hist(x_train[:, :, :, channel].ravel(), bins=256, color=['red', 'green', 'blue'][channel], alpha=0.7)
    plt.title(f"Канал {channel} (0=R, 1=G, 2=B)")
    plt.xlabel("Значение пикселя (признака)")
    plt.ylabel("Количество пикселей")
plt.tight_layout()
plt.show()

# 2.3.2 Распределение классов
plt.figure(figsize=(8, 5))
unique_classes, class_counts = np.unique(y_train, return_counts=True)
plt.bar(unique_classes, class_counts, tick_label=label_names)
plt.title("Распределение классов в обучающем наборе")
plt.xlabel("Класс")
plt.ylabel("Количество изображений")
# plt.xticks(unique_classes)
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.show()

plt.figure(figsize=(8, 5))
unique_classes_test, class_counts_test = np.unique(y_test, return_counts=True)
plt.bar(unique_classes_test, class_counts_test, tick_label=label_names)
plt.title("Распределение классов в тестовом наборе")
plt.xlabel("Класс")
plt.ylabel("Количество изображений")
# plt.xticks(unique_classes_test)
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.show()

# 2.3.3 Примеры изображений
plt.figure(figsize=(12, 12))
for i in range(10):
    indices = np.where(y_train == i)[0]
    random_indices = np.random.choice(indices, 10, replace=False)
    for j, idx in enumerate(random_indices):
        plt.subplot(10, 10, i * 10 + j + 1)
        plt.imshow(x_train[idx])
        plt.axis('off')
        if j == 0:
            plt.title(label_names[i])
plt.tight_layout()
plt.show()

# 2.3.4 "Тепловая карта" средних значений пикселей
plt.figure(figsize=(12, 4))
for channel in range(3):
    mean_image = np.mean(x_train[:, :, :, channel], axis=0)
    plt.subplot(1, 3, channel + 1)
    plt.imshow(mean_image, cmap='viridis')
    plt.title(f"Среднее изображение (Канал {channel})")
    plt.colorbar()
    plt.axis('off')
plt.tight_layout()
plt.show()

# 2.3.5 Доля RGB для каждого класса
plt.figure(figsize=(15, 10))

for i in range(10):
    class_indices = np.where(y_train == i)[0]
    class_images = x_train[class_indices]

    total_red = np.sum(class_images[:, :, :, 0])
    total_green = np.sum(class_images[:, :, :, 1])
    total_blue = np.sum(class_images[:, :, :, 2])

    total_pixels = total_red + total_green + total_blue

    red_fraction = total_red / total_pixels
    green_fraction = total_green / total_pixels
    blue_fraction = total_blue / total_pixels

    plt.subplot(2, 5, i + 1)
    plt.bar(['Red', 'Green', 'Blue'], [red_fraction, green_fraction, blue_fraction],
            color=['red', 'green', 'blue'])
    plt.title(f"Доля RGB для класса {label_names[i]}")
    plt.ylim(0, 1)
    plt.ylabel("Доля")

plt.tight_layout()
plt.show()


# 2.3.6  Корреляция между каналами
for i in range(10):
    class_indices = np.where(y_train == i)[0]
    class_images = x_train[class_indices]

    flattened_images = class_images.reshape(class_images.shape[0], -1)
    correlation_matrix = np.corrcoef(flattened_images, rowvar=False)
    channel_correlation = correlation_matrix[:3, :3]

    plt.figure(figsize=(6, 5))
    plt.imshow(channel_correlation, cmap='coolwarm', interpolation='nearest')
    plt.colorbar()
    plt.xticks(range(3), ['Red', 'Green', 'Blue'])
    plt.yticks(range(3), ['Red', 'Green', 'Blue'])
    plt.title(f'Матрица корреляции каналов для класса {label_names[i]}')
    plt.tight_layout()
    plt.show()



# 2.3.7  PCA (Анализ главных компонент) - Показывает, какие комбинации пикселей (признаков) вносят наибольший вклад в дисперсию данных
from sklearn.decomposition import PCA

plt.figure(figsize=(10, 6))

for i in range(10):
  class_indices = np.where(y_train == i)[0]
  class_images = x_train[class_indices]
  flattened_images = class_images.reshape(class_images.shape[0], -1)

  pca = PCA(n_components=2)
  principal_components = pca.fit_transform(flattened_images)

  plt.subplot(2, 5, i + 1)
  plt.scatter(principal_components[:, 0], principal_components[:, 1], alpha=0.5)
  plt.title(f'PCA для класса {label_names[i]}')
  plt.xlabel('Главная компонента 1')
  plt.ylabel('Главная компонента 2')

plt.tight_layout()
plt.show()


# 2.3.8.  t-SNE (t-distributed Stochastic Neighbor Embedding) - еще один метод понижения размерности, хорошо разделяет кластеры
from sklearn.manifold import TSNE

plt.figure(figsize=(10, 8))

all_indices = np.arange(x_train.shape[0])
sampled_indices = np.random.choice(all_indices, 5000, replace=False)
sampled_images = x_train[sampled_indices]
sampled_labels = y_train[sampled_indices]

flattened_images = sampled_images.reshape(sampled_images.shape[0], -1)


tsne = TSNE(n_components=2, random_state=42, perplexity=30, n_iter=300)
tsne_results = tsne.fit_transform(flattened_images)


for i in range(10):
    class_indices = np.where(sampled_labels == i)[0]
    plt.scatter(tsne_results[class_indices, 0], tsne_results[class_indices, 1], label=label_names[i], alpha=0.7)

plt.title('t-SNE визуализация CIFAR-10')
plt.xlabel('t-SNE компонента 1')
plt.ylabel('t-SNE компонента 2')
plt.legend()
plt.tight_layout()
plt.show()
