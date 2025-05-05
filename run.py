# run.py
from apps import create_app

app = create_app()  # Create the Flask app instance using the factory function

if __name__ == "__main__":
    app.run(debug=True)
