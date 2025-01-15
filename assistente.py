import os
import speech_recognition as sr
import webbrowser as browser
import requests
import re
from gtts import gTTS
from playsound import playsound
from datetime import datetime
from bs4 import BeautifulSoup
from translate import Translator
from pydub import AudioSegment
from pydub.playback import play


# Dicionário de programas
programas = {
    # Exemplo para o Firefox
    "navegador": r"C:\Program Files\Mozilla Firefox\firefox.exe",
    # Caminho para a discord
    "discord": r"C:\Users\DEV\AppData\Local\Discord\app-1.0.9177\Discord.exe",
    # Caminho para a notion
    "notion": r"C:\Users\DEV\AppData\Local\Programs\Notion\Notion.exe",
    # Caminho para o Brave navegador
    "bloco de notas": r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
    # Caminho para o Bloco de Notas
    "bloco de notas": r"C:\Windows\System32\notepad.exe",
    # Caminho para a Calculadora
    "calculadora": r"C:\Windows\System32\calc.exe",
    # Adicione outros programas conforme necessário
}


def cria_audio(audio, mensagem, lang='pt-br'):
    """Gera e reproduz áudio de texto."""
    try:
        tts = gTTS(mensagem, lang=lang)
        tts.save(audio)
        playsound(audio)
        os.remove(audio)
    except Exception as e:
        print(f"Erro ao criar áudio: {e}")


