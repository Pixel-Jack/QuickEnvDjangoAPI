FROM alpine:3.8

RUN apk update \
    # Install python3 and pip3, GNU gettext for internationalisation, postgresql (doesn't work in requirements)
    && apk add --no-cache python3 gettext postgresql-dev \
    # Python3 install
    && python3 -m ensurepip \
    && rm -r /usr/lib/python*/ensurepip \
    && pip3 install --upgrade pip setuptools \
    && if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi \
    && if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi \
    # Psycog2 For postgre
    && apk add --virtual build-deps gcc python3-dev musl-dev \
    && pip install psycopg2 \
    # Clean
    && apk del build-deps \
    && rm -r /root/.cache

WORKDIR /home/django

COPY . .

RUN pip install --index-url=https://pypi.python.org/simple/ -r requirements.pip
