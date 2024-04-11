# Strava Data Pipeline

![image](https://github.com/Gklimo/strava/assets/84771383/b490e090-86a7-42e6-b6c3-a7caeb721196)

Welcome to the Strava Data Engineering Pipeline project - an advanced data pipeline designed to capture, transform, and analyze Strava athletic activity data for detailed performance analytics.

## TABLE OF CONTENTS
- [1. Project Goals](#project-goals)
- [2. Solution Architecture](#solution-architecture)
- [3. Dimensional Model](#dimensional-model)
- [4. Data Pipeline](#data-pipeline)
  - [4.1. Data Extraction](#data-extraction)
  - [4.2. Change Data Capture with Airbyte](#change-data-capture-with-airbyte)
  - [4.3. Data Transformation with dbt](#data-transformation-with-dbt)
  - [4.4. Orchestration with Dagster](#orchestration-with-dagster)
  - [4.5. Data Visualization with Preset](#data-visualization-with-preset)
- [5. Project Setup](#project-setup)
  - [5.1. Strava Refresh Token](#strava-refresh-token)
  - [5.2. Manual Run](#manual-run)
  - [5.3. Cloud Deployment](#cloud-deployment)
    - [5.3.1 AWS and Airbyte](#aws-and-airbyte)
    - [5.3.2 Dagster](#dagster)
- [7. Next Steps](#next-steps)

## PROJECT GOALS
This project aims to provide a comprehensive view of athletes' performance by analyzing Strava activity data. By setting up a sophisticated ELT (Extract, Load, Transform) pipeline, we can track key performance indicators over time, compare activity types, and delve into the data on a per-athlete basis. The geospatial visualization of activities further allows us to uncover patterns and trends related to locations and movements. For the scope of this project we used data from 2 athletes.

## SOLUTION ARCHITECTURE
This data pipeline architecture extracts data from the Strava API, staging it in a PostgreSQL instance hosted on AWS RDS. Data synchronization to Snowflake is handled by Airbyte, running on an EC2 instance, employing change data capture for efficient data transfer. Transformations are orchestrated through DBT, with the entire pipeline seamlessly deployed and managed on Dagster Cloud. Visual insights are rendered via Preset to deliver actionable intelligence. Within Snowflake, data is organized across three schemas: 'strava', where Airbyte loads the data; 'raw', containing DBT models with raw data; and 'dwh', which also comprises DBT models designed for analytics and reporting, serving as the reporting warehouse to support insights and decision-making processes. The Strava API source available on Airbyte was not utilized for two key reasons. Firstly, as a community-contributed connector, it lacks the security assurances that come with official, certified connectors. Secondly, this particular source does not support Change Data Capture (CDC), a crucial feature for our real-time data synchronization needs. Consequently, these factors led to the decision against its implementation in our data pipeline.

![image](https://github.com/Gklimo/strava/assets/84771383/e596398b-f7c2-4a61-8a90-c5aabe9f3669)

![image](https://github.com/Gklimo/strava/assets/84771383/80cad6e7-087b-47da-adb5-6223744ec021)

## DIMENSIONAL MODEL
Our data warehouse is designed with a star schema in mind, optimizing for query performance and simplicity. The dimensions provide context for the activities, such as when (dim_date), where (dim_location), and by whom (dim_athlete) they were performed. The fact tables (fact_activity, fact_monthly_activities_snapshot) record the metrics and measures related to the activities themselves.

![image](https://github.com/Gklimo/strava/assets/84771383/853a8c43-75ab-40e6-b4ab-a1ed137d77ce)

## DATA PIPELINE

### Data Extraction
The project uses the Strava API to source data on athletic activities and athlete profiles. Utilizing access tokens, it performs incremental extraction based on the latest between `last_activity_date` from athletes table and dagster partition date, ensuring that each data pull is efficient and up-to-date.

### Change Data Capture with Airbyte
We utilize Airbyte's Change Data Capture (CDC) capabilities to monitor and record changes in our PostgreSQL database. This data is then streamed into our Snowflake data warehouse, allowing for real-time data updates and minimizing the load on our source database.

### Data Transformation with dbt
In Snowflake, dbt (data build tool) manages the transformation of our raw data into a refined format ready for analysis. It creates staging, dimensional, and fact tables, implementing business logic and ensuring data quality. Our slowly changing dimension for athlete data captures changes over time, preserving historical context.

![image](https://github.com/Gklimo/strava/assets/84771383/08aa557e-dfe2-4d0b-b19e-2d4fb546ae26)

![image](https://github.com/Gklimo/strava/assets/84771383/4b1d9313-2ec9-470b-99e5-006b6fd778cf)

#### Slowly Changing Dimension
The `dim_athlete` table is an example of a slowly changing dimension, which tracks the history of changes to an athlete's profile, providing insights into their development over time.

#### Aggregate Fact Table
Our `fact_monthly_activities_snapshot` table provides a monthly roll-up of activity data, which is critical for trend analysis and monthly performance tracking.

#### BI Analysis Materialized View
The `bi_analysis` materialized view is specifically structured to support the Preset dashboard visualizations, enabling easy access to pre-calculated metrics for reporting.

### Orchestration with Dagster
Dagster orchestrates the entire pipeline, managing dependencies, scheduling jobs, and ensuring data freshness. It utilizes partitions to enhance performance, making data processing more efficient. Dagster orchestrates Strava API asset to refresh data in Postgres database, airbyte asset to ingest into Snoflake, and dbt asset for transormations. Dagster has freshness and automaterialization policies set up.

![image](https://github.com/Gklimo/strava/assets/84771383/6154e32c-9af9-4e0b-b26c-61138413c339)

![image](https://github.com/Gklimo/strava/assets/84771383/70e183ef-ab11-45f0-b961-cd80b798710f)

![image](https://github.com/Gklimo/strava/assets/84771383/b786ae44-391a-47c1-89a4-903891b6f65b)

### CI/CD Integration
To ensure high-quality code and seamless integration of new features, this project incorporates Continuous Integration (CI) and Continuous Deployment (CD) practices facilitated by GitHub Actions and Dagster Cloud.

![image](https://github.com/Gklimo/strava/assets/84771383/83a54bde-4fa8-403f-a689-9e81a00dfa94)

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

### Data Visualization with Preset
Preset is the final piece of our pipeline, turning our rich datasets into actionable insights through interactive dashboards. It provides a user-friendly interface to explore the data, with the ability to drill down into specific areas of interest. You can make use of filters to accomodate for the business needs.

![image](https://github.com/Gklimo/strava/assets/84771383/a1a041dd-2ec2-42ed-82d9-61bad11d37ca)

![image](https://github.com/Gklimo/strava/assets/84771383/5ef8cbce-d5db-435f-b309-c226a1431f6c)

## PROJECT SETUP
This section will detail the necessary steps to get the pipeline up and running, including setting up the local and cloud development environments, deploying the Airbyte connectors, and configuring the dbt models in Snowflake.
Create .env file with your tokens and database credentials based on .template_env file provided.

### Strava Refresh Token

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

### Manual run
You can manually ingest data from strava api into your database.
```bash
python extract_strava/extract_strava.py
```
You can run initial integration tests
```bash
pytest extract_strava_tests/
```
### Cloud Deployment

### AWS and Airbyte

#### RDS & EC2 
Create Postgres 13 database in RDS. Select 'Manage master credentials in AWS secrets manager', the postgres user password will be available under 'Retrieve Credentials' in Secrets Manager service. This will allow for secure password storage. Set inbound rules for the security group: `SSH` type (port 22) with source `My IP` (only allows SSH connections from your IP address), `PostgreSQL` type (port 5432), and `Custom TCP` for Airbyte (port 8000).

![image](https://github.com/Gklimo/strava/assets/84771383/534af43e-af10-4684-a419-6b323815b4a3)

#### Hosting Airbyte
Launch an EC2 instance.
Turn off any VPN.
To have a fixed IP address:
Elastic IPs under the "Network and Security section" (left panel in EC2)
Click on "Allocate Elasitc IP address"
Amazon's pool of IPv4 addresses
Allocate
Select the new IP address > Associate Elastic IP address
Instance
Instance: <select_your_instance>
Associate

Connect to the instance using SSH.

Run the script bellow:
```bash
#!/bin/bash 

# Install Docker
# Reference: https://docs.airbyte.com/deploying-airbyte/on-aws-ec2
sudo yum update -y;
sudo yum install -y docker;

# Start the docker service
sudo service docker start;

# Add the current user to the docker group
sudo usermod -a -G docker $USER;

# Manually install docker compose
# Reference: https://docs.docker.com/compose/install/linux/#install-the-plugin-manually
DOCKER_CONFIG=${DOCKER_CONFIG:-$HOME/.docker};
mkdir -p $DOCKER_CONFIG/cli-plugins;
curl -SL https://github.com/docker/compose/releases/download/v2.24.2/docker-compose-linux-x86_64 -o $DOCKER_CONFIG/cli-plugins/docker-compose;
chmod +x $DOCKER_CONFIG/cli-plugins/docker-compose;
docker compose version;

# logout of the instance
exit
```
Log in again
```bash
# Download and run airbyte
mkdir airbyte && cd airbyte;
wget https://raw.githubusercontent.com/airbytehq/airbyte/master/run-ab-platform.sh;
chmod +x run-ab-platform.sh;
./run-ab-platform.sh -b;
```
In the terminal of your local machine run:
`ssh -i strava-ec2.pem -L 8000:localhost:8000 -N -f ec2-user@<your_elastic_ip_address>`

In web browser you can set up Airbyte connection at `localhost:8000`

#### Airbyte CDC Setup Instructions

To enable Change Data Capture (CDC) with Airbyte, follow the steps outlined below:
Create a New Parameter Group:

Create a New Parameter Group:

In the RDS Dashboard, go to the "Parameter groups" section.
Click "Create parameter group".
For "Parameter group family", select the family that corresponds to your PostgreSQL version (e.g., postgres13 for PostgreSQL 13).
Give it a name that reflects its use case (e.g., cdc-enabled-pg13 for a PostgreSQL 13 family with CDC enabled).
Provide a description for clarity (e.g., "Parameter group for enabling CDC on PostgreSQL 13").
Click "Create".

Once the parameter group is created, select it and click on "Parameters".
Search for and modify the following parameters:
rds.logical_replication: set its value to 1 to enable.
max_wal_senders: set to a number sufficient for your setup, typically 1 or more.
max_replication_slots: set to match the number of max_wal_senders or as required for your setup.

Open the RDS Console:

Go to the Amazon RDS console at https://console.aws.amazon.com/rds/.
Navigate to Databases:

On the navigation pane, click "Databases" to display a list of your DB instances.
Select Your Database Instance:

Click the checkbox next to the DB instance you want to modify to open it.
Modify the Instance:

With the DB instance selected, click "Modify".
Change the Parameter Group:

Scroll down to the "Database options" section.
Select the new parameter group you created from the "DB parameter group" drop-down menu. Save changes, apply immediately, and reboot RDS instance.

Configure PostgreSQL for CDC
1. Grant the necessary permissions to the `airbyte_cdc_user` user to allow for replication:
```sql
CREATE USER airbyte_cdc_user WITH LOGIN PASSWORD '<your_password>';
GRANT rds_replication TO airbyte_cdc_user;
```
2. Set up Replication Slots and Publications in PostgreSQL
```bash
SELECT pg_create_logical_replication_slot('airbyte_slot', 'pgoutput');
ALTER TABLE activities REPLICA IDENTITY DEFAULT;
ALTER TABLE athletes REPLICA IDENTITY DEFAULT;
CREATE PUBLICATION airbyte_publication FOR TABLE activities, athletes;
```
By following these steps, you will have set up CDC in Airbyte, enabling you to replicate data changes from your PostgreSQL database to the destination of your choice.

Set up airbyte source with your postgres database credentials. For local deployment set host to `host.docker.internal` and for RDS use the endpoint as the host and password from secrets manager. In advanced options select `Read Changes using Write-Ahead Log (CDC)`, set replication slot to `airbyte_slot` and publication to `airbyte_publication`.
 
![image](https://github.com/Gklimo/strava/assets/84771383/8c0a108b-112b-4aba-a1d0-d6ec0b9bb599)

Set up airbyte destination for snowflake with your snowflake credentials.

Create an airbyte connection called `RDS Postgres → Snowflake` from the source and destination you created and run sync.

![image](https://github.com/Gklimo/strava/assets/84771383/4ae7d1fa-5f83-4bb7-b93e-81498cf90c21)

### Dagster

1. To run the pipeline, you will need to set up a dagster cloud account, connect github repository, define all environmental variables.
   
![image](https://github.com/Gklimo/strava/assets/84771383/0ffe3ba6-20c4-4956-9081-385802737418)

2. Backfill data for all time

![image](https://github.com/Gklimo/strava/assets/84771383/ea2363b0-ac10-41cc-a2e8-e194dcf0ce60)

![image](https://github.com/Gklimo/strava/assets/84771383/96fc348a-c5e8-44d7-8416-a1fe754b1e60)

3. Turn on automaterialization

![image](https://github.com/Gklimo/strava/assets/84771383/5a59844f-f7c7-4977-a988-d27b43d9ef3d)

4. Unit tests available
```bash
pytest analytics_tests
```

## NEXT STEPS
Potential future enhancements for the project include scaling up the number of athletes tracked, integrating additional activity types, and developing more sophisticated visualization dashboards to explore new dimensions of the data. 

- TODO: Adding more tests in CI/CD eg. analytics_tests/ and dbt/strava/tests/
- TODO: Having more restrictive security group inbound rules for dagster and airbyte
- TODO: Setting up QA environment to avoid pushing new code to PROD without proper testing
- TODO: Creating `release` branch which will be used to push new code to production, using `main` branch only for QA
