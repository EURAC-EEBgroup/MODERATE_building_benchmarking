1. Create db.env file from "db copy.env"

2. For create database, run: 
```
    docker-compose up -d --build
```

3. add some records to db:
start FastAPI app; authenticate; post /api/v1/measurements, use file ../data/data.csv.