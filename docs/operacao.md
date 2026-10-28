# Operação e manutenção

## Credenciais e usuários

`scripts/configurar.py` gera `.env` com chave Django e senha PostgreSQL aleatórias, preservando configuração existente. O arquivo não acompanha a entrega. Não o publique no GitHub. Não existem contas padrão. Use `createsuperuser` para a primeira conta e o Django Admin para cadastrar os perfis da equipe. Desative contas antigas pelo campo Ativo.

O sistema limita falhas de login. Se ultrapassar o limite, aguarde quinze minutos para tentar novamente. Não compartilhe contas entre funcionários: as ações são associadas ao usuário autenticado.

## Backup local usando Compose

Crie a pasta de destino antes. Exemplo no PowerShell, sem expor a senha no comando:

```powershell
New-Item -ItemType Directory -Force backups
docker compose exec db sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc -f /tmp/aja-backup.dump'
docker compose cp db:/tmp/aja-backup.dump ./backups/aja-backup.dump
```

Use nomes datados para não sobrescrever cópias anteriores. Guarde backups fora do computador e restrinja o acesso: contêm clientes e custos. O volume persistente não substitui backup.

Para verificar uma restauração, crie um banco separado de homologação e use `pg_restore` nele; nunca aponte comandos de restauração para o banco principal sem procedimento validado. Planeje frequência, retenção e teste de recuperação com o responsável técnico. Não foi executada restauração nesta entrega.

## Atualizações

Antes de atualizar, faça backup e preserve `.env`. Revise mudanças e dependências, execute os testes num banco isolado e aplique migrações. Com Docker, `docker compose up --build -d` reconstrói a aplicação; a inicialização aplica migrações e coleta estáticos. Em produção com múltiplas réplicas, execute migrações como etapa de implantação única.

## Antes de publicar na internet

- Configurar domínio e HTTPS, `DJANGO_DEBUG=False`, hosts explícitos, origens CSRF e cookies seguros.
- Definir HTTPS no proxy e revisar os cabeçalhos encaminhados antes de habilitar redirecionamento SSL. O exemplo não confia automaticamente em cabeçalhos de proxy.
- Executar `python manage.py check --deploy` com o ambiente de produção e resolver os avisos aplicáveis.
- Usar banco com acesso privado, credenciais próprias, backup externo e privilégios mínimos. Permissão de criar banco é necessária para testes, não para o usuário comum da aplicação em produção.
- Configurar monitoramento de erros e disponibilidade, limitação de acesso no proxy e rotina de atualização de segurança.
- Validar regras pendentes e tratamento de dados pessoais com os responsáveis da empresa.

## Diagnóstico local

`docker compose logs --tail 100 web` mostra falhas de inicialização. `docker compose ps` mostra a saúde dos serviços. Se o navegador não abre, confira Docker Desktop, porta 8000 e criação do superusuário. No modo Python local, mantenha o PowerShell com `runserver` aberto. Esse servidor é destinado a desenvolvimento.
