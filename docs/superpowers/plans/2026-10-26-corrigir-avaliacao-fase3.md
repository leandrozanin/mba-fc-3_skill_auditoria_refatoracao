# Corrigir Avaliação da Skill — Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans to execute this plan task-by-task. Steps use checkbox syntax.

**Goal:** Atender ao parecer: manter a skill na raiz, copiá-la para os três projetos, entregar relatórios de auditoria e refatorar os projetos com validação demonstrável.

**Architecture:** `.agents/skills/refactor-arch/` e `.claude/skills/refactor-arch/` na raiz permanecem como fontes canônicas. Cada projeto recebe cópia idêntica em `.claude/skills/refactor-arch/`; relatórios e evidências ficam em `reports/`; cada projeto conserva um entry point claro e separa configuração, models/repositórios, controllers e views/routes.

**Tech Stack:** Markdown, Python 3.12/Flask/SQLite/SQLAlchemy, Node.js/Express/sqlite3, unittest e testes HTTP locais.

**Spec:** `spec.md`; feedback do avaliador enviado pelo usuário em 2026-10-26.

## Global Constraints

- A skill deve ser copiada para `.claude/skills/refactor-arch/` dentro dos três projetos.
- Gerar `reports/audit-project-1.md`, `audit-project-2.md` e `audit-project-3.md` antes da refatoração.
- Refatorar somente os três diretórios-alvo e seus testes; preservar contratos de API sempre que seguro.
- Nunca manter SQL arbitrário acessível em `/admin/query`, secrets hardcoded ou dados sensíveis em respostas/logs.
- Validar com testes locais, boot e requisições HTTP representativas; anotar limitações sem alegar cobertura não executada.
- Publicar o resultado no repositório público `leandrozanin/mba-fc-3_skill_auditoria_refatoracao`, branch `main`, conforme solicitado pelo usuário.

## Review Focus

- Relatório antes da alteração versus caminhos/linhas depois da refatoração — indicar que a auditoria é baseline e usar linhas verificadas.
- Caminhos com espaços e execução com cwd na raiz do monorepo standalone.
- Endpoints administrativos perigosos: continuar respondendo com negação/depreciação, sem executar SQL/reset.
- Testes sem serviço externo ou dados persistentes — usar cliente Flask e SQLite temporário/in-memory.
- Dependência nativa sqlite3 no Node — documentar versão/runtime se impedir boot local.

---

### Task 1: Skill copies

**Files:** Modify `tests/test_skill_assets.py`; create the 6 mirrored skill files under each `projects/*/.claude/skills/refactor-arch/`.

- [x] Atualizar o teste para exigir cópias Claude byte-a-byte idênticas às referências canônicas em cada projeto.
- [x] Rodar o teste e confirmar falha porque as cópias não existem.
- [x] Copiar a skill canônica para cada projeto sem editar o conteúdo.
- [x] Rodar novamente o teste e confirmar sucesso.

### Task 2: Baseline audit reports

**Files:** Create `reports/audit-project-1.md`, `reports/audit-project-2.md`, `reports/audit-project-3.md`.

- [ ] Auditar cada projeto contra o template e o catálogo, validar caminhos e linhas atuais, registrar stack, domínio, contagem e achados ordenados.
- [ ] Confirmar ao menos cinco achados por projeto e pelo menos um CRITICAL/HIGH em cada.
- [ ] Registrar os comandos de baseline/teste/boot existentes e separar findings iniciais dos resultados pós-refatoração.

### Task 3: Project 1 — code-smells-project

**Files:** Refactor `projects/code-smells-project/`; add tests in that project's `tests/`.

- [ ] Escrever testes de contrato para health, listagem, auth, produtos e bloqueio de `/admin/query`; validar que falham ou demonstram comportamento inseguro no baseline.
- [ ] Extrair config, repository/models, controllers, views/routes, app factory e error handling.
- [ ] Substituir `/admin/query` por resposta 410 e restringir reset; retirar segredo/DEBUG de health e entry point.
- [ ] Executar testes, inicializar app com SQLite temporário e validar endpoints originais.

### Task 4: Project 2 — ecommerce-api-legacy

**Files:** Refactor `projects/ecommerce-api-legacy/`; add tests in that project's `test/`.

- [ ] Escrever testes de rota para relatório, checkout válido/inválido e exclusão do usuário.
- [ ] Separar configuração, repositório SQLite, controller e routes/app factory; usar transação para checkout e remover logs de cartão/secrets.
- [ ] Executar a suíte, iniciar o servidor e verificar os endpoints originais com banco efêmero/in-memory.

### Task 5: Project 3 — task-manager-api

**Files:** Refactor `projects/task-manager-api/`; add tests in that project's `tests/`.

- [ ] Escrever testes de contratos para health, usuários/tasks, relatórios e endpoints inválidos.
- [ ] Extrair config/app factory, controllers/services e handlers de erro; trocar secrets por ambiente, corrigir APIs deprecated e remover N+1 do relatório.
- [ ] Executar a suíte, inicializar app com SQLite temporário e validar rotas existentes.

### Task 6: Final delivery

**Files:** Update root `README.md`, reports and validation evidence.

- [ ] Atualizar README para esclarecer cópias por projeto, relatórios, estrutura refatorada e comandos reais de validação.
- [ ] Executar testes locais disponíveis e `git diff --check`; confirmar as três cópias skill idênticas.
- [ ] Inspecionar diff para excluir dados gerados/secrets e publicar commit na branch `main`.
