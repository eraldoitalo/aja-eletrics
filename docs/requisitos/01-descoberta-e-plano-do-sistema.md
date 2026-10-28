# Sistema para empresa de motos elétricas

Data de início: 20/10/2026  
Versão: 0.2 — operação inicial identificada

## Situação atual

O objetivo confirmado é criar um sistema novo, cobrindo requisitos, documentação, design, testes e aplicação. A empresa trabalha com venda de motos e pós-venda, e o sistema será utilizado pela equipe interna. Existe uma planilha de estoque com uma moto física por linha e informações como nome, preço e cor. Na venda, a linha recebe o status de vendida. O pós-venda deverá contemplar manutenção, revisões e garantia. As demais regras e as tecnologias permanecem em definição.

## Resultado esperado

Entregar uma aplicação utilizável para os processos prioritários da empresa, acompanhada de documentação e evidências de testes. Os critérios de sucesso serão definidos a partir dos problemas reais da operação.

## 1. Descoberta do negócio

Perguntas iniciais:

- A empresa vende, aluga, oferece assinatura, opera frotas, fabrica ou combina essas atividades?
- Qual problema precisa ser resolvido primeiro? Como ele é tratado hoje?
- Quem usa o sistema: equipe interna, clientes, oficinas, concessionárias ou outros parceiros?
- Existem planilhas, sistemas, documentos e dados que precisam ser aproveitados?

Perguntas para aprofundar após a definição inicial:

- Quais são os passos do processo prioritário, do início ao encerramento?
- Quais exceções são frequentes e quem pode autorizá-las?
- Quantas unidades, usuários e motos serão atendidos inicialmente?
- Há necessidade de uso por celular, funcionamento sem internet ou acompanhamento em tempo real?
- Quais integrações são necessárias e quais fornecedores já foram contratados?
- Qual é a primeira data desejada para uso e quais são as restrições de orçamento?

Entregáveis: visão do produto, mapa dos processos, perfis de usuários, problemas prioritários e indicadores de sucesso.

Critério para avançar: identificar o primeiro processo completo que a aplicação deverá atender.

## 2. Requisitos e escopo da primeira versão

Cada requisito terá identificador, origem, prioridade, regra de negócio, critério de aceite e relação com os testes.

Modelo:

| Campo | Conteúdo esperado |
|---|---|
| Identificador | RF-001, RN-001 ou RNF-001 |
| Necessidade | O que o usuário precisa fazer e com qual finalidade |
| Perfil | Quem executa a ação |
| Pré-condições | O que precisa ser verdadeiro antes da ação |
| Fluxo e exceções | Comportamento normal e situações de falha |
| Critérios de aceite | Resultados observáveis que demonstram atendimento |
| Prioridade | Essencial para a primeira versão ou posterior |
| Validação | Caso de teste associado |

Separar requisitos funcionais, regras de negócio e requisitos de qualidade. Definir metas mensuráveis para desempenho, disponibilidade, recuperação de dados e acessibilidade conforme o contexto da operação.

Entregáveis: catálogo de requisitos, regras, matriz de permissões e escopo da primeira versão, incluindo o que fica para depois.

Critério para avançar: ter critérios de aceite verificáveis para os fluxos prioritários.

## 3. Experiência e design de interface

Mapear jornadas e navegação antes de detalhar telas. Criar fluxos, wireframes e protótipo dos processos principais. Incluir estados vazios, carregamento, erros, validações e restrições de acesso.

Definir componentes, tipografia, cores e comportamento responsivo a partir da marca e dos dispositivos utilizados.

Entregáveis: mapa de navegação, protótipo e biblioteca inicial de componentes.

Critério para avançar: verificar os fluxos com cenários reais e usuários representativos, quando disponíveis.

## 4. Arquitetura e dados

Escolher tecnologias após conhecer os requisitos e as restrições. Registrar as decisões com suas justificativas e consequências.

Definir modelo de dados, estados das entidades, contratos de integração, autenticação, autorização, trilha de auditoria, armazenamento, backup, recuperação e ambientes de execução.

