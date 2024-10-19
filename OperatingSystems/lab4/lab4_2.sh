#!/bin/bash

# Извлечение путей из переменной PATH
paths=$(echo $PATH | tr ":" "\n")

counter=1

# Обработка каждого пути
for path in $paths; do
  if [ -d "$path" ]; then
    if [ $counter -le 2 ]; then
      echo "Содержимое каталога: $path"
      ls -l "$path"
    else
      echo "Информация о каталоге: $path"
      ls -ld "$path"
    fi

    counter=$((counter + 1))
  fi
done