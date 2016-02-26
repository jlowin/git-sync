FROM python:3-alpine

# install git
RUN apk update \
    && apk add git

# install click
RUN pip install click

# copy script
COPY git-sync.py /git-sync.py
RUN chmod +x /git-sync.py

# run
ENTRYPOINT ["./git-sync.py"]