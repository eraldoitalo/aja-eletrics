# Oficina e pós-venda integrados

Versão: 0.2 — 21/10/2026

## Escopo confirmado

O sistema deve combinar controle de estoque com operação de oficina, fornecendo checklists, ordens de serviço e registro de clientes vinculados aos serviços. Manutenção, revisões e garantia fazem parte do pós-venda. O uso continua interno.

Decisões adicionais confirmadas: atender motos da empresa e de outros clientes; exigir orçamento e aprovação do cliente antes da execução de serviços cobrados; registrar peças na OS sem controle de saldo ou baixa de estoque de peças na primeira versão.

O custo de aquisição da moto permanece exclusivo do administrativo, conforme 03-dados-e-permissoes.md. Valores cobrados por serviços são um conceito diferente; suas permissões ainda serão definidas.

Os fluxos, campos e regras a seguir são propostas para concretizar esse escopo, ainda sujeitos ao funcionamento real da empresa.

## Vínculos e histórico

- Um cliente pode estar relacionado a várias motos e a várias ordens de serviço.
- Cada OS atende uma moto e identifica o cliente responsável por aquele atendimento.
- Cada OS possui seus serviços, checklists e registros de execução.
- O histórico da moto reúne vendas e atendimentos; o histórico do cliente reúne seus próprios vínculos e atendimentos.
- O cliente da OS não precisa ser presumido como proprietário atual: pode ser o solicitante ou responsável. A relação e eventual autorização devem ser registradas conforme a operação.
- A troca de proprietário não reatribui vendas ou OS antigas ao novo cliente. O histórico da moto preserva os vínculos originais e o acesso aos dados pessoais respeita as permissões.
- Motos externas serão cadastradas como veículos de atendimento sem criar estoque disponível para venda. A origem da moto será independente do seu histórico de atendimento.

## Ordem de serviço proposta

| Grupo | Informações |
|---|---|
| Identificação | Número único, abertura, cliente responsável e moto |
| Entrada | Quilometragem informada, relato do cliente, acessórios recebidos e observações |
| Classificação | Manutenção, revisão ou atendimento com solicitação de garantia |
| Responsabilidade | Atendente, mecânico responsável e prazo previsto quando definido |
| Inspeção | Checklist de entrada e evidências, se necessárias |
| Diagnóstico | Constatações e serviços recomendados, separados do relato do cliente |
| Serviços | Descrição, responsável, situação, execução e eventual valor cobrado |
| Peças | Descrição e quantidade; valor cobrado quando aplicável; sem controle de saldo ou baixa de estoque de peças nesta versão |
| Aprovação | Orçamento versionado e decisão do cliente antes da execução de serviço cobrado |
| Garantia | Solicitação, análise e decisão de cobertura, sem aprovação automática |
| Saída | Checklist final, resumo do executado, encerramento e registro de entrega |

Campos obrigatórios e visibilidade por perfil serão definidos na matriz de permissões. Documentos de impressão e exportação da OS devem excluir o custo de aquisição da moto.

## Fluxo operacional proposto

Recepção e identificação do cliente/moto → abertura da OS → checklist de entrada → diagnóstico → orçamento → aprovação do cliente para serviços cobrados → execução → checklist final → pronta para retirada → entrega e encerramento.

A cobrança de diagnóstico, se existir, também exige orçamento e aprovação antes de sua execução. O fluxo para diagnósticos e serviços sem cobrança ou cobertos por garantia ainda será definido.

Estados sugeridos: aberta, em diagnóstico, aguardando aprovação, autorizada, em execução, aguardando peça, pronta para retirada, encerrada e cancelada. A lista final depende das etapas reais da oficina.

- Cada mudança registra autor e data. Transições incompatíveis são rejeitadas no servidor.
- Cancelamento preserva o histórico e exige motivo. Reabertura, quando permitida, registra justificativa.
- Atendimento de garantia registra cobertura separadamente da evolução técnica da OS.
- Uma moto vendida pode estar em manutenção sem deixar de estar vendida. Estado comercial e situação de oficina são independentes.
- A OS encerrada preserva o executado. Correções posteriores precisam de registro rastreável.

