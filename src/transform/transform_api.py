# transform_api_data.py
import pandas as pd
import numpy as np # Para np.nan si es necesario, aunque pd.NA es más moderno.
import logging

# Configuración básica de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

country_mapping = {
    # Ciudades/estados de Estados Unidos
    'SAN FRANCISCO': 'United States', 'NEW YORK': 'United States', 'RENTON, WASHINGTON': 'United States',
    'SEATTLE, WA': 'United States', 'PORTLAND, OR': 'United States', 'PHILADELPHIA USA': 'United States',
    'HAWAII': 'United States', 'NEW ORLEANS': 'United States', 'BOSTON': 'United States',
    'EST. AKRON': 'United States', 'ST. LOUIS, MO': 'United States', 'HILLSBOROUGH, CA': 'United States',
    'SAN DIEGO, CA': 'United States', 'MASSACHUSETTS, USA': 'United States', 'MENLO PARK': 'United States',
    'MIAMI, FL': 'United States', 'BAY AREA': 'United States', 'CAMBRIDGE, MA': 'United States',
    'SF BAY AREA': 'United States', 'OAKLAND, CALIFORNIA': 'United States', 'DENVER, CO': 'United States',
    'LOS ANGELES, CA': 'United States', 'SANTA CLARA, CA': 'United States', 'SAN JOSE, CA': 'United States',
    'BERKELEY, CA': 'United States', 'PITTSBURGH, PA': 'United States', 'CHARLOTTESVILLE, VA': 'United States',
    'CALIFORNIA, US': 'United States', 'UNITED STATES': 'United States', 'NORTH CAROLINA, US': 'United States',
    'HOUSTON': 'United States', 'JACKSONVILLE, FL': 'United States', 'MARLBOROUGH, MA': 'United States',
    'GREENBELT, MD': 'United States', 'SUMMIT PARK, UT': 'United States', 'NYC': 'United States',
    'ENDICOTT, NY': 'United States', 'ANN ARBOR, MI, USA': 'United States', 'BUFFALO NY': 'United States',
    'SEATTLE': 'United States', 'VIRGINIA, USA': 'United States', 'DE': 'United States',
    'BALTIMORE, MD': 'United States', 'LAFAYETTE, LA': 'United States', 'COLORADO': 'United States',
    'PORTLAND, OR, USA': 'United States', 'LONGMONT, COLORADO, USA': 'United States', 'AUSTIN, TX': 'United States',
    'PALO ALTO, CALIFORNIA, USA': 'United States', 'WASHINGTON': 'United States', 'WASHINGTON, DC': 'United States',
    'BROOKLYN, NY': 'United States',

    # Ciudades/estados de China
    'GUANGZHOU, CHINA': 'China', 'CHENGDU SICHUAN, CHINA': 'China', 'WUHAN, HUBEI': 'China',
    'BEIJING, CHINA': 'China', 'HANGZHOU CHINA': 'China', 'SHANGHAI': 'China',
    'SHENZHEN, CHINA': 'China', 'WUXI,CHINA': 'China', 'SUZHOU, CHINA': 'China',
    'CHINA': 'China', 'CHENGDU SICHUAN CHINA': 'China', 'BEIJING': 'China',
    'SHENZHEN': 'China', 'HANGZHOU, CHINA': 'China', 'ZHENGZHOU, CHINA': 'China',
    'CHONGQING, CHINA': 'China', 'HEFEI, ANHUI, CHINA': 'China', 'XI\'AN, CHINA': 'China',
    'TIANJIN': 'China', 'HONG KONG, CHINA': 'China', 'TAIYUAN,SHANXI,CHINA': 'China',
    'WUHAN. CHINA': 'China', 'HONG KONG': 'China',

    # Ciudades/estados de India
    'BHAVNAGAR, GUJARAT': 'India', 'INDIA': 'India', 'PUNE, INDIA': 'India',
    'KERALA, INDIA': 'India', 'BANGALORE, INDIA': 'India', 'MUMBAI': 'India',
    'NEW DELHI , INDIA': 'India', 'GUJARAT, INDIA': 'India', 'HYDERABAD': 'India',
    'COIMBATORE': 'India', 'BANGALORE': 'India', 'NEW DELHI': 'India',

    # Ciudades/estados de Italia
    'BOLOGNA, ITALY': 'Italy', 'ITALY': 'Italy', 'CHIOGGIA, ITALY': 'Italy',
    'PROVINCIA DI VARESE, ITALY': 'Italy', 'ROME': 'Italy',

    # Ciudades/estados de Reino Unido
    'LONDON, UK': 'United Kingdom', 'LONDON, UNITED KINGDOM': 'United Kingdom', 'LONDON': 'United Kingdom',
    'BRIGHTON, UK': 'United Kingdom', 'EDINBURGH, UK': 'United Kingdom', 'DEVON, UK': 'United Kingdom',
    'GLASGOW, UK': 'United Kingdom', 'CAMBRIDGE, UK': 'United Kingdom', 'CARDIFF, UNITIED KINGDOM': 'United Kingdom',
    'UK': 'United Kingdom', 'UNITED KINGDOM': 'United Kingdom', 'ENGLAND': 'United Kingdom',

    # Ciudades/estados de Francia
    'PARIS': 'France', 'PARIS, FRANCE': 'France', 'FRANCE': 'France',
    'LILLE, FRANCE': 'France', 'UNIVERSITÉ PARIS-SACLAY': 'France', 'FRANCE, BORDEAUX': 'France',
    'FRANCE - LYON': 'France', 'VALBONNE, FRANCE': 'France', 'GRENOBLE - FRANCE': 'France',
    'LYON, FRANCE': 'France', 'LYON': 'France',

    # Ciudades/estados de Alemania
    'DRESDEN, GERMANY': 'Germany', 'BERLIN, GERMANY': 'Germany', 'DÜSSELDORF, DE': 'Germany',
    'NORTH RHINE-WESTPHALIA, GERMANY': 'Germany', 'GERMANY, MAGDEBURG': 'Germany', 'BREMEN': 'Germany',
    'HAMBURG, GERMANY, EARTH (SOL)': 'Germany', 'HAMBURG': 'Germany', 'ERLANGEN, GERMANY': 'Germany',
    'KARLSRUHE, GERMANY': 'Germany', 'MUNICH, GERMANY': 'Germany', 'FRANKFURT/MAIN (GERMANY)': 'Germany',
    'GERMANY': 'Germany', 'BERLIN': 'Germany', 'MUNICH': 'Germany',

    # Ciudades/estados de Canadá
    'TORONTO, CANADA': 'Canada', 'VANCOUVER, BC': 'Canada', 'CANADA / QUÉBEC': 'Canada',
    'TORONTO, ON': 'Canada', 'BURLINGTON, CANADA': 'Canada', 'KINGSTON, ONTARIO, CANADA': 'Canada',
    'MONTREAL, QUEBEC': 'Canada', 'WATERLOO, CANADA': 'Canada', 'VANCOUVER, CANADA': 'Canada',
    'CANADA': 'Canada', 'TORONTO': 'Canada', 'MONTREAL': 'Canada',

    # Ciudades/estados de Japón
    'JAPAN': 'Japan', 'TOKYO, JAPAN': 'Japan', 'TORISHIRO JIMA': 'Japan',
    'TOKYO': 'Japan',

    # Ciudades/estados de España
    'BARCELONA, SPAIN': 'Spain', 'GETAFE, SPAIN': 'Spain', 'MADRID - SPAIN': 'Spain',
    'BUILDING SOFTWARE WITH  ♥ FROM GALICIA (SPAIN) TO THE WORLD.': 'Spain', 'MADRID, SPAIN': 'Spain',
    'MURCIA': 'Spain', 'SPAIN': 'Spain', 'BARCELONA': 'Spain', 'MADRID': 'Spain',

    # Ciudades/estados de Países Bajos
    'AMSTERDAM': 'Netherlands', 'DELFT, NL': 'Netherlands', 'THE NETHERLANDS': 'Netherlands',
    'NETHERLANDS': 'Netherlands', 'AMSTERDAM, NETHERLANDS': 'Netherlands',

    # Ciudades/estados de Suecia
    'STOCKHOLM, SWEDEN': 'Sweden', 'SWEDEN': 'Sweden', 'MALMÖ, SWEDEN': 'Sweden',
    'STOCKHOLM, SE': 'Sweden', 'STOCKHOLM': 'Sweden',

    # Ciudades/estados de Suiza
    'SWITZERLAND': 'Switzerland', 'ZÜRICH, SCHWEIZ': 'Switzerland', 'ZÜRICH, ZURICH, SWITZERLAND': 'Switzerland',
    'ZURICH, SWITZERLAND': 'Switzerland', 'ZURICH': 'Switzerland',

    # Ciudades/estados de Brasil
    'FRANCA, SÃO PAULO, BRAZIL': 'Brazil', 'RIBEIRÃO PIRES - SP': 'Brazil', 'BRAZIL': 'Brazil',
    'SÃO PAULO': 'Brazil',

    # Ciudades/estados de Polonia
    'POLAND': 'Poland', 'TORUŃ, POLAND': 'Poland', 'WROCŁAW, POLAND': 'Poland',
    'WARSAW, POLAND': 'Poland', 'POZNAŃ': 'Poland', 'WARSAW': 'Poland',

    # Ciudades/estados de Australia
    'MELBOURNE, AUSTRALIA': 'Australia', 'SYDNEY, AUSTRALIA': 'Australia', 'SYDNEY': 'Australia',
    'MELBOURNE, AU': 'Australia', 'AUSTRALIA': 'Australia',

    # Ciudades/estados de Rusia
    'SAINT-PETERSBURG, RUSSIA': 'Russia', 'ISRAEL, TEL-AVIV /// RUSSIA, SAINT PETERSBURG/KIROV': 'Russia',
    'RUSSIA': 'Russia', 'MOSCOW': 'Russia',

    # Ciudades/estados de Israel
    'ISRAEL': 'Israel', 'TEL AVIV, ISRAEL': 'Israel', 'TEL AVIV': 'Israel',

    # Ciudades/estados de Ucrania
    'UKRAINE, KYIV': 'Ukraine', 'KYIV, UKRAINE': 'Ukraine', 'UKRAINE': 'Ukraine', 'KYIV': 'Ukraine',

    # Ciudades/estados de Turquía
    'ISTANBUL, TURKEY': 'Turkey', 'TURKEY': 'Turkey', 'ISTANBUL': 'Turkey',

    # Ciudades/estados de Grecia
    'ATHENS, GREECE': 'Greece', 'GREECE': 'Greece', 'ATHENS': 'Greece',

    # Ciudades/estados de Hungría
    'BUDAPEST, HUNGARY': 'Hungary', 'BUDAPEST 🇭🇺': 'Hungary', 'HUNGARY': 'Hungary', 'BUDAPEST': 'Hungary',

    # Ciudades/estados de Sudáfrica
    'GEORGE. SOUTH AFRICA': 'South Africa', 'SOUTH AFRICA': 'South Africa',

    # Ciudades/estados de Finlandia
    'FINLAND': 'Finland', 'HELSINKI': 'Finland',

    # Ciudades/estados de Noruega
    'NORWAY': 'Norway', 'OSLO': 'Norway',

    # Ciudades/estados de Taiwán
    'TAIWAN': 'Taiwan', 'TAICHUNG, TAIWAN': 'Taiwan', 'TAIWAN, R.O.C': 'Taiwan', 'TAIPEI': 'Taiwan',

    # Ciudades/estados de Singapur
    'SINGAPORE': 'Singapore',

    # Ciudades/estados de Kenia
    'KENYA': 'Kenya', 'NAIROBI': 'Kenya',

    # Ciudades/estados de Dinamarca
    'SKALS, DENMARK': 'Denmark', 'ELSINORE': 'Denmark', 'DENMARK': 'Denmark', 'COPENHAGEN': 'Denmark',

    # Ciudades/estados de Bélgica
    'GHENT, BELGIUM': 'Belgium', 'BELGIUM': 'Belgium', 'BRUSSELS': 'Belgium',

    # Ciudades/estados de Rumania
    'ROMANIA': 'Romania',

    # Ciudades/estados de Malta
    'MALTA': 'Malta',

    # Ciudades/estados de Egipto
    'ASSIUT': 'Egypt', 'EGYPT': 'Egypt',

    # Ciudades/estados de Nueva Zelanda
    'PARAPARAUMU, NEW ZEALAND': 'New Zealand', 'AUCKLAND': 'New Zealand', 'NEW ZEALAND': 'New Zealand',

    # Ciudades/estados de Austria
    'VIENNA, AUSTRIA': 'Austria', 'AUSTRIA': 'Austria', 'VIENNA': 'Austria',

    # Ciudades/estados de Malasia
    'MALAYSIA': 'Malaysia',

    # Ciudades/estados de Irán
    'MASHHAD, IRAN': 'Iran', 'IRAN': 'Iran', 'TEHRAN': 'Iran',

    # Ciudades/estados de Corea del Sur
    'SEOUL': 'South Korea', 'SOUTH KOREA': 'South Korea',

    # Ciudades/estados de Lituania
    'LITHUANIA': 'Lithuania',

    # Ciudades/estados de Estonia
    'TALLINN': 'Estonia', 'ESTONIA': 'Estonia',

    # Ciudades/estados de Bosnia y Herzegovina
    'BOSNIA AND HERZEGOVINA': 'Bosnia and Herzegovina',

    # Ciudades/estados de Argentina
    'ARGENTINA': 'Argentina', 'BUENOS AIRES': 'Argentina',

    # Ciudades/estados de Kazajistán
    'KAZAKHSTAN, ASTANA': 'Kazakhstan', 'KAZAKHSTAN': 'Kazakhstan',

    # Ciudades/estados de Tailandia
    'BANGKOK, THAILAND': 'Thailand', 'THAILAND': 'Thailand', 'BANGKOK': 'Thailand',

    # Ciudades/estados de Irlanda
    'DUBLIN, IRELAND': 'Ireland', 'IRELAND': 'Ireland', 'DUBLIN': 'Ireland',

    # Ciudades/estados de Portugal
    'PORTUGAL': 'Portugal', 'LISBON': 'Portugal',

    # Ciudades/estados de Bangladesh
    'BANGLADESH': 'Bangladesh',

    # Otros
    'EUROPE': 'Europe',
    'EARTH': 'Earth',
    'BASH': 'Other'
}

