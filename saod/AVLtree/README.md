# AVL Tree

Это программа на C++, которая реализует структуру данных AVL-дерево (дерево самобалансирующееся по высоте). Программа позволяет добавлять, искать и удалять элементы, а также выводить дерево на экран.

## Описание

AVL-дерево - это двоичное дерево поиска, в котором разница высот поддеревьев каждого узла ограничена определенным значением (в данной программе - балансом). Это позволяет гарантировать логарифмическую сложность операций вставки, удаления и поиска элемента в сбалансированном дереве.

## Основные функции

- `avltree_add`: добавляет новый узел в дерево.
- `avltree_lookup`: ищет узел по ключу.
- `avltree_delete`: удаляет узел из дерева.
- `avltree_print_dfs`: выводит дерево на экран в глубину.

## Как использовать

1. Запустите программу.
2. Выберите одно из следующих действий:
   - **1.** Поиск слова по ключу.
   - **2.** Удаление слова по ключу.
   - **3.** Вывод дерева на экран.
   - **4.** Завершение программы.
3. Введите номер выбранного действия и следуйте инструкциям.

## Примечания

- Программа читает слова из файла "words.txt" и строит AVL-дерево по ключам, представленным целыми числами от 0 до 49999.
- После вставки всех слов из файла, программа выполняет операции поиска случайного ключа в диапазоне от 1 до числа вставленных слов, замеряя время выполнения.
- При завершении работы программы, память освобождается с помощью функции `avltree_free`.

