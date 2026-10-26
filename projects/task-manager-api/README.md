# task-manager-api

API de gerenciamento de tarefas em Flask, usada como alvo da skill `refactor-arch`.

## Instalação e execução

```powershell
pip install -r requirements.txt
python seed.py
python app.py
```

A API inicia em `http://127.0.0.1:5000`. `seed.py` cria usuários, categorias e tarefas de exemplo no SQLite. Configure `DATABASE_URL`, `SECRET_KEY` e `CORS_ORIGINS` no ambiente para personalizar a execução; debug fica desativado por padrão.

## Testes

```powershell
python -m unittest discover -s tests -v
```

Os testes usam SQLite temporário e cobrem health, criação/login de usuários, não exposição de hashes e validação de prioridade.
