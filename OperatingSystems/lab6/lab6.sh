#!/bin/bash

while getopts "fm:" OPTION; do
    case "$OPTION" in
        f)
            echo "Введите команду:"
            read user_command
            echo "Выполнение команды: $user_command"
            eval "$user_command"
            ;;
        m)
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
            echo "Недопустимая опция: -$OPTARG"
            exit 1
            ;;
    esac
done
