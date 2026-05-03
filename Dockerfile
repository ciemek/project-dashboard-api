FROM tiangolo/meinheld-gunicorn-flask:latest

# Copy requirements and install
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy app code
COPY ./app /app/app
