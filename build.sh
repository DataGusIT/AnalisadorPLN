#!/usr/bin/env bash
# build.sh

# Sai o script se qualquer comando falhar
set -o errexit

# 1. Instala as dependências
pip install -r requirements.txt

# 2. Coleta os arquivos estáticos
python manage.py collectstatic --no-input

# 3. Aplica as migrações do banco de dados
python manage.py migrate
