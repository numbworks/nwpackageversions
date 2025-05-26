FROM python:3.12.5-bookworm

# MODULE DEPENDENCIES
RUN pip install requests==2.32.3
RUN pip install lxml==5.3.0

# JUPYTER NOTEBOOK
RUN pip install ipykernel==6.29.5 ipython==7.23.1
RUN pip install jupyter==1.1.0

# UNIT TESTING
RUN pip install coverage==7.6.4
RUN pip install parameterized==0.9.0
RUN wget https://github.com/jgm/pandoc/releases/download/3.4/pandoc-3.4-1-amd64.deb \
    && dpkg -i pandoc-3.4-1-amd64.deb \
    && rm -f pandoc-3.4-1-amd64.deb

# MAKEFILE
RUN pip install mypy==1.13.0
RUN pip install types-requests==2.32.0.20241016
RUN pip install lxml-stubs==0.5.1
RUN pip install radon==6.0.1
RUN pip install pylint==3.3.3

# OTHERS
RUN pip install --upgrade pip==25.1.1