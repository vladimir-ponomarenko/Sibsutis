/*Ponomarenko IA-231*/

#include <iostream>
#include <cmath>
#include <limits>

using namespace std;

double f(double x) {
    return exp(-x * x);
}

double integrateRightRectangle(double a, double b, double epsylon, int N) {
    double h;
    if (N == 0) {
        h = (b - a) / 2.0;
    } else {
        h = (b - a) / static_cast<double>(N);
    }

    double I_prev = 0.0;
    double I = h * f(a + h); 

    int iterations = 0;
    do {
        I_prev = I;
        h /= 2;
        double sum = 0.0;
        for (double x = a + h; x <= b; x += h) {
            sum += f(x);
        }
        I = h * sum;
        iterations++;
    } while (fabs(I - I_prev) > epsylon);
    
    cout << "Количество итераций: " << iterations << endl;
    return I;
}

int main() {
    double a, b, I;
    double epsylon;
    int N;

    cout << "Введите границы интервала [a, b]: ";
    cin >> a >> b;

    cout << "Введите погрешность вычисления интеграла epsylon (или введите 0 для использования N): ";
    cin >> epsylon;

    if (epsylon == 0.0) { 
        cout << "Введите количество разбиений N: ";
        cin >> N;
        cin.ignore(numeric_limits<streamsize>::max(), '\n');
    } else {
        N = 0; 
    }

    I = integrateRightRectangle(a, b, epsylon, N);

    cout << "Численное значение интеграла: " << I << endl;

    return 0;
}
