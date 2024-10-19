#!/bin/bash

# 1. Определение типа командной оболочки
echo "Тип оболочки: $SHELL"

# 2. Вывод значений переменных окружения
echo "UID: $UID"
echo "USER: $USER"
echo "BASH: $BASH"
echo "HOME: $HOME"
echo "PATH: $PATH"
echo "PS1: $PS1" 
echo "PS2: $PS2" 
echo "PWD: $PWD"
echo "TERM: $TERM"
echo "HOSTNAME: $HOSTNAME"
echo "SECONDS: $SECONDS"

# 3. HOME
cd "$HOME"
cat "STUDENT/MPM/vladimir.txt" 

# 4. Приглашение пользователю с помощью printf и read
printf "Введите команду: "
read command

# 5. Выполнение команды пользователя
if [ -z "$command" ]; then
  echo "Ошибка: команда не введена."
else
  eval "$command"
fi