#include <iostream>
#include <string>  // Добавляем заголовок для использования std::string
using namespace std;

class organization {
   public:
    string orgtype;
    string owntype;
    organization(string org, string own) {
        orgtype = org;
        owntype = own;
    }
    string get_own() { return owntype; }
    string get_org() { return orgtype; }
    void set_org(string org) { orgtype = org; }
    void set_own(string own) { owntype = own; }
    // Исправленный метод print без возвращаемого значения
    void print() {
        // Исправлен синтаксис вывода
        cout << "Тип организации: " << orgtype << endl;
        cout << "Тип собственности: " << owntype << endl;
    }
};

int main() {
    organization obj("Управляющая к.", "Общий");
    obj.print();
    cout << "\n" << endl;
    cout << obj.get_own() << endl;
    cout << obj.get_org() << endl;
    cout << "\n" << endl;
    obj.set_org("А");
    obj.set_own("Частная");
    cout << obj.get_own() << endl;
    cout << obj.get_org() << endl;

    organization obj2("Дочерняя к.", "Общий");
    obj2.print();

    return 0;  // Добавляем возвратное значение для функции main()
}
