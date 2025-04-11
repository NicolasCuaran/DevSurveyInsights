# DevSurveyInsights

In this project we to automate the processing of developer surveys. We have implemented an ETL pipeline using **Docker** to containerize the entire environment, which simplifies installation, deployment, and maintenance. Task orchestration is handled via **Apache Airflow**, and the selected database is **PostgreSQL**. This setup allows us to extract, transform, and load data efficiently.

---

## Project Objectives

- **Extraction:**  
  Gather and consolidate data from CSV survey files and, when applicable, data fetched from external APIs.

- **Transformation:**  
  Clean, validate, and enrich the data using Jupyter notebooks and Python scripts, ensuring the processed information is accurate for further analysis.

- **Loading:**  
  Insert the processed data into a PostgreSQL database for efficient analysis, report generation, and trend visualization.

---

## Project Dataset

This dataset comes from the Stack Overflow Developer Survey 2018 and can be downloaded from:

🔗 [Download the dataset](https://www.kaggle.com/datasets/stackoverflow/stack-overflow-2018-developer-survey?select=survey_results_public.csv)

### Dataset Description

- **Name:** `survey_results_public.csv`  
- **Source:** Stack Overflow Developer Survey 2018  

### Dataset Columns

Below is a concise description of each column from the dataset:

- **Respondent:** Randomized ID for each respondent.
- **Hobby:** Indicates if the respondent codes as a hobby.
- **OpenSource:** Indicates if the respondent contributes to open-source projects.
- **Country:** Respondent's current country of residence.
- **Student:** Indicates whether the respondent is currently enrolled in formal education.
- **Employment:** Current employment status.
- **FormalEducation:** Highest level of formal education completed.
- **UndergradMajor:** Main field of undergraduate study.
- **CompanySize:** Approximate size of the respondent's company.
- **DevType:** Developer roles and types.
- **YearsCoding:** Total years of coding experience.
- **YearsCodingProf:** Years of professional coding experience.
- **JobSatisfaction:** Satisfaction level with the current job.
- **CareerSatisfaction:** Overall career satisfaction.
- **HopeFiveYears:** Job expectations for the next five years.
- **JobSearchStatus:** Current job-seeking status.
- **AssessJob1-10:** Importance of various job aspects (industry, technologies, salary, etc.).
- **AssessBenefits1-11:** Importance of job benefits (salary, healthcare, etc.).
- **JobContactPriorities1-5:** Preferences for how to be contacted about job opportunities.
- **JobEmailPriorities1-7:** Importance of details included in recruitment emails.
- **Salary:** Current salary before taxes and deductions.
- **ConvertedSalary:** Annual salary converted to USD.
- **CommunicationTools:** Tools used for workplace communication.
- **TimeFullyProductive:** Estimated time for a new developer to become fully productive.
- **EducationTypes:** Types of non-degree education used.
- **SelfTaughtTypes:** Resources used for self-taught programming.
- **TimeAfterBootcamp:** Time to secure a job after a coding bootcamp.
- **HackathonReasons:** Reasons for participating in hackathons.
- **AdsAgreeDisagree:** Opinions about relevant online advertising.
- **AdsPriorities:** Importance of various advertising qualities.
- **UpdateCV:** Reason for the most recent CV update.
- **Currency:** Currency used daily.
- **SalaryType:** Frequency of salary payment (weekly, monthly, yearly).
- **Gender:** Gender identity.
- **RaceEthnicity:** Race or ethnicity identity.
- **Age:** Age of the respondent.
- **Dependents:** Number of dependents.
- **OperatingSystem:** Primary operating system used for work.
- **NumberMonitors:** Number of monitors at the workspace.
- **Methodology:** Work methodologies used.
- **VersionControl:** Version control systems regularly used.

---

## Technologies and Tools

- **Language:** Python
- **Task Orchestration:** Apache Airflow (containerized)
- **Database:** PostgreSQL (containerized)
- **Containers:** Docker and Docker Compose

### Libraries Used

- **pandas:** Data manipulation, cleaning, and analysis using DataFrames.
- **SQLAlchemy (create_engine):** Establishing connections and interacting with PostgreSQL.
- **python-dotenv (load_dotenv):** Secure management of environment variables.
- **os:** Interacting with the operating system for file paths and environment variables.
- **matplotlib.pyplot:** Creating clear and detailed visualizations and charts.
- **seaborn:** Generating statistical graphics and visually appealing charts.
- **numpy:** Efficient numerical data handling and performing statistical operations.

---

## GitHub GraphQL API Integration

In our project, we also leverage the **GitHub GraphQL API** to enhance our analysis of developer data. This API allows us to:

- Retrieve detailed information on repositories, commits, pull requests, and issues.
- Perform complex queries that fetch nested data structures in a single request, thereby improving efficiency.
- Integrate data directly from GitHub to enrich our developer surveys, providing a deeper insight into open source contributions and related activities.

For authentication, we use a personal access token stored in our **.env** file as `GITHUB_TOKEN`. This token is essential for authorizing our queries and ensuring secure interaction with the GitHub GraphQL API.

---

## Repository Organization

```
DevSurveyInsights/
├── airflow/             
│   ├── dags/                    # Definition of Airflow DAGs.
│   ├── config/                  # Airflow-specific configurations.
│   ├── logs/                    # Logs generated during DAG executions.
│   └── plugins/                 # Additional Airflow plugins.
│
├── data/                        
│   ├── data_api.csv             # Data extracted from APIs.
│   ├── survey_results_public.csv# Raw survey results.
│   └── survey_results_schema.csv# Schema detailing the data structure.
│
├── notebooks/                   
│   ├── .env                     # Environment variables for notebooks.
│   ├── 01_extract_load.ipynb    # Notebook for data extraction and initial loading.
│   ├── 02_survey_eda.ipynb      # Exploratory analysis of the survey data.
│   ├── 03_load_clean_survey.ipynb# Data cleaning and transformation.
│   ├── 04_Api_EDA.ipynb         # Analysis of data extracted via API.
│   └── data_piplane.ipynb       # Additional or specialized analysis.
│
├── scripts/                     
│   └── setup.py                 # Script to initialize the project's database.
│
├── src/                         
│   ├── database/                # Modules for database operations.
│   │   ├── .env                 
│   │   └── db_operations.py     # Functions to insert, update, and delete data.
│   │
│   ├── extract/                 # Modules for data extraction.
│   │   ├── .env                 
│   │   ├── extract_api.py       # Module for API-based data extraction.
│   │   └── extract_db.py        # Module for database-based data extraction.
│   │
│   ├── load/                    # Modules for loading processed data.
│   │   └── load_dm.py           # Specific functions for data loading.
│   │
│   └── transform/               # Modules for data transformation and cleaning.
│       ├── transform_api.py     
│       ├── transform_dm.py      
│       └── __pycache__/         # Compiled files.
│
├── venv/                        # Local virtual environment (not used with Docker).
│
├── .env                         # Global environment variable file.
├── .gitignore                   # Files and directories excluded from versioning.
├── docker-compose.yaml          # Docker Compose orchestration file.
├── Dockerfile                   # Docker image build definition.
├── README.md                    # This file.
├── requirements.txt             # General project dependencies.
└── requirements_docker.txt      # Dependencies for the Docker environment.
```

---

## Installation and Execution Using Docker

We use Docker exclusively for this project implementation, ensuring a robust and reproducible environment.

### 1. Clone the Repository

```bash
git clone https://github.com/your_username/DevSurveyInsights.git
cd DevSurveyInsights
```

### 2. Configure Environment Variables

Ensure that the **.env** file is present at the project root and contains the necessary configuration, as detailed above.

### 3. Launch the Docker Environment

Run the following command to start all services with Docker Compose:

```bash
docker-compose up
```

This command will:
- Build the necessary images if they are not already built.
- Start the **Apache Airflow** container, which handles the execution and orchestration of the ETL pipeline.
- Launch the **PostgreSQL** container for data storage.
- Coordinate any additional services defined in *docker-compose.yaml*.

### 4. Access the Airflow Interface

Once the environment is up and running, access the Airflow interface via:

[http://localhost:8080](http://localhost:8080)

From the Airflow interface, our team can:
- Visualize and manage the DAGs.
- Trigger the ETL pipeline.
- Monitor task execution and review logs.

---

## Running the Project and Data Visualization

### Data Extraction and Loading

- **Step 1:** Open and run the `01_extract_load.ipynb` notebook to load the CSV data into your PostgreSQL database.
- **Step 2:** Execute the `02_survey_eda.ipynb` notebook to perform exploratory analysis on the dataset.
- **Step 3:** Run the `03_load_clean_survey.ipynb` notebook to clean and transform the data (this includes applying the "HIRED" logic).
- **Step 4:** Use the `setup.py` script to initialize the database. This script loads configuration from the environment and creates the necessary database tables if they don’t exist.

### Creating a Power BI Connection to PostgreSQL

To visualize the data using Power BI:
1. Open Power BI and click on **Get Data**.
2. Search for PostgreSQL and select it.
3. Enter your server name (e.g., localhost) and your database name (e.g., dev_survey_insights).
4. Provide your PostgreSQL username and password.
5. Select the appropriate table (e.g., the table containing your cleaned survey data).
6. Click **Load** to import the data into Power BI.
7. Create interactive dashboards and visualizations based on the imported data.

---

## Conclusions

From the implementation and configuration of **DevSurveyInsights** using Docker, our team has learned that:

1. **Complete Containerization Simplifies Deployment:**  
   Using Docker exclusively allows us to quickly bring up the entire environment (Airflow and PostgreSQL) without worrying about machine-specific dependencies.

2. **Effective Automation and Orchestration:**  
   Apache Airflow integrates seamlessly into the Docker environment, enabling scheduled and monitored execution of DAGs, which ensures repeatability and reliability of the ETL pipeline.

3. **Centralized and Secure Configuration:**  
   Managing environment variables through a centralized **.env** file keeps the configuration organized, simplifies modifications, and enhances security by keeping sensitive credentials in one place.

4. **Integration and Flexibility:**  
   Although the main environment is containerized, the notebooks remain a powerful tool for exploratory analysis and testing, perfectly integrating with our Docker-managed system.



---