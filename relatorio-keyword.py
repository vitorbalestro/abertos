import tweepy
import subprocess
import time
import regex as re
import pandas as pd
import matplotlib.pyplot as plt
import datetime

# TOKENS DE AUTENTIFICAÇÃO
auth = tweepy.OAuthHandler('', '')
auth.set_access_token('','')

api = tweepy.API(auth, wait_on_rate_limit=True)

AMOUNT = 1200
SIZE = 50
PARAMETRO = 20
AMOUNTRTS = 1000


def deEmojify(text):
    # evita emoticons e outros caracteres não-existentes no pacote utf8 do LaTeX.

    regrex_pattern = re.compile(pattern="["
                                        u"\U0001F600-\U0001F64F"  # emoticons
                                        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                        u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                        u"\U00002500-\U00002BEF"  # chinese char
                                        u"\U00002702-\U000027B0"
                                        u"\U00002702-\U000027B0"
                                        u"\U000024C2-\U0001F251"
                                        u"\U0001f926-\U0001f937"
                                        u"\U00010000-\U0010ffff"
                                        u"\u2640-\u2642"
                                        u"\u2600-\u2B55"
                                        u"\u2070"
                                        u"\u200d"
                                        u"\u23cf"
                                        u"\u23e9"
                                        u"\u231a"
                                        u"\ufe0f"  # dingbats
                                        u"\u3030"
                                        "]+", flags=re.UNICODE)
    return regrex_pattern.sub(r'', text)


def conversorData(string):
    """Converte a data para uma string válida.

        Recebe uma data em formato inválido e a converte para uma string em
        formato válido.

        Args:
            string: data em formato inválido.
        Retorna:
            dataPorExtenso: data em formato válido (string).
        """

    listaString = list(string)
    dicionarioMes = {'Jan': 'Janeiro', 'Feb': 'Fevereiro', 'Mar': 'Março',
                     'Apr': 'April', 'May': 'Maio', 'Jun': 'Junho', 'Jul': 'Julho',
                     'Aug': 'Agosto', 'Sep': 'Setembro', 'Oct': 'Outubro', 'Nov': 'Novembro',
                     'Dec': 'Dezembro'}
    dicionarioDia = {'Mon': 'segunda-feira', 'Tue': 'terça-feira', 'Wed': 'quarta-feira',
                     'Thu': 'quinta-feira', 'Fri': 'sexta-feira', 'Sat': 'sábado',
                     'Sun': 'domingo'}

    diaSemana = dicionarioDia["".join(listaString[0:3])]
    mes = dicionarioMes["".join(listaString[4:7])]
    if listaString[9] == " ":
        dia = listaString[8]
        hora = "".join(listaString[10:12])
        minuto = "".join(listaString[13:15])
    else:
        dia = "".join(listaString[8:10])
        hora = "".join(listaString[11:13])
        minuto = "".join(listaString[14:16])

    ano = "".join(listaString[len(listaString) - 4:len(listaString)])

    dataPorExtenso = '{} de {} de {} ({}), às {} horas e {} minutos '.format(dia, mes, ano, diaSemana, hora, minuto)

    return dataPorExtenso


def lista_tweets_usuario(userID):
    # a função recebe um userID no formato da arroba entre aspas simples
    """Cria uma lista com os autores do tweets.

       Recebe os autores dos tweets e os aloca em uma lista.

       Args:
           userID: Id do usuário a ser inserido
       Retorna:
           lista_tweet_user: Lista com os autores dos tweets
       """

    tweets_user = api.user_timeline(screen_name=userID,
                                    count=SIZE,
                                    include_rts=False,
                                    tweet_mode='extended')

    lista_tweet_user = []
    for each_json_tweet in tweets_user:
        lista_tweet_user.append(each_json_tweet._json)

    return lista_tweet_user


