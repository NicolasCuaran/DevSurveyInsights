import pandas as pd

def dimensional_model(df):
    try:
        # Rename columns to match SQL schema and be valid identifiers
        # (Handle C#, C++, Notepad++)
        rename_map = {
            'Lang_C#': 'Lang_C_sharp',
            'Lang_C++': 'Lang_C_plusplus',
            'IDE_Notepad++': 'IDE_Notepad_plus__plus' # Match SQL definition
        }
        df = df.rename(columns=rename_map)
        print("Renamed columns with special characters.")

        # Optional: Handle potential 'Unknown' strings if they should be NaN
        # For dimension attributes, 'Unknown' might be a valid category.
        # For measures like Salary, they might need conversion or replacement.
        # df.replace('Unknown', np.nan, inplace=True) 
        # Ensure numeric columns are numeric (errors='coerce' turns invalid entries into NaN)
        numeric_cols = ['Age', 'YearsCoding', 'YearsCodingProf', 'ConvertedSalary']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Ensure integer columns (like language/IDE usage) are integers, handling potential NaN/Floats
        int_cols = [col for col in df.columns if col.startswith('Lang_') or col.startswith('DB_') or col.startswith('IDE_')]
        for col in int_cols:
             if col in df.columns:
                # Convert to nullable Integer type to handle potential NaNs gracefully
                df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64') 

        print("Performed initial data type conversions.")

        # --- 2. Create Dimension DataFrames ---

        # Dim_User
        user_cols = [
            'Respondent', 'Country', 'Gender', 'Age', 'FormalEducation',
            'RaceEthnicity', 'DevType', 'CompanySize', 'Employment'
        ]
        dim_user = df[user_cols].drop_duplicates().reset_index(drop=True)
        dim_user['Dim_User_ID'] = dim_user.index + 1
        dim_user = dim_user[['Dim_User_ID'] + user_cols] # Reorder columns
        print(f"Created Dim_User with {len(dim_user)} unique rows.")

        # Dim_PerfilComportamental
        perfil_cols = ['JobSatisfaction', 'CareerSatisfaction', 'HopeFiveYears']
        dim_perfil = df[perfil_cols].drop_duplicates().reset_index(drop=True)
        dim_perfil['Dim_PerfilComportamental_ID'] = dim_perfil.index + 1
        dim_perfil = dim_perfil[['Dim_PerfilComportamental_ID'] + perfil_cols]
        print(f"Created Dim_PerfilComportamental with {len(dim_perfil)} unique rows.")

        # Dim_HabilidadesTecnicas
        habilidades_cols = [
            'OperatingSystem', 'IDE_Visual_Studio_Code', 'IDE_Visual_Studio',
            'IDE_Notepad_plus__plus', 'IDE_Sublime_Text', 'IDE_Vim', 'IDE_Other'
        ]
         # Ensure all expected columns exist, add if missing and fill with a default (e.g., 0 or NaN)
        for col in habilidades_cols:
            if col not in df.columns:
                print(f"Warning: Column '{col}' not found in CSV. Adding it with default value 0.")
                df[col] = 0 # Or np.nan if appropriate
                df[col] = df[col].astype('Int64') # Match type if needed

        dim_habilidades = df[habilidades_cols].drop_duplicates().reset_index(drop=True)
        dim_habilidades['Dim_HabilidadesTecnicas_ID'] = dim_habilidades.index + 1
        dim_habilidades = dim_habilidades[['Dim_HabilidadesTecnicas_ID'] + habilidades_cols]
        print(f"Created Dim_HabilidadesTecnicas with {len(dim_habilidades)} unique rows.")


        # Dim_Database
        database_cols = ['DB_DataWarehouse', 'DB_NoSQL', 'DB_Other', 'DB_SQL']
        # Ensure all expected columns exist
        for col in database_cols:
            if col not in df.columns:
                 print(f"Warning: Column '{col}' not found in CSV. Adding it with default value 0.")
                 df[col] = 0
                 df[col] = df[col].astype('Int64')

        dim_database = df[database_cols].drop_duplicates().reset_index(drop=True)
        dim_database['Dim_Database_ID'] = dim_database.index + 1
        dim_database = dim_database[['Dim_Database_ID'] + database_cols]
        print(f"Created Dim_Database with {len(dim_database)} unique rows.")


        # Dim_ProgrammingLanguages
        languages_cols = [
            'Lang_JavaScript', 'Lang_HTML', 'Lang_CSS', 'Lang_Python', 'Lang_Java',
            'Lang_Bash_Shell', 'Lang_C_sharp', 'Lang_C_plusplus', 'Lang_PHP',
            'Lang_C', 'Lang_TypeScript', 'Lang_Ruby', 'Lang_Swift', 'Lang_Kotlin',
            'Lang_Other'
        ]
         # Ensure all expected columns exist
        for col in languages_cols:
            if col not in df.columns:
                 print(f"Warning: Column '{col}' not found in CSV. Adding it with default value 0.")
                 df[col] = 0
                 df[col] = df[col].astype('Int64')

        dim_languages = df[languages_cols].drop_duplicates().reset_index(drop=True)
        dim_languages['Dim_ProgrammingLanguages_ID'] = dim_languages.index + 1
        dim_languages = dim_languages[['Dim_ProgrammingLanguages_ID'] + languages_cols]
        print(f"Created Dim_ProgrammingLanguages with {len(dim_languages)} unique rows.")

        # --- 3. Create Fact Table ---

        # Start with the original data (or a copy)
        fact_survey = df.copy()

        # Merge with dimensions to get foreign keys
        print("Merging data to create Fact table...")
        fact_survey = pd.merge(fact_survey, dim_user, on=user_cols, how='left')
        fact_survey = pd.merge(fact_survey, dim_perfil, on=perfil_cols, how='left')
        fact_survey = pd.merge(fact_survey, dim_habilidades, on=habilidades_cols, how='left')
        fact_survey = pd.merge(fact_survey, dim_database, on=database_cols, how='left')
        fact_survey = pd.merge(fact_survey, dim_languages, on=languages_cols, how='left')
        print("Merging complete.")

        # Select only necessary columns (FKs and Measures)
        fact_cols_final = [
            'Dim_User_ID',
            'Dim_PerfilComportamental_ID',
            'Dim_Database_ID',
            'Dim_HabilidadesTecnicas_ID',
            'Dim_ProgrammingLanguages_ID',
            'ConvertedSalary',
            'YearsCoding',
            'YearsCodingProf'
        ]
        fact_survey = fact_survey[fact_cols_final]

        # Add Fact_ID
        fact_survey['Fact_ID'] = fact_survey.index + 1
        
        # Reorder columns to have Fact_ID first
        fact_survey = fact_survey[['Fact_ID'] + fact_cols_final]
        print(f"Created Fact_Survey with {len(fact_survey)} rows.")


        # --- 4. Return DataFrames ---
        return (dim_user, dim_perfil, dim_habilidades, dim_database, 
                dim_languages, fact_survey)

    except KeyError as e:
        print(f"Error: A required column is missing from the CSV: {e}")
        print("Please check the CSV headers against the expected columns.")
        return (None,) * 6
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return (None,) * 6