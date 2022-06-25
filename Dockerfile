FROM python:3.10.4

COPY . .

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update
RUN apt-get install -y ghostscript
RUN apt-get install ffmpeg libsm6 libxext6  -y

# gunicorn
ENTRYPOINT ["python3"]
# CMD ["gunicorn", "--config", "gunicorn-cfg.py", "run:app"]
CMD ["run.py"]