def all_last_tweets(search_words):
    # recebe a palavra-chave e chama da API os ultimos tweets.
    # Após, criamos uma lista de dicionários em que cada dicionário é um tweet
    # com as infos que desejamos.

    cursor_tweets = tweepy.Cursor(api.search, q=search_words, lang='pt', tweet_mode='extended').items(AMOUNT)

    tweet_list = []
    for each_json_tweet in cursor_tweets:
        tweet_list.append(each_json_tweet._json)

    lista_tweet = []
    for i in range(0, len(tweet_list)):
        Texto = tweet_list[i]["full_text"]
        Username = tweet_list[i]["user"]["screen_name"]
        Contagem = tweet_list[i]["retweet_count"]
        HoraPostagem = tweet_list[i]["created_at"]
        try:
            Hora = tweet_list[i]["retweeted_status"]["created_at"]
        except:
            Hora = 0
        lista_tweet.append({'Username': str(Username),
                            'Texto': str(Texto),
                            'Total RTs': Contagem,
                            'Hora': Hora,
                            'HoraPostagem': HoraPostagem})

    return lista_tweet


def tweetsEmListaSemRepeticao(search_words):
    lista_completa = TODOSTUITES

    lista_completa_sem_repeticao = []

    for i in range(0, len(lista_completa)):
        if lista_completa[i]['Texto'] not in lista_completa_sem_repeticao:
            lista_completa_sem_repeticao.append(lista_completa[i]['Texto'])

    lista_de_ocorrencias = []

    for tweet in lista_completa_sem_repeticao:
        lista_de_usuarios = []
        for i in range(0, len(lista_completa)):
            if lista_completa[i]['Texto'] == tweet and \
                    lista_completa[i]['Username'] not in lista_de_usuarios:
                Total = lista_completa[i]['Total RTs']
                Hora = lista_completa[i]['Hora']
                lista_de_usuarios.append(lista_completa[i]['Username'])
        lista_de_ocorrencias.append({'Tweet': tweet,
                                     'Quantidade': int(len(lista_de_usuarios)),
                                     'Autor': 'Vários',
                                     'Total RTs': Total,
                                     'Hora': Hora})

    return lista_de_ocorrencias  # {'Tweet', 'Quantidade', 'Usuarios que postaram'}, ordem
    # decrescente de quantidades.


def principaisTweetsAutores(search_words):
    # cria a lista dos autores dos principais tweets (mais retuitados).

    lista = tweetsEmListaSemRepeticao(search_words)

    resultados_filtrados_2 = []
    for dict in lista:
        if dict['Total RTs'] >= AMOUNTRTS:
            resultados_filtrados_2.append(dict)

    for i in range(0, len(resultados_filtrados_2) - 1):
        for j in range(i + 1, len(resultados_filtrados_2)):
            if resultados_filtrados_2[i]['Total RTs'] < resultados_filtrados_2[j]['Total RTs']:
                armazena = resultados_filtrados_2[i]
                resultados_filtrados_2[i] = resultados_filtrados_2[j]
                resultados_filtrados_2[j] = armazena

    return resultados_filtrados_2


def stringSaidaPrincipaisTuites(search_words):
    listaTweets = principaisTweetsAutores(search_words)

    if listaTweets == []:
        return 'Não houve tuítes retuitados mais do que' + ' {} vezes.'.format(AMOUNTRTS)

    else:
        stringSaida = ""
        for dict in listaTweets:
            if dict['Hora'] == 0:
                stringAux = 'A hora da postagem não pode ser obtida.' + r"""\\"""
            else:
                stringAux = 'O tuíte foi postado em ' + '{}'.format(conversorData(dict['Hora'])) + r"""\\"""
            tweet = deEmojify(dict['Tweet'])
            if tweet[0] == 'R' and tweet[1] == 'T':
                stringSaida += r"""
                \noindent O tuíte
                \begin{quote}    
                \begin{verbatim}""" + '{}...'.format(tweet[0:min(len(tweet), 70)]) + \
                               r""" 
                               \end{verbatim}
                               \end{quote}
                            \noindent foi retuitado """ + '{} '.format(dict['Total RTs']) + \
                               r"""vezes no total. """ + stringAux + r"""\\"""

        return stringSaida


def TTslist(WOE_ID):
    # WOE_ID = 23424768  codigo do Brasil

    BR_trends = api.trends_place(WOE_ID)

    trends_list = []
    for trend in BR_trends[0]["trends"]:
        trends_list.append(trend["name"])

    return trends_list


def agregador(dicionario):
    dicionario_agregado = {}
    for i in range(0, 25):
        soma = dicionario[4 * i] + dicionario[4 * i + 1] + dicionario[4 * i + 2] + dicionario[4 * i + 3]
        dicionario_agregado['{}-{}'.format(4 * i, 4 * i + 3)] = soma

    return dicionario_agregado


