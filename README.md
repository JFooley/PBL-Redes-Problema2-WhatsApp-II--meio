<div align="center">
  <h1>
  Universidade Estadual de Feira de Santana (UEFS)

  Problema 3: ZapZap RC
  </h1>

  <h3>
    João Gabriel Lima Almeida
  </h3>

  <p>
  DEPARTAMENTO DE TECNOLOGIA
    
  TEC502 - CONCORRÊNCIA E CONECTIVIDADE
  </p>
</div>

# 1. Introdução

<p style="text-align: justify;">
A atualização e o crescimento do software é tão importante quanto sua construção. Desenvolver pensando na melhoria e na escalabilidade é muito importante para garantir que o código seja fácil de atualizar e se adaptar aos novos requisitos que venham a surgir.

Pensando nisso, este relatório descreve atualização do chat instantâneo "ZapZap" desenvolvido no problema 2 da disciplina TEC502 - Concorrência e Conectividade. O chat, previamente construido, possui os seguintes requisitos:

- Utilizar socket do tipo UDP

- Considerar o modelo de falhas, ou seja, que possa ocorrer perda de pacotes

- Solução distribuida, descentralizada

- Não utilizar relógio fisico nem medidas de tempo do gênero uma vez que são imprecisas e não confiáveis

- Não utilizar servidores de tempo

Além deles, também foi adicionado o seguinte requisito: O chat agora precisa ter confiabilidade, ou seja, uma mensagem só vai ser exibida para um usuário se, garantidamente, for exibida para todos. Ou seja, é necessário uma forma de confirmar que a mensagem tenham chegado a todos os usuários e haver uma sincronia na exibição.

A linguagem de programação utilizada foi o Python na versão 3.12. A metodologia do desenvolvimento utilizada foi a Problem Based Learning (PBL), onde os alunos discutiram em grupo a os passos para solucionar o problema apresentadoe e construir a aplicação com os requisitos determinados pelos tutores.
</p>

# 2. Desenvolvimento

<p style="text-align: justify;">
O funcionamento do programa base segue o seguinte fluxo: Cada usuário da rede vai executar o programa e este vai se conectar diretamente a todos os demais nós (usuários) da rede realizando trocas de pacotes peer-to-peer. Cada programa possui uma thread que recebe os pacotes e os coloca em um cache, uma thread para "desembrulhar" o pacote, identifica-lo e fazer o devido tratamento para o tipo do pacote e o contexto em que ele foi recebido. Uma thread de sincronização que envia a conversa antiga, sincronizando as dos demais nós. E a execução principal, que recebe o input do usuário e o envia como uma mensagem.

Partindo dessa base, a estrutura foi mantida porém com algumas alterações importantes. Para garantir que a sincronia na exibição fosse bem sucessidade, foi necessário implementar um sistema de confirmação em que cada nó que, ao enviar uma mensagem, deve garantir que essa mensgem chegue para todos os nós e posteriormente enviar um pacote indicando aos nós que eles devem exibir a mensagem pois todos os demais nós já confirmaram o recebimento. Porém, esse sistema apresenta uma grande fragilidade no modelo de falhas pois se algum pacote de se perder, toda a sincronia se perde, além de que é necessário diferenciar quando um nó não recebe uma mensagem por perda de pacote de quando ele não recebe por ter ficado offline. 

Dado essa base, foi necessário duas implementações: Uma forma de verificar se os pacotes foram entregues, uma forma de tratar os casos em que houve perda de pacotes e uma forma de saber se aquele nó está online ou offline. 

Para resolver o problema da verificação dos pacotes foi decidido utilizar o modelo de pacotes de confirmação, onde pacotes ACK são enviados de volta do destinatário ao remetente do pacote que se deseja confirmar. Dessa forma, o remetente tem noção se aquele pacote chegou ou não no seu destino caso, dentro de um certo periodo de tempo, ele receba um pacote ACK que confirme o pacote enviado. No caso de não receber o ACK, seja por o ACK ou a mensagem enviada ter sido perdida, o remetente considera que a transmissão falhou e ai entramos na segunda parte: A retransmissão. Para corrigir os casos em que a mensagem ou o pacote de confirmação dela se percam, se viu necessário implementar um sistem simples de retransmissão. Esse sistema tem como objetivo re-enviar o pacote caso ele não seja confirmado em um certo periodo de tempo. Já na questão de verificar se o nó está online ou não, foi decidido implementar uma troca de mensagens simples em que cada nó, em um periodo de tempo fixo e regular, envia uma solicitação e os demais respondem ela, demonstrando que ainda estão online no sistema.

