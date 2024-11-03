FROM python:3.12.5-bookworm

RUN pip install requests==2.32.3
RUN pip install lxml==5.3.0

RUN pip install coverage==7.6.4
RUN pip install parameterized==0.9.0

RUN pip install ipykernel==6.29.5
RUN pip install jupyter==1.1.1

RUN wget https://github.com/jgm/pandoc/releases/download/3.4/pandoc-3.4-1-amd64.deb \
    && dpkg -i pandoc-3.4-1-amd64.deb \
    && rm -f pandoc-3.4-1-amd64.deb