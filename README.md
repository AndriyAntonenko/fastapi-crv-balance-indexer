### Instructions to run

1. Create .env file in the root with the next content

   ```
   CRV_DAO_TOKEN_ADDRESS=0xD533a949740bb3306d119CC777fa900bA034cd52
   ETHEREUM_RPC_URL=<PROVIDE_YOUR_RPC_URL>
   MONGO_URL=mongodb://mongo:27017
   ```

2. Run docker compose:

   ```
   docker compose up
   ```

3. Test application

   ```zsh
   # get current balance and store it to db
   curl -X 'GET' 'http://localhost:8000/balance/0x7a16ff8270133f063aab6c9977183d9e72835428' \
   -H 'accept: application/json'

   # get history
   curl -X 'GET' 'http://localhost:8000/history/0x7a16ff8270133f063aab6c9977183d9e72835428' \
   -H 'accept: application/json'
   ```