def ordenacao(lista):  # ordena uma lista de forma não-crescente
    n = len(lista)
    for i in range(0, n - 1):
        for j in range(i + 1, n):
            if lista[j] < lista[i]:
                a = lista[i]
                lista[i] = lista[j]
                lista[j] = a

    return None


def contador(lista):
    ordenacao(lista)

    dicionario = {}

    for chave in range(0, len(lista)):
        k = 0
        for i in range(0, len(lista)):
            if lista[i] == chave:
                k += 1
        dicionario[chave] = k

    return dicionario


def RTpercent(userID):
    # a função recebe um userID no formato da arroba entre aspas simples
    # calcula a porcentagem dos últimos tweets do usuário que são RTs

    tweets_user = api.user_timeline(screen_name=userID,
                                    count=SIZE,
                                    include_rts=True,
                                    )

    lista_tweet_user = []
    for each_json_tweet in tweets_user:
        lista_tweet_user.append(each_json_tweet._json)
    size = len(lista_tweet_user)
    RT_lista = []
    for i in range(0, size):
        try:
            RTbool = lista_tweet_user[i]["retweeted_status"]["retweet_count"]
        except KeyError:
            RT_lista.append({'RT'})

    n = len(RT_lista)
    if size == 0:
        return 0
    else:
        return int((size - n) * 100 / size)


def distribuicaoRT(keyword):
    users_list = []
    deleted_users_list = []
    RT_percent_list = []
    RT_percent_deleted = []
    current_list = TODOSTUITES
    amount = len(current_list)
    for i in range(0, amount):
        userID = current_list[i]['Username']
        if userID in users_list:
            users_list.remove(userID)
            deleted_users_list.append(userID)
        else:
            users_list.append(userID)

    for userID in users_list:
        RT_percent_list.append(RTpercent(userID))

    for userID in deleted_users_list:
        RT_percent_deleted.append(RTpercent(userID))

    RT_percent_dict = contador(RT_percent_list)
    count = agregador(RT_percent_dict)

    RT_percent_deleted = contador(RT_percent_deleted)
    count_deleted = agregador(RT_percent_deleted)

    df = pd.DataFrame.from_dict(count, orient='index')
    df.plot(kind='bar')
    plt.savefig('Legitimo.png')

    df = pd.DataFrame.from_dict(count_deleted, orient='index')
    df.plot(kind='bar')
    plt.savefig('Deletado.png')

    return [len(users_list), len(deleted_users_list)]


def horaInt(stringDataHora):
    data_lista = list(stringDataHora.split())
    hora_lista_str = list(data_lista[3].split(':'))
    hora_lista_int = list(map(int, hora_lista_str))

    return hora_lista_int


# a função abaixo recebe duas listas de horário como acima e calcula a diferença em minutos

def tempoDecorrido(hora_lista_1, hora_lista_2):
    h = (hora_lista_1[0] - hora_lista_2[0]) * 60
    m = hora_lista_1[1] - hora_lista_2[1] + h
    if hora_lista_1[2] >= hora_lista_2[2]:
        s = hora_lista_1[2] - hora_lista_2[2]
    else:
        m = m - 1
        s = 60 + hora_lista_1[2] - hora_lista_2[2]

    return [m, s]


def tempoString():
    hora_1 = horaInt(TODOSTUITES[0]['HoraPostagem'])
    hora_2 = horaInt(TODOSTUITES[len(TODOSTUITES) - 1]['HoraPostagem'])

    string = 'Os últimos ' + '{} '.format(AMOUNT) + 'tuítes com a palavra-chave foram postados em ' + \
             '{} minutos e {} segundos'.format(tempoDecorrido(hora_1, hora_2)[0], tempoDecorrido(hora_1, hora_2)[1])

    return string


