from dotenv import load_dotenv
import os
import pickle

load_dotenv()

# Load environment variables
OPENAI_API_KEY = os.getenv("OAI_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

# Load in ML Models
mentalHealthModel =  pickle.load(open("model_data/mental_model-n.sav", 'rb'))
