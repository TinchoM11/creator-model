from dotenv import load_dotenv
import chromadb
import os

load_dotenv()

config_list = [{
    'model': os.getenv('GPT_MODEL'),
    'api_key': os.getenv('GPT_API_KEY')
}]

brwoserless_api_key = os.getenv('BROWSERLESS_API_KEY')

serper_api_key = os.getenv('SERPER_API_KEY')

chroma_client = chromadb.HttpClient(host=os.getenv("CHROMADB_HOST"), port=os.getenv("CHROMADB_PORT"))
