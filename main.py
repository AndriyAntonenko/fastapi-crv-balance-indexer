from fastapi import FastAPI
from datetime import datetime
from pymongo import MongoClient
from web3 import Web3
import requests
import os
from decimal import Decimal

#############################################
# Initialize environment                    #
#############################################

MONGO_URL = os.getenv("MONGO_URL")
if MONGO_URL == None:
    raise Exception("MONGO_URL environment variable not set")

ETHEREUM_RPC_URL = os.getenv("ETHEREUM_RPC_URL")
if ETHEREUM_RPC_URL == None:
    raise Exception("ETHEREUM_RPC_URL environment variable not set")

CRV_DAO_TOKEN_ADDRESS = os.getenv("CRV_DAO_TOKEN_ADDRESS")
if CRV_DAO_TOKEN_ADDRESS == None:
    raise Exception("CRV_DAO_TOKEN_ADDRESS environment variable not set")

#############################################
# Setup mongo DB                            #
#############################################

client = MongoClient(MONGO_URL)
db = client["balances"]
balances_collection = db["wallet_balances"]

#############################################
# Setup web3 instance and CRV Dao contract  #
#############################################

web3 = Web3(Web3.HTTPProvider(ETHEREUM_RPC_URL))

contract_address = Web3.to_checksum_address(CRV_DAO_TOKEN_ADDRESS)
contract_abi = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    }
]

contract = web3.eth.contract(address=contract_address, abi=contract_abi)

#############################################################################
# Helper function which fetch CRV DAO token price in USD from CoinGecko API #
#############################################################################


def get_token_to_usd_price():
    token_symbol = "curve-dao-token"  # Replace with the correct token symbol
    base_url = "https://api.coingecko.com/api/v3"

    # Fetch token price data from CoinGecko
    response = requests.get(f"{base_url}/simple/price", params={"ids": token_symbol, "vs_currencies": "usd"})
    if response.status_code == 200:
        price_data = response.json()
        token_price_usd = price_data[token_symbol]["usd"]
        return token_price_usd
    else:
        # Handle error case
        return None

#############################################
# The API functions                         #
#############################################

app = FastAPI()

@app.get("/balance/{wallet}")
async def get_balance(wallet: str):
    wallet = wallet.lower()
    checksum_wallet = Web3.to_checksum_address(wallet)
    token_balance_dec = contract.functions.balanceOf(checksum_wallet).call()

    price = get_token_to_usd_price()
    if price == None:
        return {"error": "Could not fetch token price"}
    
    token_balance = Web3.from_wei(token_balance_dec, "ether")
    usd_balance = float(token_balance) * price  # You need to implement this function
    timestamp = datetime.now().isoformat()

    print(token_balance, usd_balance, timestamp)
    data = {
        "wallet": wallet,
        "last_update_time": timestamp,
        "price": str(price),
        "balance": str(token_balance),
        "balance_dec": str(token_balance_dec),
        "balance_usd": str(usd_balance)
    }
    balances_collection.insert_one(data)
    del data["_id"]
    return data

@app.get("/history/{wallet}")
async def get_history(wallet: str):
    wallet = wallet.lower()
    history = list(balances_collection.find({"wallet": wallet}))
    
    mapped_history = map(
        lambda x: {
            "wallet": x["wallet"],
            "last_update_time": x["last_update_time"], 
            "price": x["price"],
            "balance": x["balance"],
            "balance_dec": x["balance_dec"],
            "balance_usd": x["balance_usd"]
        },
        history
    )
    
    return list(mapped_history)
