import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score

X_train_reduced = np.delete(X_train, 0, axis=1)
X_test_reduced = np.delete(X_test, 0, axis=1)

reduced_classifier = KNeighborsClassifier(n_neighbors=optimal_K_cv)
reduced_classifier.fit(X_train_reduced, y_train)

y_pred_reduced = reduced_classifier.predict(X_test_reduced)
accuracy_reduced = accuracy_score(y_test, y_pred_reduced)

print(f"Точность модели без первого признака: {accuracy_reduced:.2f}")
