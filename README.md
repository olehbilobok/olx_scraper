
# Scraper

This scraper is intended to parse data from the web site and store to Postgres DB.  




## Features

- The app launches every minute
- Parse the first 5 pages and store to db without duplications
- The app makes DB dump every day at 12:00 pm
- The app is provided with a logging 
- The app is dockerized








## Run Locally
Clone the project
```bash
git clone https://github.com/olehbilobok/olx_scraper.git
```
Run command to build image
```bash
docker-compose build
```
Run command to up the containers 
```bash
docker-compose up
```





    