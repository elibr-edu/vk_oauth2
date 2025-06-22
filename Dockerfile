FROM python:3.10.18-bookworm

WORKDIR /app

RUN pip install --upgrade pip wheel "poetry==1.6.1"

RUN poetry config virtualenvs.create false  

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-root --no-interaction --no-ansi

COPY . .

ENV PYTHONPATH=/app/fastapi-application
CMD ["uvicorn", "fastapi-application.main:main_app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