## Checklists propostos

Fornecer modelos editáveis de entrada, revisão e saída. Os itens concretos deverão ser definidos com os responsáveis técnicos e as orientações aplicáveis a cada modelo de moto. O sistema não substituirá procedimentos técnicos por uma lista genérica.

Cada modelo terá nome, versão, itens e indicação de obrigatoriedade. Cada preenchimento pertencerá a uma OS e registrará respostas, observações, autor e data.

Respostas sugeridas: conforme, não conforme e não se aplica, com justificativa quando exigida. Itens ainda sem resposta permanecem pendentes; não são interpretados como aprovados.

Alterar um modelo cria uma nova versão e não modifica checklists de atendimentos anteriores. Pendências obrigatórias bloqueiam a conclusão da etapa correspondente. O tratamento de itens não conformes deve ser definido por item ou modelo, com registro de resolução ou decisão autorizada.

## Clientes e catálogo de serviços

Cadastro inicial proposto: nome, contato e identificador interno. Documentos e endereço só serão exigidos quando necessários ao processo definido. Pesquisa de possíveis duplicidades deve ajudar a equipe sem juntar pessoas automaticamente pelo nome ou telefone.

O catálogo de serviços padroniza nomes e descrições. Valores sugeridos e duração prevista são opcionais a validar. A OS preserva uma cópia da descrição e do valor acordado de seus itens, para que mudanças no catálogo não reescrevam atendimentos antigos.

Uma nova necessidade de serviço deve ser registrada como item vinculado à OS. Acréscimos após aprovação passam por nova versão e autorização, sem sobrescrever a aprovação anterior.

## Orçamento e aprovação

A exigência de aprovação antes de serviços cobrados está confirmada. As regras detalhadas abaixo são propostas de implementação.

- Cada orçamento identifica OS, versão, serviços, peças, quantidades, valores unitários cobrados, descontos e total. Valores de serviço e peças não representam o custo de aquisição da moto.
- A versão apresentada ao cliente fica preservada. Revisões posteriores geram nova versão, sem editar o conteúdo aprovado.
- Registrar aprovação ou recusa, versão correspondente, cliente ou representante, data da decisão, usuário que a registrou e forma de comprovação. O canal de aprovação e a necessidade de anexos ainda serão definidos.
- Serviços cobrados só podem iniciar quando estiverem incluídos na versão aprovada. A validação deve ocorrer no servidor, inclusive em chamadas diretas.
- Alterações em escopo, quantidade ou preço de itens aprovados exigem nova aprovação dos itens afetados antes da execução. Serviços já executados mantêm sua referência de autorização original.
- Na primeira versão, propor aprovação integral do orçamento. Aprovação parcial só deve entrar se o processo da oficina exigir esse comportamento.
- Orçamento recusado não autoriza execução. Deve ser possível registrar revisão ou encaminhar a OS para devolução sem execução, conforme o procedimento acordado.
- Não considerar pagamento ou silêncio do cliente como aprovação automática.
- A aprovação será registrada pela equipe no sistema interno; portal do cliente, assinatura digital e envio automático de mensagens não estão confirmados.

## Peças na primeira versão

Registrar peças dentro da OS e do orçamento: descrição, quantidade, unidade de medida e valor cobrado quando aplicável. Separar peças previstas das efetivamente utilizadas e preservar a relação com a autorização.

Não haverá saldo, reserva, entrada de compra ou baixa automática de peças. Alterar a quantidade prevista não pode reescrever o orçamento aprovado. A troca ou inclusão de peça cobrada segue a regra de nova aprovação.

## Permissões propostas para discussão

| Atividade | Administrativo | Vendedor/atendente | Mecânico |
|---|---|---|---|
| Consultar COMPRA da moto | Permitido (confirmado) | Negado (confirmado) | Negado (confirmado) |
| Cadastrar cliente e abrir OS | Proposto | Proposto | A definir |
| Registrar diagnóstico, execução e checklist | Proposto | A definir | Proposto, nas OS autorizadas |
| Definir modelos de checklist e catálogo | Proposto | A definir | A definir |
| Aprovar descontos, cancelar ou reabrir OS | A definir | A definir | A definir |
| Consultar valores cobrados de serviços | A definir | A definir | A definir |

