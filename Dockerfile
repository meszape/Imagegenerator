FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir .
ENV DATABASE_URL=sqlite:////app/data/image_service.db ASSET_ROOT=/app/data/assets
RUN mkdir -p /app/data/assets
EXPOSE 8000
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000"]
