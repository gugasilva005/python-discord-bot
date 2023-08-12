import asyncio
import discord
from key import token
from discord.ext import commands, tasks
from funcoes import funcao_le_arquivos, enviar_email, bane_usuario, distribui_cargos, encontra_nome_planilha
from funcoes import altera_apelido
import constants
import random

TOKEN = token.get('TOKEN')


# ID's do canal de autenticação, do servidor e do cargo inicial de pretendente

CANAL_ID = constants.CANAL_AUTENTICACAO_ID              # ID DO CANAL DE AUTENTICAÇÃO
GUILD_ID = constants.ID_SERVIDOR                        # ID DO SERVIDOR
ROLE_ID = constants.ID_CARGO_PRETENDENTE                # ID DO CARGO - PRETENDENTE


# PARAMETROS E PERMISSÕES PARA ATUAÇÃO DO BOT

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.bans = True
bot = commands.Bot(intents=intents, command_prefix="!")


class VerificacaoState:
    def __init__(self, email):
        self.email = email
        self.codigo = None
        self.tentativas = 3



# FUNÇÃO ASSINCRONA QUE PREPARA O BOT

@bot.event
async def on_ready():
    print(f'{bot.user.name} está online')


# FUNÇÃO ASSINCRONA QUE VERIFICA SE A MENSAGEM NAO É DO PROPRIO BOT, EVITANDO LOOPING INFINITO

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.channel.id == CANAL_ID:
        await bot.process_commands(message)    # VERIFICA SE A MENSAGEM É DO CANAL DE AUTENTICAÇÃO E EXECUTA COMANDOS


# FUNÇÃO ASSINCRONA PARA NOVOS MEMBROS QUE ENTRAM NO SERVIDOR

