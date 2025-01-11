FROM python:3.9-slim

# Install MLflow and any other needed packages
RUN pip install mlflow boto3 psycopg2-binary

# Copy start script
COPY start_mlflow.sh /start_mlflow.sh
RUN chmod +x /start_mlflow.sh

# Expose the MLflow default port
EXPOSE 5000

CMD ["/start_mlflow.sh"]