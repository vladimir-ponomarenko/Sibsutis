#include <cmath>
#include <iostream>

using namespace std;

double f(double x) { return 1 - x * log(x) + 0.3 * sqrt(x); }

double df(double x, double h) { return (f(x + h) - f(x)) / h; }

double newtonMethod(double a, double b, double epsilon) {
    double x0 = (a + b) / 2;
    double h = 0.0001;

    while (fabs(f(x0)) > epsilon) {
        x0 = x0 - f(x0) / df(x0, h);
    }

    return x0;
}

void localizeRoots(double a, double b, double epsilon) {
    double step = 0.1;  // Шаг разбиения интервала

    for (double x = a; x < b; x += step) {
        if (f(x) * f(x + step) <= 0) {
            double root = newtonMethod(x, x + step, epsilon);
            cout << "Найденный корень на интервале [" << x << ", " << x + step
                 << "]: " << root << endl;
        }
    }
}

int main() {
    double a, b, epsilon;

    cout << "Введите границы интервала [a, b]: ";
    cin >> a >> b;

    if (f(a) * f(b) > 0) {
        cout << "Ошибка: На данном интервале нет одного корня уравнения."
             << endl;
        return 1;
    }

    cout << "Введите точность решения (epsilon): ";
    cin >> epsilon;

    cout << "Локализация корней:" << endl;
    localizeRoots(a, b, epsilon);

    return 0;
}