@bot.event
async def on_member_join(member):
    guild = member.guild
    role = discord.utils.get(guild.roles, name='Pretendente')
    channel = discord.utils.get(guild.channels, name='canal-de-autenticação')
    usuario = member.name

    # CONFIGURAÇÕES DO EMBED INICIAL

    link = 'https://www.youtube.com/watch?v=U2yQ5MqlhUU'
    embed = discord.Embed(
        title=constants.EMBED_TITULO,
        description=constants.EMBED_DESCRICAO,
        colour=constants.EMBED_COR
    )

    embed.set_image(url=constants.EMBED_URL_IMAGEM)

    embed.add_field(name='LINK', value=link)

    # ENVIA TEXTO DE BOAS VINDAS E O EMBED INICIAL

    await channel.send(f"Olá, {usuario} " + constants.TEXTO_BOAS_VINDAS)
    await channel.send(embed=embed)

    # DEFINE CARGO DE PRETENDENTE PARA NOVOS MEMBROS

    if role is not None:
        await member.add_roles(role)
        print(f'Added role {role.name} to {member.name}')
    else:
        print(f'Role not found in server {guild.name}. Make sure the role exists.')


    # INICIA LAÇO PARA ENVIAR E-MAIL

    tentativas_email = 0
    email = ""
    ban = False
    while True:
        channel_id = CANAL_ID
        channel = bot.get_channel(channel_id)
        if tentativas_email == 3:
            ban = True
            break
        else:
            resposta_email = await bot.wait_for('message', check=lambda x: x.author == member)
            tentativas_email += 1
            email_a_verificar = str(resposta_email.content).lower()
            if constants.DADOS_AP_FORMATO_EMAIL_ALUNO in email_a_verificar or constants.DADOS_AP_FORMATO_EMAIL_PROFESSOR in email_a_verificar:

                # LE AS PLANILHAS DE PROFESSORES E ALUNOS

                le_planilha_alunos = funcao_le_arquivos(constants.DADOS_AP_NOME_PLANILHA_ALUNOS,
                                                        constants.DADOS_AP_CABECALHO_PLANILHA_ALUNOS, email_a_verificar)
                le_planilha_professores = funcao_le_arquivos(constants.DADOS_AP_NOME_PLANILHA_PROFESSORES,
                                                             constants.DADOS_AP_CABECALHO_PLANILHA_PROFESSORES,
                                                             email_a_verificar)
                # SALVA O CODIGO DE VERIFICACAO

                codigo_verificacao = {}

                # SALVA O E-MAIL NA VARIAVEL E-MAIL

                email = (str(email_a_verificar)).lower().strip()
                print(email)

                # VERIFICA SE O EMAIL PRESENTE NA MENSAGEM LIDA CONSTA EM UMA DAS PLANILHAS

                if le_planilha_alunos == True or le_planilha_professores == True:

                    # GERA UMA SEQUENCIA DE NUMEROS ALEATORIOS QUE SERAO ENVIADOS PARA O EMAIL

                    sequencia = ''.join(random.choices('0123456789', k=6))

                    # ENVIA UMA MENSAGEM PARA O EMAIL COM A SEQUENCIA GERADA

                    enviar_email(email, sequencia)

                    # SALVA O CÓDIGO GERADO E O EMAIL DO DESTINATARIO

                    codigo_verificacao[email] = VerificacaoState(email)
                    codigo_verificacao[email].codigo = sequencia

                    # ENVIA UMA MENSAGEM NO DISCORD AVISANDO SOBRE O ENVIO DO EMAIL COM O CÓDIGO

                    print(constants.MENSAGEM_QUE_ENVIA_CODIGO_EMAIL)

                    await channel.send(constants.MENSAGEM_QUE_ENVIA_CODIGO_EMAIL + f' {email}' + constants.MENSAGEM_QUE_ENVIA_CODIGO_EMAIL_2)

                    # INICIA LAÇO PARA VERIFICAÇÃO DO CODIGO ENVIADO PARA O EMAIL

                    for attemps in range(3):

                        resposta_codigo = await bot.wait_for('message', check=lambda x: x.author.id == member.id)
                        codigo = resposta_codigo.content
                        print('E-mail consta dentro do banco de dados')

                        # VERIFICA SE O CODIGO DIGITADO É IGUAL AO QUE FOI ENVIADO PARA O EMAIL

                        if codigo_verificacao[email].codigo == codigo:
                            del codigo_verificacao[email]
                            print(constants.MENSAGEM_AUTENTICACAO_BEM_SUCEDIDA)
                            await channel.send(constants.MENSAGEM_AUTENTICACAO_BEM_SUCEDIDA + f' {email}')
                            break
                        else:
                            codigo_verificacao[email].tentativas -= 1
                            if codigo_verificacao[email].tentativas == 0:
                                del codigo_verificacao[email]
                                print(constants.MENSAGEM_AUTENTICACAO_FALHA)
                                ban = True
                                break
                            else:
                                print(constants.MENSAGEM_ERRO_CODIGO)
                                await channel.send(constants.MENSAGEM_ERRO_CODIGO)
                    break

                else:
                    print(constants.MENSAGEM_NAO_CONSTA_PLANILHAS)
                    await channel.send(constants.MENSAGEM_NAO_CONSTA_PLANILHAS)

            else:
                print(constants.MENSAGEM_EMAIL_FORA_DOS_PADROES)
                await channel.send(constants.MENSAGEM_EMAIL_FORA_DOS_PADROES)

    # ARRUMAR CONDICIONAL, COLOCAR OS 15 MINUTOS
    if ban == True:
        await bane_usuario(member)
        print('Banimento')
    else:
        planilha = ''
        if constants.DADOS_AP_FORMATO_EMAIL_ALUNO in email:
            planilha = constants.DADOS_AP_NOME_PLANILHA_ALUNOS
        elif constants.DADOS_AP_FORMATO_EMAIL_PROFESSOR in email:
            planilha = constants.DADOS_AP_NOME_PLANILHA_PROFESSORES
        nome = encontra_nome_planilha(email, planilha)
        print('Alterar cargos')
        print(nome)
        await distribui_cargos(member, email)
        await altera_apelido(member, nome)

bot.run(TOKEN)