def distribuicaoRTPizza():
    lista = TODOSTUITES
    users_list = []
    for dict in lista:
        if dict['Username'] not in users_list:
            users_list.append(dict['Username'])

    RT_percent_list = []
    for user in users_list:
        percent = RTpercent(user)
        RT_percent_list.append(percent)

    list_0_25 = []
    list_25_50 = []
    list_50_75 = []
    list_75_100 = []

    for percent in RT_percent_list:
        if percent <= 25:
            list_0_25.append(percent)
        elif percent > 25 and percent <= 50:
            list_25_50.append(percent)
        elif percent > 50 and percent <= 75:
            list_50_75.append(percent)
        else:
            list_75_100.append(percent)

    labels = '0%-25%', '25%-50%', '50%-75%', '75%-100%'
    sizes = [len(list_0_25), len(list_25_50), len(list_50_75), len(list_75_100)]

    graficopizza, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels, autopct='%1.1f', shadow=True, startangle=90)
    ax1.axis('equal')

    plt.savefig('graficopizza.png')


################# SISTEMA DE SCORES ####################


def verificar_data_criacao(usuario):
    """Verifica a data de criação do usuário.

        Caso ele tenha sido criado no dia da verificação, aumenta em 20% a chance de ser bot.
        Caso ele tenha sido criado nos últimos 7 dias, aumenta em 10% a chance de ser bot.
        Se nenhum desses casos se aplicar, não aumenta a chance de ser bot.

        Args:
            usuario: user-object (json) recebido da API.
        Retorna:
            Pontuação atribuida, em decimal.
        """

    data_atual = datetime.datetime.today()
    data_criacao = usuario.created_at

    if data_atual - data_criacao == datetime.timedelta(days=0):
        return 0.2

    elif data_atual - data_criacao <= datetime.timedelta(days=7):
        return 0.1

    else:
        return 0


def verificar_nome(usuario):
    """Verifica o '@' do usuário.

       Caso o usuário tenha o nome padrão (Nome do usuário + 8 dígitos),
       aumenta em 10% a chance de ser bot. Se não for o nome padrão, não
       aumenta a chance de ser bot.

       Args:
           usuario: user-object (json) recebido da API.
       Retorna:
           Pontuação atribuida, em decimal.
       """

    if re.search(r".\d{8}", usuario.screen_name):  # Verifica se o nome é seguido por 8 dígitos quaisquer
        return 0.1

    else:
        return 0


def verificar_descricao(usuario):
    """Verifica a descrição do usuário.

       Caso não exista uma, aumenta em 10% a chance de ser bot.
       Se o usuário tiver uma descrição, não aumenta a chance de ser bot.

       Args:
           usuario: user-object (json) recebido da API.
       Retorna:
           Pontuação atribuida, em decimal.
       """

    if usuario.description == "":
        return 0.1

    else:
        return 0


def verificar_qnt_seguidores(usuario):
    """Verifica a quantidade de seguidores do usuário.

        Caso o usuário tenha até 20 seguidores,
        aumenta em 20% a chance de ser bot. Caso tenha mais do que 20 e menos de 100, aumenta em 10%.
        Se o usuário tiver mais que 100
        seguidores, não aumenta a chance de ser bot.

        Args:
            usuario: user-object (json) recebido da API.
        Retorna:
            Pontuação atribuida, em decimal.
        """

    if usuario.followers_count <= 20:
        return 0.3

    elif usuario.followers_count <= 100:
        return 0.2

    else:
        return 0


def verificar_tweets(usuario):
    """Verifica a quantidade de tweets e retweets do usuário.

        Caso o usuário tenha menos que 100 tweets e retweets, aumenta em 10%
        a chance de ser bot. Se o usuário tiver mais que 10 tweets, não aumenta
        a chance de ser bot.

        Args:
            usuario: user-object (json) recebido da API.
        Retorna:
            Pontuação atribuida, em decimal.
        """

    if usuario.statuses_count < 100:
        return 0.1

    else:
        return 0


def verificar_img_perfil(usuario):
    """Verifica se o usuário possui foto de perfil.

        Caso o usuário use a foto padrão do Twitter (sem foto), aumenta em 20%
        a chance de ser bot. Se o usuário tiver uma foto de perfil definida,
        não aumenta a chance de ser bot.

        Args:
            usuario: user-object (json) recebido da API.
        Retorna:
            Pontuação atribuida, em decimal.
        """

    if usuario.default_profile_image:
        return 0.2

    else:
        return 0


