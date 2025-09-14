import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException

def raspar_quotes_com_selenium():
    """
    Função para fazer o web scraping do site quotes.toscrape.com usando Selenium,
    coletando todas as citações, autores e tags de todas as páginas.

    Retorna:
        list: Uma lista de dicionários, onde cada dicionário representa uma citação.
    """
    # Configura opções do Chrome para melhor performance
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Executa sem interface gráfica (mais rápido)
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Configura e inicializa o navegador Chrome automaticamente
    try:
        driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()),
            options=chrome_options
        )
        print("Navegador Chrome inicializado com sucesso.")
    except WebDriverException as e:
        print(f"Erro ao inicializar o navegador: {e}")
        return []
    
    # URL inicial a ser acessada
    url = "http://quotes.toscrape.com/"
    
    try:
        driver.get(url)
        print(f"Acessando: {url}")
        
        # Aguarda a página carregar completamente
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'quote'))
        )
        
    except TimeoutException:
        print("Timeout: A página demorou muito para carregar.")
        driver.quit()
        return []
    except WebDriverException as e:
        print(f"Erro ao acessar a página: {e}")
        driver.quit()
        return []
    
    lista_de_quotes = []
    pagina_atual = 1

    while True:
        print(f"Raspando página {pagina_atual}: {driver.current_url}")
        
        try:
            # Aguarda os elementos de citação carregarem
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'quote'))
            )
            quotes = driver.find_elements(By.CLASS_NAME, 'quote')
            
            if not quotes:
                print("Nenhuma citação encontrada na página atual.")
                break
                
        except TimeoutException:
            print("Timeout: Elementos de citação não carregaram.")
            break

        # Itera sobre cada contêiner para extrair os dados
        for i, quote in enumerate(quotes, 1):
            try:
                # Extrai o texto da citação (elemento com a classe 'text')
                texto_element = quote.find_element(By.CLASS_NAME, 'text')
                texto = texto_element.text.strip('""').strip('""')
                
                # Extrai o nome do autor (elemento com a classe 'author')
                autor_element = quote.find_element(By.CLASS_NAME, 'author')
                autor = autor_element.text
                
                # Extrai as tags (elementos com a classe 'tag')
                tags_elementos = quote.find_elements(By.CLASS_NAME, 'tag')
                tags = [tag.text for tag in tags_elementos]

                # Adiciona os dados extraídos como um dicionário à lista
                quote_data = {
                    'citacao': texto,
                    'autor': autor,
                    'tags': tags,
                    'pagina': pagina_atual
                }
                lista_de_quotes.append(quote_data)
                
            except NoSuchElementException as e:
                print(f"Erro ao extrair dados da citação {i} na página {pagina_atual}: {e}")
                continue
            except Exception as e:
                print(f"Erro inesperado na citação {i}: {e}")
                continue

        # Tenta encontrar e clicar no botão "Next"
        try:
            # Aguarda o botão "Next" estar presente e clicável
            botao_next = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'li.next a'))
            )
            
            # Scroll para o botão para garantir que está visível
            driver.execute_script("arguments[0].scrollIntoView();", botao_next)
            time.sleep(0.5)
            
            botao_next.click()
            pagina_atual += 1
            
            # Pequena pausa para evitar sobrecarga do servidor
            time.sleep(1)
            
        except (NoSuchElementException, TimeoutException):
            # Se o botão "Next" não for encontrado, significa que estamos na última página
            print(f"Não há mais páginas para raspar. Total de páginas processadas: {pagina_atual}")
            break
        except Exception as e:
            print(f"Erro ao navegar para a próxima página: {e}")
            break

    # Fecha o navegador ao final do processo
    print("Fechando o navegador...")
    driver.quit()
    
    return lista_de_quotes

def salvar_resultados(dados, formato='json'):
    """
    Salva os resultados em arquivo.
    
    Args:
        dados (list): Lista de citações coletadas
        formato (str): Formato do arquivo ('json' ou 'txt')
    """
    if not dados:
        print("Nenhum dado para salvar.")
        return
    
    if formato == 'json':
        with open('quotes_coletadas.json', 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        print("Dados salvos em 'quotes_coletadas.json'")
    
    elif formato == 'txt':
        with open('quotes_coletadas.txt', 'w', encoding='utf-8') as f:
            for i, quote in enumerate(dados, 1):
                f.write(f"Citação {i}:\n")
                f.write(f"Texto: {quote['citacao']}\n")
                f.write(f"Autor: {quote['autor']}\n")
                f.write(f"Tags: {', '.join(quote['tags'])}\n")
                f.write(f"Página: {quote['pagina']}\n")
                f.write("-" * 50 + "\n\n")
        print("Dados salvos em 'quotes_coletadas.txt'")

# --- Execução Principal do Script ---
if __name__ == "__main__":
    print("=== Iniciando Web Scraping de Citações ===")
    
    try:
        resultado_final = raspar_quotes_com_selenium()
        
        if resultado_final:
            print(f"\n✅ Web scraping concluído com sucesso!")
            print(f"📊 Total de {len(resultado_final)} citações coletadas.")
            
            # Estatísticas adicionais
            autores_unicos = len(set(quote['autor'] for quote in resultado_final))
            paginas_processadas = max(quote['pagina'] for quote in resultado_final)
            
            print(f"👥 Autores únicos: {autores_unicos}")
            print(f"📄 Páginas processadas: {paginas_processadas}")
            
            # Salva os resultados
            salvar_resultados(resultado_final, 'json')
            
            # Exemplo da primeira citação coletada
            print("\n📝 Exemplo da primeira citação coletada:")
            primeira_citacao = resultado_final[0]
            print(f"Texto: {primeira_citacao['citacao']}")
            print(f"Autor: {primeira_citacao['autor']}")
            print(f"Tags: {', '.join(primeira_citacao['tags'])}")
            
        else:
            print("❌ Nenhuma citação foi coletada. Verifique a conexão e tente novamente.")
            
    except KeyboardInterrupt:
        print("\n⚠️ Operação interrompida pelo usuário.")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")