def monitora_audio():
    """Escuta e retorna o comando de voz."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Diga algo, estou te ouvindo...")
        try:
            audio = recognizer.listen(source)
            mensagem = recognizer.recognize_google(
                audio, language='pt-br').lower()
            print(f"Você disse: {mensagem}")
            return mensagem
        except sr.UnknownValueError:
            cria_audio(
                "não_entendi.mp3", "Desculpe, não consegui entender o que você disse. Pode repetir, por favor?")
            return None
        except sr.RequestError as e:
            cria_audio("erro_microfone.mp3",
                       f"Houve um problema no reconhecimento de voz.: {e}")
            return None


def melhora_audio(arquivo_audio):
    audio = AudioSegment.from_file(arquivo_audio)
    audio = audio.normalize()  # Normaliza o volume
    audio = audio.low_pass_filter(3000)  # Filtro para remover ruídos altos
    play(audio)


def noticias():
    """Obtém e lê as 5 principais notícias."""
    try:
        response = requests.get(
            'https://news.google.com/news/rss?ned=pt_br&gl=BR&hl=pt')
        noticias = BeautifulSoup(response.text, 'html.parser')
        mensagens = [item.title.text for item in noticias.find_all('item')[:5]]
        for mensagem in mensagens:
            cria_audio("noticia.mp3", mensagem)
    except Exception as e:
        print(f"Erro ao obter notícias: {e}")
        cria_audio("erro_noticias.mp3", "Erro ao obter notícias.")


def cotacao(moeda):
    """Obtém a cotação de uma moeda específica."""
    try:
        response = requests.get(
            f'https://economia.awesomeapi.com.br/all/{moeda}-BRL')
        dados = response.json()
        if moeda in dados:
            nome = dados[moeda]['name']
            data = dados[moeda]['create_date']
            valor = dados[moeda]['bid']
            cria_audio("cotacao.mp3", f"Cotação do {
                       nome} em {data}: {valor} reais.")
        else:
            cria_audio("erro_cotacao.mp3", "Moeda não encontrada.")
    except Exception as e:
        print(f"Erro ao obter cotação: {e}")
        cria_audio("erro_cotacao.mp3", "Erro ao obter cotação.")


def clima(cidade):
    """Obtém o clima de uma cidade específica."""
    token = "137cb54d58a1a69d7d052cabebf5998f"
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {"q": cidade, "appid": token, "lang": "pt", "units": "metric"}
    try:
        response = requests.get(base_url, params=params)
        dados = response.json()
        if dados.get("cod") == 200:
            temperatura = dados["main"]["temp"]
            umidade = dados["main"]["humidity"]
            descricao = dados["weather"][0]["description"]
            mensagem = (f"Em {cidade}, a temperatura é de {temperatura}°C, "
                        f"umidade de {umidade}% e condição: {descricao}.")
            cria_audio("clima.mp3", mensagem)
        else:
            cria_audio("erro_clima.mp3",
                       "Cidade não encontrada. Tente novamente.")
    except Exception as e:
        print(f"Erro ao obter clima: {e}")
        cria_audio("erro_clima.mp3", "Erro ao obter informações do clima.")


def tradutor(texto, idioma_destino):
    """Traduz texto para o idioma especificado."""
    try:
        idioma_origem = "pt" if idioma_destino == "en" else "en"
        translator = Translator(from_lang=idioma_origem,
                                to_lang=idioma_destino)
        traducao = translator.translate(texto)
        cria_audio("traducao.mp3", f"A tradução é: {
                   traducao}.", lang=idioma_destino)
    except Exception as e:
        print(f"Erro ao traduzir: {e}")
        cria_audio("erro_tradutor.mp3", "Erro ao traduzir.")


def calcula(mensagem):
    """Interpreta e realiza cálculos básicos."""
    try:
        # Verificar a mensagem original
        print(f"Mensagem recebida: {mensagem}")

        match = re.search(r"quanto é (.+)", mensagem)
        if not match:
            raise ValueError("Nenhuma operação encontrada.")

        operacao = match.group(1)
        print(f"Operação extraída: {operacao}")  # Antes das substituições

        # Substituições
        operacao = operacao.replace("mais", "+")
        operacao = operacao.replace("menos", "-")
        operacao = operacao.replace("vezes", "*")
        operacao = operacao.replace("dividido por", "/")
        print(f"Operação formatada: {operacao}")  # Após as substituições

        # Avaliar a operação matematicamente
        resultado = eval(operacao)
        print(f"Resultado do cálculo: {resultado}")  # Resultado do cálculo

        cria_audio("calculo.mp3", f"O resultado é {resultado}.")
    except ZeroDivisionError:
        cria_audio("erro_divisao.mp3",
                   "Não é possível dividir por zero. Tente novamente.")
    except ValueError as e:
        cria_audio("erro_entrada.mp3",
                   "Não entendi o cálculo. Certifique-se de usar números e operações válidas.")
        print(f"Erro de validação: {e}")
    except Exception as e:
        cria_audio("erro_calculo.mp3",
                   "Desculpe, ocorreu um erro ao realizar o cálculo. Tente novamente.")
        print(f"Erro ao calcular: {e}")



def executa_comandos(mensagem):
    """Executa ações com base no comando recebido."""
    if mensagem is None:
        return
    
    # Verificar se o comando começa com "Ana"
    if not mensagem.startswith("ana"):
        cria_audio("não_chama.mp3", "Você me chamou? Não consegui identificar.")
        return
    
    # Remove "Ana" do comando para processar o resto
    mensagem = mensagem.replace("Ana", "").strip()

    if any(palavra in mensagem for palavra in ["fechar", "encerrar", "sair"]):
        cria_audio("encerrando.mp3", "até logo!")
        exit() #Encerra o programa

    # Comando para cálculos básicos
    if "quanto é" in mensagem:
        calcula(mensagem)
        return
    
    elif "notícias" in mensagem:
        noticias()
    elif "cotação do" in mensagem:
        moeda = mensagem.split("cotação do")[-1].strip().upper()
        cotacao(moeda)
    elif "clima em" in mensagem:
        cidade = mensagem.split("clima em")[-1].strip()
        clima(cidade)
    elif "traduzir para inglês" in mensagem:
        cria_audio("traducao_pedir.mp3",
                   "O que você gostaria de traduzir para o inglês?")
        texto = monitora_audio()
        tradutor(texto, "en")
    elif "traduzir para português" in mensagem:
        cria_audio("traducao_pedir.mp3",
                   "O que você gostaria de traduzir para o português?")
        texto = monitora_audio()
        tradutor(texto, "pt")
    elif "abrir navegador" in mensagem:
        cria_audio("navegador.mp3", "Abrindo o navegador.")
        browser.open("https://www.google.com")
    elif any(palavra in mensagem for palavra in ["que horas são", "são que horas", "hora"]):
        hora_atual = datetime.now() .strftime("%H:%M")
        cria_audio("hora.mp3", f"agora são {hora_atual}.")
    elif "abrir" in mensagem:
        programa_desejado = mensagem.split("abrir")[-1].strip().lower()
        if programa_desejado in programas:
            cria_audio("abrir_programa.mp3", f"Abrindo {programa_desejado}.")
            try:
                # Abre o programa com base no dicionário
                os.startfile(programas[programa_desejado])
            except Exception as e:
                cria_audio("erro_abrir_programa.mp3",
                           f"Erro ao abrir {programa_desejado}: {e}")
        else:
            cria_audio("erro_programa.mp3",
                       "Desculpe, não encontrei o programa.")
    else:
        cria_audio("nao_entendido.mp3",
                   "Desculpe, ainda não sei como ajudar com isso. Pode tentar reformular o comando?")


def main():
    """Função principal."""
    cria_audio("ola.mp3", "Olá! Estou pronta para ajudar.")
    while True:
        mensagem = monitora_audio()
        executa_comandos(mensagem)


if __name__ == "__main__":
    main()