def verificar_RT_percent(usuario):
    """Verifica a quantidade de RT's do usuário

       Se o usuário tiver 75 RT's ou mais, aumenta em 40% a chance de ser bot.
       Se o usuário tiver 50 RT's ou mais, aumenta em 10% a chance de ser bot.
       Caso contrário, nenhum aumenta a chance de ser bot.

       Args:
           usuario: user-object (json) recebido da API.
       Retorna:
           Pontuação atribuida, em decimal.
       """
    if RTpercent(usuario) >= 75:
        return 0.4
    elif RTpercent(usuario) >= 50:
        return 0.1
    else:
        return 0


def pontuar_usuario(id_usuario):
    """Pontua o usuário com base nos retornos das funções de verificação.

        Pede para a API pegar o usuário (user-object) com base no seu id,
        e o armazena em 'usuario_analisado'. Depois, inicializa a pontuação
        do usuário como '0.0' em 'pontuação_usuario'. Então, armazena as
        funções de verificação em 'lista_verificacoes' e executa cada uma
        com o 'usuario_analisado' como argumento. A cada função executada,
        soma o resultado com 'pontuacao_usuario'.

        Args:
            id_usuario: id referente a um usuário. (recebido da API)
        Retorna:
            A pontuação final do usuário, como float.
        """

    usuario_analisado = api.get_user(id_usuario)
    pontuacao_usuario = 0

    # Lista que armazena as funções de verificação.
    lista_verificacoes = [verificar_data_criacao, verificar_nome,
                          verificar_descricao, verificar_qnt_seguidores, verificar_tweets,
                          verificar_img_perfil, verificar_RT_percent]

    # Atribui cada função de verificação à variável verificação.
    for verificacao in lista_verificacoes:
        pontuacao_usuario += verificacao(usuario_analisado)

    return pontuacao_usuario


def bots():
    """Verifica se o usuário é um bot com base na pontuação atribuida.

        Pega o autor do tweet e verifica se ele possui mais do que 40% de
        chance de ser um bot. Se possuir, aumenta o número de bots em 1.
        Caso contrário, não aumenta o número de bots.

        Retorna:
            number_bots: número de bots encontrados pelo sistema de pontos.
        """

    number_bots = 0
    for tweet in TODOSTUITES:
        usuario = tweet['Username']
    if pontuar_usuario(usuario) >= 0.39:
        number_bots += 1

    return number_bots


################################################ FIM DO SISTEMA DE SCORES ###########################

