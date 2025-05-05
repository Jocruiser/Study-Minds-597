# Flashcard_generator
Setting up environment
WINDOWS ---
Open Powershell > Run as admin
Set-ExecutionPolicy -ExecutionPolicy Unrestricted -Scope CurrentUser

1. Delete the old venv/ folder from the project
 - In VS Code or File Explorer → right-click venv/ → Delete.
2. Create a new virtual environment locally in your project folder:
   python -m .venv venv
 - This creates a new clean venv/ folder that matches your system.
3. Activate environment in powershell - Do all of this in VENV always
In Powershell: .venv\Scripts\Activate
4. Install dependencies from requirements.txt
   pip install -r requirements.txt

Setting an API key on OpenRouter 
1. Create an account with OpenRouter
2. Go to profile > Keys > API Keys > Create Key > Name it and create > copy and store the key in a .env file in VS code for security purposes

In VS Code:
Run (In Terminal)
python app.py 


