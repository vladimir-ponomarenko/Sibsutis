#include <iostream>
#include <cmath>

using namespace std;

int correlation(int a[], int b[], int n){
    int sum=0;
    for(int i=0; i<n; i++){
        sum+=a[i]*b[i];
    }
    return sum;
}

double normCorr(int a[], int b[], int n){
    int corr = correlation(a,b,n);
    int sumA = 0, sumB=0;
    for(int i=0;i<n;i++){
        sumA+=a[i]*a[i];
        sumB+=b[i]*b[i];
    } 
    double result = corr/sqrt(sumA*sumB);
    return result;
}

int main(){
    int n=8;
    int a[] = {1,3,5,-1,-4,-5,1,4};
    int b[] = {2,4,7,0,-3,-4,2,5};
    int c[] = {-5,-1,3,-4,2,-6,4,-1};

    double corAB = correlation(a, b, n);
    double corAC = correlation(a, c, n);
    double corBC = correlation(b, c, n);

    double corNormAB = normCorr(a, b, n);
    double corNormAC = normCorr(a, c, n);
    double corNormBC = normCorr(b, c, n);

    cout << "Корреляция между a, b и c:" << endl;
    cout << "\\ | a | b | c" << endl;
    cout << "a | - | " << corAB << " | " << corAC << endl;
    cout << "b | " << corAB << " | - | " << corBC << endl;
    cout << "c | " << corAC << " | " << corBC << " | -" << endl << endl;

    cout << "Нормализованная корреляция между a, b и c:" << endl;
    cout << "\\ | a | b | c" << endl;
    cout << "a | - | " << corNormAB << " | " << corNormAC << endl;
    cout << "b | " << corNormAB << " | - | " << corNormBC << endl;
    cout << "c | " << corNormAC << " | " << corNormBC << " | -" << endl;

    return 0;
}