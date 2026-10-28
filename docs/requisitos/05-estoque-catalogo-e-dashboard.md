# Estoque, consulta comercial e dashboard administrativo

Versão: 0.1 — 21/10/2026

## Decisões confirmadas

- Apenas usuários administrativos podem incluir um novo veículo no estoque e preencher os dados de entrada.
- O veículo deve ter classificação novo ou seminovo, denominada status pelo usuário.
- O cadastro terá descrição com informações da ficha técnica para auxiliar os vendedores.
- Vendedores poderão consultar todos os veículos disponíveis para venda, sem acesso ao custo de aquisição.
- Haverá uma aba de dashboard exclusiva de usuários administrativos, com gráficos de faturamento semanal e mensal, quantidade de motos vendidas, motos mais vendidas e tipos de serviços mais realizados.

Os detalhes abaixo são propostas de especificação para implementar essas decisões. Não há implementação nem testes executados nesta etapa.

## Classificação e disponibilidade

Manter duas informações independentes:

| Informação | Valores | Exemplo |
|---|---|---|
| Status de condição | Novo ou seminovo | Moto seminova |
| Situação comercial | Disponível, vendida e demais situações a definir | Moto seminova disponível |

O status novo/seminovo não permite concluir que a moto está disponível para venda. O andamento da oficina também permanece separado dessas duas informações.

Na migração, a coluna Condição será candidata ao status novo/seminovo e a coluna STATUS à situação comercial. A correspondência dos valores deve ser conferida, sem converter status vazios em disponível. Os campos da planilha original permanecem intactos.

## Cadastro de entrada proposto

| Grupo | Campos |
|---|---|
| Identificação | Código interno único, marca, modelo/nome e chassi ou número de série quando disponível |
| Características da unidade | Cor, ano, quilometragem e status novo/seminovo |
| Entrada | Data de entrada, situação comercial e responsável pelo cadastro |
| Valores | Preço anunciado e custo de aquisição, com visibilidade independente |
| Apoio à venda | Descrição técnica e observações comerciais próprias da unidade |

Obrigatoriedade de chassi/série, marca e data histórica de entrada precisa ser definida antes da migração. Dados desconhecidos não serão inventados. Registro incompleto pode ficar como rascunho administrativo, se esse fluxo for adotado, sem aparecer automaticamente como disponível.

A descrição poderá apresentar potência, bateria, autonomia informada, tempo de recarga, dimensões e outros dados pertinentes, quando fornecidos pela empresa. Não inventar especificações nem presumir que características de um modelo valem para todas as unidades.

Proposta de modelagem: ficha técnica comum ao modelo e observações específicas por unidade, apresentadas juntas ao vendedor. A empresa ainda pode optar por uma descrição única por veículo.

A descrição comercial será separada de observações administrativas. Custos, margens e documentos de compra não podem ser incluídos no conteúdo destinado aos vendedores.

## Acesso e consulta comercial

| Operação | Administrativo | Vendedor | Mecânico |
|---|---|---|---|
| Incluir veículo no estoque | Permitido (confirmado) | Negado (confirmado) | Negado (confirmado) |
| Importar veículos para estoque | Permitido, sujeito às validações | Negado | Negado |
| Informar custo na entrada | Permitido no cadastro administrativo | Negado | Negado |
| Consultar disponíveis e descrição técnica | Permitido | Permitido (confirmado) | A definir |
| Consultar custo de aquisição | Permitido | Negado | Negado |
| Abrir dashboard e consultar seus dados | Permitido (confirmado) | Negado (confirmado) | Negado (confirmado) |
| Alterar cadastro após entrada | Proposta: administrativo | A definir; sem permissão por padrão | A definir; sem permissão por padrão |

A exclusividade de cadastro em estoque não decide quem cadastra motos externas para oficina. Esse cadastro será independente e jamais criará estoque comercial por consequência automática.

Consulta comercial proposta: lista ou cartões com modelo, cor, ano, quilometragem, novo/seminovo e preço anunciado; detalhe com descrição técnica. Filtros por esses campos e busca por código/modelo. Todos os veículos comercialmente disponíveis devem ser acessíveis ao vendedor, independentemente do responsável pelo cadastro.

Não incluir veículos externos de oficina ou unidades vendidas no resultado de disponíveis. Antes de confirmar uma venda, validar novamente a disponibilidade no servidor.

## Dashboard exclusivo do administrativo

Todos os gráficos terão período explícito, unidades, legenda e opção de consultar os registros de origem autorizados. A tela e as APIs de indicadores exigirão perfil administrativo. Ocultar a aba não substitui a autorização no servidor.

