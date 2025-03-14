import numpy as np
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeClassifier, export_graphviz
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import mean_squared_error
import tensorflow as tf
from tensorflow.keras.datasets import cifar10
import graphviz
import seaborn as sns
import pandas as pd

# 1. Загрузка и предварительная обработка данных CIFAR-10
(X_train, y_train), (X_test, y_test) = cifar10.load_data()

X_train = X_train.reshape(X_train.shape[0], -1)
X_test = X_test.reshape(X_test.shape[0], -1)
y_train = y_train.ravel()
y_test = y_test.ravel()

X_train, _, y_train, _ = train_test_split(X_train, y_train, train_size=5000, random_state=42)
X_test, _, y_test, _ = train_test_split(X_test, y_test, train_size=1000, random_state=42)

X_train = X_train / 255.0
X_test = X_test / 255.0

print("Данные загружены и обработаны:")
print(f"X_train shape: {X_train.shape}")
print(f"X_test shape: {X_test.shape}")

# 2.1 Построение классификатора с заданными параметрами и визуализация дерева
clf = DecisionTreeClassifier(max_depth=5, max_features=100, random_state=42)
clf.fit(X_train, y_train)

dot_data = export_graphviz(clf, out_file=None, feature_names=[f'pixel_{i}' for i in range(X_train.shape[1])],
                           class_names=[str(i) for i in range(10)], filled=True, rounded=True)
graph = graphviz.Source(dot_data)
graph.render("decision_tree_initial", format="png", cleanup=True)
print("2.1 Дерево сохранено как 'decision_tree_initial.png'")

# 2.2 Cross-validation для max_depth
max_depth_values = range(1, 15)
mse_scores_depth = []

for depth in max_depth_values:
    clf = DecisionTreeClassifier(max_depth=depth, max_features=100, random_state=42)
    scores = cross_val_score(clf, X_train, y_train, cv=5, scoring='neg_mean_squared_error')
    mse_scores_depth.append(-scores.mean())

plt.figure(figsize=(10, 6))
plt.plot(max_depth_values, mse_scores_depth, marker='o')
plt.title('Зависимость MSE от max_depth')
plt.xlabel('max_depth')
plt.ylabel('MSE')
plt.grid()
plt.savefig('mse_vs_max_depth.png')
plt.show()

# 2.3 Cross-validation для max_features
max_features_values = [50, 100, 200, 500]
mse_scores_features = []

for features in max_features_values:
    clf = DecisionTreeClassifier(max_depth=5, max_features=features, random_state=42)
    scores = cross_val_score(clf, X_train, y_train, cv=5, scoring='neg_mean_squared_error')
    mse_scores_features.append(-scores.mean())

plt.figure(figsize=(10, 6))
plt.plot(max_features_values, mse_scores_features, marker='o')
plt.title('Зависимость MSE от max_features')
plt.xlabel('max_features')
plt.ylabel('MSE')
plt.grid()
plt.savefig('mse_vs_max_features.png')
plt.show()

# 2.4 Поиск оптимальных параметров с помощью GridSearchCV
param_grid = {'max_depth': [3, 5, 7, 10], 'max_features': [50, 100, 200]}
grid_search = GridSearchCV(DecisionTreeClassifier(random_state=42), param_grid, cv=5, scoring='neg_mean_squared_error')
grid_search.fit(X_train, y_train)

print("2.4 Лучшие параметры:", grid_search.best_params_)
best_clf = grid_search.best_estimator_
y_pred = best_clf.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
print(f"MSE на тестовой выборке: {mse}")

# 2.5 Визуализация оптимального дерева
dot_data = export_graphviz(best_clf, out_file=None, feature_names=[f'pixel_{i}' for i in range(X_train.shape[1])],
                           class_names=[str(i) for i in range(10)], filled=True, rounded=True)
graph = graphviz.Source(dot_data)
graph.render("decision_tree_optimal", format="png", cleanup=True)
print("2.5 Оптимальное дерево сохранено как 'decision_tree_optimal.png'")

# 2.6 Решающие границы в стиле pairplot
selected_features = [100, 200, 300, 400]
X_train_selected = X_train[:, selected_features]
feature_names = [f'pixel_{i}' for i in selected_features]

clf_selected = DecisionTreeClassifier(max_depth=grid_search.best_params_['max_depth'],
                                      max_features=grid_search.best_params_['max_features'],
                                      random_state=42)
clf_selected.fit(X_train, y_train)

df = pd.DataFrame(X_train_selected, columns=feature_names)
df['class'] = y_train

def plot_decision_boundaries(ax, x_idx, y_idx, x_name, y_name):
    x_min, x_max = X_train_selected[:, x_idx].min() - 0.1, X_train_selected[:, x_idx].max() + 0.1
    y_min, y_max = X_train_selected[:, y_idx].min() - 0.1, X_train_selected[:, y_idx].max() + 0.1
    xx, yy = np.meshgrid(np.arange(x_min, x_max, 0.01), np.arange(y_min, y_max, 0.01))

    clf_2d = DecisionTreeClassifier(max_depth=grid_search.best_params_['max_depth'],
                                    max_features=2, random_state=42)
    clf_2d.fit(X_train_selected[:, [x_idx, y_idx]], y_train)
    Z = clf_2d.predict(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)

    ax.contourf(xx, yy, Z, alpha=0.3, cmap='viridis')
    ax.scatter(X_train_selected[:, x_idx], X_train_selected[:, y_idx], c=y_train, s=10, cmap='viridis', edgecolor='k')
    ax.set_xlabel(x_name)
    ax.set_ylabel(y_name)

fig, axes = plt.subplots(4, 4, figsize=(15, 15))
for i in range(4):
    for j in range(4):
        if i == j:
            axes[i, j].hist(X_train_selected[:, i][y_train == 0], bins=20, alpha=0.5, label='Class 0')
            axes[i, j].hist(X_train_selected[:, i][y_train == 1], bins=20, alpha=0.5, label='Class 1')
            axes[i, j].set_title(feature_names[i])
        else:
            plot_decision_boundaries(axes[i, j], j, i, feature_names[j], feature_names[i])

plt.suptitle('Pairplot с решающими границами', fontsize=16)
plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig('decision_boundaries_pairplot.png')
plt.show()

