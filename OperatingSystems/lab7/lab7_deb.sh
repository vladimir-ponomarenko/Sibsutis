#!/bin/bash

# ls /var/cache/apt/archives/*.deb

script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
workdir="${script_dir}"

if [ $# -ne 1 ]; then
    echo "Ошибка: Требуется один аргумент - имя deb-пакета"
    echo "Использование: $0 <имя_пакета.deb>"
    exit 1
fi

if [[ "$1" == /* ]]; then
    package_file="$1"
else
    package_file="$(pwd)/$1"
fi

output_file="${workdir}/$(basename ${package_file%.*}).test"

echo "Текущий каталог: $(pwd)"
echo "Путь к скрипту: $script_dir"
echo "Полный путь к пакету: $package_file"

if [ ! -f "$package_file" ]; then
    echo "Ошибка: Файл $package_file не найден"
    echo "Содержимое текущего каталога:"
    ls -l
    exit 1
fi

write_section() {
    local section_name="$1"
    echo "=== $section_name ===" >> "$output_file"
    shift
    "$@" >> "$output_file" 2>&1
    echo -e "\n" >> "$output_file"
}

{
    echo "Отчет по анализу пакета: $package_file"
    echo "Дата создания отчета: $(date)"
    echo "----------------------------------------"
    echo

    write_section "Список файлов в архиве" dpkg-deb -c "$package_file"

    write_section "Информация о пакете" dpkg-deb -I "$package_file"

    write_section "Проверка возможности установки" dpkg -i --dry-run "$package_file"
    
    if [ $? -eq 0 ]; then
        echo "Статус проверки установки: УСПЕШНО" >> "$output_file"
    else
        echo "Статус проверки установки: ОШИБКА" >> "$output_file"
    fi
    echo >> "$output_file"

    write_section "Проверка контрольной суммы" dpkg --verify "$package_file"
    
    echo "----------------------------------------" >> "$output_file"
    echo "Анализ завершен" >> "$output_file"
    echo "Путь к отчету: $output_file" >> "$output_file"
}

echo "Отчет создан: $output_file"