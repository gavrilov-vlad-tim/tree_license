#!/bin/bash
LIC_PATH=
LOG_PATH=''
PRJ_PATH=

# Обработка параметров
while [ -n "$1" ]
do
  case "$1" in
  -f) shift
    LIC_PATH="$1";;
  -l) shift
    LOG_PATH="$1";;
  *) PRJ_PATH="$1";;
  esac
  shift
done

# Валидация пути к файлу лицензии
if [ -z $LIC_PATH ]; then LIC_PATH=$LICENSE_FILE_PATH; fi
if [ -z $LIC_PATH ]; then echo 'Missing path to license file'; return 1; fi
if [ ! -f $LIC_PATH ]; then echo "No such license file: $LIC_PATH"; return 1; fi

# Валидация пути к файлу лога
if [ ! -f $LOG_PATH ] | [ -z $LOG_PATH]; then
  echo "No such log file: $LOG_PATH"
  LOG_PATH="$(pwd)/license.log"
  if [ -f "$LOG_PATH" ]; then rm $LOG_PATH; fi
  touch license.log
  echo "license.log was created in current directory"
  echo "Log will write to: $LOG_PATH"
fi

# Валидация пути к проекту
if [ ! -d $PRJ_PATH ]; then echo "No such project directory: $PRJ_PATH"; return 1; fi

# Итерация по файлам проекта
PRJ_PATH_NAME=$(basename $PRJ_PATH)
EXTS=(py sh html css)

for current_file in $(find $PRJ_PATH -type f); do
  FILENAME=$(basename $current_file)
  EXT=$(echo "$FILENAME" | cut -f 2 -d '.')

# Пропуска файла с расширением отличным от предустановленного
  if [[ ! " ${EXTS[*]} " =~ " ${EXT} " ]]; then continue; fi
# Пропуск не текстовых файлов
  if [ -z "$(file $current_file | grep -w text)" ]; then continue; fi
# Пропуск файлов имеющих лицензию
  if [ -n "$(grep -w "File: $FILENAME" "$current_file")" ] && [ -n "$(grep -w "Project: $PRJ_PATH_NAME" "$current_file")" ]; then
     continue
  fi
  touch tmp_license
  python3 render.py --filename=$FILENAME --root_folder=$PRJ_PATH_NAME\
          --year=$(date +%Y) $LIC_PATH > tmp_license

# Постобработка и вставка текста лицензии с учетов расширения файла
  case "$EXT" in
  css) sed -i '1 s/^/\x2F\x2A\n/' tmp_license
       sed -i '$a*/\n' tmp_license
       tac tmp_license | xargs --replace=INS -- sed -i '1 i INS' $current_file;;
  html) sed -i '1 s/^/<!--\n/' tmp_license
        sed -i '$a-->\n' tmp_license
        sed -i '/<head>/ r tmp_license' $current_file;;
  *) sed -i 's/^/#/' tmp_license
     SHEBANG=$(cat $current_file)
     if [ "${SHEBANG:0:2}" = '#!' ]
     then
       tac tmp_license | xargs --replace=INS -- sed -i '2i INS' $current_file
     else
       tac tmp_license | xargs --replace=INS -- sed -i '1i INS' $current_file
     fi;;
  esac
  rm -f tmp_license
  echo $current_file | tee -a $LOG_PATH > /dev/null
done

# Вывод статистики
  echo "Total files updated: $(wc -l $LOG_PATH | cut -f1 -d ' ')"
  echo "Updated files:"
  cat $LOG_PATH