valid_countries = [
    'United States', 'China', 'India', 'Italy', 'United Kingdom', 'France', 'Germany', 'Canada',
    'Japan', 'Spain', 'Netherlands', 'Sweden', 'Switzerland', 'Brazil', 'Poland', 'Australia',
    'Russia', 'Israel', 'Ukraine', 'Turkey', 'Greece', 'Hungary', 'South Africa', 'Finland',
    'Norway', 'Taiwan', 'Singapore', 'Kenya', 'Denmark', 'Belgium', 'Romania', 'Malta', 'Egypt',
    'New Zealand', 'Austria', 'Malaysia', 'Iran', 'South Korea', 'Lithuania', 'Estonia',
    'Bosnia and Herzegovina', 'Argentina', 'Kazakhstan', 'Thailand', 'Ireland', 'Portugal',
    'Bangladesh', 'Europe', 'Earth', 'Other'
]


def _normalize_country_value(value, mapping_dict, valid_list):
    """
    Normaliza un valor de país dado utilizando un diccionario de mapeo y una lista de países válidos.
    """
    if pd.isna(value) or not isinstance(value, str) or value.strip() == "" or value.lower() == "none" or value.lower() == "unknown":
        return "Other"
    
    value_upper = value.upper()

    if value_upper in mapping_dict:
        return mapping_dict[value_upper]

    for key_map_upper, mapped_country in mapping_dict.items():
        if key_map_upper in value_upper:
            return mapped_country
            
    value_title_case = value.strip().title()
    if value_title_case in valid_list:
        return value_title_case
        
    return "Other"


