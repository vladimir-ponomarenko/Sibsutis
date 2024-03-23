#include <cmath>
#include <iostream>
#include <sstream>
using namespace std;

int main() {
    int n, m;

    while (true) {
        cout << "Enter number of variables: ";
        string input;
        cin >> input;
        std::stringstream strValue(input);
        if (strValue >> n) {
            break;
        } else {
            cout << "Invalid input! Please enter an integer." << endl;
        }
    }

    while (true) {
        cout << "Enter number of equations: ";
        string input;
        cin >> input;
        std::stringstream strValue(input);
        if (strValue >> m) {
            break;
        } else {
            cout << "Invalid input! Please enter an integer." << endl;
        }
    }

    double A[m][n + 1];

    cout << "Enter SLE coefficients:" << endl;

    for (int i = 0; i < m; i++) {
        cout << "Equation " << i + 1 << ":" << endl;

        for (int j = 0; j < n + 1; j++) {
            string input;
            cin >> input;
            std::stringstream strValue(input);
            double enteredValue;

            if (strValue >> enteredValue) {
                A[i][j] = enteredValue;

            } else {
                cout << "Invalid input! Please retry: " << endl;
                j--;
                continue;
            }

            cout << "Current matrix:" << endl;

            for (int k = 0; k < m; k++) {
                for (int l = 0; l < n + 1; l++) {
                    if (k > i || (k == i && l > j)) {
                        cout << "* ";
                    } else {
                        cout << A[k][l] << " ";
                    }
                }
                cout << endl;
            }
            cout << endl;
        }
    }

    double B[m][n];
    double c[m];

    for (int i = 0; i < m; i++) {
        for (int j = 0; j < n; j++) {
            if (i == j) {
                B[i][j] = 0;
            } else {
                B[i][j] = -A[i][j] / A[i][i];
            }
        }
        c[i] = A[i][n] / A[i][i];
    }

    double x[n];
    for (int i = 0; i < n; i++) {
        x[i] = 0;
    }

    double tol = 1e-6;

    int iter = 0;
    bool done = false;

    while (!done) {
        double x_new[n];
        for (int i = 0; i < n; i++) {
            double sum = 0;
            for (int j = 0; j < n; j++) {
                sum += B[i][j] * x[j];
            }
            x_new[i] = sum + c[i];
        }

        double error = 0;
        for (int i = 0; i < n; i++) {
            error += abs(x_new[i] - x[i]);
        }
        if (error < tol) {
            done = true;
        }

        for (int i = 0; i < n; i++) {
            x[i] = x_new[i];
        }

        iter++;
    }

    cout << "SLE solution by simple iteration method:" << endl;
    cout << "Number of iterations: " << iter << endl;
    for (int i = 0; i < n; i++) {
        cout << "x" << i + 1 << " = " << x[i] << endl;
    }

    return 0;
}
