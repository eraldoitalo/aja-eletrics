# Visão e requisitos iniciais

Versão: 0.4 — entrada administrativa de estoque, descrição técnica e dashboard incluídos

## Base confirmada

- Negócio: venda de motos elétricas e pós-venda.
- Público: equipe interna.
- Fonte atual de estoque: planilha com uma moto física por linha.
- Campos examinados: ID, Nome, COR, Ano, KM, Preço, Condição, STATUS, Coluna 9, DATA VENDA, OBS, VALOR_VENDA, VENDEDOR e COMPRA.
- Processo atual de venda: atualizar o status da linha para vendida.
- Pós-venda desejado: manutenção, revisões e garantia.
- Escopo confirmado em 21/10/2026: controle de estoque integrado a sistema de oficina com checklists, ordens de serviço e clientes vinculados aos serviços.
- A oficina atenderá motos da empresa e de outros clientes. Serviços cobrados exigirão orçamento e aprovação. Peças serão registradas na OS, sem controle de saldo na primeira versão.
- Apenas administrativo inclui veículos no estoque e preenche seus dados de entrada. Vendedores consultam todos os disponíveis com descrição técnica, sem custo de aquisição.
- O cadastro distingue novo/seminovo da situação comercial. O dashboard com faturamento semanal/mensal, unidades e modelos mais vendidos e serviços mais realizados é exclusivo do administrativo.

A planilha foi recebida e examinada em leitura. O usuário confirmou que COMPRA representa o custo de aquisição de cada unidade e só pode ser acessado por usuários administrativos. Vendedores e mecânicos não podem acessar esse campo. Essa restrição está confirmada; os demais requisitos abaixo continuam como propostas, salvo os fatos indicados na base confirmada. O detalhamento da importação e da proteção está em 03-dados-e-permissoes.md.

## Visão proposta

Permitir que a equipe acompanhe cada moto desde a entrada no estoque até a venda e o atendimento pós-venda, preservando seu histórico.

Primeira versão proposta: estoque, clientes, vendas e um fluxo completo de oficina com ordem de serviço, checklist e histórico. A entrega pode ocorrer em incrementos, mantendo a oficina como parte do escopo principal. O detalhamento está em 04-oficina-e-pos-venda.md.

## Conceitos do domínio

| Conceito | Significado proposto | Pontos a definir |
|---|---|---|
| Modelo | Características compartilhadas por várias motos | Se o campo nome atual identifica modelo ou unidade |
| Unidade de moto | Uma moto física, com identificação própria; a planilha possui ID | Relação do ID com chassi ou número de série |
| Cliente | Pessoa ou empresa relacionada a uma venda ou atendimento | Dados necessários e situações de troca de proprietário |
| Venda | Registro da negociação de uma unidade | Pagamento, desconto, cancelamento e momento da baixa |
| Atendimento | Registro de manutenção, revisão ou avaliação de garantia | Etapas, responsáveis, peças e custos |
| Garantia | Condições e histórico de análise de cobertura | Prazos, cobertura, documentação e autoridade de decisão |

A planilha já separa Preço, VALOR_VENDA e COMPRA. O modelo proposto mantém essa separação: preço anunciado, valor efetivo da venda e custo de aquisição restrito. Alterações futuras no preço de estoque não devem reescrever vendas anteriores.

## Fluxos propostos

1. Estoque: cadastrar ou importar uma unidade → consultar e conferir seus dados → corrigir dados com histórico da alteração.
2. Venda: selecionar uma unidade disponível → informar cliente e condições → confirmar a venda → atualizar o status da unidade e manter vínculo com a venda.
3. Pós-venda: localizar a moto → abrir atendimento → registrar diagnóstico e serviços → tratar eventual garantia → concluir com histórico acessível.

Reserva, entrega, devolução e cancelamento precisam de regras próprias caso existam na operação. A confirmação da venda como momento da baixa é uma hipótese, ainda a validar.

## Catálogo inicial e critérios de aceite

As capacidades de estoque, oficina, checklists, ordens de serviço e cadastro de clientes estão confirmadas como escopo. Os critérios detalhados continuam propostos, exceto pela restrição de custo explicitamente confirmada. Os testes listados são cenários planejados, ainda não executados.

