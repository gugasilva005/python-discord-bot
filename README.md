# discord_bot_project
 
Este é um projeto de um bot para Discord, desenvolvido com o objetivo de realizar a autenticação de alunos de uma Instituição em um servidor.

> Funcionalidades

* Autenticação de Membros: O bot permite a autenticação de novos membros através do envio de um código de confirmação por e-mail. Os membros devem inserir corretamente o código recebido para obter acesso ao servidor. Caso excedam o limite de tentativas incorretas, o bot os bane automaticamente.

* Definição de cargos: Após a autenticação bem-sucedida, o bot atribui automaticamente um cargo específico aos membros, proporcionando acesso a determinados canais e permissões no servidor. Isso ajuda a organizar e diferenciar os membros com base em sua autorização.

* Controle de tentativas: O bot controla o número de tentativas de autenticação de cada membro, evitando abusos e ataques de força bruta. Se um membro ultrapassar o limite de tentativas permitidas, o bot toma medidas de segurança, banindo-o automaticamente.

> Tecnologias utilizadas

* Python: linguagem de programação de sintaxe simples;
* Discord Developer Portal: site para registrar sua aplicação/bot;
* Discord.py: Biblioteca para integração com o discord;
* Pandas: Biblioteca para análise e manipulação de dados;
