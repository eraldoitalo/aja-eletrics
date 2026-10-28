# Análise de caso · AJA Eletrics

## Contexto e objetivo

A empresa vende motos elétricas e atende manutenção, revisão e garantia, inclusive de veículos que não vendeu. O controle inicial é uma planilha com uma linha por moto física, dados de identificação, preço, cor e situação comercial. O campo Compra informa o custo da unidade e só pode ser acessado pelo administrativo.

O sistema integra estoque, vendas, clientes e oficina para manter o histórico do pós-venda. A mudança tecnológica solicitada preserva as regras do projeto anterior, utilizando Django, templates HTML/CSS e PostgreSQL. Os documentos em `requisitos/` preservam a descoberta original; referências antigas a Node, React ou outro banco são substituídas pelas decisões em `arquitetura.md`.

## Atores e responsabilidades

| Ação | Administrativo | Vendedor | Mecânico |
|---|---|---|---|
| Cadastrar veículo e entrada no estoque | Sim | Não | Não |
| Consultar custo de aquisição | Sim | Não | Não |
| Consultar catálogo disponível | Sim | Sim | Não |
| Registrar cliente, venda e abrir OS | Sim | Sim | Não |
| Elaborar orçamento e registrar decisão do cliente | Sim | Sim | Não |
| Diagnóstico, checklists e execução | Sim | Não | Nas suas OS |
| Consultar histórico de clientes | Sim | Sim | Pela OS atribuída |
| Encerrar OS pronta | Sim | Sim | Não |
| Cancelar OS com motivo | Sim | Não | Não |
| Consultar dashboard | Sim | Não | Não |

O administrativo pode acompanhar e executar operações de outros perfis. A gestão técnica de usuários é reservada a superusuários. A atribuição de OS ao mecânico e a matriz acima são decisões do MVP que devem ser homologadas pela empresa.

## Fluxo de venda

1. Administrativo cadastra uma unidade física, sua origem, condição, ficha técnica, preço de venda e custo.
2. Vendedor consulta unidades disponíveis e sua descrição técnica.
3. Equipe comercial cadastra ou seleciona o cliente e confirma o valor da venda.
4. O servidor bloqueia a linha da unidade, registra uma única venda e muda a situação para Vendida na mesma transação.
5. O histórico do cliente e o dashboard passam a refletir a venda.

Novo/seminovo é condição do veículo. Disponível/vendido é situação comercial independente. A confirmação registra a venda imediatamente; não há reserva, parcelamento ou cancelamento de venda nesta versão.

## Fluxo de oficina

1. Administrativo cadastra veículos externos com origem Oficina; eles não entram no catálogo de vendas.
2. Equipe comercial abre OS vinculando cliente, moto, categoria, relato e mecânico.
3. Mecânico responsável preenche o checklist de entrada e o diagnóstico.
4. Comercial elabora orçamento com serviços e peças; cada revisão gera nova versão.
5. Comercial registra aprovação ou recusa, nome do cliente, canal e referência da comprovação. O sistema registra responsável e data. Não envia mensagens automaticamente e não oferece assinatura ou upload de comprovantes.
6. Apenas a aprovação da versão atual autoriza o início. Serviços adicionais após o início exigem outra OS nesta versão.
7. Mecânico registra as peças efetivamente usadas, limitadas ao orçamento, e conclui o checklist de saída.
8. Todos os itens obrigatórios precisam estar conformes para a OS ficar pronta. Comercial registra o encerramento/entrega.

Estados: Aberta → Aguardando aprovação → Autorizada → Em execução → Pronta → Encerrada. Recusa mantém a OS aguardando, permitindo novo orçamento. Cancelamento administrativo exige motivo. OS encerrada ou cancelada não aceita mutações operacionais.

## Indicadores

O dashboard é administrativo. A série semanal/mensal soma valores de vendas de motos por data de confirmação, usando o fuso de São Paulo. Semanas começam na segunda-feira; meses são civis. Cartões e rankings abrangem o histórico completo. Serviços mais realizados contam quantidades de serviços no último orçamento aprovado de OS prontas/encerradas. Isso não representa caixa recebido nem faturamento fiscal; receita de oficina ainda não integra os gráficos financeiros.

## Pendências de negócio

- Aprovar o instante de confirmação da venda e regras de devolução/cancelamento/reserva.
- Definir se faturamento significa vendas, recebimentos, emissão fiscal ou composição com serviços.
- Detalhar garantia: cobertura, prazo, fabricante, evidências, análise, decisão e custos.
- Validar checklists técnicos por modelo e procedimentos de revisão com a equipe da oficina.
- Definir importação da planilha: identificadores, valores ausentes, devoluções e linhas sem situação.
- Homologar matriz de permissões, atribuição de mecânicos e acesso a históricos.
- Definir retenção de dados pessoais, backups, hospedagem e responsáveis operacionais.

A migração da planilha real não foi executada. A entrega não contém dados reais de clientes, motos ou custos e não deve inferir decisões para linhas incompletas.
