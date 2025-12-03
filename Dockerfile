FROM apache/airflow:2.8.3-python3.11

# No additional system dependencies are required; the project uses only Airflow and the Python standard library.
# The repository content (dags, scripts, data) is mounted at runtime via docker-compose volumes.
USER root

# Switch back to the airflow user provided by the base image
USER ${AIRFLOW_UID:-50000}
