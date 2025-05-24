# Great Expectations - Data Validation
import great_expectations as gx
import great_expectations.expectations as gxe
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    datefmt="%d/%m/%Y %I:%M:%S %p",
)

# ---------------------------------------------------------------------------
# Utilidades comunes
# ---------------------------------------------------------------------------

def get_gx_context():
    """Retrieve the Great Expectations context."""
    logging.info("Retrieving Great Expectations context.")
    return gx.get_context()

def gx_validation(asset_name, suite_name, df, gx_expectations_object):
    """Lanza la validación y devuelve un ExpectationSuiteValidationResult."""
    logging.info(
        f"Starting validation for asset '{asset_name}' with suite '{suite_name}'."
    )
    gx_context = get_gx_context()

    # ---- Datasource -------------------------------------------------------
    try:
        data_source = gx_context.data_sources.add_pandas("pandas")
        logging.info("Added new pandas data source.")
    except gx.exceptions.DataContextError:
        data_source = gx_context.data_sources.get("pandas")
        logging.info("Retrieved existing pandas data source.")

    # ---- Data asset -------------------------------------------------------
    try:
        data_source.delete_asset(name=asset_name)
        logging.info(f"Deleted existing asset '{asset_name}'.")
    except Exception:
        logging.info(f"No existing asset '{asset_name}' to delete.")

    data_asset = data_source.add_dataframe_asset(name=asset_name)
    logging.info(f"Added data asset '{asset_name}'.")

    # ---- Batch ------------------------------------------------------------
    batch_definition_name = f"batch_definition_{asset_name}"
    try:
        batch_definition = data_asset.get_batch_definition(
            name=batch_definition_name
        )
        logging.info(f"Retrieved batch definition '{batch_definition_name}'.")
    except KeyError:
        batch_definition = data_asset.add_batch_definition_whole_dataframe(
            name=batch_definition_name
        )
        logging.info(f"Added new batch definition '{batch_definition_name}'.")

    batch_parameters = {"dataframe": df}
    batch = batch_definition.get_batch(batch_parameters=batch_parameters)
    logging.info("Created batch for validation.")

    # ---- Expectation suite -----------------------------------------------
    try:
        suite = gx_context.suites.add(gx.ExpectationSuite(name=suite_name))
        logging.info(f"Added new expectation suite '{suite_name}'.")
    except gx.exceptions.DataContextError:
        gx_context.suites.delete(name=suite_name)
        suite = gx_context.suites.add(gx.ExpectationSuite(name=suite_name))
        logging.info(f"Replaced existing expectation suite '{suite_name}'.")

    for expectation in gx_expectations_object:
        suite.add_expectation(expectation)
        logging.info(f"Added expectation '{expectation}'.")

    # ---- Validación -------------------------------------------------------
    logging.info("Beginning data validation.")
    validation_results = batch.validate(suite)
    logging.info("Data validation completed.")

    if not validation_results.success:
        logging.error(
            f"Validation failed for {asset_name} with suite {suite_name}."
        )
        for result in validation_results.results:
            logging.error(result)
    else:
        logging.info(
            f"Validation succeeded for {asset_name} with suite {suite_name}."
        )
        for result in validation_results.results:
            logging.info(result)

    return validation_results  # ← sigue devolviendo el ESVR

# ---------------------------------------------------------------------------
# Validaciones específicas (DB y API)
# ---------------------------------------------------------------------------

def _build_not_null_expectations(columns):
    """Devuelve una lista de ExpectColumnValuesToNotBeNull para las columnas."""
    return [gxe.ExpectColumnValuesToNotBeNull(column=col) for col in columns]

def validate_db(df_gtd):
    """Valida el dataframe de base de datos y devuelve el df si pasa."""
    db_columns = [
        "Country", "Gender", "Age", "FormalEducation", "RaceEthnicity",
        "DevType", "CompanySize", "Employment", "YearsCodingProf",
        "UndergradMajor", "UpdateCV", "LanguageWorkedWith",
        "DatabaseWorkedWith", "PlatformWorkedWith", "FrameworkWorkedWith",
        "IDE", "OperatingSystem", "CommunicationTools", "Methodology",
        "VersionControl", "JobSatisfaction", "CareerSatisfaction",
        "HopeFiveYears", "AvgAdminInterest", "AvgAltContactImportance",
        "AvgNonSalaryBenefitsImportance", "OpenSource", "StackOverflowVisit",
        "StackOverflowHasAccount", "StackOverflowParticipate", "AIDangerous",
        "AIInteresting", "AIResponsible", "AIFuture", "Hobby",
        "Benefit_SalaryBonuses", "Benefit_RetirementPlan",
        "Importance_Industry", "Importance_RemoteWork",
        "Importance_Technologies", "StandardizedMonthlySalaryCOP",
    ]

    validation_results = gx_validation(
        "gtd",
        "gtd_suite",
        df_gtd,
        _build_not_null_expectations(db_columns),
    )

    # --- CAMBIO 1 ---------------------------------------------------------
    if not validation_results.success:
        raise ValueError("GX validation failed for GTD dataset")
    return df_gtd  # <- ahora tu DAG recibe un DataFrame válido

def validate_api(df_api):
    """Valida el dataframe de API y devuelve el df si pasa."""
    api_columns = [
        "Country", "LanguageWorkedWith", "RepositoryName",
        "Owner", "Stars", "Forks",
    ]

    validation_results = gx_validation(
        "gtd",
        "gtd_suite",
        df_api,
        _build_not_null_expectations(api_columns),
    )

    # --- CAMBIO 2 ---------------------------------------------------------
    if not validation_results.success:
        raise ValueError("GX validation failed for API dataset")
    return df_api