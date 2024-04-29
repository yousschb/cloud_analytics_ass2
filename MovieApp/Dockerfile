
FROM python:3.8-slim

WORKDIR /app

ADD . /app

RUN pip install --trusted-host pypi.python.org -r requirements.txt

EXPOSE 8080

ENV NAME World

CMD ["streamlit", "run", "Movie_selection.py", "--server.port=$PORT", "--server.enableCORS=false"]