def transform__api_data(input_df: pd.DataFrame) -> pd.DataFrame:
    if not isinstance(input_df, pd.DataFrame):
        logging.error("La entrada no es un DataFrame de Pandas. No se puede transformar.")
        return pd.DataFrame()

    if input_df.empty:
        logging.info("El DataFrame de entrada está vacío. No hay datos para transformar.")
        return input_df

    logging.info(f"Iniciando transformación de datos. DataFrame original con {input_df.shape[0]} filas.")
    
    df = input_df.copy()

    # 1. Manejo de nulos y placeholders para 'LanguageWorkedWith'
    df['LanguageWorkedWith'] = df['LanguageWorkedWith'].replace('None', 'Not Specified', regex=False)
    df['LanguageWorkedWith'].fillna('Not Specified', inplace=True)
    logging.info("Columna 'LanguageWorkedWith' limpiada: Nulos y 'None' reemplazados por 'Not Specified'.")

    # 2. Normalización de la columna 'Country'
    uppercase_country_mapping = {k.upper(): v for k, v in country_mapping.items()}
    df['Country'] = df['Country'].apply(
        lambda x: _normalize_country_value(x, uppercase_country_mapping, valid_countries)
    )
    logging.info("Columna 'Country' normalizada.")

    # 3. Verificación de tipos
    df['Stars'] = pd.to_numeric(df['Stars'], errors='coerce').fillna(0).astype(int)
    df['Forks'] = pd.to_numeric(df['Forks'], errors='coerce').fillna(0).astype(int)
    
    for col in ['LanguageWorkedWith', 'RepositoryName', 'Owner', 'Country']:
        df[col] = df[col].astype(str)
        
    logging.info(f"Transformación completada. DataFrame resultante con {df.shape[0]} filas.")
    
    logging.info("Conteo de nulos por columna después de la transformación:")
    logging.info(df.isnull().sum())

    return df