# DevSurveyInsights

## Project Dataset

This dataset comes from the Stack Overflow Developer Survey 2018 and can be downloaded from the following link:

🔗 [Download the dataset](https://www.kaggle.com/datasets/stackoverflow/stack-overflow-2018-developer-survey?select=survey_results_public.csv)

### Dataset Description

**Name:** `survey_results_public.csv`
**Source:** Stack Overflow Developer Survey 2018

### Dataset Column

Below is a concise description of each column from the dataset:

Respondent: Randomized ID for each respondent.

Hobby: Indicates if respondent codes as a hobby.

OpenSource: Indicates if the respondent contributes to open-source projects.

Country: Respondent's current country of residence.

Student: Whether currently enrolled in formal education.

Employment: Current employment status.

FormalEducation: Highest level of formal education completed.

UndergradMajor: Main field of undergraduate study.

CompanySize: Approximate size of the respondent's company.

DevType: Developer roles and types.

YearsCoding: Total years of coding experience.

YearsCodingProf: Years of professional coding experience.

JobSatisfaction: Satisfaction level with current job.

CareerSatisfaction: Overall career satisfaction.

HopeFiveYears: Job expectations for the next five years.

JobSearchStatus: Current job-seeking status.

AssessJob1-10: Importance of various job aspects (industry, technologies, salary, etc.).

AssessBenefits1-11: Importance of job benefits (salary, healthcare, etc.).

JobContactPriorities1-5: Preferences for how to be contacted about job opportunities.

JobEmailPriorities1-7: Importance of details included in recruitment emails.

Salary: Current salary before taxes and deductions.

ConvertedSalary: Annual salary converted to USD.

CommunicationTools: Tools used for workplace communication.

TimeFullyProductive: Estimated time for a new developer to become fully productive.

EducationTypes: Types of non-degree education used.

SelfTaughtTypes: Resources used for self-taught programming.

TimeAfterBootcamp: Time to secure a job after a coding bootcamp.

HackathonReasons: Reasons for participating in hackathons.

AdsAgreeDisagree: Opinions about relevant online advertising.

AdsPriorities: Importance of various advertising qualities.

UpdateCV: Reason for the most recent CV update.

Currency: Currency used daily.

SalaryType: Frequency of salary payment (weekly, monthly, yearly).

Gender: Gender identity.

RaceEthnicity: Race or ethnicity identity.

Age: Age of respondent.

Dependents: Number of dependents.

OperatingSystem: Primary operating system used for work.

NumberMonitors: Number of monitors at workspace.

Methodology: Work methodologies used.

VersionControl: Version control systems regularly used.

### Tools Used

The following tools were utilized to carry out the analysis and visualization of the Stack Overflow Developer Survey 2018 data:

Python 3: The primary programming language used for data processing, analysis, and cleaning, chosen for its versatility and ability to efficiently handle large datasets.

Jupyter Notebook: An interactive environment that enables step-by-step execution of Python code, simplifying exploratory data analysis and clearly documenting the analysis process.

PostgreSQL: A relational database management system used for efficient storage of cleaned and processed data, enabling quick and complex data querying for further analysis.

Power BI: Utilized for creating interactive visualizations and dashboards, allowing clear and effective interpretation of analytical results.

### Libraries Used

During the project's development, several Python libraries were employed to facilitate data processing, analysis, and visualization of the Stack Overflow Developer Survey 2018 data:

pandas: Used for data manipulation, cleaning, and analysis, thanks to its efficient data structures such as DataFrames.

SQLAlchemy (create_engine): Library used to establish connections and facilitate interaction between Python and the PostgreSQL database, specifically through the create_engine function.

dotenv (load_dotenv): Used for securely managing environment variables and credentials stored in .env files, specifically using the load_dotenv function.

os: Standard library for interacting with the operating system, especially useful for handling file paths and environment variables.

matplotlib.pyplot: Fundamental library for creating clear and detailed visualizations and charts.

seaborn: Library built on Matplotlib, used to generate statistical graphics and visually appealing, easily interpretable visualizations.

numpy: Employed for efficient numerical data handling, facilitating statistical calculations and mathematical operations required for analysis.

### Repository Organization

notebooks:
This folder contains all the Jupyter notebooks:

01_extraction_load.ipynb: Responsible for data extraction and loading.

02_survey_EDA.ipynb: Used for exploratory data analysis (EDA) on the dataset.

03_Load_Clean_Survey.ipynb: Handles data cleaning and transformation

Scrips:is script is responsible for initializing the project's database. It loads database configuration from environment variables, connects to a PostgreSQL instance using SQLAlchemy, and creates the database if it doesn't already exist.

### Installation and Setup

Follow these steps to set up the project on your local machine:

1. **Clone the Repository:**

    ```bash
    git clone https://github.com/NicolasCuaran/DevSurveyInsights/tree/feature/gomez
    ```

2. **Navigate to the Project Directory:**

    ```bash
    cd devsurveyinsights
    ```

3. **Create a Virtual Environment:**

    ```bash
    python -m venv venv
    ```

4. **Activate the Virtual Environment:**

    ```bash
    venv\Scripts\activate
    ```

5. **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

6. **Create Database in postgreSQL**

## Running the Project

### running setup.py:

It loads database configuration from environment variables, connects to a PostgreSQL instance using SQLAlchemy, and creates the database if it doesn't already exist. Then, it defines the schema for a table named raw_survey—with columns corresponding to various survey fields from the Stack Overflow Developer Survey 2018—and creates the table within the database.

1. **Data Extraction and Load:**

    - Open and run the `01_extraction_load.ipynb` notebook to load the CSV data into your database.

2. **Exploratory Data Analysis (EDA):**

    - Execute the `02_survey_EDA.ipynb` notebook to explore the dataset and understand its characteristics.

3. **Data Cleaning and Transformation:**
    - Run the `03_Load_Clean_Survey.ipynb` notebook to clean the data and apply the necessary transformations (including the "HIRED" logic).

# Creating a Power BI Connection to PostgreSQL

In the top menu bar of Power BI, click Get Data.

Search for PostgreSQL and select it.

In the connection dialog, enter your server name (for example, localhost) and your database name (for example, postgres).

When prompted, provide the username and password for your PostgreSQL database.

Choose the table candidates_hired from the available list.

Click Load to import the data into Power BI.

You can now start creating your visualizations using the imported data.
