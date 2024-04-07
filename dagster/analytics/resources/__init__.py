from dagster import ConfigurableResource

class PostgresqlDatabaseResource(ConfigurableResource):
    postgres_host: str
    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_port: str