| Indicador confirmado | Visual proposto | Definição proposta |
|---|---|---|
| Faturamento semanal | Colunas por semana | Somar valores efetivos dos eventos comerciais válidos, conforme a regra de faturamento a confirmar |
| Faturamento mensal | Colunas por mês | Mesma base e regra do semanal, agrupadas por mês |
| Quantidade de motos vendidas | Cartão e série temporal | Contar unidades com venda válida no período, sem duplicar registros |
| Motos mais vendidas | Barras por modelo | Ordenar modelos pela quantidade de unidades vendidas no período |
| Tipos de serviços mais realizados | Barras por tipo de serviço | Contar itens de serviço concluídos por tipo e data de conclusão; peças não contam como serviços |

Antes de implementar faturamento, confirmar se o usuário quer acompanhar vendas realizadas, valores recebidos ou ambos. Também definir inclusão de oficina e peças cobradas, datas de referência, descontos, cancelamentos, devoluções e eventuais estornos. Não misturar essas bases em uma única série sem identificação.

Proposta inicial de calendário: fuso America/Sao_Paulo, semanas de segunda a domingo e meses civis. Identificar períodos ainda em andamento e comparar intervalos equivalentes. Mostrar data/hora de atualização.

Rankings devem usar cadastros de modelo e de serviço padronizados, evitando que variações de escrita dividam os resultados. Definir quantidade de posições exibidas e tratamento de empates.

### Indicadores adicionais sugeridos

- Disponíveis por modelo e por novo/seminovo.
- Tempo em estoque desde a entrada, apenas quando houver data conhecida.
- Valor médio de venda por moto, calculado sobre vendas válidas.
- OS abertas por etapa e tempo de atendimento.
- Percentual de aprovação de orçamentos, definindo a população de propostas e evitando contar versões como clientes distintos.
- Atendimentos com solicitação de garantia e resultados das análises.

Esses indicadores adicionais são sugestões, ainda não confirmadas. Lucro líquido não será calculado somente a partir do custo de compra da moto, pois faltam outras despesas e regras.

## Qualidade dos dados históricos

Os dados da planilha permitem iniciar análise de estoque e vendas após validação. O dashboard não pode preencher lacunas com valores inventados: datas ou valores de venda ausentes devem aparecer como pendências de qualidade dos dados. Registros sem data não entram silenciosamente em uma semana ou mês arbitrário.

O ranking de serviços começará a ser formado pelos atendimentos registrados no sistema; não há histórico de serviços confirmado na fonte atual. Distinguir zero ocorrências de período sem cobertura de dados.

## Requisitos e testes planejados

| Requisito | Critério de aceite | Teste |
|---|---|---|
| RF-018: entrada de estoque exclusiva do administrativo | Cadastro e importação negados a vendedores e mecânicos, inclusive por chamada direta | CT-037: tentar criar/importar com cada perfil; apenas administrativo autorizado consegue |
| RF-019: classificar novo/seminovo independentemente de disponibilidade | Venda não apaga nem altera a classificação de condição | CT-038: vender moto seminova; mantém condição e muda situação comercial |
| RF-020: descrição técnica e consulta dos disponíveis | Vendedor consulta todas as unidades disponíveis e respectivos dados comerciais, sem custos | CT-039: conferir filtros, detalhes, ausência de custo e exclusão de motos externas/vendidas |
| RF-021: dashboard administrativo | Aba, endpoints e eventuais exportações de indicadores negados a outros perfis | CT-040: tentar acessar como vendedor e mecânico; nenhuma informação do dashboard é entregue |
| RF-022: indicadores comerciais e de serviços | Resultados reconciliam com registros válidos e suas datas de referência | CT-041 a CT-043 |

- CT-041: usando dados fictícios e regra de faturamento definida, conferir venda com desconto, cancelamento, devolução e transação no limite entre semanas/meses; cartões e séries reconciliam com a origem.
- CT-042: concluir dois serviços do mesmo tipo e outro de tipo distinto; ranking conta itens concluídos, sem incluir peças ou serviços apenas orçados.
- CT-043: registro sem data ou valor obrigatório não é convertido em receita zero ou atribuído a período arbitrário; pendência é indicada.
- CT-044: vendedor consulta veículo disponível e outro usuário o vende antes da confirmação; segunda venda é rejeitada.

## Pontos a definir

1. Faturamento significa valor vendido, valor recebido ou ambos em indicadores separados? A oficina entra junto ou em uma série separada?
2. Administrativo também será o único perfil que poderá alterar os dados do veículo depois da entrada?
3. Nome/modelo da planilha já é suficiente ou existe catálogo técnico por modelo?
4. Quem cadastra veículos externos no atendimento da oficina?

As pendências de disponibilidade e devolução da planilha continuam abertas.
