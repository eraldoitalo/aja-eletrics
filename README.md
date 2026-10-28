# AJA Eletrics · Django

Cópia independente do ERP e da oficina, desenvolvida em **Python/Django, HTML/CSS e PostgreSQL**. A interface usa templates renderizados no servidor, tema claro/escuro e navegação responsiva. Não precisa de Node, React ou npm.

## Executar no Windows com Docker Desktop

Extraia o ZIP, abra o PowerShell na pasta que contém `manage.py` e mantenha o Docker Desktop iniciado. É necessário Python 3.12 ou superior para gerar a configuração inicial.

```powershell
python scripts/configurar.py
docker compose up --build -d
docker compose exec web python manage.py createsuperuser
```

Informe seu email e uma senha com pelo menos 12 caracteres. A senha não aparece enquanto você digita. Abra **http://127.0.0.1:8000** e entre com essas credenciais. O sistema inicia vazio; não há senha padrão nem importação automática da planilha.

Para criar os demais usuários, acesse **http://127.0.0.1:8000/admin/** com o superusuário e escolha o perfil Administrativo, Vendedor ou Mecânico. Deixe os campos `is_staff` e `is_superuser` desmarcados para os usuários operacionais. Somente superusuários gerenciam contas nessa área técnica; os administrativos comuns usam o ERP normalmente.

Para parar e iniciar novamente:

```powershell
docker compose stop
docker compose start
```

O banco fica no volume Docker `aja_postgres`. Preserve esse volume e o arquivo `.env`. Não use `docker compose down -v` se quiser manter os dados. Alterar a senha do `.env` depois da criação do banco não altera automaticamente a senha dentro do PostgreSQL.

## Desenvolvimento com Python local e PostgreSQL no Docker

Esta foi a combinação validada nesta entrega. No PowerShell, dentro da pasta do projeto:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts/configurar.py
docker compose up -d db
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py createsuperuser
.\.venv\Scripts\python.exe manage.py runserver
```

Não é necessário ativar o ambiente virtual nem alterar a política de execução do PowerShell. Caso o comando `python` não exista, instale Python e reabra o terminal. Caso a porta 5433 esteja ocupada, ajuste `POSTGRES_PORT` no `.env` antes de iniciar o banco. Não inicie simultaneamente o servidor local e o serviço `web` na mesma porta 8000.

## Funcionalidades

- Entrada de veículos exclusivamente administrativa, com condição novo/seminovo, ficha técnica e custo de aquisição separado.
- Catálogo de unidades disponíveis e registro de venda vinculado ao cliente, protegendo contra duas vendas da mesma unidade.
- Clientes e histórico de vendas e atendimentos.
- Oficina com OS, mecânico responsável, checklists de entrada/saída, diagnóstico, orçamento versionado e registro de aprovação ou recusa do cliente.
- Execução autorizada, registro de peças previstas no orçamento e encerramento da OS.
- Dashboard administrativo com vendas semanais/mensais, modelos mais vendidos e serviços mais realizados.

O custo de compra exige autorização no servidor. Não é enviado nas páginas dos vendedores ou mecânicos. Os mecânicos acessam somente as OS atribuídas a eles. Veículos externos são cadastrados pelo administrativo com origem Oficina e não aparecem como estoque disponível para venda.

## Documentação e testes

- [Análise de caso e escopo](docs/analise-de-caso.md)
- [Arquitetura e modelo de dados](docs/arquitetura.md)
- [Requisitos, implementação e testes](docs/rastreabilidade-e-testes.md)
- [Operação, backup e implantação](docs/operacao.md)
- [Requisitos históricos reaproveitados](docs/requisitos/)

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\.venv\Scripts\python.exe manage.py test erp.tests --verbosity 2
```

Os testes usam PostgreSQL real e criam um banco temporário `test_aja_eletrics`; o usuário do banco precisa de permissão `CREATEDB`. Nunca execute os testes apontando para credenciais de produção. O relatório registra 31 testes aprovados em PostgreSQL 16.13 e Python 3.14.3. O build completo do contêiner web está preparado, mas não foi executado nesta máquina: o ambiente de automação não tinha acesso ao pipe do Docker. O banco Docker foi iniciado pelo proprietário e validado por conexão PostgreSQL.

## Limites desta versão

Esta é uma base funcional para desenvolvimento e homologação. A categoria Garantia existe na OS; o processo completo de análise de garantia ainda precisa ser especificado. Também ficam pendentes reservas e cancelamento de venda, recebimentos, emissão fiscal, estoque de peças, anexos de aprovação, importação da planilha e modelos de checklist técnico configuráveis. O checklist inicial tem três itens de processo e deve ser validado pela oficina.

Os gráficos financeiros representam valores de vendas confirmadas de motos, sem recebimentos ou receita da oficina. A definição de faturamento consolidado ainda precisa ser aprovada. Consulte a análise de caso antes de usar indicadores para decisões financeiras.

O projeto original permanece separado. Esta cópia não migra automaticamente contas ou dados do sistema anterior e não foi publicada no GitHub.