Entregáveis: diagramas, dicionário de dados, contratos de API e registros de decisões de arquitetura.

Critério para avançar: demonstrar que a arquitetura atende aos fluxos e requisitos de qualidade da primeira versão.

## 5. Estratégia de testes

Os critérios de aceite serão definidos junto dos requisitos. A automação dos testes acompanhará a implementação.

- Testes de unidade para regras de negócio relevantes.
- Testes de integração para persistência e comunicação entre serviços.
- Testes de ponta a ponta para jornadas críticas.
- Verificação de permissões, validação de entradas e isolamento de dados, conforme o modelo de operação.
- Verificação de acessibilidade e uso nos dispositivos definidos.
- Testes de carga, backup e recuperação conforme as metas acordadas.
- Homologação com cenários da empresa e dados de teste sem informações pessoais reais.

Entregáveis: plano de testes, casos rastreáveis aos requisitos e evidências dos resultados.

## 6. Implementação e entrega

Implementar em incrementos que permitam executar processos completos. Cada incremento deve incluir código, testes pertinentes e atualização da documentação.

Preparar configuração, migrações de dados, monitoramento, manual de operação e procedimento de implantação e reversão.

Critério de conclusão da primeira versão: fluxos essenciais funcionando, critérios de aceite atendidos, testes pertinentes aprovados e instruções suficientes para executar e operar a aplicação.

## Hipóteses a investigar

As possibilidades abaixo servem apenas para orientar a descoberta:

- Cadastro e identificação de motos e baterias.
- Vendas, locações ou assinaturas, conforme a operação.
- Estoque, manutenção, garantia e assistência.
- Controle de contratos, cobranças e entregas.
- Telemetria e localização, se houver equipamentos e integração disponíveis.
- Indicadores operacionais e financeiros, conforme a necessidade.

## Registro de decisões

| ID | Decisão | Situação |
|---|---|---|
| D-001 | Construir requisitos, documentação, design, testes e aplicação | Confirmada pelo pedido inicial |
| D-002 | Operação de venda e pós-venda; sequência de implementação a definir | Operação confirmada |
| D-003 | Uso pela equipe interna; dispositivos e canais a definir | Público confirmado |
| D-004 | Tecnologias, integrações e hospedagem | Em aberto |
| D-005 | Uma moto física por linha na planilha; venda registrada por status | Confirmada |
| D-006 | Pós-venda com manutenção, revisões e garantia | Confirmada |
| D-007 | COMPRA é custo por unidade, acessível apenas a usuários administrativos; acesso negado a vendedores e mecânicos | Confirmada |
| D-008 | Planilha examinada em leitura; dicionário e restrição detalhados em 03-dados-e-permissoes.md | Documentada |
| D-009 | Integrar estoque e oficina com checklists, ordens de serviço e clientes vinculados aos serviços | Confirmada em 21/10/2026 |
| D-010 | Atender motos da empresa e de outros clientes | Confirmada em 21/10/2026 |
| D-011 | Exigir orçamento e aprovação do cliente antes de executar serviços cobrados | Confirmada em 21/10/2026 |
| D-012 | Registrar peças na OS sem controle de estoque de peças na primeira versão | Confirmada em 21/10/2026 |
| D-013 | Entrada de veículos no estoque exclusiva do administrativo | Confirmada em 21/10/2026 |
| D-014 | Novo/seminovo e descrição técnica no cadastro; vendedores consultam todos os disponíveis sem custo | Confirmada em 21/10/2026 |
| D-015 | Dashboard exclusivo do administrativo com faturamento semanal/mensal, motos vendidas, modelos mais vendidos e serviços mais realizados | Confirmada em 21/10/2026 |

## Próximo passo

Detalhar a proposta em 02-visao-e-requisitos-iniciais.md, verificar os campos da planilha e definir os fluxos de venda e atendimento. Não tratar as hipóteses deste documento como requisitos confirmados.
