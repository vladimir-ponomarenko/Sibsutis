#include <iostream>
#include <cmath>
using namespace std;

class Quadrilateral {
protected:
    double x1, y1;  // Координаты точки 1
    double x2, y2;  // Координаты точки 2
    double x3, y3;  // Координаты точки 3
    double x4, y4;  // Координаты точки 4

public:
    // Конструктор класса
    Quadrilateral(double x1, double y1, double x2, double y2,
                  double x3, double y3, double x4, double y4) {
        this->x1 = x1;
        this->y1 = y1;
        this->x2 = x2;
        this->y2 = y2;
        this->x3 = x3;
        this->y3 = y3;
        this->x4 = x4;
        this->y4 = y4;
    }

    // Методы вычисления длин сторон
    double side1() {
        return sqrt(pow(x2 - x1, 2) + pow(y2 - y1, 2));
    }

    double side2() {
        return sqrt(pow(x3 - x2, 2) + pow(y3 - y2, 2));
    }

    double side3() {
        return sqrt(pow(x4 - x3, 2) + pow(y4 - y3, 2));
    }

    double side4() {
        return sqrt(pow(x1 - x4, 2) + pow(y1 - y4, 2));
    }

    // Методы вычисления диагоналей
    double diagonal1() {
        return sqrt(pow(x3 - x1, 2) + pow(y3 - y1, 2));
    }

    double diagonal2() {
        return sqrt(pow(x4 - x2, 2) + pow(y4 - y2, 2));
    }

    // Метод вычисления периметра
    double perimeter() {
        return side1() + side2() + side3() + side4();
    }

    // Метод вычисления площади
    virtual double area() {
        // Реализация в подклассе
        return 0;
    }
};

class Trapezoid : public Quadrilateral {
public:
    // Конструктор класса
    Trapezoid(double x1, double y1, double x2, double y2,
              double x3, double y3, double x4, double y4)
        : Quadrilateral(x1, y1, x2, y2, x3, y3, x4, y4) {}
     bool check(){
        double c = side2();
        double d = side4();
        double a = side1();
        double b = side3();
        if ((a == b && c != d) || (c == d && a != b))
            return true;
        else return false;
    }
      // Переопределение метода вычисления площади
    double area() override {
        double c = side2();
        double d = side4();
        double a = side1();
        double b = side3();
        double h = sqrt(pow(c,2) - ((pow((a - b),2) + pow(c,2) - pow(d,2))/(2*(a-b))));
        return (a + b) * h / 2;
    }
};

int main() {
    // Создание объектов трапеций
    Trapezoid trapezoid1(0, 0, -5, 0, -4, -3, -1, -3);
    Trapezoid trapezoid2(2, 2, 8, 2, 7, 5, 4, 5);
Trapezoid trapezoid3(-3, -2, 2, -2, 4, 1, -1, 1);
// Вычисление и вывод информации о трапециях
cout << "Трапеция 1:" << endl;
cout << "Длины сторон: " << trapezoid1.side1() << ", " << trapezoid1.side2() << ", "
     << trapezoid1.side3() << ", " << trapezoid1.side4() << endl;
cout << "Диагонали: " << trapezoid1.diagonal1() << ", " << trapezoid1.diagonal2() << endl;
cout << "Периметр: " << trapezoid1.perimeter() << endl;
if (trapezoid1.check())
    cout << "Площадь: " << trapezoid1.area() << endl;
else  cout << "Площадь: Не трапеция." << endl;

cout << "Трапеция 2:" << endl;
cout << "Длины сторон: " << trapezoid2.side1() << ", " << trapezoid2.side2() << ", "
     << trapezoid2.side3() << ", " << trapezoid2.side4() << endl;
cout << "Диагонали: " << trapezoid2.diagonal1() << ", " << trapezoid2.diagonal2() << endl;
cout << "Периметр: " << trapezoid2.perimeter() << endl;
if (trapezoid2.check())
    cout << "Площадь: " << trapezoid2.area() << endl;
else  cout << "Площадь: Не трапеция." << endl;

cout << "Трапеция 3:" << endl;
cout << "Длины сторон: " << trapezoid3.side1() << ", " << trapezoid3.side2() << ", "
     << trapezoid3.side3() << ", " << trapezoid3.side4() << endl;
cout << "Диагонали: " << trapezoid3.diagonal1() << ", " << trapezoid3.diagonal2() << endl;
cout << "Периметр: " << trapezoid3.perimeter() << endl;
if (trapezoid3.check())
    cout << "Площадь: " << trapezoid3.area() << endl;
else  cout << "Площадь: Не трапеция." << endl;

// Поиск трапеции с минимальной и максимальной площадью
double minArea = trapezoid1.area();
double maxArea = trapezoid1.area();
int minIndex = 1;
int maxIndex = 1;

double areas[] = {trapezoid1.area(), trapezoid2.area(), trapezoid3.area()};

for (int i = 1; i < 3; i++) {
    if (areas[i] < minArea) {
        if (trapezoid3.check()){
            minArea = areas[i];
            minIndex = i + 1;}
    }

    if (areas[i] > maxArea) {
        if (trapezoid3.check()){
            maxArea = areas[i];
            maxIndex = i + 1;}
    }
}

cout << "Трапеция с минимальной площадью: " << "Трапеция " << minIndex << ", площадь = " << minArea << endl;
cout << "Трапеция с максимальной площадью: " << "Трапеция " << maxIndex << ", площадь = " << maxArea << endl;
return 0;
}
