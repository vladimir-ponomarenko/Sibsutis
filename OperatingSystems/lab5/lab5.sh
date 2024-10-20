#!/bin/bash

if [ $# -eq 0 ]; then
  echo "Использование: $0 имя_файла1 ..."
  exit 1
fi

for filename in "$@"; do
  if [ ! -f "$filename" ]; then
    echo "Ошибка: Файл '$filename' не найден."
    continue
  fi

  echo "Файл: $filename"

  total_chars=0

  while  read -r line || [[ -n "$line" ]]; do
    line=$(echo "$line" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//') 

    for word in $line; do
      word_length=${#word}
      total_chars=$((total_chars + word_length))
      echo "Слово: $word, Длина: $word_length"
    done
  done < "$filename"

  echo "Общий размер: $total_chars символов" 
  echo "-----------------------------------"
done