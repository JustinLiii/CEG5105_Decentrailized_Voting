NUS CEG5105 Course Project based on https://github.com/Krish-Depani/Decentralized-Voting-System

1. run block chain & deploy contract
```bash
bash chain/run.sh
```

2. run sql
```bash
cd sql
docker-compose up -d
```
3. run backend
   - Configure environement according to `requirements.txt`
   - Then run
```bash
cd backend
python setup.py
python server.py
```
4. run frontend
   - Configure environement according to `package.json`
   - Then run
```bash
cd frontend
bash run.sh
```