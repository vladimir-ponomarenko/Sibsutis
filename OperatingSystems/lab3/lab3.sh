#!/bin/bash

# 1. Копирование содержимого файла vladimir.txt в файл envs
cat /home/user/STUDENT/MPM/vladimir.txt > envs.txt

# 2. Проверка содержимого файла envs
echo "Задание 2:"
cat envs.txt

# 3. Вывод содержимого файла /etc/passwd
echo "Задание 3:"
echo "Содержимое файла /etc/passwd:"
cat /etc/passwd
echo "Информация в /etc/passwd содержит записи о пользователях системы."

# 4. Сортировка содержимого /etc/passwd и сохранение в passwd.orig
cat /etc/passwd | sort > passwd.orig 

# 6. Добавление нового пользователя в passwd.orig
echo "newuser:x:1001:1001:New User,,,:/home/newuser:/bin/bash" >> passwd.orig

# 7. Проверка успешного добавления пользователя
echo "Задание 7:"
echo "Проверка добавления пользователя:"
tail -n 1 passwd.orig

# 8. Создание файла a1 и заполнение его текстом
cat > a1 << EOF
1. Первая строка
2. Вторая строка
3. Третья строка
4. Четвертая строка
5. Пятая строка
6. Шестая строка
EOF

# 9. Создание файла a2
touch a2

# 11. Проверка файлов и сохранение вывода ls -l в f3
ls -l a1 a2 > f3
echo "Задание 11:"
cat f3

# 12.
head -n 2 a1 >> a2
tail -n 2 a1 >> f3
echo "Задание 12:"
cat f3

# 13. Сортировка a2 по второму столбцу и сохранение в a2_s2
sort -k 2 a2 > a2_s2
echo "Задание 13:"
cat a2_s2

# 14. Создание файла mix из строк a1, a2 и f3
head -n 2 a2 > mix
head -n 3 a1 | tail -n 1 >> mix
head -n 5 f3 | tail -n 2 >> mix
echo "Задание 14:"
cat mix

# 15. Поиск строк с цифрой "3" и сохранение в a_g
grep "3" ~/ * > a_g

# 16. Поиск файлов в /etc/ с IP-адресами и сохранение уникальных имен в g_ip
grep -l '[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}' /etc/* | sort -u > g_ip

# 17. Рекурсивный поиск файлов с буквой "а" в имени и сохранение списка в spisok_a
find ~ -type f -iname "*a*" -print | sort -u > spisok_a