FROM python:3

WORKDIR /usr/src/app

COPY log_analysis.py .
RUN chmod +x log_analysis.py

RUN pip install Flask

COPY . .

ENTRYPOINT [ "python", "./log_analysis.py"]
