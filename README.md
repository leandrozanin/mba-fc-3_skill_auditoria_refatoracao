# Auditoria e Refatoração Arquitetural

Desafio 3: a skill `refactor-arch` existe na raiz para Codex e Claude Code. Para atender ao exercício, a cópia Claude também está instalada em `.claude/skills/refactor-arch/` dentro de cada projeto.

## Projetos e relatórios

| Projeto | Skill Claude | Relatório |
|---|---|---|
| `code-smells-project` | `projects/code-smells-project/.claude/skills/refactor-arch/` | `reports/audit-project-1.md` |
| `ecommerce-api-legacy` | `projects/ecommerce-api-legacy/.claude/skills/refactor-arch/` | `reports/audit-project-2.md` |
| `task-manager-api` | `projects/task-manager-api/.claude/skills/refactor-arch/` | `reports/audit-project-3.md` |

Os três relatórios incluem a auditoria inicial e a evidência da Fase 3. A Fase 3 foi autorizada para os três projetos nesta revisão. Cada projeto preserva suas rotas existentes, separa composição/configuração, valida entradas e adiciona testes de regressão.

## Testes locais

```powershell
cd projects/code-smells-project
.venv\Scripts\python.exe -m unittest discover -s tests -v

cd ..\ecommerce-api-legacy
npm test

cd ..\task-manager-api
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Instale as dependências de cada projeto antes de executar os testes. A suíte cobre contratos e regressões em memória/SQLite temporário; não exige Docker nem serviços externos.

## Estrutura

- Projeto 1: `config/`, `views/`, `controllers/`, `models/` e `middlewares/`; remove execução arbitrária de SQL e protege credenciais.
- Projeto 2: `src/config/`, `src/views/`, `src/controllers/`, `src/models/` e `src/middlewares/`; checkout transacional e logs sem dados de pagamento.
- Projeto 3: `create_app` sem debug por padrão, segredo externo, serialização de usuário sem senha e hash adaptativo com migração no login; rotas usam blueprints e modelos/services existentes.

Consulte os relatórios para limitações e findings que permanecem fora do escopo.
