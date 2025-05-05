from apps import create_app, db

# creates the flask app instance
app = create_app()

# Use the app context so db.create_all() works
with app.app_context():
    db.create_all()
    print("✅ Database tables created successfully!")

# only need to run once to create tables