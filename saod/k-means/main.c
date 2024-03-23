#include <math.h>
#include <stdio.h>
#include <stdlib.h>

struct Point {
    double x;
    double y;
};

struct Cluster {
    struct Point center;
    struct Point* points;
    int num_points;
};

double distance(struct Point a, struct Point b) {
    return sqrt(pow(a.x - b.x, 2) + pow(a.y - b.y, 2));
}

void initialize_points(struct Point* points, int num_points) {
    for (int i = 0; i < num_points; i++) {
        printf("Enter coordinates for point %d (format: x y): ", i + 1);
        scanf("%lf %lf", &points[i].x, &points[i].y);
    }
}

void initialize_clusters(struct Point* points, struct Cluster* clusters,
                         int k) {
    for (int i = 0; i < k; i++) {
        printf("Enter coordinates for center of cluster %d (format: x y): ",
               i + 1);
        scanf("%lf %lf", &clusters[i].center.x, &clusters[i].center.y);

        clusters[i].points = NULL;
        clusters[i].num_points = 0;
    }
}

int find_nearest_cluster(struct Point point, struct Cluster* clusters, int k) {
    int nearest_cluster = 0;
    double min_distance = distance(point, clusters[0].center);

    for (int i = 1; i < k; i++) {
        double d = distance(point, clusters[i].center);
        if (d < min_distance) {
            min_distance = d;
            nearest_cluster = i;
        }
    }

    return nearest_cluster;
}

void k_means(struct Point* points, struct Cluster* clusters, int num_points,
             int k) {
    for (int i = 0; i < num_points; i++) {
        int nearest_cluster = find_nearest_cluster(points[i], clusters, k);

        clusters[nearest_cluster].num_points++;
        clusters[nearest_cluster].points = (struct Point*)realloc(
            clusters[nearest_cluster].points,
            clusters[nearest_cluster].num_points * sizeof(struct Point));
        clusters[nearest_cluster]
            .points[clusters[nearest_cluster].num_points - 1] = points[i];
    }

    for (int i = 0; i < k; i++) {
        double sum_x = 0.0, sum_y = 0.0;

        for (int j = 0; j < clusters[i].num_points; j++) {
            sum_x += clusters[i].points[j].x;
            sum_y += clusters[i].points[j].y;
        }

        clusters[i].center.x = sum_x / clusters[i].num_points;
        clusters[i].center.y = sum_y / clusters[i].num_points;
    }
}

void print_clusters(struct Cluster* clusters, int k) {
    for (int i = 0; i < k; i++) {
        printf("Cluster %d center: (%lf, %lf)\n", i + 1, clusters[i].center.x,
               clusters[i].center.y);
        printf("Points in Cluster %d:\n", i + 1);
        for (int j = 0; j < clusters[i].num_points; j++) {
            printf("(%lf, %lf)\n", clusters[i].points[j].x,
                   clusters[i].points[j].y);
        }
        printf("\n");
    }
}

int main() {
    int k, num_points;

    printf("Enter the number of clusters: ");
    scanf("%d", &k);

    if (k <= 0) {
        printf("Invalid number of clusters. Exiting.\n");
        return 1;
    }

    printf("Enter the number of points: ");
    scanf("%d", &num_points);

    if (num_points < k) {
        printf(
            "Number of points should be greater than or equal to the number of "
            "clusters. Exiting.\n");
        return 1;
    }

    struct Point* points =
        (struct Point*)malloc(num_points * sizeof(struct Point));
    if (points == NULL) {
        printf("Memory allocation failed. Exiting.\n");
        return 1;
    }
    initialize_points(points, num_points);

    struct Cluster* clusters =
        (struct Cluster*)malloc(k * sizeof(struct Cluster));
    if (clusters == NULL) {
        printf("Memory allocation failed. Exiting.\n");
        free(points);
        return 1;
    }
    initialize_clusters(points, clusters, k);

    k_means(points, clusters, num_points, k);

    print_clusters(clusters, k);

    // Free allocated memory
    for (int i = 0; i < k; i++) {
        free(clusters[i].points);
    }
    free(clusters);
    free(points);

    return 0;
}
