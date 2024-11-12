#include <iostream>
#include <vector>
#include <algorithm>
#include <numeric>
#include <random>

using namespace std;

vector<int> calculate_crc(const vector<int>& data, const vector<int>& generator){
    int data_size = data.size();
    int generator_size = generator.size();
    vector<int> extended_data = data;
    extended_data.resize(data_size + generator_size - 1, 0);

    for(int i = 0; i < data_size; ++i){
        if (extended_data[i] == 1) {
            for(int j = 0; j < generator_size; ++j){
                extended_data[i + j] ^= generator[j];
            }
        }   
    }

    vector<int> crc(generator_size-1);
    copy(extended_data.begin() + data_size, extended_data.end(), crc.begin());
    return crc;
}

// True - no errors, false - errors
bool check_errors(const vector<int>& data, const vector<int>& generator){
    vector<int> crc = calculate_crc(data, generator);
    return all_of(crc.begin(), crc.end(), [](int i){return i == 0;});
}

void print_vector(const vector<int>& vec, const string& name){
        cout << name << ": [";
    for (size_t i = 0; i < vec.size(); ++i) {
        cout << vec[i];
        if (i < vec.size() - 1) {
            cout << " ";
        }
    }
    cout << "]" << endl; 
}

int main(){
    vector<int> generator = {1, 0, 1, 1, 1, 0, 1, 1};
    random_device rd;
    mt19937 gen(rd());
    uniform_int_distribution<> dist(0, 1);
    

    int n1 = 20+12;
    vector<int> data1(n1);
    generate(data1.begin(), data1.end(), [&](){ return dist(gen); });

    vector<int> crc1 = calculate_crc(data1, generator);
    vector<int> data_with_crc1 = data1;
    data_with_crc1.insert(data_with_crc1.end(), crc1.begin(), crc1.end());

    cout << "---- N = " << n1 << " ----" << endl;
    print_vector(data1, "Data"); 
    print_vector(crc1, "CRC");
    print_vector(data_with_crc1, "Data with CRC");

    bool no_errors1 = check_errors(data_with_crc1, generator);
    cout << (no_errors1 ? "No errors detected." : "Errors detected!") << endl;


    int n2 = 250;  
    vector<int> data2(n2);  
    generate(data2.begin(), data2.end(), [&](){ return dist(gen); }); 

    vector<int> crc2 = calculate_crc(data2, generator); 
    vector<int> data_with_crc2 = data2; 
    data_with_crc2.insert(data_with_crc2.end(), crc2.begin(), crc2.end()); 

    cout << "\n---- N = " << n2 << " ----" << endl;
    print_vector(data2, "Data"); 
    print_vector(crc2, "CRC"); 
    print_vector(data_with_crc2, "Data with CRC"); 

    bool no_errors2 = check_errors(data_with_crc2, generator); 
    cout << (no_errors2 ? "No errors detected." : "Errors detected!") << endl; 


    int errors_detected = 0;
    int errors_missed = 0;
    int total_iterations = data_with_crc2.size();
    vector<int> data_with_errors = data_with_crc2;

    for(int i = 0; i<total_iterations; ++i){
        vector<int> data_with_errors = data_with_crc2;

        data_with_errors[i] ^= 1;

        if(check_errors(data_with_errors, generator)){
            errors_missed++;
        }
        else{
            errors_detected++;
        }
    }

    cout << "\n---- Data with errors ----";
    cout << "\nError detection results, N = 250" << endl;
    cout << "Errors Detected: " << errors_detected << endl;
    cout << "Errors Missed: " << errors_missed << endl;


    return 0;
}