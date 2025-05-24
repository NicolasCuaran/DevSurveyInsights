import requests
import pandas as pd
from dotenv import load_dotenv
import os
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def _get_github_token():
    route = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    load_dotenv(route)
    
    token = os.getenv("GITHUB_TOKEN")
    
    if not token:
        logging.error("GITHUB_TOKEN no encontrado. Verifica el archivo .env o las variables de entorno de Airflow.")
        raise ValueError("GITHUB_TOKEN no se pudo cargar.")
    
    return token

def _get_query(cursor=None):
    cursor_str = f', after: "{cursor}"' if cursor else ""
    return f"""
    query {{
      search(query: "stars:>100", type: REPOSITORY, first: 5{cursor_str}) {{
        pageInfo {{
          endCursor
          hasNextPage
        }}
        nodes {{
          ... on Repository {{
            name
            owner {{
              login
              ... on User {{
                location
              }}
            }}
            primaryLanguage {{
              name
            }}
            stargazers {{
              totalCount
            }}
            forkCount
            defaultBranchRef {{
              target {{
                ... on Commit {{
                  history(first: 1) {{
                    nodes {{
                      author {{
                        user {{
                          login
                          location
                        }}
                      }}
                    }}
                  }}
                }}
              }}
            }}
          }}
        }}
      }}
      rateLimit {{
        limit
        cost
        remaining
        resetAt
      }}
    }}
    """

def _fetch_github_page(token, cursor=None, retries=3, delay=5):
    """
    Realiza una solicitud a la API de GitHub para una página de datos.
    """
    url = "https://api.github.com/graphql"
    query = _get_query(cursor)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    for attempt in range(retries):
        try:
            response = requests.post(url, json={"query": query}, headers=headers, timeout=30)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 502:
                logging.warning(f"Error 502 en intento {attempt + 1}/{retries}. Reintentando en {delay} segundos...")
                time.sleep(delay)
                continue
            else:
                logging.error(f"Error en la solicitud: {response.status_code} - {response.text}")
                response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logging.warning(f"Error de red en intento {attempt + 1}/{retries}: {e}. Reintentando en {delay} segundos...")
            time.sleep(delay)
            continue
    raise Exception(f"Falló la obtención de datos de GitHub después de {retries} intentos.")

def _process_repository_data(raw_page_data):
    """
    Procesa los datos JSON de una página y los transforma en una lista de diccionarios.
    Devuelve la lista de datos de repositorios y la información de paginación.
    """
    if not raw_page_data or "data" not in raw_page_data or "search" not in raw_page_data["data"]:
        logging.error("Formato de datos inesperado de la API de GitHub.")
        return [], {"hasNextPage": False, "endCursor": None}
        
    repos_nodes = raw_page_data["data"]["search"].get("nodes", [])
    repo_data_list = []

    for repo in repos_nodes:
        if not repo: continue

        contributor_location = "Unknown"
        if (
            repo.get("defaultBranchRef") and 
            repo["defaultBranchRef"].get("target") and 
            repo["defaultBranchRef"]["target"].get("history") and 
            repo["defaultBranchRef"]["target"]["history"].get("nodes")
        ):
            history_nodes = repo["defaultBranchRef"]["target"]["history"]["nodes"]
            if history_nodes and history_nodes[0].get("author") and history_nodes[0]["author"].get("user"):
                contributor_user = history_nodes[0]["author"]["user"]
                if contributor_user:
                     contributor_location = contributor_user.get("location", "Unknown")


        final_country_location = contributor_location
        if final_country_location == "Unknown" or not final_country_location:
            owner = repo.get("owner", {})
            if owner:
                final_country_location = owner.get("location", "Unknown")
        
        if final_country_location is None:
            final_country_location = "Unknown"

        repo_data_list.append({
            "Country": final_country_location,
            "LanguageWorkedWith": repo.get("primaryLanguage", {}).get("name") if repo.get("primaryLanguage") else "None",
            "RepositoryName": repo.get("name", "N/A"),
            "Owner": repo.get("owner", {}).get("login", "N/A"),
            "Stars": repo.get("stargazers", {}).get("totalCount", 0),
            "Forks": repo.get("forkCount", 0)
        })
        
    page_info = raw_page_data["data"]["search"].get("pageInfo", {"hasNextPage": False, "endCursor": None})
    return repo_data_list, page_info

def fetch_github_repositories_data(target_repos=1000):
    """
    Función principal para extraer datos de repositorios de GitHub.
    Orquesta la paginación y la recolección de datos hasta alcanzar target_repos.
    Devuelve un DataFrame de Pandas con los datos recolectados.
    """
    try:
        github_token = _get_github_token()
    except ValueError as e:
        logging.error(f"No se pudo obtener el GITHUB_TOKEN: {e}")
        return pd.DataFrame()

    all_repo_data = []
    cursor = None
    
    logging.info(f"Iniciando recolección de datos de GitHub. Objetivo: {target_repos} repositorios.")
    page_num = 1

    while len(all_repo_data) < target_repos:
        try:
            logging.info(f"Solicitando página {page_num} de GitHub...")
            raw_data_page = _fetch_github_page(token=github_token, cursor=cursor)
        except Exception as e:
            logging.error(f"Fallo crítico al obtener la página {page_num} de GitHub: {e}")
            break

        if not raw_data_page:
            logging.warning(f"No se recibieron datos para la página {page_num}. Deteniendo paginación.")
            break
            
        rate_limit_info = raw_data_page.get("data", {}).get("rateLimit", {})
        logging.info(
            f"Página {page_num} - Costo: {rate_limit_info.get('cost', 'N/A')}, "
            f"Restante: {rate_limit_info.get('remaining', 'N/A')}, "
            f"Reseteo: {rate_limit_info.get('resetAt', 'N/A')}"
        )

        if rate_limit_info.get("remaining", float('inf')) < 100 :
            reset_time_str = rate_limit_info.get("resetAt", "un momento")
            logging.warning(f"Límite de tasa de API bajo ({rate_limit_info.get('remaining', 'N/A')}). Esperando para evitar errores...")
            time.sleep(100)

        repo_data_list_from_page, page_info_from_api = _process_repository_data(raw_data_page)
        
        if not repo_data_list_from_page and not page_info_from_api.get("hasNextPage"):
            logging.info("No se procesaron más repositorios y no hay página siguiente.")
            break

        all_repo_data.extend(repo_data_list_from_page)
        logging.info(f"Recolectados {len(repo_data_list_from_page)} repositorios en esta página. Total acumulado: {len(all_repo_data)}.")

        if len(all_repo_data) >= target_repos:
            all_repo_data = all_repo_data[:target_repos]
            logging.info(f"Objetivo de {target_repos} repositorios alcanzado.")
            break

        if page_info_from_api.get("hasNextPage"):
            cursor = page_info_from_api["endCursor"]
        else:
            logging.info("No hay más páginas disponibles según la API de GitHub.")
            break
        
        page_num += 1
        time.sleep(2) # Pausa prudente entre solicitudes para no sobrecargar la API.

    if not all_repo_data:
        logging.warning("No se recolectaron datos de repositorios.")
        return pd.DataFrame()

    repo_df = pd.DataFrame(all_repo_data)
    logging.info(f"Total de repositorios recolectados: {len(repo_df)}")
    return repo_df