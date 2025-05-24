
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import pandas as pd
import numpy as np
import pytest


#Tests para transform_api.py

from src.transform.transform_api import transform__api_data, _normalize_country_value

def test_transform_api_non_dataframe_input():
    """Si la entrada no es DataFrame, debe devolver un DataFrame vacío."""
    result = transform__api_data("not a df")
    assert isinstance(result, pd.DataFrame)
    assert result.empty

def test_transform_api_empty_df():
    """Si el DataFrame está vacío, debe retornarlo tal cual."""
    df = pd.DataFrame()
    result = transform__api_data(df)
    assert result is df

def test_normalize_country_value_edge_cases():
    """Prueba _normalize_country_value con varios casos límite."""
    assert _normalize_country_value(None, {}, []) == "Other"
    assert _normalize_country_value("unknown", {}, []) == "Other"
    assert _normalize_country_value("", {}, []) == "Other"
    mapping = {"TEST": "TestLand"}
    assert _normalize_country_value("test", mapping, []) == "TestLand"
    mapping = {"TES": "TesLand"}
    assert _normalize_country_value("xxxTEstyyy", mapping, []) == "TesLand"
    valid = ["Val"]
    assert _normalize_country_value("Val", {}, valid) == "Val"
    assert _normalize_country_value("NoMap", {}, valid) == "Other"

def test_transform_api_data_language_and_country_and_counts():
    """Verifica LanguageWorkedWith, Country, Stars y Forks."""
    df = pd.DataFrame({
        "LanguageWorkedWith": [None, "None", "Python"],
        "Country": ["Barcelona, Spain", "uNkNoWn", "USA"],
        "Stars": ["10", "abc", 5],
        "Forks": ["", "2", np.nan],
        "RepositoryName": ["repo1", None, "repo3"],
        "Owner": ["owner1", "owner2", None],
    })
    out = transform__api_data(df)


    assert out["LanguageWorkedWith"].tolist() == ["Not Specified", "Not Specified", "Python"]

    assert out["Country"].tolist() == ["Spain", "Other", "Other"]


    assert out["Stars"].tolist() == [10, 0, 5]
    assert out["Forks"].tolist() == [0, 2, 0]

   
    for col in ["LanguageWorkedWith", "RepositoryName", "Owner", "Country"]:
        assert out[col].dtype == object


#Tests para transform_dm.py

from src.transform.transform_dm import create_dimensional_model

def test_create_dimensional_model_missing_columns():
    """Si faltan columnas obligatorias, retorna (None,)*6."""
    df = pd.DataFrame({"foo": [1]})
    dims = create_dimensional_model(df)
    assert dims == (None, None, None, None, None, None)

def test_create_dimensional_model_full_cycle():
    """Flujo completo: dimensiones únicas y fact table con FKs y medidas."""
    df = pd.DataFrame({
       
        'Country': ['A', 'B'],
        'Gender': ['M', 'F'],
        'Age': [30, 40],
        'FormalEducation': ['X', 'Y'],
        'RaceEthnicity': ['R1', 'R2'],
        
        'DevType': ['D1', 'D2'],
        'CompanySize': ['C1', 'C2'],
        'Employment': ['E1', 'E2'],
        'YearsCodingProf': [1, 2],
        'UndergradMajor': ['U1', 'U2'],
        'UpdateCV': ['Yes', 'No'],
        
        'LanguageWorkedWith': ['L1', 'L2'],
        'DatabaseWorkedWith': ['DB1', 'DB2'],
        'PlatformWorkedWith': ['P1', 'P2'],
        'FrameworkWorkedWith': ['F1', 'F2'],
        'IDE': ['I1', 'I2'],
        'OperatingSystem': ['OS1', 'OS2'],
        'CommunicationTools': ['C1', 'C2'],
        'Methodology': ['M1', 'M2'],
        'VersionControl': ['V1', 'V2'],
        
        'JobSatisfaction': [3, 4],
        'CareerSatisfaction': [5, 6],
        'HopeFiveYears': [7, 8],
        'AvgAdminInterest': [1.1, 2.2],
        'AvgAltContactImportance': [3.3, 4.4],
        'AvgNonSalaryBenefitsImportance': [5.5, 6.6],
        
        'OpenSource': ['Y', 'N'],
        'StackOverflowVisit': [True, False],
        'StackOverflowHasAccount': [False, True],
        'StackOverflowParticipate': [False, False],
        'AIDangerous': [0, 1],
        'AIInteresting': [1, 0],
        'AIResponsible': [0, 1],
        'AIFuture': [1, 0],
        'Hobby': ['H1', 'H2'],
       
        'Benefit_SalaryBonuses': [1, 2],
        'Benefit_RetirementPlan': [3, 4],
        'Importance_Industry': [5, 6],
        'Importance_RemoteWork': [7, 8],
        'Importance_Technologies': [9, 10],
        'StandardizedMonthlySalaryCOP': [100.0, 200.0],
    })

    dim_dem, dim_prof, dim_tech, dim_job, dim_misc, fact = create_dimensional_model(df)

   
    assert dim_dem["DimDemographic_ID"].tolist() == [1, 2]
    assert dim_dem.columns.tolist()[0] == "DimDemographic_ID"

    
    expected_fk = [
        "DimDemographic_ID",
        "DimProfessionalExperience_ID",
        "DimTechnologiesAndTools_ID",
        "DimJobSatisfaction_ID",
        "DimMiscellaneous_ID"
    ]
    expected_measures = [
        "Benefit_SalaryBonuses",
        "Benefit_RetirementPlan",
        "Importance_Industry",
        "Importance_RemoteWork",
        "Importance_Technologies",
        "StandardizedMonthlySalaryCOP"
    ]
    cols = fact.columns.tolist()
    assert cols[0] == "FactSurveyResponse_ID"
    for fk in expected_fk:
        assert fk in cols
    for m in expected_measures:
        assert m in cols

    assert fact["Benefit_SalaryBonuses"].dtype == "Int64"
    assert fact["StandardizedMonthlySalaryCOP"].dtype == float
