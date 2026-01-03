FROM python:3.13.9-slim

RUN pip install --no-cache uv

WORKDIR /app

COPY pyproject.toml uv.lock requirements.txt ./

RUN uv pip install --system -r requirements.txt

COPY . .

CMD ["python", "src/main.py"]