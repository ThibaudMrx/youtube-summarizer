import logging
import os
import pwd

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s'
)




logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Get the current user's name.
uid = os.getuid()
user_info = pwd.getpwuid(uid)
current_user = user_info.pw_name
logging.info("Current user: %s", current_user)

# Determine the endpoint based on the current user.
if current_user == "thibaud":
    OLLAMA_CLIENT_URL = "http://ollama:11434"
    OLLAMA_MODEL = "mistral"
else:
    OLLAMA_CLIENT_URL = "http://ollama:11434"
    OLLAMA_MODEL = "mistral"

logging.info(f"Using OLLAMA_CLIENT_URL: {OLLAMA_CLIENT_URL} and OLLAMA_MODEL: {OLLAMA_MODEL}")


# Here you might use requests or another HTTP client to interact with the API.
