#include <algorithm>
#include <iostream>
#include <vector>

using namespace std;

class Book {
   public:
    Book(string udc, string author, string title, int year, int copies)
        : udc_(udc),
          author_(author),
          title_(title),
          year_(year),
          copies_(copies) {}

    void print() const {
        cout << "Номер УДК: " << udc_ << endl;
        cout << "Автор: " << author_ << endl;
        cout << "Название: " << title_ << endl;
        cout << "Год издания: " << year_ << endl;
        cout << "Количество экземпляров: " << copies_ << endl;
    }

    string getUdc() const { return udc_; }
    int getYear() const { return year_; }

   private:
    string udc_;
    string author_;
    string title_;
    int year_;
    int copies_;
};

bool compareBooksByYear(const Book& book1, const Book& book2) {
    return book1.getYear() < book2.getYear();
}

int main() {
    vector<Book> library;

    // Начальное формирование данных о книгах
    library.push_back(Book("001", "Автор 1", "Книга 1", 2000, 5));
    library.push_back(Book("002", "Автор 2", "Книга 2", 2010, 3));
    library.push_back(Book("003", "Автор 3", "Книга 3", 1995, 8));

    // Сортировка списка книг по годам издания
    sort(library.begin(), library.end(), compareBooksByYear);

    int choice;
    string udc;
    string author;
    string title;
    int year;
    int copies;

    while (true) {
        cout << "Выберите действие:" << endl;
        cout << "2. Удалить книгу" << endl;
        cout << "3. Поиск книги" << endl;
        cout << "4. Вывести список книг" << endl;
        cout << "5. Выход" << endl;
        cout << "Введите номер действия: ";
        cin >> choice;

        if (choice == 1) {
            cout << "Введите номер УДК: ";
            cin >> udc;
            cout << "Введите автора: ";
            cin.ignore();
            getline(cin, author);
            cout << "Введите название: ";
            getline(cin, title);
            cout << "Введите год издания: ";
            cin >> year;
            cout << "Введите количество экземпляров: ";
            cin >> copies;
            library.push_back(Book(udc, author, title, year, copies));
            // Сортировка списка книг по годам издания
            sort(library.begin(), library.end(), compareBooksByYear);

            cout << "Книга добавлена в библиотеку." << endl;
        } else if (choice == 2) {
            cout << "Введите номер УДК книги, которую нужно удалить: ";
            cin >> udc;

            auto it =
                find_if(library.begin(), library.end(),
                        [&](const Book& book) { return book.getUdc() == udc; });
            if (it != library.end()) {
                library.erase(it);
                cout << "Книга удалена из библиотеки." << endl;
            } else {
                cout << "Книга с указанным номером УДК не найдена." << endl;
            }
        } else if (choice == 3) {
            cout << "Введите номер УДК книги для поиска: ";
            cin >> udc;

            auto it =
                find_if(library.begin(), library.end(),
                        [&](const Book& book) { return book.getUdc() == udc; });

            if (it != library.end()) {
                it->print();
            } else {
                cout << "Книга с указанным номером УДК не найдена." << endl;
            }
        } else if (choice == 4) {
            cout << "Список книг в библиотеке:" << endl;
            for (const Book& book : library) {
                book.print();
                cout << "--------------------------" << endl;
            }
        } else if (choice == 5) {
            cout << "Программа завершена." << endl;
            break;
        } else {
            cout << "Неправильный ввод. Попробуйте еще раз." << endl;
        }
    }

    return 0;
}
