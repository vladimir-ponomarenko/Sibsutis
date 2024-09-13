#include <iostream>
#include <fstream>
#include <vector>
#include <cstdio>

double a = 1, y = 0, cisol = 0, mu = 0.0188, beta = 0.999, rho = 0.952, kappa = 0.042, alphaI = 0.999, alphaE = 0.999;
double h = 1, t = 0, day = 90, N = 2798170, D0 = 0, I0 = 0, R0 = 24, E0 = 99, S0 = N - E0 - R0;

double func_c(double c_isol);
double func_S(double S, double E, double I, double R, double N);
double delta_S(double S, double E, double I, double R, double N, double h);
double func_E(double S, double E, double I, double N);
double delta_E(double S, double E, double I, double N, double h);
double func_I(double E, double I);
double delta_I(double E, double I, double h);
double func_R(double E, double I, double R);
double delta_R(double E, double I, double R, double h);
double func_D(double I);

int main() {
    std::vector<double> S_t = {S0}, E_t = {E0}, I_t = {I0}, R_t = {R0}, D_t = {D0}, N_t = {S_t.back() + E_t.back() + I_t.back() + R_t.back() + D_t.back()};
    std::vector<int> days;
    
    for (int i = 0; i <= day; i++) {
        days.push_back(t + i * h);
        S_t.push_back(S_t.back() + delta_S(S_t.back(), E_t.back(), I_t.back(), R_t.back(), N_t.back(), h));
        E_t.push_back(E_t.back() + delta_E(S_t.back(), E_t.back(), I_t.back(), N_t.back(), h));
        I_t.push_back(I_t.back() + delta_I(E_t.back(), I_t.back(), h));
        R_t.push_back(R_t.back() + delta_R(E_t.back(), I_t.back(), R_t.back(), h));
        D_t.push_back(D_t.back() + func_D(I_t.back()));
        N_t.push_back(S_t.back() + E_t.back() + I_t.back() + R_t.back() + D_t.back());
    }
    
    std::ofstream file("result.txt", std::ios::out);
    
    for (int i = 0; i <= day; i++) {
        char str_data[100];
        sprintf(str_data, "%d %.2lf %.2lf %.2lf %.2lf %.2lf %.2lf\n", days[i], N_t[i], S_t[i], E_t[i], I_t[i], R_t[i], D_t[i]);
        std::string data(str_data);
        file << data;
    }
    
    file.close();

    std::ofstream data_file("data_plot.txt", std::ios::out);
    for (int i = 0; i <= day; i++) {
        data_file << I_t[i] << " " << days[i] << std::endl;
    }
    data_file.close();

    std::ofstream script_file("plot_script.plt", std::ios::out);
    script_file << "set title 'Number of Infected Over Time'\n";
    script_file << "set xlabel 'Number of Infected'\n";
    script_file << "set ylabel 'Days'\n";
    script_file << "set term x11\n";
    script_file << "plot 'data_plot.txt' with lines\n";
    script_file << "pause -1 'Press any key to exit'\n";
    script_file.close();

    system("gnuplot plot_script.plt");

    return 0;
}

double func_c(double c_isol) {
    return 1 + c_isol * (1 - 2 / 5 * a);
}

double func_S(double S, double E, double I, double R, double N) {
    return -1 * func_c(cisol) * S / N * (alphaI * I + alphaE * E) + y * R;
}

double delta_S(double S, double E, double I, double R, double N, double h) {
    return h * func_S(S + h / 2 * func_S(S, E, I, R, N), E, I, R, N);
}

double func_E(double S, double E, double I, double N) {
    return func_c(cisol) * S / N * (alphaI * I + alphaE * E) - (kappa + rho) * E;
}

double delta_E(double S, double E, double I, double N, double h) {
    return h * func_E(S, E + h / 2 * func_E(S, E, I, N), I, N);
}

double func_I(double E, double I) {
    return kappa * E - beta * I - mu * I;
}

double delta_I(double E, double I, double h) {
    return h * func_I(E, I + h / 2 * func_I(E, I));
}

double func_R(double E, double I, double R) {
    return beta * I + rho * E - y * R;
}

double delta_R(double E, double I, double R, double h) {
    return h * func_R(E, I, R + h / 2 * func_R(E, I, R));
}

double func_D(double I) {
    return mu * I;
}
