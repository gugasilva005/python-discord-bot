import discord
import pandas
import pandas as pd
import email.message
import smtplib
import asyncio
import constants


def funcao_le_arquivos(x: str, y: str, z: str):
    """
    Função que lê um elemento e verifica se ele está presente em uma coluna especifica de uma planilha escolhida
    :param x: nome da planilha que será lida
    :param y: nome da coluna
    :param z: valor a encontrar
    :return: True se o valor estiver presente e False se o valor não estiver presente
    """
    planilha = pd.read_csv(x)

    esta_presente = z in planilha[y].values

    if esta_presente:
        return True
    else:
        return False


############################
def enviar_email(destinatario, sequencia):
    """
    Função que envia o código gerado para o e-mail especificado pelo Pretendente.
    :param destinatario: destino da mensagem (código)
    :param sequencia: código enviado na mensagem
    :return:
    """
    # Configuracoes do servidor de e-mail

    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_username = 'projeto.bot.discord.ifpb@gmail.com'
    smtp_password = 'ppjwpxvpprurppek'
    remetente = 'projeto.bot.discord.ifpb@gmail.com'

    # Cria o objeto de e-mail
    mensagem = 'Olá, \n\nSua sequência de verificação é: {}'.format(sequencia)

    # Conexão ao servidor do Gmail
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(smtp_username, smtp_password)

    # Envio do e-mail
    server.sendmail(remetente, destinatario, mensagem.encode('utf-8'))
    print('Email enviado com sucesso!')

    # Encerra a conexão ao servidor
    server.quit()


async def bane_usuario(member):
    """
    Função que bane um membro a partir do ID.
    :param member: É o membro que será banido
    """
    usuario_id = member.id

    tempo_banimento = 60  # TEMPO DE BANIMENTO EM SEGUNDOS

    embed = discord.Embed(title=constants.BAN_EMBED_TITULO,
                          description=constants.BAN_EMBED_DESCRICAO,
                          colour=constants.EMBED_COR)

    embed.add_field(name=constants.BAN_EMBED_FIELD_NOME, value=constants.BAN_EMBED_FIELD_VALOR)

    if member is not None:
        await member.send(constants.MENSAGEM_AUTENTICACAO_FALHA)
        await member.send(embed=embed)
        await member.guild.ban(member, reason='Tempo limite')
        print(f'Usuario banido por {tempo_banimento} segundos')

        await asyncio.sleep(tempo_banimento)
        await member.guild.unban(member)
    else:
        print('Usuario nao encontrado')


async def distribui_cargos(member, email):
    """
    Função responsável por distruibuir o cargo de professor ou aluno ao novo membro que entrou para o servidor
    :param member: O membro a qual será atribuido o novo cargo e removido o de Pretendente
    :param email: E-mail especificando se é aluno ou professor
    """
    guild = member.guild
    role_pretendente = discord.utils.get(guild.roles, name='Pretendente')
    if constants.DADOS_AP_FORMATO_EMAIL_ALUNO in email:
        role = discord.utils.get(guild.roles, name='Aluno')
        if role is not None:
            # adiciona cargo de aluno
            await member.add_roles(role)
            await member.remove_roles(role_pretendente)
        else:
            print('cargo vazio')
    elif constants.DADOS_AP_FORMATO_EMAIL_PROFESSOR in email:
        role = discord.utils.get(guild.roles, name='Professor')
        if role is not None:
            # adiciona cargo de professor
            await member.add_roles(role)
            await member.remove_roles(role_pretendente)
        else:
            print('cargo vazio')



############### ASYNC OU NAO ASYNC ############## ?
def encontra_nome_planilha(email, planilha):
    """
    Função responsável por identificar o e-mail de um Pretendente em uma coluna da planilha especificada e a partir
    disso identificar na coluna de nomes o nome correspondente aquele e-mail.
    :param email: E-mail do Pretendente
    :param planilha: Planilha que será usada para procurar o nome
    :return: O nome completo do Pretendente
    """

    tabela = pd.read_csv(planilha)

    # Colunas de Interesse
    c1 = ''
    if planilha == constants.DADOS_AP_NOME_PLANILHA_ALUNOS:
        c1 = constants.DADOS_AP_CABECALHO_PLANILHA_ALUNOS
    elif planilha == constants.DADOS_AP_CABECALHO_PLANILHA_PROFESSORES:
        c1 = constants.DADOS_AP_CABECALHO_PLANILHA_PROFESSORES
    c2 = 'Nome'

    email_conhecido = email
    nomes_coluna2 = tabela.loc[tabela[c1] == email_conhecido, c2].tolist()

    return nomes_coluna2[0]


async def altera_apelido(member, novo_apelido):
    """
    Função que altera o apelido de um usuário do servidor
    :param member: Membro que terá o apelido alterado para o nome completo
    :param novo_apelido: Nome completo do usuário que se tornará o novo apelido
    """
    try:
        await member.edit(nick=novo_apelido)
    except discord.Forbidden:
        print('Nao tenho permissao para alterar o apelido')
    except discord.HTTPException:
        print('Ocorreu um erro ao tentar alterar apelido')