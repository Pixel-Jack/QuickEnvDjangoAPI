FROM alpine:3.8

RUN apk update

# Install python3 and pip3
RUN apk add --no-cache python3 && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --upgrade pip setuptools && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
    if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi

# Install postgresql (doesn't work in requirements)
RUN apk update \
  && apk add --virtual build-deps gcc python3-dev musl-dev \
  && apk add --no-cache postgresql-dev \
  && pip install psycopg2 \
  && apk del build-deps

RUN rm -r /root/.cache

# Install bash
RUN apk add --no-cache bash \
    && apk add --no-cache bash-completion

RUN mkdir -p /home/django/webapp
WORKDIR /home/django/webapp

COPY . .
RUN pip install --index-url=https://pypi.python.org/simple/ -r requirements.pip
