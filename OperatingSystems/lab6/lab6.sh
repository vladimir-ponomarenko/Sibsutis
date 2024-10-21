#!/bin/bash

while getopts "fm:" OPTION; do
    case "$OPTION" in
        f)
            # Опция -f: запросить команду от пользователя и выполнить ее
            echo "Введите команду:"
            read user_command
            echo "Выполнение команды: $user_command"
            eval "$user_command"
            ;;
        m)
            # Опция -m: проверка наличия файла с именем, указанным в качестве параметра и вывод содержимого
            filename="$OPTARG"
            if [ -e "$filename" ]; then
                echo "Файл '$filename' найден. Содержимое файла:"
                cat "$filename"
                echo 
            else
                echo "Такого файла нет: $filename"
            fi
            ;;
        \?)
            # Обработка недопустимых опций
            echo "Недопустимая опция: -$OPTARG"
            exit 1
            ;;
    esac
done
