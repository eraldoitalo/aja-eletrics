# Rastreabilidade e validação

Validação executada em 22/10/2026 com Python 3.14.3, Django 5.2.18 e PostgreSQL 16.13. Resultado: **31 testes aprovados**. Não foi usado SQLite.

| Requisito | Implementação | Evidência automatizada |
|---|---|---|
| Entrada exclusiva do administrativo | Serviço e formulário de veículo | Permissão e criação de unidade |
| Sigilo de Compra | Acquisition e rota restrita; contexto por perfil | Ausência de custo no HTML, acesso direto e injeção de campos rejeitados |
| Unidade física e catálogo comercial | Origem, condição, situação e descrição | Catálogo disponível, externo excluído e condição preservada |
| Venda única vinculada ao cliente | Transação, bloqueio da unidade e Sale única | Unicidade no banco; duas conexões simultâneas, só uma venda |
| Entrada sem custo negativo | Validação e transação da entrada | Custo negativo rejeitado sem deixar veículo parcial |
| Histórico e atendimento de motos vendidas | Relacionamentos de cliente, veículo, venda e OS | Histórico e OS sem alterar situação vendida |
| Oficina de terceiros | Origem Oficina | Veículo externo não vendável |
| Atribuição de mecânico | Filtro e verificação na OS | Acesso de outro mecânico negado |
| Checklist e diagnóstico | Snapshot e regras por etapa | Pré-requisitos do orçamento e conclusão obrigatória |
| Aprovação anterior à execução | Orçamento versionado e decisão documentada | Aprovação antiga recusada, recusa e execução bloqueada sem aprovação |
| Peças registradas na OS | PartUsage do orçamento aprovado | Limite de quantidade e vínculo com orçamento |
| Encerramento e cancelamento | Transições autorizadas e motivo | Fluxo completo, imutabilidade final e cancelamento administrativo |
| Dashboard administrativo | Agregações no PostgreSQL | Restrição de perfil, limites temporais em São Paulo e última versão de orçamento |
| Segurança web | CSRF, escape, logout POST e redirecionamento seguro | CSRF inválido, HTML escapado, logout GET rejeitado e tema sem redirecionamento externo |
| Proteção de login | LoginThrottle compartilhado no banco | Limite por combinação email/IP |
| Páginas operacionais | Templates HTML renderizados | Rotas principais sem erro de renderização |

Comando executado: `.venv\Scripts\python.exe manage.py test erp.tests --verbosity 1`. Django cria e destrói o banco de testes. O teste de concorrência usa conexões independentes e barreira entre threads, não uma simulação do bloqueio.

Também foram executados `manage.py check`, aplicação das migrações e coleta de arquivos estáticos. A interface foi aberta no navegador com base temporária e dados fictícios; esses dados não acompanham o pacote e não foram inseridos no banco principal.

## Limites da evidência

O ambiente web completo do Docker ainda exige validação de build e inicialização: o pipe Docker estava inacessível à automação. O PostgreSQL real estava disponível por TCP e foi usado em todos os testes de banco. Não foram executados testes de carga, pentest independente, restauração de backup de produção ou homologação com a equipe da empresa. A verificação automatizada não substitui validação dos procedimentos técnicos da oficina.

## Homologação sugerida

1. Criar um usuário de cada perfil e uma moto fictícia, verificando o custo apenas no administrativo.
2. Efetuar uma venda fictícia e conferir cliente, situação e dashboard.
3. Cadastrar veículo externo e abrir OS; completar checklist e diagnóstico.
4. Criar orçamento, registrar recusa, revisar e aprovar a versão atual.
5. Iniciar execução, registrar peças, concluir checklist, marcar pronta e encerrar.
6. Validar nomes de campos, checklists e indicadores com usuários reais antes da importação.

A rotina de integração contínua em `.github/workflows/tests.yml` reproduz os testes com PostgreSQL 16. O arquivo está pronto para publicação, mas não houve execução no GitHub nesta entrega.
