FROM python:3.11

WORKDIR /app

COPY requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt

COPY . /app


EXPOSE 8501


ENV PORT 8080


CMD ["streamlit", "run", "--server.port", "8080", "Movie_selection.py"]
