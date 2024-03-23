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

    for (int k = 0; k < n; k++) {
        for (int i = k + 1; i < m; i++) {
            double t = A[i][k] / A[k][k];
            for (int j = 0; j < n + 1; j++) {
                A[i][j] -= t * A[k][j];
            }
        }
    }

    double x[n];
    for (int i = n - 1; i >= 0; i--) {
        double sum = 0;
        for (int j = i + 1; j < n; j++) {
            sum += A[i][j] * x[j];
        }
        x[i] = (A[i][n] - sum) / A[i][i];
    }

    cout << "SLE solution by Gauss method:" << endl;
    for (int i = 0; i < n; i++) {
        cout << "x" << i + 1 << " = " << x[i] << endl;
    }

    return 0;
}