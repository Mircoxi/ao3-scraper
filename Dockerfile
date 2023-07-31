FROM python:3.11-bullseye

# Create limited user
RUN groupadd scraper && useradd --create-home --home-dir /home/scraper -g scraper scraper

# Set WORKDIR to /home/user
WORKDIR /home/scraper

COPY requirements.txt /home/scraper
RUN pip3 install -r requirements.txt


ADD . /home/scraper

RUN python3 setup.py install

# Expose
EXPOSE 8000

# Set user
USER scraper

CMD python3 ao3scraper/main.py