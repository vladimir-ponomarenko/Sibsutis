import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
import seaborn as sns
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

# --- 1. Загрузка и подготовка данных ---

(x_train, y_train), (x_test, y_test) = tf.keras.datasets.cifar10.load_data()
label_names = ['airplane', 'automobile', 'bird', 'cat', 'deer',
               'dog', 'frog', 'horse', 'ship', 'truck']

y_train = y_train.flatten()
y_test = y_test.flatten()

# --- 2. Первичный анализ и визуализация ---

# 2.1.  Гистограммы распределения по каналам
print("2.1 Гистограммы распределения значений пикселей по каналам")
plt.figure(figsize=(12, 4))
for channel in range(3):
    plt.subplot(1, 3, channel + 1)
    plt.hist(x_train[:, :, :, channel].ravel(), bins=256, color=['red', 'green', 'blue'][channel], alpha=0.7)
    plt.title(f"Канал {channel} (0=R, 1=G, 2=B)")
    plt.xlabel("Значение пикселя")
    plt.ylabel("Количество пикселей")
plt.tight_layout()
plt.show()


# 2.2. Boxplot для каждого канала
print("2.2 Boxplot для каждого канала")
plt.figure(figsize=(12, 4))
for channel in range(3):
    plt.subplot(1, 3, channel + 1)
    channel_data = x_train[:, :, :, channel].flatten()
    plt.boxplot(channel_data, vert=False, patch_artist=True,
                boxprops=dict(facecolor=['red', 'green', 'blue'][channel], color='black'),
                whiskerprops=dict(color='black'),
                capprops=dict(color='black'),
                medianprops=dict(color='black'))
    plt.title(f"Канал {channel} (R, G, B)")
    plt.xlabel("Значение пикселя")
    plt.yticks([1], [''])
plt.tight_layout()
plt.show()


# 2.3.  Распределение классов
print("2.3 Распределение классов (обучающий и тестовый наборы)")
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
unique_classes_train, class_counts_train = np.unique(y_train, return_counts=True)
plt.bar(unique_classes_train, class_counts_train, tick_label=label_names)
plt.title("Распределение классов (Обучающий набор)")
plt.xlabel("Класс")
plt.ylabel("Количество изображений")
plt.xticks(rotation=45, ha="right")

plt.subplot(1, 2, 2)
unique_classes_test, class_counts_test = np.unique(y_test, return_counts=True)
plt.bar(unique_classes_test, class_counts_test, tick_label=label_names)
plt.title("Распределение классов (Тестовый набор)")
plt.xlabel("Класс")
plt.ylabel("Количество изображений")
plt.xticks(rotation=45, ha="right")

plt.tight_layout()
plt.show()



# 2.4.  Violin plot (Скрипичные диаграммы) для каналов по классам
print("2.4 Violin plot для каналов по классам")

data_list = []
for i in range(x_train.shape[0]):
    for channel in range(3):
        data_list.append([y_train[i], channel, x_train[i, :, :, channel].mean()])
df = pd.DataFrame(data_list, columns=['Class', 'Channel', 'Mean_Channel_Value'])
df['Channel'] = df['Channel'].map({0: 'Red', 1: 'Green', 2: 'Blue'})
df['Class'] = df['Class'].map(lambda x: label_names[x])

plt.figure(figsize=(14, 7))
sns.violinplot(x='Class', y='Mean_Channel_Value', hue='Channel', data=df, palette="muted", split=True)
plt.title("Распределение средних значений каналов по классам")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.show()

# 2.5.  Heatmap (тепловая карта) корреляции между каналами

print("2.5 Heatmap корреляции между каналами (все изображения)")

flattened_images = x_train.reshape(x_train.shape[0], -1)

correlation_matrix = np.corrcoef(flattened_images, rowvar=False)

channel_correlation = correlation_matrix[:3, :3]

plt.figure(figsize=(6, 5))
sns.heatmap(channel_correlation, annot=True, cmap='coolwarm', vmin=-1, vmax=1,
            xticklabels=['Red', 'Green', 'Blue'], yticklabels=['Red', 'Green', 'Blue'])
plt.title('Матрица корреляции каналов (все изображения)')
plt.tight_layout()
plt.show()




# 2.6.  Pairplot (парные диаграммы) для уменьшенной размерности (PCA)
print("2.6 Pairplot для уменьшенной размерности (PCA)")

pca = PCA(n_components=3)
flattened_images = x_train.reshape(x_train.shape[0], -1)
principal_components = pca.fit_transform(flattened_images)

pca_df = pd.DataFrame(principal_components, columns=['PCA1', 'PCA2', 'PCA3'])
pca_df['Class'] = y_train
pca_df['Class'] = pca_df['Class'].map(lambda x: label_names[x])

sns.pairplot(pca_df, hue='Class', palette='tab10', diag_kind='kde')
plt.suptitle("Pairplot для главных компонент (PCA)", y=1.02)
plt.show()


# 2.7.  3D Scatter plot (3D-диаграмма рассеяния) для главных компонент
print("2.7 3D Scatter plot для главных компонент")

fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

for i in range(10):
  class_indices = np.where(y_train == i)[0]
  ax.scatter(principal_components[class_indices, 0], principal_components[class_indices, 1], principal_components[class_indices, 2],
              label=label_names[i], alpha=0.6)

ax.set_xlabel('PCA Component 1')
ax.set_ylabel('PCA Component 2')
ax.set_zlabel('PCA Component 3')
ax.set_title('3D Scatter Plot of PCA Components')
ax.legend()
plt.tight_layout()
plt.show()

# 2.8.  t-SNE
print("2.8 t-SNE визуализация")

plt.figure(figsize=(10, 8))

all_indices = np.arange(x_train.shape[0])
sampled_indices = np.random.choice(all_indices, 5000, replace=False)
sampled_images = x_train[sampled_indices]
sampled_labels = y_train[sampled_indices]
flattened_images = sampled_images.reshape(sampled_images.shape[0], -1)


tsne = TSNE(n_components=2, random_state=42, perplexity=30, n_iter=500, verbose=1)
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

# 2.9.  Примеры изображений
print("2.9 Примеры изображений")
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

# 2.10.  Тепловая карта средних изображений по классам
print("2.10 Тепловая карта средних изображений по классам")

plt.figure(figsize=(15, 8))
for i in range(10):
    class_indices = np.where(y_train == i)[0]
    class_images = x_train[class_indices]
    mean_image = np.mean(class_images, axis=0)

    plt.subplot(2, 5, i + 1)
    plt.imshow(mean_image.astype(np.uint8))
    plt.title(f"Среднее {label_names[i]}")
    plt.axis('off')

plt.tight_layout()
plt.show()

# # 2.11.  Boxplot для средних значений пикселей по классам (усреднение по всем пикселям изображения)
# print("2.11 Boxplot средних значений пикселей по классам (усреднение по изображению)")

# plt.figure(figsize=(14, 7))

# data_list = []
# for i in range(x_train.shape[0]):
#     mean_pixel_value = x_train[i].mean()
#     data_list.append({'Class': label_names[y_train[i]], 'Mean_Pixel_Value': mean_pixel_value})

# df_pixels = pd.DataFrame(data_list)
# sns.boxplot(x='Class', y='Mean_Pixel_Value', data=df_pixels, palette='viridis')
# plt.title("Распределение средних значений пикселей по классам")
# plt.xticks(rotation=45, ha="right")
# plt.tight_layout()
# plt.show()
