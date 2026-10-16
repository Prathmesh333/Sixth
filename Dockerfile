FROM node:22-alpine AS frontend
WORKDIR /build
COPY package.json package-lock.json ./
COPY apps/web/package.json apps/web/package.json
RUN npm ci
COPY apps/web apps/web
COPY design design
RUN npm run build

FROM python:3.12-slim
WORKDIR /app
COPY requirements.lock ./
RUN pip install --no-cache-dir --require-hashes -r requirements.lock
COPY apps/api apps/api
COPY --from=frontend /build/apps/web/dist apps/web/dist
ENV PYTHONPATH=/app/apps/api SIXTH_DATA_DIR=/app/data
RUN useradd --create-home sixth && mkdir /app/data && chown sixth:sixth /app/data
USER sixth
EXPOSE 8000
CMD ["uvicorn", "sixth.main:app", "--host", "0.0.0.0", "--port", "8000"]
