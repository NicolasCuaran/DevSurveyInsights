import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_dimensional_model(df_clean_survey):
    try:
        demographic_cols = [
            'Country', 'Gender', 'Age', 'FormalEducation', 'RaceEthnicity'
        ]

        professional_experience_cols = [
            'DevType', 'CompanySize', 'Employment', 'YearsCodingProf',
            'UndergradMajor', 'UpdateCV'
        ]

        tech_tools_cols = [
            'LanguageWorkedWith', 'DatabaseWorkedWith', 'PlatformWorkedWith',
            'FrameworkWorkedWith', 'IDE', 'OperatingSystem', 'CommunicationTools',
            'Methodology', 'VersionControl'
        ]

        job_satisfaction_cols = [
            'JobSatisfaction', 'CareerSatisfaction', 'HopeFiveYears',
            'AvgAdminInterest', 'AvgAltContactImportance', 'AvgNonSalaryBenefitsImportance'
        ]

        miscellaneous_cols = [
            'OpenSource', 'StackOverflowVisit', 'StackOverflowHasAccount',
            'StackOverflowParticipate', 'AIDangerous', 'AIInteresting',
            'AIResponsible', 'AIFuture', 'Hobby'
        ]

        measure_cols = [
            'Benefit_SalaryBonuses', 'Benefit_RetirementPlan', 'Importance_Industry',
            'Importance_RemoteWork', 'Importance_Technologies', 'StandardizedMonthlySalaryCOP'
        ]

        all_needed_cols = list(set(
            demographic_cols + professional_experience_cols + tech_tools_cols +
            job_satisfaction_cols + miscellaneous_cols + measure_cols
        ))

        missing_cols = [col for col in all_needed_cols if col not in df_clean_survey.columns]
        if missing_cols:
            logging.error(f"Faltan las siguientes columnas requeridas en el DataFrame: {missing_cols}")
            return (None,) * 6

        logging.info("Creando tabla de dimensión: DimDemographic")
        dim_demographic = df_clean_survey[demographic_cols].drop_duplicates().reset_index(drop=True)
        dim_demographic['DimDemographic_ID'] = dim_demographic.index + 1
        dim_demographic = dim_demographic[['DimDemographic_ID'] + demographic_cols]
        logging.info(f"DimDemographic creada con {len(dim_demographic)} filas.")

        logging.info("Creando tabla de dimensión: DimProfessionalExperience")
        dim_professional_experience = df_clean_survey[professional_experience_cols].drop_duplicates().reset_index(drop=True)
        dim_professional_experience['DimProfessionalExperience_ID'] = dim_professional_experience.index + 1
        dim_professional_experience = dim_professional_experience[['DimProfessionalExperience_ID'] + professional_experience_cols]
        logging.info(f"DimProfessionalExperience creada con {len(dim_professional_experience)} filas.")

        logging.info("Creando tabla de dimensión: DimTechnologiesAndTools")
        dim_tech_tools = df_clean_survey[tech_tools_cols].drop_duplicates().reset_index(drop=True)
        dim_tech_tools['DimTechnologiesAndTools_ID'] = dim_tech_tools.index + 1
        dim_tech_tools = dim_tech_tools[['DimTechnologiesAndTools_ID'] + tech_tools_cols]
        logging.info(f"DimTechnologiesAndTools creada con {len(dim_tech_tools)} filas.")

        logging.info("Creando tabla de dimensión: DimJobSatisfaction")
        dim_job_satisfaction = df_clean_survey[job_satisfaction_cols].drop_duplicates().reset_index(drop=True)
        dim_job_satisfaction['DimJobSatisfaction_ID'] = dim_job_satisfaction.index + 1
        dim_job_satisfaction = dim_job_satisfaction[['DimJobSatisfaction_ID'] + job_satisfaction_cols]
        logging.info(f"DimJobSatisfaction creada con {len(dim_job_satisfaction)} filas.")

        logging.info("Creando tabla de dimensión: DimMiscellaneous")
        dim_miscellaneous = df_clean_survey[miscellaneous_cols].drop_duplicates().reset_index(drop=True)
        dim_miscellaneous['DimMiscellaneous_ID'] = dim_miscellaneous.index + 1
        dim_miscellaneous = dim_miscellaneous[['DimMiscellaneous_ID'] + miscellaneous_cols]
        logging.info(f"DimMiscellaneous creada con {len(dim_miscellaneous)} filas.")

        logging.info("Creando tabla de hechos: FactSurveyResponse")
        fact_survey_response = df_clean_survey.copy()

        fact_survey_response = pd.merge(fact_survey_response, dim_demographic, on=demographic_cols, how='left')
        fact_survey_response = pd.merge(fact_survey_response, dim_professional_experience, on=professional_experience_cols, how='left')
        fact_survey_response = pd.merge(fact_survey_response, dim_tech_tools, on=tech_tools_cols, how='left')
        fact_survey_response = pd.merge(fact_survey_response, dim_job_satisfaction, on=job_satisfaction_cols, how='left')
        fact_survey_response = pd.merge(fact_survey_response, dim_miscellaneous, on=miscellaneous_cols, how='left')
        logging.info("Merge con dimensiones completado para la tabla de hechos.")

        foreign_key_cols = [
            'DimDemographic_ID', 'DimProfessionalExperience_ID', 'DimTechnologiesAndTools_ID',
            'DimJobSatisfaction_ID', 'DimMiscellaneous_ID'
        ]

        final_fact_cols = foreign_key_cols + measure_cols
        fact_survey_response = fact_survey_response[final_fact_cols]

        fact_survey_response['FactSurveyResponse_ID'] = fact_survey_response.index + 1

        fact_survey_response = fact_survey_response[['FactSurveyResponse_ID'] + final_fact_cols]
        logging.info(f"FactSurveyResponse creada con {len(fact_survey_response)} filas.")

        logging.info("Ajustando tipos de datos para columnas de medidas.")
        for col in measure_cols:
            if col in fact_survey_response.columns:
                if fact_survey_response[col].dtype == 'object':
                    fact_survey_response[col] = pd.to_numeric(fact_survey_response[col], errors='coerce')

                if 'Benefit_' in col or 'Importance_' in col:
                    fact_survey_response[col] = fact_survey_response[col].astype('Int64')
                elif col == 'StandardizedMonthlySalaryCOP':
                    fact_survey_response[col] = fact_survey_response[col].astype(float)
        logging.info("Ajuste de tipos de datos completado.")

        return (dim_demographic, dim_professional_experience, dim_tech_tools,
                dim_job_satisfaction, dim_miscellaneous,
                fact_survey_response)

    except KeyError as e:
        logging.error(f"Error al procesar las columnas: {e}")
        return (None,) * 6
    except Exception as e:
        logging.error(f"Ocurrió un error durante la creación del modelo dimensional: {e}", exc_info=True)
        return (None,) * 6