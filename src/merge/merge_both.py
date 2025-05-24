import pandas as pd
import io
import logging

logger = logging.getLogger(__name__)

country_mapping = {
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
    'BROOKLYN, NY': 'United States', 'GUANGZHOU, CHINA': 'China', 'CHENGDU SICHUAN, CHINA': 'China',
    'WUHAN, HUBEI': 'China', 'BEIJING, CHINA': 'China', 'HANGZHOU CHINA': 'China',
    'SHANGHAI': 'China', 'SHENZHEN, CHINA': 'China', 'WUXI,CHINA': 'China',
    'SUZHOU, CHINA': 'China', 'CHINA': 'China', 'CHENGDU SICHUAN CHINA': 'China',
    'BEIJING': 'China', 'SHENZHEN': 'China', 'HANGZHOU, CHINA': 'China',
    'ZHENGZHOU, CHINA': 'China', 'CHONGQING, CHINA': 'China', 'HEFEI, ANHUI, CHINA': 'China',
    'XI\'AN, CHINA': 'China', 'TIANJIN': 'China', 'HONG KONG, CHINA': 'China',
    'TAIYUAN,SHANXI,CHINA': 'China', 'WUHAN. CHINA': 'China', 'BHAVNAGAR, GUJARAT': 'India',
    'INDIA': 'India', 'PUNE, INDIA': 'India', 'KERALA, INDIA': 'India',
    'BANGALORE, INDIA': 'India', 'MUMBAI': 'India', 'NEW DELHI , INDIA': 'India',
    'GUJARAT, INDIA': 'India', 'HYDERABAD': 'India', 'COIMBATORE': 'India',
    'BANGALORE': 'India', 'BOLOGNA, ITALY': 'Italy', 'ITALY': 'Italy',
    'CHIOGGIA, ITALY': 'Italy', 'PROVINCIA DI VARESE, ITALY': 'Italy', 'LONDON, UK': 'United Kingdom',
    'LONDON, UNITED KINGDOM': 'United Kingdom', 'LONDON': 'United Kingdom', 'BRIGHTON, UK': 'United Kingdom',
    'EDINBURGH, UK': 'United Kingdom', 'DEVON, UK': 'United Kingdom', 'GLASGOW, UK': 'United Kingdom',
    'CAMBRIDGE, UK': 'United Kingdom', 'CARDIFF, UNITIED KINGDOM': 'United Kingdom', 'UK': 'United Kingdom',
    'UNITED KINGDOM': 'United Kingdom', 'PARIS': 'France', 'PARIS, FRANCE': 'France',
    'FRANCE': 'France', 'LILLE, FRANCE': 'France', 'UNIVERSITÉ PARIS-SACLAY': 'France',
    'FRANCE, BORDEAUX': 'France', 'FRANCE - LYON': 'France', 'VALBONNE, FRANCE': 'France',
    'GRENOBLE - FRANCE': 'France', 'LYON, FRANCE': 'France', 'DRESDEN, GERMANY': 'Germany',
    'BERLIN, GERMANY': 'Germany', 'DÜSSELDORF, DE': 'Germany', 'NORTH RHINE-WESTPHALIA, GERMANY': 'Germany',
    'GERMANY, MAGDEBURG': 'Germany', 'BREMEN': 'Germany', 'HAMBURG, GERMANY, EARTH (SOL)': 'Germany',
    'HAMBURG': 'Germany', 'ERLANGEN, GERMANY': 'Germany', 'KARLSRUHE, GERMANY': 'Germany',
    'MUNICH, GERMANY': 'Germany', 'FRANKFURT/MAIN (GERMANY)': 'Germany', 'GERMANY': 'Germany',
    'TORONTO, CANADA': 'Canada', 'VANCOUVER, BC': 'Canada', 'CANADA / QUÉBEC': 'Canada',
    'TORONTO, ON': 'Canada', 'BURLINGTON, CANADA': 'Canada', 'KINGSTON, ONTARIO, CANADA': 'Canada',
    'MONTREAL, QUEBEC': 'Canada', 'WATERLOO, CANADA': 'Canada', 'VANCOUVER, CANADA': 'Canada',
    'CANADA': 'Canada', 'JAPAN': 'Japan', 'TOKYO, JAPAN': 'Japan',
    'TORISHIRO JIMA': 'Japan', 'TOKYO': 'Japan', 'BARCELONA, SPAIN': 'Spain',
    'GETAFE, SPAIN': 'Spain', 'MADRID - SPAIN': 'Spain',
    'BUILDING SOFTWARE WITH  ♥ FROM GALICIA (SPAIN) TO THE WORLD.': 'Spain',
    'MADRID, SPAIN': 'Spain', 'MURCIA': 'Spain', 'AMSTERDAM': 'Netherlands',
    'DELFT, NL': 'Netherlands', 'THE NETHERLANDS': 'Netherlands', 'NETHERLANDS': 'Netherlands',
    'AMSTERDAM, NETHERLANDS': 'Netherlands', 'STOCKHOLM, SWEDEN': 'Sweden', 'SWEDEN': 'Sweden',
    'MALMÖ, SWEDEN': 'Sweden', 'STOCKHOLM, SE': 'Sweden', 'SWITZERLAND': 'Switzerland',
    'ZÜRICH, SCHWEIZ': 'Switzerland', 'ZÜRICH, ZURICH, SWITZERLAND': 'Switzerland',
    'ZURICH, SWITZERLAND': 'Switzerland', 'FRANCA, SÃO PAULO, BRAZIL': 'Brazil',
    'RIBEIRÃO PIRES - SP': 'Brazil', 'BRAZIL': 'Brazil', 'POLAND': 'Poland',
    'TORUŃ, POLAND': 'Poland', 'WROCŁAW, POLAND': 'Poland', 'WARSAW, POLAND': 'Poland',
    'POZNAŃ': 'Poland', 'MELBOURNE, AUSTRALIA': 'Australia', 'SYDNEY, AUSTRALIA': 'Australia',
    'SYDNEY': 'Australia', 'MELBOURNE, AU': 'Australia', 'SAINT-PETERSBURG, RUSSIA': 'Russia',
    'ISRAEL, TEL-AVIV /// RUSSIA, SAINT PETERSBURG/KIROV': 'Russia', 'ISRAEL': 'Israel',
    'TEL AVIV, ISRAEL': 'Israel', 'UKRAINE, KYIV': 'Ukraine', 'KYIV, UKRAINE': 'Ukraine',
    'ISTANBUL, TURKEY': 'Turkey', 'TURKEY': 'Turkey', 'ATHENS, GREECE': 'Greece',
    'BUDAPEST, HUNGARY': 'Hungary', 'BUDAPEST 🇭🇺': 'Hungary', 'GEORGE. SOUTH AFRICA': 'South Africa',
    'FINLAND': 'Finland', 'NORWAY': 'Norway', 'TAIWAN': 'Taiwan',
    'TAICHUNG, TAIWAN': 'Taiwan', 'TAIWAN, R.O.C': 'Taiwan', 'SINGAPORE': 'Singapore',
    'KENYA': 'Kenya', 'NAIROBI': 'Kenya', 'SKALS, DENMARK': 'Denmark',
    'ELSINORE': 'Denmark', 'DENMARK': 'Denmark', 'GHENT, BELGIUM': 'Belgium',
    'BELGIUM': 'Belgium', 'ROMANIA': 'Romania', 'MALTA': 'Malta',
    'ASSIUT': 'Egypt', 'EGYPT': 'Egypt', 'PARAPARAUMU, NEW ZEALAND': 'New Zealand',
    'AUCKLAND': 'New Zealand', 'VIENNA, AUSTRIA': 'Austria', 'AUSTRIA': 'Austria',
    'MALAYSIA': 'Malaysia', 'MASHHAD, IRAN': 'Iran', 'SEOUL': 'South Korea',
    'SOUTH KOREA': 'South Korea', 'LITHUANIA': 'Lithuania', 'TALLINN': 'Estonia',
    'BOSNIA AND HERZEGOVINA': 'Bosnia and Herzegovina', 'ARGENTINA': 'Argentina',
    'KAZAKHSTAN, ASTANA': 'Kazakhstan', 'BANGKOK, THAILAND': 'Thailand', 'DUBLIN, IRELAND': 'Ireland',
    'PORTUGAL': 'Portugal', 'BANGLADESH': 'Bangladesh', 'HONG KONG': 'China',
    'ROME': 'Italy', 'ENGLAND': 'United Kingdom', 'LYON': 'France', 'BERLIN': 'Germany', 'MUNICH': 'Germany',
    'TORONTO': 'Canada', 'MONTREAL': 'Canada', 'SPAIN': 'Spain', 'BARCELONA': 'Spain', 'MADRID': 'Spain',
    'STOCKHOLM': 'Sweden', 'ZURICH': 'Switzerland', 'SÃO PAULO': 'Brazil', 'WARSAW': 'Poland',
    'AUSTRALIA': 'Australia', 'RUSSIA': 'Russia', 'MOSCOW': 'Russia', 'TEL AVIV': 'Israel',
    'UKRAINE': 'Ukraine', 'KYIV': 'Ukraine', 'ISTANBUL': 'Turkey', 'GREECE': 'Greece', 'ATHENS': 'Greece',
    'HUNGARY': 'Hungary', 'BUDAPEST': 'Hungary', 'SOUTH AFRICA': 'South Africa', 'HELSINKI': 'Finland',
    'OSLO': 'Norway', 'TAIPEI': 'Taiwan', 'COPENHAGEN': 'Denmark', 'BRUSSELS': 'Belgium',
    'NEW ZEALAND': 'New Zealand', 'VIENNA': 'Austria', 'IRAN': 'Iran', 'TEHRAN': 'Iran',
    'ESTONIA': 'Estonia', 'BUENOS AIRES': 'Argentina', 'KAZAKHSTAN': 'Kazakhstan',
    'THAILAND': 'Thailand', 'BANGKOK': 'Thailand', 'IRELAND': 'Ireland', 'DUBLIN': 'Ireland',
    'LISBON': 'Portugal', 'EUROPE': 'Europe', 'EARTH': 'Earth', 'BASH': 'Other'
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

uppercase_country_mapping = {k.upper().replace(',', '').replace('  ', ' ').strip(): v for k, v in country_mapping.items()}

def _normalize_country_value(value: str | None) -> str:
    if pd.isna(value) or not isinstance(value, str) or not value.strip() or value.lower() == "none" or value.lower() == "unknown":
        return "Other"
    value_normalized_for_lookup = value.upper().replace(',', '').replace('  ', ' ').strip()
    if value_normalized_for_lookup in uppercase_country_mapping:
        return uppercase_country_mapping[value_normalized_for_lookup]
    for map_key_original, map_value_country in country_mapping.items():
        processed_map_key = map_key_original.upper().replace(',', '').replace('  ', ' ').strip()
        if processed_map_key in value_normalized_for_lookup:
            return map_value_country
    value_title_case = value.strip().title()
    if value_title_case in valid_countries:
        return value_title_case
    return "Other"

def _get_first_language(lang_string: str | None) -> str:
    if pd.isna(lang_string) or not isinstance(lang_string, str) or not lang_string.strip():
        return 'Not Specified'
    first_lang = lang_string.split(';')[0].strip()
    return first_lang if first_lang else 'Not Specified'

def merge_survey_and_api_data(df_db_json: str | None, df_api_json: str | None) -> str | None:
    logger.info("Iniciando merge de datos de encuesta (DB) y API.")
    if df_db_json is None:
        logger.warning("JSON de datos de DB (encuesta) es None. No se puede realizar el merge.")
        return None
    
    if df_api_json is None:
        logger.warning("JSON de datos de API es None. Se devolverán los datos de DB (encuesta) tal cual, añadiendo columnas API vacías.")
        try:
            df_db_temp = pd.read_json(io.StringIO(df_db_json), orient="records")
            df_db_temp['APIRepo_Stars'] = pd.NA 
            df_db_temp['APIRepo_Forks'] = pd.NA
            logger.info(f"API JSON es None. Devolviendo df_db_temp con columnas: {df_db_temp.columns.tolist()}")
            return df_db_temp.to_json(orient="records", date_format="iso")
        except Exception as e:
            logger.error(f"Error al procesar df_db_json cuando df_api_json es None: {e}", exc_info=True)
            return None
    try:
        df_db = pd.read_json(io.StringIO(df_db_json), orient="records")
        df_api = pd.read_json(io.StringIO(df_api_json), orient="records")

        logger.info(f"Columnas iniciales en df_db: {df_db.columns.tolist()}")
        logger.info(f"Columnas iniciales en df_api: {df_api.columns.tolist()}")

        if df_db.empty:
            logger.info("DataFrame de DB (encuesta) está vacío. Devolviendo DataFrame vacío.")
            if not df_api.empty: 
                df_db['APIRepo_Stars'] = pd.NA 
                df_db['APIRepo_Forks'] = pd.NA
            logger.info(f"df_db vacío. Devolviendo df_db con columnas: {df_db.columns.tolist()}")
            return df_db.to_json(orient="records", date_format="iso")
            
        if df_api.empty:
            logger.info("DataFrame de API está vacío. Añadiendo columnas APIRepo_Stars/Forks vacías a df_db.")
            df_db['APIRepo_Stars'] = pd.NA
            df_db['APIRepo_Forks'] = pd.NA
            logger.info(f"df_api vacío. Devolviendo df_db con columnas: {df_db.columns.tolist()}")
            return df_db.to_json(orient="records", date_format="iso")

        required_db_cols = ['LanguageWorkedWith', 'Country']
        missing_db_cols = [col for col in required_db_cols if col not in df_db.columns]
        if missing_db_cols:
            logger.error(f"CRÍTICO: Las columnas {missing_db_cols} FALTAN en df_db ANTES de crear columnas derivadas. No se puede proceder con el merge de forma segura.")
            df_db['APIRepo_Stars'] = pd.NA
            df_db['APIRepo_Forks'] = pd.NA
            return df_db.to_json(orient="records", date_format="iso")

        df_db['FirstLanguage_DB'] = df_db['LanguageWorkedWith'].apply(_get_first_language)
        df_db['Country_DB_Normalized'] = df_db['Country'].apply(_normalize_country_value)
        logger.info(f"Columnas en df_db DESPUÉS de crear FirstLanguage_DB y Country_DB_Normalized: {df_db.columns.tolist()}")
        
        required_api_cols = ['LanguageWorkedWith', 'Country', 'Stars', 'Forks']
        missing_api_cols = [col for col in required_api_cols if col not in df_api.columns]
        if missing_api_cols:
            logger.error(f"Faltan columnas requeridas en df_api: {missing_api_cols}. Añadiendo APIRepo_Stars/Forks vacías a df_db.")
            df_db['APIRepo_Stars'] = pd.NA
            df_db['APIRepo_Forks'] = pd.NA
            logger.info(f"Faltan columnas en df_api. Devolviendo df_db con columnas: {df_db.columns.tolist()}")
            return df_db.to_json(orient="records", date_format="iso")

        df_api_unique_best = df_api.sort_values('Stars', ascending=False)
        df_api_unique_best = df_api_unique_best.drop_duplicates(subset=['LanguageWorkedWith', 'Country'], keep='first')
        
        df_api_to_merge = df_api_unique_best[['LanguageWorkedWith', 'Country', 'Stars', 'Forks']].copy()
        df_api_to_merge = df_api_to_merge.rename(columns={'Stars': 'APIRepo_Stars', 'Forks': 'APIRepo_Forks'})
        logger.info(f"Columnas en df_api_to_merge ANTES del merge: {df_api_to_merge.columns.tolist()}")


        merged_df = pd.merge(
            df_db,
            df_api_to_merge,
            left_on=['FirstLanguage_DB', 'Country_DB_Normalized'],
            right_on=['LanguageWorkedWith', 'Country'], 
            how='left',
            suffixes=('_survey', '_api') 
        )
        logger.info(f"Columnas en merged_df DESPUÉS del merge (con sufijos _survey/_api si hubo colisión): {merged_df.columns.tolist()}")
        
        cols_to_rename_back = {}
        if 'LanguageWorkedWith_survey' in merged_df.columns:
            cols_to_rename_back['LanguageWorkedWith_survey'] = 'LanguageWorkedWith'
        elif 'LanguageWorkedWith' not in merged_df.columns and 'LanguageWorkedWith_x' in merged_df.columns: 
            cols_to_rename_back['LanguageWorkedWith_x'] = 'LanguageWorkedWith'


        if 'Country_survey' in merged_df.columns:
            cols_to_rename_back['Country_survey'] = 'Country'
        elif 'Country' not in merged_df.columns and 'Country_x' in merged_df.columns: 
            cols_to_rename_back['Country_x'] = 'Country'

        if cols_to_rename_back:
            merged_df = merged_df.rename(columns=cols_to_rename_back)
            logger.info(f"Columnas renombradas desde _survey/_x a original. Columnas actuales: {merged_df.columns.tolist()}")
        else:
            logger.info("No se necesitaron renombres desde _survey/_x (o las columnas _survey/_x no existían).")


        cols_to_drop_api_keys = []
        if 'LanguageWorkedWith_api' in merged_df.columns: 
            cols_to_drop_api_keys.append('LanguageWorkedWith_api')
        if 'Country_api' in merged_df.columns: 
            cols_to_drop_api_keys.append('Country_api')
        
        if 'LanguageWorkedWith_y' in merged_df.columns and 'LanguageWorkedWith_api' not in merged_df.columns:
            cols_to_drop_api_keys.append('LanguageWorkedWith_y')
        if 'Country_y' in merged_df.columns and 'Country_api' not in merged_df.columns:
            cols_to_drop_api_keys.append('Country_y')


        if cols_to_drop_api_keys:
            merged_df = merged_df.drop(columns=cols_to_drop_api_keys, errors='ignore')
            logger.info(f"Columnas clave de API (_api o _y) eliminadas. Columnas actuales: {merged_df.columns.tolist()}")
        
        if 'APIRepo_Stars' not in merged_df.columns:
            merged_df['APIRepo_Stars'] = pd.NA
            logger.info("Columna 'APIRepo_Stars' añadida con NA porque no existía post-merge.")
        if 'APIRepo_Forks' not in merged_df.columns:
            merged_df['APIRepo_Forks'] = pd.NA
            logger.info("Columna 'APIRepo_Forks' añadida con NA porque no existía post-merge.")
            
        merged_df['APIRepo_Stars'] = pd.to_numeric(merged_df['APIRepo_Stars'], errors='coerce').astype('Int64')
        merged_df['APIRepo_Forks'] = pd.to_numeric(merged_df['APIRepo_Forks'], errors='coerce').astype('Int64')

        final_check_cols = ['LanguageWorkedWith', 'Country']
        missing_final_cols = [col for col in final_check_cols if col not in merged_df.columns]
        if missing_final_cols:
            logger.error(f"VERIFICACIÓN FINAL FALLIDA: Las columnas {missing_final_cols} AÚN FALTAN antes de to_json. Columnas actuales: {merged_df.columns.tolist()}")
        else:
            logger.info(f"VERIFICACIÓN FINAL OK: Las columnas {final_check_cols} están presentes. Columnas actuales: {merged_df.columns.tolist()}")

        return merged_df.to_json(orient="records", date_format="iso")

    except KeyError as e:
        logger.error(f"Error de KeyError (columna faltante) durante el merge: {e}", exc_info=True)
        if 'df_db' in locals() and isinstance(df_db, pd.DataFrame):
            logger.warning("KeyError durante el merge. Devolviendo df_db (posiblemente modificado) con columnas API vacías.")
            if 'LanguageWorkedWith' not in df_db.columns: df_db['LanguageWorkedWith'] = "Error - Missing in DB"
            if 'Country' not in df_db.columns: df_db['Country'] = "Error - Missing in DB"
            df_db['APIRepo_Stars'] = pd.NA
            df_db['APIRepo_Forks'] = pd.NA
            logger.info(f"KeyError. Devolviendo df_db con columnas: {df_db.columns.tolist()}")
            return df_db.to_json(orient="records", date_format="iso")
        return None 
    except Exception as e:
        logger.error(f"Error general durante el proceso de merge: {e}", exc_info=True)
        return None