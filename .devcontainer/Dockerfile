FROM python:3.12.5-bookworm

RUN pip install requests==2.31.0
RUN pip install ipykernel==6.29.5
RUN pip install jupyter==1.0.0
RUN pip install coverage==7.6.1
RUN pip install parameterized==0.9.0

RUN wget https://github.com/jgm/pandoc/releases/download/3.4/pandoc-3.4-1-amd64.deb \
    && dpkg -i pandoc-3.4-1-amd64.deb \
    && rm -f pandoc-3.4-1-amd64.deb