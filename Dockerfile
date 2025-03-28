FROM python:3.11-slim

WORKDIR /weirdcalc

RUN pip install --no-cache-dir flask

COPY . .

CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
