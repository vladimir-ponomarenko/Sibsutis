#include <time.h>

#include <iostream>
#include <limits>
#include <queue>
#include <vector>
using namespace std;

const int INF = numeric_limits<int>::max();

void dijkstra(const vector<vector<int> >& graph, vector<int>& dist, int start) {
    int n = graph.size();
    dist.assign(n, INF);
    dist[start] = 0;

    priority_queue<pair<int, int>, vector<pair<int, int> >,
                   greater<pair<int, int> > >
        pq;  // Мин-heap
    pq.push({0, start});

    while (!pq.empty()) {
        int u = pq.top().second;
        int du = pq.top().first;
        pq.pop();

        if (du > dist[u]) continue;

        for (int v = 0; v < n; ++v) {
            int weight = graph[u][v];
            if (weight > 0 && dist[u] + weight < dist[v]) {
                dist[v] = dist[u] + weight;
                pq.push({dist[v], v});
            }
        }
    }
}

int main() {
    // Создание графа-решетки размерностью 100x100 вершин
    int n = 100;
    vector<vector<int> > graph2(
        n * n,
        vector<int>(n * n, 0));  // Инициализация нулевой матрицы смежности

    // Заполнение графа-решетки
    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n; ++j) {
            int u = i * n + j;  // Индекс текущей вершины
            if (i > 0) {        // Добавление ребра сверху
                int v = (i - 1) * n + j;
                graph2[u][v] = 1;
                graph2[v][u] = 1;
            }
            if (j > 0) {  // Добавление ребра слева
                int v = i * n + (j - 1);
                graph2[u][v] = 1;
                graph2[v][u] = 1;
            }
            if (i < n - 1) {  // Добавление ребра снизу
                int v = (i + 1) * n + j;
                graph2[u][v] = 1;
                graph2[v][u] = 1;
            }
            if (j < n - 1) {  // Добавление ребра справа
                int v = i * n + (j + 1);
                graph2[u][v] = 1;
                graph2[v][u] = 1;
            }
        }
    }

    // Вызов алгоритма Дейкстры для графа-решетки размерностью 100x100 вершин
    vector<int> dist2;
    clock_t start1 = clock();
    dijkstra(graph2, dist2, 0);
    clock_t end1 = clock();
    double seconds1 = (double)(end1 - start1) / CLOCKS_PER_SEC;
    // Вывод результатов
    cout << "Результаты для графа-решетки размерностью 100x100 вершин:" << endl;
    for (int i = 0; i < n * n; ++i) {
        cout << "Кратчайший путь от вершины 1 до вершины " << i + 1 << ": "
             << dist2[i] << endl;
    }
    printf("Время работы алгоритма для графа-решётки 100х100: %f seconds\n",
           seconds1);

    // Создание связного графа из 20 вершин
    vector<vector<int> > graph1(
        20, vector<int>(20, 0));  // Инициализация нулевой матрицы смежности

    // Заполнение графа случайными весами ребер (от 1 до 100)
    for (int i = 0; i < 20; ++i) {
        for (int j = i + 1; j < 20; ++j) {
            int weight = rand() % 100 + 1;
            graph1[i][j] = weight;
            graph1[j][i] = weight;
        }
    }

    // Вызов алгоритма Дейкстры для связного графа из 20 вершин
    vector<int> dist1;
    clock_t start2 = clock();
    dijkstra(graph1, dist1, 0);
    clock_t end2 = clock();
    double seconds2 = (double)(end2 - start2) / CLOCKS_PER_SEC;

    // Вывод результатов
    cout << "Результаты для связного графа из 20 вершин:" << endl;
    for (int i = 0; i < 20; ++i) {
        cout << "Кратчайший путь от вершины 1 до вершины " << i + 1 << ": "
             << dist1[i] << endl;
    }
    printf(
        "Время работы алгоритма для связного графа из 20 вершин: %f seconds\n",
        seconds2);

    return 0;
}