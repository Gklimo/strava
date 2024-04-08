# Strava Data Engineering Pipeline

Welcome to the Strava Data Engineering Pipeline project - an advanced data pipeline designed to capture, transform, and analyze Strava athletic activity data for detailed performance analytics.

## TABLE OF CONTENTS
- [1. Project Goals](#project-goals)
- [2. Solution Architecture](#solution-architecture)
- [3. Dimensional Model](#dimensional-model)
- [4. Data Engineering Pipeline](#data-engineering-pipeline)
  - [4.1. Data Extraction](#data-extraction)
  - [4.2. Change Data Capture with Airbyte](#change-data-capture-with-airbyte)
  - [4.3. Data Transformation with dbt](#data-transformation-with-dbt)
  - [4.4. Orchestration with Dagster](#orchestration-with-dagster)
  - [4.5. Data Visualization with Preset](#data-visualization-with-preset)
- [5. Project Setup](#project-setup)
- [6. Next Steps](#next-steps)
- [7. Acknowledgements](#acknowledgements)

## PROJECT GOALS
This project aims to provide a comprehensive view of athletes' performance by analyzing Strava activity data. By setting up a sophisticated ELT (Extract, Load, Transform) pipeline, we can track key performance indicators over time, compare activity types, and delve into the data on a per-athlete basis. The geospatial visualization of activities further allows us to uncover patterns and trends related to locations and movements.

## SOLUTION ARCHITECTURE
The pipeline employs a multi-faceted approach, starting with data extraction from the Strava API, followed by a replication into a PostgreSQL database in Docker container. The data is then processed through a series of transformations in Snowflake using dbt, orchestrated by Dagster, and finally visualized using Preset for easy interpretation and insight gathering.

![Solution Architecture Overview](/path/to/solution_architecture_image.png)

## DIMENSIONAL MODEL
Our data warehouse is designed with a star schema in mind, optimizing for query performance and simplicity. The dimensions provide context for the activities, such as when (dim_date), where (dim_location), and by whom (dim_athlete) they were performed. The fact tables (fact_activity, fact_monthly_activities_snapshot) record the metrics and measures related to the activities themselves.

![Entity Relationship Diagram](/path/to/erd_image.png)

## DATA ENGINEERING PIPELINE
![image](https://github.com/Gklimo/strava/assets/84771383/4fadb915-f9e0-4ae8-9e39-c3351eb82080)

### Data Extraction
The project uses the Strava API to source data on athletic activities and athlete profiles. Utilizing access tokens, it performs incremental extraction based on the `activity_date`, ensuring that each data pull is efficient and up-to-date.

### Change Data Capture with Airbyte
We utilize Airbyte's Change Data Capture (CDC) capabilities to monitor and record changes in our PostgreSQL database. This data is then streamed into our Snowflake data warehouse, allowing for real-time data updates and minimizing the load on our source database.

### Data Transformation with dbt
In Snowflake, dbt (data build tool) manages the transformation of our raw data into a refined format ready for analysis. It creates staging, dimensional, and fact tables, implementing business logic and ensuring data quality. Our slowly changing dimension for athlete data captures changes over time, preserving historical context.

#### Slowly Changing Dimension
The `dim_athlete` table is an example of a slowly changing dimension, which tracks the history of changes to an athlete's profile, providing insights into their development over time.

#### Aggregate Fact Table
Our `fact_monthly_activities_snapshot` table provides a monthly roll-up of activity data, which is critical for trend analysis and monthly performance tracking.

#### BI Analysis Table
The `bi_analysis` table is specifically structured to support the Preset dashboard visualizations, enabling easy access to pre-calculated metrics for reporting.

### Orchestration with Dagster
Dagster orchestrates the entire pipeline, managing dependencies, scheduling jobs, and ensuring data freshness. It utilizes partitions to enhance performance, making data processing more efficient.

### CI/CD Integration
To ensure high-quality code and seamless integration of new features, this project incorporates Continuous Integration (CI) and Continuous Deployment (CD) practices facilitated by GitHub Actions and Dagster Cloud.

#### Continuous Integration
Our CI pipeline is designed to automatically trigger a series of checks and tests upon each code commit to the repository. This includes:

- **Code Linting with Flake8**: We use Flake8 in `.github/workflows/deploy.yml` to enforce Python code standards and detect errors. The linter is configured to catch issues related to syntax errors (E9), name errors (F63), most other error rules (F7), and systematic errors (F82). Here's the GitHub Actions configuration snippet for Flake8:
- **dbt Tests**: dbt models are tested to ensure data integrity and consistency within our transformations.
- **Dagster Op Tests**: The `test_ops.py` script contains unit tests that validate the functionality of custom operations and logic within the pipeline.
- **Python Environment Check**: We are verifying the Python interpreter's basic functionality by defining tests in`.github/workflows/deploy.yml` to ensure our environment is correctly set up for further tasks


#### Continuous Deployment
Our CD pipeline automates the deployment process, allowing for tested and verified code to be deployed to the production environment with minimal manual intervention. Key components include:

- **Environment Variable Management**: Critical for maintaining security and operability across different stages of deployment.
- **Automated Deployment**: The `.github/workflows/deploy.yml` file defines the CD pipeline that automates the deployment of dbt models and Dagster assets to the cloud environment upon successful CI checks.

By integrating CI/CD into our workflow, we maintain a robust, agile, and error-resistant development cycle, ensuring that our data pipeline remains reliable and up-to-date with the latest code enhancements and bug fixes.

---
*Integration of CI/CD processes into the project is streamlining development and deployment, ensuring code quality and operational continuity.*

### Data Visualization with Preset
Preset is the final piece of our pipeline, turning our rich datasets into actionable insights through interactive dashboards. It provides a user-friendly interface to explore the data, with the ability to drill down into specific areas of interest.

## PROJECT SETUP
This section will detail the necessary steps to get the pipeline up and running, including setting up the local development environment, deploying the Airbyte connectors, and configuring the dbt models in Snowflake.

### Create .env file with your tokens and database credentials based on .template_env file provided

### Generating a Strava Refresh Token

To access Strava activities with extended permissions, you'll need to obtain a refresh token with the appropriate scope. Follow these steps to generate your token:

1. **Create a Strava App**: Register your application in the Strava settings to receive a Client ID and Client Secret.

2. **Request Access with Extended Scope**:
   Construct and visit the URL in your browser, replacing `[REPLACE_WITH_YOUR_CLIENT_ID]` with your actual Client ID.
`http://www.strava.com/oauth/authorize?client_id=[REPLACE_WITH_YOUR_CLIENT_ID]&response_type=code&redirect_uri=http://localhost/exchange_token&approval_prompt=force&scope=activity:read_all`

3. **Authorize and Capture the Code**:
- After clicking 'Authorize' on the Strava authorization page, you'll be redirected to a URL containing a code parameter.
- The redirect will look something like this: `http://localhost/exchange_token?state=&code=[CODE]&scope=read,activity:read_all`
- Extract the `[CODE]` value from the URL.

4. **Exchange Code for Token**:
Run the following `curl` command, replacing `[YOUR_CLIENT_SECRET]` with your Client Secret and `[CODE]` with the code extracted in the previous step.
```bash
curl -X POST https://www.strava.com/oauth/token \
-d "client_id=[YOUR_CLIENT_ID]" \
-d "client_secret=[YOUR_CLIENT_SECRET]" \
-d "code=[CODE]" \
-d "grant_type=authorization_code"
```
5. **Retrieve Your Refresh Token**:
The response from the above command will include your refresh_token.
Store this token securely, as you will use it to authenticate API requests to Strava.
Remember to keep your Client Secret and Refresh Token private to protect your Strava account's security.

### Airbyte CDC Setup Instructions

To enable Change Data Capture (CDC) with Airbyte, follow the steps outlined below:

#### Install Airbyte
1. Download Airbyte version 0.50.44 from the [Airbyte GitHub releases page](https://github.com/airbytehq/airbyte/releases?page=3).
2. Unzip the downloaded file in your desired location.

#### Configure PostgreSQL for CDC
1. Grant the necessary permissions to the `postgres` user to allow for replication:
```sql
ALTER USER postgres REPLICATION;
```
2. Execute a bash shell on your running PostgreSQL container:
```bash   
docker exec -it <container_id> /bin/bash
```
3. Navigate to the PostgreSQL data directory:
```bash
cd /var/lib/postgresql/data
```
4. Append configuration settings for logical replication to the postgresql.conf file:
```bash
echo '# Replication
wal_level = logical
max_wal_senders = 1
max_replication_slots = 1
' >> postgresql.conf
cat postgresql.conf
exit
```
5. Restart docker 
```bash
docker restart <container_id>
```
6. Set up Replication Slots and Publications in PostgreSQL
```bash
SELECT pg_create_logical_replication_slot('airbyte_slot', 'pgoutput');
ALTER TABLE activities REPLICA IDENTITY DEFAULT;
ALTER TABLE athletes REPLICA IDENTITY DEFAULT;
CREATE PUBLICATION airbyte_publication FOR TABLE activities, athletes;
```
By following these steps, you will have set up CDC in Airbyte, enabling you to replicate data changes from your PostgreSQL database to the destination of your choice.

7. Set up airbyte source with your postgres database credentials. Set host to `host.docker.internal`. In advanced options select `Read Changes using Write-Ahead Log (CDC)`, set replication slot to `airbyte_slot` and publication to `airbyte_publication`.
![image](https://github.com/Gklimo/strava/assets/84771383/8c0a108b-112b-4aba-a1d0-d6ec0b9bb599)

8. Set up airbyte destination for snowflake with your snowflake credentials.

9. Create an airbyte connection called `Strava API` from the source and destination you created and run sync.
![image](https://github.com/Gklimo/strava/assets/84771383/c26b0841-546c-462d-a12a-7c9e7966ee18)

### Running the Dagster Project

To run the Dagster project for orchestrating the data pipeline, you will need to set up a dedicated Python environment and install the necessary dependencies. Here's how you can do it:

1. Create a new Conda environment with Python 3.11:
```bash
   conda create -n dagster python=3.11
```
2. Activate the newly created environment:
```bash
conda activate dagster
```
3. Install dagster and project dependencies
```bash
pip install dagster==1.6.8
pip install -e ".[dev]"
```
4. CD into dagster project directory and run orchestration
```
dagster dev
```
![image](https://github.com/Gklimo/strava/assets/84771383/b9fc8925-f64f-4cef-929e-3def5cf54aa4)

5. Turn on deployment schedule to start materializing assets
![image](https://github.com/Gklimo/strava/assets/84771383/4087e219-4bab-460f-9d78-5ffcaa775f0a)

#### Cloud Deployment

Repository deployed to Dagster Cloud: `https://github.com/Gklimo/strava_dagster_cloud`
Its contents are also cloned in dagster_cloud directory in the current repository.

TODO: Host Airbyte and Postgres database on EC2 instances

## NEXT STEPS
Potential future enhancements for the project include scaling up the number of athletes tracked, integrating additional activity types, and developing more sophisticated visualization dashboards to explore new dimensions of the data. And of course deploying all steps in cloud.