def produzRelatorio(keyword):
    """Produz um relatório, em PDF, do resultado obtido.

        Prepara o arquivo .PDF e, após isso, adiciona as informações obtidas nele.

        Args:
            keyword: Palavra chave a ser usada para a pesquisa.
            """

    texto = r"""\documentclass[a4paper,12pt]{article}


    \usepackage[textwidth=125mm, textheight=195mm]{geometry}
    \usepackage[brazilian]{babel}
    \usepackage{graphicx}
    \usepackage{amsmath}
    \usepackage{amsfonts}
    \usepackage{amsthm}
    \usepackage{fancyvrb,cprotect}
    \usepackage{epstopdf}
    \usepackage{color}
    \usepackage{lipsum}
    \usepackage[center]{caption}
    \usepackage[utf8]{inputenc}

    \makeatletter
\def\UTFviii@defined#1{%
  \ifx#1\relax
      ?%
  \else\expandafter
    #1%
  \fi
}

\makeatother
    \usepackage{verbatim}


    \geometry{verbose,a4paper,tmargin=20mm,bmargin=30mm,lmargin=19mm,rmargin=19mm}


    \begin{document} 

    \begin{center} \end{center}
    \begin{center} \Large{Relatório de busca por palavra-chave:} \verb|""" + '{}'.format(keyword) + \
            r"""|
            \end{center}
            \begin{center} Em """ + '{}'.format(conversorData(tempoAtual)) + r"""  \end{center}

    \section{Dados gerais}""" + \
            '{}'.format(tempoString()) + \
            r"""\section{Tuítes com mais RTs}
        
                    Os \emph{principais tuítes} contendo determinada palavra-chave são definidos como aqueles
                    que foram retuitados pelo menos """ + '{}'.format(AMOUNTRTS) + r""" vezes. A busca feita pelo algoritmo pode não ser exaustiva:
            Consideramos apenas os últimos """ + '{}'.format(AMOUNT) + r""" tuítes com a palavra-chave. Assim,
            tuítes com mais de """ + '{}'.format(AMOUNTRTS) + r""" RTs no total mas sem ocorrência dentre os últimos 
            """ + '{}'.format(AMOUNT) + r""" tuítes com a palavra-chave não aparecerão abaixo.
            \\

            """ + \
            r"""\noindent$\bullet$ Palavra-chave: \verb|""" + '{}'.format(keyword) + \
            r"""|\\

            """ + \
            stringSaidaPrincipaisTuites(keyword) + \
            r"""
            \section{Distribuição de usuários por porcentagem de RTs}

            Para cada usuário que tuitou a palavra-chave, calculamos a porcentagem dos últimos """ + \
            '{}'.format(SIZE) + r""" que são retuítes (RTs). Um percentual muito alto de RTs é um indício de que a
            conta é dedicada à impulsionamentos ilegítimos. 

            Recebemos os últimos """ + '{} '.format(AMOUNT) + r""" tuítes contendo a palavra-chave
            e calculamos o percentual de RTs dentre os últimos """ + '{}'.format(SIZE) + r""" tuítes de 
            cada usuário. Construímos abaixo dois gráficos com a distribuição destes usuários
            por porcentagem de RTs. O primeiro deles refere-se aos """ + '{} '.format(qtde_usuarios[0]) + \
            r"""usuários que postaram apenas um tuite
            com a palavra-chave. O segundo traz 
            os """ + '{} '.format(qtde_usuarios[1]) + \
            r"""usuários que postaram mais de um tuíte com a palavra-chave 
            (sempre dentre os últimos """ + '{} tuítes). '.format(AMOUNT) + r"""

            \begin{figure}[!h]
            \centering
            \includegraphics[scale = 0.7]{Legitimo.png}
            \caption{Distribuição por porcentagem de RTs dos usuários que postaram apenas 
            um tuíte contendo a palavra-chave.}
            \end{figure}

            \begin{figure}[!h]
            \centering
            \includegraphics[scale = 0.7]{Deletado.png}
            \caption{Distribuição por 
            porcentagem de RTs dos usuários que postaram mais de um tuíte contendo a palavra-chave.}
            \end{figure}

            Abaixo destes, um gráfico do tipo \emph{pie} mostra a proporção de usuários em cada 
            faixa de porcentagem de RTs. Uma proporção muito grande na faixa de 75\% a 100\% 
            pode ser um indicativo de que muitas contas ilegítimas tuitaram a palavra-chave.

            \begin{figure}[!h]
            \centering
            \includegraphics{graficopizza.png}
            \caption{Distribuição por porcentagem de RTs dos usuários.}
            \end{figure}

            \section{Contas \emph{bot}}

            Alguns parâmetros além da porcentagem de RTs podem indicar que determinada conta 
            é um \emph{bot}, isto é, uma conta com postagens automatizadas. Propomos criar um sistema 
            de \emph{scores} baseados nestes parâmetros. Um \emph{score} alto significa alta probabilidade
            de determinada conta ser uma conta \emph{bot}.
            Para exemplificar, alguns dos parâmetros considerados são: quantidade de total de seguidores,
            quantidade total de postagens, usuário sem foto de perfil e data de criação da conta.

            Dentre os usuários que postaram os últimos """ + '{} tuítes'.format(AMOUNT) + r""" 
            com a palavra chave, há """ + '{}'.format(bots()) + r""" perfis com alta probabilidade de serem bots.

            \end{document}"""

    with open("Relatorio10.tex", "w") as tex_file:
        tex_file.write(texto)

    subprocess.call(["pdflatex", "Relatorio10.tex"])


tempoAtual = time.ctime()

# listaTTs = TTslist(23424768)

keyword = ''
TODOSTUITES = all_last_tweets(keyword)
distribuicaoRTPizza()

# Abaixo, pode ocorrer erro: a hora recebida é a hora original. Se um dos
# tuites é RT, a hora não será a hora em que o tuite foi retuitado, e sim a hora
# original do tuite.

hora_1 = horaInt(TODOSTUITES[0]['HoraPostagem'])
hora_2 = horaInt(TODOSTUITES[len(TODOSTUITES) - 1]['HoraPostagem'])

qtde_usuarios = distribuicaoRT(keyword)
produzRelatorio(keyword)