Não criar um perfil de atendente separado sem confirmar se essa função é exercida pelos vendedores ou por outra equipe.

## Testes de aceite planejados

Estes testes complementam CT-001 a CT-018 e ainda não foram executados.

| ID | Cenário | Resultado esperado |
|---|---|---|
| CT-019 | Cliente com duas motos e atendimentos distintos | Histórico do cliente reúne suas OS; cada moto mostra apenas os seus atendimentos |
| CT-020 | Abertura de OS sem cliente ou sem moto | Abertura rejeitada com indicação dos vínculos ausentes |
| CT-021 | Atualização do diagnóstico e dos serviços | Dados preservados na OS correta, com responsável e histórico |
| CT-022 | Tentativa de concluir checklist com item obrigatório sem resposta | Conclusão bloqueada; item pendente identificado |
| CT-023 | Alteração de modelo após preencher checklist | Atendimento antigo mantém perguntas, respostas e versão anteriores |
| CT-024 | Moto vendida recebe OS | OS aberta sem alterar a situação comercial para disponível |
| CT-025 | Novo atendimento após troca de proprietário | Nova OS usa responsável correto; vínculos das OS antigas permanecem |
| CT-026 | Mecânico consulta OS, anexo ou impressão | Custo de aquisição e dados que permitam deduzi-lo não são entregues |
| CT-027 | Alteração de serviço no catálogo | OS anterior preserva descrição e valor registrados |
| CT-028 | Mudança de estado incompatível ou sem permissão | Requisição rejeitada; estado anterior preservado |
| CT-029 | Oficina recebe moto externa | Cadastro de atendimento não aumenta o estoque comercial |
| CT-030 | Acréscimo de serviço após aprovação | Nova autorização exigida para o acréscimo; aprovação anterior preservada |
| CT-031 | Iniciar serviço cobrado sem aprovação, inclusive pela API | Execução bloqueada sem alterar o estado do serviço |
| CT-032 | Cliente aprova uma versão do orçamento | Identidade, versão, data, responsável pelo registro e forma de comprovação ficam associados à decisão |
| CT-033 | Cliente recusa orçamento | Serviços cobrados recusados não podem iniciar |
| CT-034 | Quantidade ou preço de peça muda após aprovação | Nova versão exige aprovação; versão anterior e seu total permanecem preservados |
| CT-035 | Peça é registrada como utilizada na OS | Registro aparece no histórico; não ocorre alteração de saldo de estoque |
| CT-036 | Diagnóstico é um serviço cobrado | Exige aprovação do orçamento correspondente antes de iniciar |

## Primeira versão proposta

Incluir cadastro de clientes e motos próprias ou externas, estoque comercial, vendas, catálogo básico de serviços, abertura e acompanhamento de OS, orçamento e aprovação, registro de peças na OS, checklists versionados, histórico por cliente/moto, registro de análise de garantia e controle de acesso.

Estoque de peças fica fora da primeira versão por decisão do usuário. Agendamento, cobranças, mensagens automáticas e portal do cliente continuam sem escopo definido. A inclusão de oficina não implica um ERP fiscal, contábil ou financeiro completo.

## Definições prioritárias

1. Como o cliente aprova hoje: WhatsApp, assinatura em papel ou outro canal? Qual comprovação precisa ser guardada?
2. Quem recebe a moto, prepara o orçamento, registra a aprovação, distribui o trabalho e encerra a OS?
3. A oficina precisa de aprovação parcial ou a aprovação integral do orçamento atende?
4. Existe diagnóstico cobrado? Como são autorizados os atendimentos sem cobrança e de garantia?

Continuam abertas as perguntas de estoque: significado dos status vazios e de devolução, identificação por chassi/série e momento da baixa de venda.