| ID | Requisito proposto | Critério de aceite inicial | Teste |
|---|---|---|---|
| RF-001 | Consultar estoque por unidade, com filtros de nome/modelo, cor e status | Ao aplicar um filtro, listar apenas as unidades correspondentes e permitir abrir seus detalhes | CT-001: combinar filtros e conferir resultados |
| RF-002 | Cadastrar unidade com acesso exclusivo do administrativo; permissões de edição posterior a definir | Salvar campos válidos; impedir ID repetido e cadastro por outros perfis | CT-002 e CT-037 |
| RF-003 | Importar a planilha com conferência prévia | Mostrar mapeamento, linhas válidas e erros antes de gravar; informar o resultado e impedir duplicação ao repetir a importação | CT-003: importar arquivo com duplicidade e preço inválido; repetir importação |
| RF-004 | Registrar a venda vinculada à unidade e ao cliente | Ao confirmar, preservar valor e data da venda e atualizar o status da unidade sem apagar seu cadastro | CT-004: vender e consultar histórico e estoque |
| RF-005 | Impedir vendas simultâneas da mesma unidade | Duas confirmações concorrentes para a mesma moto permitem apenas uma venda ativa | CT-005: confirmar duas vendas concorrentes |
| RF-006 | Consultar histórico da moto | Exibir venda e atendimentos vinculados à unidade selecionada | CT-006: conferir histórico de duas motos distintas |
| RF-007 | Abrir e acompanhar manutenção e revisão | Registrar moto, solicitação, responsável, andamento e conclusão; manter o histórico consultável | CT-007: abrir, atualizar e concluir atendimento |
| RF-008 | Registrar análise de garantia | Registrar solicitação, documentação, decisão, justificativa e responsável; não presumir cobertura automática | CT-008: registrar aprovação e negativa em solicitações diferentes |
| RF-009 | Controlar acesso por usuário e função | Permitir operações autorizadas e rejeitar tentativas diretas de operações restritas | CT-009: tentar alterar preço com perfil sem permissão |
| RF-010 | Registrar alterações relevantes | Identificar autor, data e valores anterior e novo em mudanças de preço e status | CT-010: alterar preço e conferir registro |
| RF-011 | Restringir acesso ao custo de aquisição a usuários administrativos (confirmado) | Vendedores e mecânicos não recebem nem alteram COMPRA por telas, API, exportações, relatórios ou históricos | CT-011 a CT-018 em 03-dados-e-permissoes.md |
| RF-012 | Cadastrar clientes e vincular seus atendimentos | Ao abrir um cliente, consultar suas ordens de serviço e respectivas motos | CT-019 em 04-oficina-e-pos-venda.md |
| RF-013 | Emitir e acompanhar ordens de serviço | Cada OS identifica cliente, moto, solicitação, responsável, serviços e andamento | CT-020 e CT-021 em 04-oficina-e-pos-venda.md |
| RF-014 | Fornecer checklists por atendimento | Preenchimentos pertencem à OS e preservam a versão aplicada | CT-022 e CT-023 em 04-oficina-e-pos-venda.md |
| RF-015 | Atender motos externas (escopo confirmado) | Cadastro para atendimento não cria unidade disponível no estoque comercial | CT-029 |
| RF-016 | Registrar orçamento e aprovação antes de serviço cobrado (confirmado) | Execução exige aprovação da versão que contém o serviço; revisões preservam decisões anteriores | CT-030 a CT-034 e CT-036 |
| RF-017 | Registrar peças na OS, sem estoque de peças nesta versão (confirmado) | Registrar peças previstas e utilizadas sem movimentação de saldo | CT-035 |
| RF-018 a RF-022 | Entrada administrativa, condição novo/seminovo, descrição técnica, consulta dos disponíveis e dashboard exclusivo do administrativo | Especificação em 05-estoque-catalogo-e-dashboard.md | CT-037 a CT-044 no mesmo documento |

## Regras propostas

- RN-001: uma unidade possui um identificador interno estável; sua associação com chassi ou série dependerá dos dados existentes.
- RN-002: duas motos do mesmo modelo e cor continuam sendo unidades distintas.
- RN-003: uma unidade não pode ter duas vendas ativas ao mesmo tempo.
- RN-004: o histórico da moto permanece acessível depois da venda.
- RN-005: preço anunciado e valor negociado usam valores monetários com precisão definida, sem valores negativos.
- RN-006: cancelamentos devem preservar rastreabilidade; suas condições e efeito no estoque serão definidos com a empresa.
- RN-007: prazo e cobertura de garantia não serão presumidos; dependem das condições aplicáveis ao produto e da operação.

## Qualidade e operação a dimensionar

| Tema | Direção proposta | Informação necessária |
|---|---|---|
| Acesso | Autenticação individual e permissões verificadas no servidor | Funções e responsabilidades da equipe |
| Recuperação | Backups e procedimento de restauração testado | Perda de dados e tempo de parada toleráveis |
| Desempenho | Metas mensuráveis para consulta e gravação | Volume de motos e acessos simultâneos |
| Interface | Uso claro nos dispositivos da equipe, com mensagens de erro e navegação acessível | Computadores, celulares e condições de conexão |
| Dados | Coletar dados necessários e definir acesso, retenção e exclusão | Dados de clientes e documentos utilizados |

## Estrutura de telas sugerida

- Estoque: consulta de disponíveis para vendedores; cadastro/importação exclusivos do administrativo; condição novo/seminovo separada da situação comercial.
- Detalhe da moto: identificação, preço, cor e histórico de venda e atendimentos.
- Vendas: registros e formulário de nova venda vinculada à unidade.
- Clientes: cadastro e histórico de vendas, motos e ordens de serviço conforme as permissões.
- Oficina: fila de ordens de serviço e detalhe com checklists, diagnóstico, serviços e análise de garantia.
- Administração: usuários e permissões.
- Dashboard: indicadores e gráficos de vendas, faturamento e serviços, exclusivo do administrativo.

Estão confirmadas as permissões sobre custo, entrada de estoque, consulta comercial dos vendedores e exclusividade administrativa do dashboard. As demais permissões estão em definição. Detalhes em 03-dados-e-permissoes.md, 04-oficina-e-pos-venda.md e 05-estoque-catalogo-e-dashboard.md.

## Limites desta proposta

Não há implementação, protótipo ou testes executados nesta etapa. Estoque de peças fica fora da primeira versão por decisão do usuário; o registro de peças na OS está incluído. Integrações fiscais, pagamentos, contabilidade, telemetria e mensagens externas ainda não possuem requisitos definidos e não entram na estimativa da primeira versão por enquanto.

## Próximas definições

1. Resolver os status vazios, o significado de devolução e os detalhes de importação descritos em 03-dados-e-permissoes.md.
2. Definir o caminho real da venda: reserva, pagamento, entrega, baixa e cancelamento.
3. Definir o atendimento: execução interna ou externa, responsáveis e documentos de garantia.
4. Dimensionar equipe e estoque para propor arquitetura e metas de qualidade.
