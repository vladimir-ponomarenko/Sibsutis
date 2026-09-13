#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <sstream>
#include <cmath>
#include <iomanip>
#include <optional>
#include <string_view>

std::optional<double> parse_value(const std::string &token)
{
    if (token.empty() || token == "NN")
    {
        return std::nullopt;
    }
    try
    {
        return std::stod(token);
    }
    catch (...)
    {
        return std::nullopt;
    }
}

double calculate_pearson(const std::vector<double> &x, const std::vector<double> &y)
{
    if (x.empty() || x.size() != y.size())
    {
        return 0.0;
    }

    const size_t n = x.size();
    double sum_x = 0.0, sum_y = 0.0;
    double sum_xy = 0.0, sum_x2 = 0.0, sum_y2 = 0.0;

    for (size_t i = 0; i < n; ++i)
    {
        sum_x += x[i];
        sum_y += y[i];
        sum_xy += x[i] * y[i];
        sum_x2 += x[i] * x[i];
        sum_y2 += y[i] * y[i];
    }

    const double numerator = static_cast<double>(n) * sum_xy - sum_x * sum_y;
    const double denominator = std::sqrt((static_cast<double>(n) * sum_x2 - sum_x * sum_x) *
                                         (static_cast<double>(n) * sum_y2 - sum_y * sum_y));

    return (denominator != 0.0) ? (numerator / denominator) : 0.0;
}

std::string_view interpret_correlation(double r)
{
    const double abs_r = std::abs(r);
    if (abs_r < 0.3)
    {
        return "Зависимость практически отсутствует";
    }

    std::string_view direction = (r > 0) ? "прямая" : "обратная";

    if (abs_r < 0.5)
        return (r > 0) ? "Умеренная прямая зависимость" : "Умеренная обратная зависимость";
    if (abs_r < 0.7)
        return (r > 0) ? "Заметная прямая зависимость" : "Заметная обратная зависимость";
    return (r > 0) ? "Высокая прямая зависимость" : "Высокая обратная зависимость";
}

struct SamplePair
{
    std::vector<double> feature;
    std::vector<double> age;

    void add(double f_val, double age_val)
    {
        feature.push_back(f_val);
        age.push_back(age_val);
    }

    [[nodiscard]] size_t size() const noexcept
    {
        return feature.size();
    }
};

int main()
{
    constexpr const char *FILENAME = "WHOLE1.DAT";
    constexpr int COL_1 = 49;
    constexpr int COL_2 = 50;
    constexpr int AGE_COL = 51;

    std::ifstream file(FILENAME);
    if (!file.is_open())
    {
        std::cerr << "Ошибка: не удалось открыть файл " << FILENAME << '\n';
        return 1;
    }

    SamplePair pair1;
    SamplePair pair2;

    std::string line;
    while (std::getline(file, line))
    {
        if (line.empty())
            continue;

        std::stringstream ss(line);
        std::string token;
        std::vector<std::string> row;

        while (ss >> token)
        {
            row.push_back(token);
        }

        if (row.size() >= AGE_COL)
        {
            auto opt_age = parse_value(row[AGE_COL - 1]);
            if (!opt_age)
                continue;

            if (auto opt_val1 = parse_value(row[COL_1 - 1]))
            {
                pair1.add(*opt_val1, *opt_age);
            }
            if (auto opt_val2 = parse_value(row[COL_2 - 1]))
            {
                pair2.add(*opt_val2, *opt_age);
            }
        }
    }
    file.close();

    const double corr1 = calculate_pearson(pair1.feature, pair1.age);
    const double corr2 = calculate_pearson(pair2.feature, pair2.age);

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "====================================================\n";

    auto print_result = [](int col, std::string_view name, size_t n, double r)
    {
        std::cout << "\nПараметр: [" << col << "] " << name << '\n'
                  << "  Объем выборки (N)       : " << n << '\n'
                  << "  Коэффициент Пирсона (r) : " << r << '\n'
                  << "  Интерпретация           : " << interpret_correlation(r) << '\n';
    };

    print_result(COL_1, "Стопа левая, низ", pair1.size(), corr1);
    print_result(COL_2, "Стопа правая, низ", pair2.size(), corr2);

    std::cout << "\n====================================================\n";
    return 0;
}