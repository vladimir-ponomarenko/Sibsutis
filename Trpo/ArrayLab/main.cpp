#include <iostream>
#include <cstdlib> 
#include <time.h>

int *Create (int N)
{
    int *arr = new int [N];
    for (int i = 0; i<N; i++){
        arr[i] = rand()%100-50;
    std::cout << arr[i]<<"  ";
    }
    return arr;
}

int *del(int *array, int length) {    
    for(int j = 0; j<length; j++){
        array[j] = array[j+2];
    }
    return array;
} 

int ind(int *array, int length){
    int max=0;
    for(int h = 0; h<length; h++)
        if(array[h]>array[max]) max = h;
    return max;
}


int main() {
    srand(time(0));
    int N;
    int *arr;
        std::cout << "Input N: ";
        std::cin >> N;
        std::cout << "Массив до: ";
    arr = Create(N);
        std::cout<< "\n";
    int sum = 0;
    float sred = 0;
    int count =0;
    for(int k=0; k<N; k++){
        if(arr[k]>0){
        count++;
        sum = sum+arr[k];
        }
    }
    sred=sum/count;
        std::cout << "среднее: ";
        std::cout<< sred <<std::endl;
    int max1 = ind(arr, N);
        std::cout << "макс: "<< max1<<std::endl;

    N = N-2;
        std::cout << "Массив после: ";
    arr = del(arr, N);
        std:: cout << "\n";
    for (int i=0; i < N; i++){
        std::cout<< arr[i]<<"  ";
    }
        std::cout<< "\n";
    sum = 0;
    sred = 0;
    count =0;
    for(int k=0; k<N; k++){
        if(arr[k]>0){
        count++;
        sum = sum+arr[k];
         }
    }
    sred=sum/count;
        std::cout << "среднее: ";
        std::cout<< sred <<std::endl;
        
    int max2 = ind(arr, N);
        std::cout << "макс: "<< max2<<std::endl;
            if (max1!=max2)
                std::cout<< "изменилось положение\n";
              else std::cout<< "не изменилось положение\n";
}