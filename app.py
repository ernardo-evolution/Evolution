# PROMPT PROFISSIONAL — CENTRAL DE SUPORTE E ATENDIMENTO
**Projeto: Evolution Gestão Online**

Quero implementar no Evolution Gestão Online uma central de suporte profissional para que os usuários possam entrar em contato com o responsável pelo sistema quando tiverem dúvidas, encontrarem erros ou precisarem de ajuda para concluir alguma operação.

## 1. Criar uma nova seção
Adicionar ao menu lateral uma opção chamada **Suporte e Atendimento**, mantendo o padrão visual atual do sistema.

A página deve apresentar uma interface moderna, organizada e fácil de utilizar.

## 2. Oferecer dois canais de atendimento

### Opção A — Atendimento por e-mail
Criar um cartão com:
- Ícone de e-mail.
- Título: "Atendimento por e-mail".
- Descrição: "Envie sua dúvida ou relate um problema. Nossa equipe receberá sua mensagem para análise."
- Botão: **Enviar e-mail**.

Ao clicar no botão, abrir o aplicativo de e-mail padrão do usuário, com o endereço de suporte preenchido.

Utilizar um endereço configurável nas definições do sistema, sem inventar ou colocar um endereço fictício em produção.

### Opção B — Atendimento pelo WhatsApp
Criar outro cartão com:
- Ícone oficial ou visualmente reconhecível do WhatsApp.
- Título: "Atendimento pelo WhatsApp".
- Descrição: "Entre em contato diretamente para esclarecer dúvidas ou solicitar ajuda."
- Botão: **Conversar pelo WhatsApp**.

O botão deve abrir uma conversa com o responsável pelo sistema usando um link oficial no formato `https://wa.me/NUMERO`.

O número deverá ser configurável e armazenado no formato internacional, com código do país e DDD, sem espaços, sinais ou parênteses.

Se houver uma mensagem inicial configurada, utilizar o parâmetro `text` do link para preencher automaticamente uma mensagem como:

"Olá! Sou usuário do Evolution Gestão Online e preciso de ajuda com o sistema."

Não afirmar que a mensagem foi enviada automaticamente: o usuário deverá confirmar o envio no WhatsApp.

## 3. Formulário de suporte
Adicionar um formulário opcional para registrar:
- Nome do usuário.
- E-mail para resposta.
- Assunto.
- Tipo de solicitação: dúvida, erro técnico, sugestão ou outro.
- Descrição detalhada do problema.

Incluir validação dos campos obrigatórios e mensagens de erro claras.

Se houver integração de envio de e-mail configurada, permitir que o formulário envie a solicitação ao endereço de suporte. Caso contrário, apresentar os canais de contato disponíveis sem simular um envio bem-sucedido.

## 4. Experiência do usuário
- Manter a identidade visual escura e profissional do Evolution.
- Utilizar cartões bem organizados e botões claramente identificados.
- Adaptar a página para computadores e dispositivos móveis.
- Exibir os canais de contato somente quando estiverem configurados.
- Evitar botões sem funcionalidade.

## 5. Segurança e implementação
- Não expor senhas, tokens ou credenciais de e-mail no código-fonte.
- Utilizar variáveis de ambiente ou o mecanismo de segredos já adotado pelo projeto.
- Não enviar dados confidenciais do sistema automaticamente para terceiros.
- Preservar as funcionalidades atuais.
- Testar os links, as validações e o envio do formulário, quando implementado.

## Resultado esperado
Criar uma central de suporte funcional, integrada ao Evolution Gestão Online, que permita ao usuário escolher entre e-mail, WhatsApp ou formulário de contato para solicitar ajuda de maneira simples e profissional.
