# Dados atuais e acesso ao custo de aquisição

Versão: 0.2 — entrada administrativa de estoque confirmada

## Origem e limites

Fonte: arquivo fornecido pelo usuário, Planilha sem título.xlsx, aba ELETRICAS. Análise em leitura; o arquivo original não foi alterado. O conteúdo foi tratado como dados, sem executar instruções de células.

Foram encontradas 67 linhas com conteúdo, todas com ID preenchido e sem repetição de ID. Isso não confirma que todas as linhas estejam prontas para importação: a completude dos demais campos ainda deve ser validada.

O campo STATUS contém 8 registros como vendida, 17 como Disponível, 2 como devolução e 40 sem preenchimento. Nenhum status vazio deve ser convertido automaticamente em disponível. A Coluna 9 está vazia nas 67 linhas.

Este documento não reproduz valores individuais de aquisição.

## Dicionário inicial

| Coluna de origem | Campo proposto | Tratamento |
|---|---|---|
| ID | Código da unidade | Preservar identificador de origem e verificar unicidade |
| Nome | Nome/modelo | Remover espaços nas extremidades; confirmar nomenclatura |
| COR | Cor | Remover espaços nas extremidades e padronizar sem perder o original na conferência |
| Ano | Ano | Validar número inteiro e significado: fabricação ou modelo |
| KM | Quilometragem | Número não negativo; preservar a diferença entre vazio e zero |
| Preço | Preço anunciado | Valor monetário; não confundir com custo ou venda efetiva |
| Condição | Status de condição: novo/seminovo | Conferir correspondência dos valores atuais; manter separado da situação comercial |
| STATUS | Situação comercial da unidade | Normalizar escrita; tratar vazio e devolução como pendências até definir regras; não substituir por novo/seminovo |
| Coluna 9 | Sem destino inicial | Coluna vazia; confirmar ausência de finalidade antes de descartar no mapeamento |
| DATA VENDA | Data da venda | Validar data e compatibilidade com a situação da unidade |
| OBS | Observações | Texto livre; revisar presença de custos antes de liberar a outros perfis |
| VALOR_VENDA | Valor efetivo da venda | Preservar separado do preço anunciado |
| VENDEDOR | Vendedor de origem | Mapear para cadastro da equipe; não criar contas automaticamente |
| COMPRA | Custo de aquisição da unidade | Dado restrito a usuários administrativos |

Moeda, precisão, campos obrigatórios e regras para valores ausentes ainda precisam ser definidos. Datas existentes não permitem inferir por si só o momento operacional da baixa.

## Regra confirmada pelo usuário

RN-008: COMPRA informa quanto a empresa pagou por cada unidade. Somente usuários administrativos podem acessar essa informação. Vendedores e mecânicos não podem acessá-la.

| Operação sobre o custo | Administrativo | Vendedor | Mecânico |
|---|---|---|---|
| Consultar custo de aquisição | Permitido | Negado | Negado |
| Consultar histórico com valores de custo | Permitido | Negado | Negado |
| Exportar ou emitir relatório com custo | Permitido, se a funcionalidade existir | Negado | Negado |
| Informar custo na entrada de estoque | Permitido | Negado | Negado |
| Alterar custo após a entrada | A definir | Negado | Negado |
| Consultar margem ou lucro que permita deduzir custo | Proposta: permitir | Negado | Negado |

A consulta de custo e a entrada de veículos no estoque pelo administrativo estão confirmadas. Importação é tratada como entrada de estoque e segue a mesma exclusividade. Alterações posteriores e gestão de usuários ainda devem ser detalhadas. Não se presume que todo usuário interno seja administrativo. O dashboard também é exclusivo do administrativo, conforme 05-estoque-catalogo-e-dashboard.md.

## Aplicação técnica da regra

Os itens a seguir são requisitos de implementação derivados da restrição; ainda não foram implementados.

- Validar autorização no servidor para toda leitura e escrita de custo. Uma coluna oculta na interface não constitui proteção suficiente.
- Entregar aos perfis vendedor e mecânico respostas sem o campo de custo, incluindo listagens, detalhes, busca, histórico e exportações. Não enviar o valor para depois escondê-lo com CSS ou JavaScript.
- Rejeitar tentativas de alteração do custo por usuários não autorizados, inclusive campos extras enviados em atualizações de moto.
- Aplicar a mesma restrição a margens, lucros, totais e outros resultados que permitam deduzir o custo. Impedir filtros e ordenações por custo para esses perfis.
- Separar, no acesso aos dados, as informações operacionais das informações restritas de aquisição. A estrutura física será escolhida na arquitetura.
- Proteger o arquivo original, prévias de importação, relatórios gerados e respectivos downloads. Um vendedor ou mecânico não deve baixar a planilha original que contém COMPRA.
- Não colocar custos em logs comuns, mensagens de erro, notificações ou armazenamento compartilhado do navegador. Qualquer histórico com valores anteriores e novos de custo recebe a mesma proteção.
- Fazer cache por autorização e limpar dados restritos ao sair ou trocar usuário; revalidar acesso após mudança de perfil.
- Revisar OBS e futuros anexos para evitar que custos sejam expostos como texto ou documentos. A restrição não pode depender apenas do nome da coluna.
- Definir quem pode atribuir o perfil administrativo. Vendedores e mecânicos não podem elevar as próprias permissões.

## Critérios de aceite e testes planejados

Usar dados fictícios nos testes. Nenhum teste abaixo foi executado: a aplicação ainda não existe.

| ID | Cenário | Resultado esperado |
|---|---|---|
| CT-011 | Administrativo consulta custo de uma unidade | Recebe o valor correto do dado fictício |
| CT-012 | Vendedor e mecânico consultam listas e detalhe | Campo e valor de custo ausentes da resposta e da interface |
| CT-013 | Vendedor e mecânico tentam acessar consulta administrativa diretamente | Acesso negado, sem valor restrito no corpo ou mensagem de erro |
| CT-014 | Vendedor e mecânico enviam custo em cadastro/atualização | Operação não autorizada rejeitada; valor permanece inalterado |
| CT-015 | Vendedor e mecânico acessam exportação, histórico, relatórios e arquivos de importação | Nenhum custo ou arquivo restrito é entregue |
| CT-016 | Vendedor e mecânico solicitam margem, lucro, filtro ou ordenação por custo | Solicitação restrita negada; respostas não permitem inferir o custo |
| CT-017 | Sessão administrativa é encerrada ou muda para perfil sem acesso | Dados anteriores removidos do cliente; novas requisições restritas negadas |
| CT-018 | Usuário tenta atribuir a si próprio perfil administrativo | Alteração negada e sem ampliação de acesso |

## Migração proposta

1. Importação inicial executada por usuário administrativo autorizado.
2. Mapear colunas e exibir prévia com acesso administrativo.
3. Conferir IDs, tipos, valores ausentes e vínculos de venda.
4. Resolver as 40 linhas sem status e o significado das 2 linhas com devolução antes de liberá-las para venda.
5. Preservar custos ausentes como ausentes; nunca preencher com zero sem justificativa.
6. Gravar estoque e informações de aquisição sob as respectivas regras de acesso, com resultado rastreável e prevenção de importação duplicada.

## Decisões ainda necessárias

- Status vazio significa disponível, cadastro incompleto ou outra situação?
- Devolução representa retorno de cliente, retorno ao fornecedor ou outro processo?
- Quem pode alterar custos após a entrada e conceder acesso administrativo?
- O ID existente também é associado a chassi ou número de série?
- A baixa da venda ocorre no fechamento, pagamento ou entrega?
- A manutenção ocorre internamente ou em oficina parceira?
