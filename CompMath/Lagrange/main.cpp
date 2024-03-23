#include <cmath>
#include <fstream>
#include <iostream>
#include <vector>

using namespace std;

double lagrange_interpolation(const vector<double>& x, const vector<double>& y,
                              double x_value) {
    double result = 0.0;
    int n = x.size();

    for (int i = 0; i < n; i++) {
        double term = y[i];
        for (int j = 0; j < n; j++) {
            if (j != i) {
                term *= (x_value - x[j]) / (x[i] - x[j]);
            }
        }
        result += term;
    }

    return result;
}

int main() {
    string filename = "in.txt";
    ifstream file(filename);
    if (!file) {
        cerr << "Ошибка открытия файла " << filename << endl;
        return 1;
    }

    vector<double> x, y;
    double value;
    while (file >> value) {
        x.push_back(value);
        if (!(file >> value)) {
            cerr << "Ошибка чтения данных из файла " << filename << endl;
            return 1;
        }
        y.push_back(value);
    }

    file.close();

    if (x.size() != y.size()) {
        cerr << "Количество элементов в векторах x и y не совпадает" << endl;
        return 1;
    }

    double x_value;
    cout << "Введите значение x: ";
    cin >> x_value;

    double result = lagrange_interpolation(x, y, x_value);

    cout << "Значение полинома Лагранжа L(" << x_value << ") = " << result
         << endl;

    return 0;
}