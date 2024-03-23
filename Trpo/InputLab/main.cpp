#include <malloc.h>
#include <stdio.h>

#include <cmath>
#include <iostream>
using namespace std;
int main() {
    string a;
    std::cout << "text: ";
    getline(cin, a);
    int n = 0;
    for (int i = 0; i <= a.size(); i++) {
        if (a[i] == '?') n = n + 1;
    }
    std::cout << n;
    return 0;
}