Os pacotes do sistema que não podem ser perdidos são: as mensagens novas, as mensagens antigas (em caso de sincronização) e os pacotes que autorizam a exibição de uma mensagem. A imagem abaixo demonstra um exemplo de como essa sistema funciona na teoria e porque ele garante que o nó vai receber o pacote. 
</p>

![Exemplo de funcionamento da confirmação e reenvio dos pacotes.](https://github.com/JFooley/PBL-Redes-Problema3-WhatsApp-II-RC/blob/c1055a3d59a52a5637fa94e7b3499cf4965d42ef/Imagens/Imagem1.png)

# 3. Resultados
<p style="text-align: justify;">
A partir da abordagem proposta, foi mantida boa parte da estrutura base do sistema. A primeira grande alteração foi a re-estruturação das funções e classes em arquivos diferentes, com destaque para o Classes que contem todas as classes utiliazadas na implementação. Sobre as alterações, a classe Mensagem recebeu um atributo "confirmations", que consiste em um dicionário do endereço dos membros em que o valor de cada chave indica se aquele nó identificado pelo endereço já confirmou ou não a chegada da mensagem. 

- Status do nó

Para fazer rastreamento do status dos outros nós (saber se ele está on ou off) foi necessário alterar a função de sincronização. Ela deixa de ser "eventual sync" e se torna "Online requester", uma função que fica enviando mensagens "PING" para os outros nós e sendo respondida com mensagens "PONG". Esses pings são enviados de tempos em tempos em um intervalo fixo. Antes de enviar um ping, o nó altera o status do nó alvo para um nível abaixo, ou seja, se o status for ON (online) ele se torna UNK (deseconhecido) e se for UNK se torna OFF (offline), cada pong recebido altera o status daquele nó (na lista do nó que recebeu o pong) para online. Dessa forma, enquanto um nó continuar respondendo os PINGs, ele será considerado como online para os demais nós. O status UNK é necessário pois pode ser que algum desses pacotes PING/PONG se perca, mas não necessáriamente signfica que aquele nó se tornou offline, apenas que a resposta ou a pergunta foi perdida. Através desse sistema, os nós conseguem diferenciar quem está online de quem está offline.

- Confirmação e retransmissão

Como citado, a abordagem escolhida para tratar o problema da perda de pacotes foi a de confirmação e retransmissão das mensagens. Para atingir esse objetivo, foram criados novos caches de pacotes: waiting, confirms e um set de mensagens não confirmadas: no_confirmed. 

Já que algumas mensagens precisam de confirmação (mensagens nova, antigas e "shows") e outras não (ACK, PING, PONG, SYN) foi criada uma nova função de envio chamada assure_send, utilizada para enviar os pacotes do primeiro grupo. Quando um pacote é enviado por assure_send, é adicionada uma copia das informações do pacote no cache waiting, além de um timestamp que indica quando (no tempo do remetente) aquele pacote foi enviado. A medida que os pacote ACK chegam, a thread de tratamento de pacotes (pkgSort) coloca esses pacotes no cache confirms e uma outra thread chamada confirm_handler verifica para cada pacote do cache de espera (waiting) se existe um ACK que o confirme no cache de confirmações (confirms). Caso exista, aquele pacote é retirado da lista de espera, do contrário, é comparado o timestamp da hora atual com o do pacote e verifica-se se o tempo maximo de esperar do ACK foi excedido. Caso o tempo já tenha passado, aquele pacote é re-enviado, o seu timestamp é atualizado para a hora atual (nao confundir com o logicstamp, do relógio lógico) e ele é adicionado novamente em waiting até a proxima verificação. Dessa forma, o pacote fica sendo re-enviando enquanto não houve um ACK que o confirme no cache confirms. Entretanto, para evitar que o pacote fica preso em um looping de reenvio devido ao destinatário ficar offline, além de verificar se o tempo de reenvio foi passado também é verificado se o nó alvo ainda está online.

No caso das mensagens (novas), elas são adicionadas também ao set no_confirmed onde aguardam até serem movidas para a conversa (ou seja, exibidas). Toda vez que um ACK que confirme uma mensagem do no_confirmed chega, é alterado no atributo confirmations da mensagem o valor da chave equivalente ao endereço que enviou o ACK, ou seja, é marcado que aquele endereço confirmou a chegada da mensagem. Na thread pkgSort, a cada pacote tratado, a thread também verifica, para cada mensagem de no_confirmed, se a mensagem possui todas as confirmações de todos os nós online. Caso a resposta seja sim, ela retira a mensagem de no_confirmed e coloca na conversa (exibe ela) e envia com assure_send (envio com confirmação e re-tranmissão) um pacote do tipo SHOW que indica que aquela mensagem em específico deve ser exibida pelos nós. Ou seja, toda vez que uma mensagem nova é enviada, primeiro o nó garante que todos vão receber ela e depois envia uma mensagem SHOW que manda os nós exibirem a mensagem, garantindo a sincronia.

Tendo em vista agora que, teoricamente, as mensagens novas não vão ser perdidas, o sistema de sincronização/recuperação das mensagens antigas foi alterado para só ser chamado quando um novo nó fique online ou quando houver uma queda significativa de rede em um nó. Todas as mensagens CSP (mensagens antigas re-enviadas na recuperação) seguem o mesmo processo de envio dos pacotes MSG e SHOW, com a unica diferença de que elas não são adicionadas em no_confirmed e nem precisam ser confirmadas, já que o unico nó que não possui elas é aquele que solicitou a recuperação das mensagens antigas. 

Com esse sistema descrito, dada condições normais de funcionamento, todas as mensagens enviadas devem chegar para todos os nós online e todos eles devem exibi-las de forma sincronizada, mesmo com possíveis perdas de pacote podendo ocorrer.

- Extras

Os membros deixaram de ser guardados como uma lista de endereços e agora se tornam objetos da classe Membro, que guardam também o nome e status daquele membro (online ou offline). Além disso foi criada uma classe singleton Contatos que lê os contatos a partir de um arquivo TXT e possui métodos que facilitam a criação da lista de contatos (que agora são indicados pelo nome). Por fim, também foram adicionadas alguns comandos de chat utilizando "/" no início que melhoram a utilização do chat, permitindo funções como: exibir uma quantidade especifica de mensagens na tela, ver os usuários que compõe o grupo e seus status, gerar um arquivo de saída .txt com a conversa, enviar mensagens pré escritas em um arquivo de input e ver a chave de criptografia do grupo. 

</p>

# 4. Considerações finais
<p style="text-align: justify;">
O programa, de forma geral, cumpre os objetivos propostos pelo problema. Com a implementação da confirmação e reenvio de pacotes, o problema da perda de pacotes é solucionado ao custo de mais processamento, já que uma nova thread paralela e mais operações foram necessárias. A utilização de um sistema simples de mensagens PING e PONG para verificar os membros online consegue garantir que o chat funcione sempre considerando a lista de membros online e não a de membros do grupo, evitando que o sistema fique travado devido a um membro está offline. 

Mesmo que teoricamente não possa haver dessincronia e perda de pacotes, ainda existem casos em que falhas podem acontecer devido a estresse do sistema. Um caso reportado durante a implementação é durante o uso da função de envio automatico /input, devido ao fluxo grande de mensagens saíndo do nó e a inundação dos cache de wainting, pode ocorrer de que algumas mensagens recebidas pelo nó não sejam exibidas, mesmo eles recebendo a mensagem, confirmando e recebendo a mensagem SHOW. A hipótese mais provável do motivo do problema o pacote SHOW pode estar confirmando outra mensagem devido a um conflito no ID (logicstamp), fazendo com que a mensagem correta não seja exibida. Outro provavel motivo é que como o cache de pacotes fica inundado por ACKs das mensagens que estão sendo enviadas (um pra cada nó por mensagem), os pacotes de PING dos outros nós demorem para serem tratados, fazendo com que aquele nó demore para responder com um PONG e ele seja identificado como offline pelos demais nós, o que explicaria o motivo de todos exibirem a mensagem e ele não. 

No mais, algumas melhorias podem ser futuramente implementadas no chat, como separação dos pacotes PING e PONG dos demais pacotes (evitar dessincronia); sistema de identificação de mensagens mais robusto que não permita possíveis conflitos, como o uso de mais de um dado para identificar a mensagem; função de exibir mensagens na tela mais estável e entre outras funcionalidades menores. 
</p>

# 5. Referencias
<p style="text-align: justify;">
  threading — Thread-based parallelism. Python Software Foundation. 2023. Disponível em: https://docs.python.org/3/library/threading.html. Acesso em: 22 de novembro de 2023.

  socket — Interface de rede de baixo nível. Python Software Foundation. 2023. Disponível em: https://docs.python.org/pt-br/3/library/socket.html Acesso em: 24 de novembro de 2023.

  pickle — Python object serializatio. Python Software Foundation. 2023. Disponível em: https://docs.python.org/3/library/pickle.html Acesso em: 24 de novembro de 2023.

  CARVALHO, Marcus. Sistemas Distribuídos - 5.2 Relógios lógicos. YouTube, 2023. Disponível em: https://www.youtube.com/watch?v=xK0K3RY5xco&t=1452s Acesso em: 01 de Dezembro de 2023.

</p>
