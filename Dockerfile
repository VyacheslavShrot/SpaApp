FROM python:3.11

RUN apt update
RUN mkdir /spa

WORKDIR /spa

COPY ./src ./src
COPY ./requirements.txt ./requirements.txt
COPY src/commands ./commands

RUN python -m pip install --upgrade pip
RUN pip install -r ./requirements.txt

CMD ["bash"]