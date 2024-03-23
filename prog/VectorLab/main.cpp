#include <algorithm>  
#include <iostream>
#include <vector>
using namespace std;

class organization {
public:
    string orgtype;
    string owntype;
    organization(string org, string own) {
        orgtype = org;
        owntype = own;
    }
    string get_own() const { return owntype; }
    string get_org() const { return orgtype; }
    void set_org(string org) { orgtype = org; }
    void set_own(string own) { owntype = own; }
    void print() const {
        cout << "Тип организации: " << orgtype << endl;
        cout << "Тип собственности: " << owntype << endl;
    }
};

bool compareOrgByType(const organization &org1, const organization &org2) {
    return org1.get_org() < org2.get_org();  
}

int main() {
    int size;
    cout << "Введите количество объектов в векторе: ";
    cin >> size;
    vector<organization> orgVector;
    for (int i = 0; i < size; i++) {
        string orgType, ownType;
        cout << "Введите тип организации для объекта " << i + 1 << ": ";
        cin >> orgType;
        cout << "Введите тип собственности для объекта " << i + 1 << ": ";
        cin >> ownType;
        organization obj(orgType, ownType);
        orgVector.push_back(obj);
    }  

    vector<organization> newOrgVector;
    for (const organization &org : orgVector) {
        if (org.get_own() == "Частная") {
            newOrgVector.push_back(org);
        }
    }
    cout << "Размер нового вектора: " << newOrgVector.size() << endl;
    if (!newOrgVector.empty()) {
        sort(newOrgVector.begin(), newOrgVector.end(), compareOrgByType);
        cout << "Объекты в отсортированном новом векторе:" << endl;
        for (const organization &org : newOrgVector) {
            org.print();
        }
    }
    return 0;
}
