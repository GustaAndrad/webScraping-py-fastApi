from time import sleep
import pandas
import unicodedata
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from twocaptcha import TwoCaptcha
import schemas.schemas as schemas


async def detran_mg(entrada_detran: schemas.EntradaDetranMG):

    # Variaveis
    site = 'https://www.detran.mg.gov.br/veiculos/situacao-do-veiculo/consultar-situacao-do-veiculo'
    placa = entrada_detran.placa
    chassi = entrada_detran.chassi
    listaRestricao = []
    listaMultas = []
    listaDados = []
    listaDesc = []

    # Key da api do 2captcha
    API_KEY = 'YOUR_KEY_API_FROM_2CAPTCHA'

    # configs da navegador
    options = Options()
    # options abaixo para rodar sem abrir navegador quando 'True'
    options.headless = True

    # Driver do navegador pelo DriverManager e acesso ao site
    navegador = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    navegador.get(site)
    sleep(2)

    # Digitar placa e chassi nos inputs
    navegador.find_element(By.ID, 'placa').send_keys(placa)
    navegador.find_element(By.ID, 'chassi').send_keys(chassi)

    # Quebrar captcha e clicar em pesquisar
    navegador.execute_script('var element=document.getElementById("g-recaptcha-response"); element.style.display="";')
    twoCaptcha = TwoCaptcha(API_KEY)
    try:
        result = twoCaptcha.recaptcha(
            sitekey='6LfVpnIUAAAAAHkISk6Z6juZcsUx6hbyJGwfnfPL',
            url=site)
    except Exception as e:
        print(e)
    else:
        print('code captcha: ' + str(result['code']))
        code = (result['code'])
        sleep(1)
        navegador.find_element(By.CSS_SELECTOR, '#g-recaptcha-response').send_keys(code)  # Captcha quebrado
        sleep(1)
        navegador.find_element(By.CSS_SELECTOR, '#content > form > button').click()  # clicar em pesquisar
        sleep(2)

        # Pagina de informaçoes do veiculo
        site = BeautifulSoup(navegador.page_source, 'html.parser')
        dados = site.findAll('dd')
        desc = site.findAll('dt')

        for valor in dados:
            dado = valor.get_text()
            dadoSemAcentos = ''.join(ch for ch in unicodedata.normalize('NFKD', dado) if not unicodedata.combining(ch))
            listaDados.append(dadoSemAcentos)

        for valor in desc:
            desc = valor.get_text()
            descSemAcentos = ''.join(ch for ch in unicodedata.normalize('NFKD', desc) if not unicodedata.combining(ch))
            listaDesc.append(descSemAcentos)

        dadosJson = pandas.DataFrame(listaDados, index=listaDesc, columns=['Dados veiculo'])

        # Informações de multas
        multas = site.findAll('td')

        for multa in multas:
            valor = multa.get_text()
            listaMultas.append(valor)
        multasJson = pandas.DataFrame(listaMultas, columns=['Debitos Detran'])

        # Entrar na pagina de restricao
        try:
            WebDriverWait(navegador, 5).until(
                expected_conditions.presence_of_element_located((By.XPATH,
                                                                 "// a [contains (text(), 'Veículo com Impedimentos e/ou Restrições')]"))
            )
            navegador.find_element(By.XPATH, "// a [contains (text(), 'Veículo com Impedimentos e/ou Restrições')]")\
                .click()
            sleep(2)
            paginaRestricao = BeautifulSoup(navegador.page_source, 'html.parser')
            divRestricoes = paginaRestricao.find('div', attrs={'id': 'content'})
            restricoes = divRestricoes.findAll('div', attrs={'class': 'row'})

            for restricao in restricoes:
                restricao = restricao.text.replace("- ", "")
                listaRestricao.append(restricao)

            restricoesJson = pandas.DataFrame(listaRestricao, columns=['Restricoes Detran'])

            # Unificar dados em um Json
            consulta = [dadosJson, multasJson, restricoesJson]
            jSonConsulta = pandas.DataFrame(consulta, index=['Dados', 'Multas', 'Restricoes'],
                                            columns=['Consulta Detran']).to_dict()

        except Exception as e:  # Caso nao tiver restriçoes
            print(e)
            # Unificar dados em um Json
            consulta = [dadosJson, multasJson]
            jSonConsulta = pandas.DataFrame(consulta, index=['Dados', 'Multas'],
                                            columns=['Consulta Detran']).to_dict()

        resposta: dict = jSonConsulta

        return resposta
