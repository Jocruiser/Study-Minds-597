# apps/routes.py

from fileinput import filename
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json

from .models import Deck, User, Flashcard
from .db import db

auth = Blueprint('auth', __name__)

# External helper functions (assumed to be defined elsewhere)
from .app import extract_text_from_pdf, extract_text_from_pptx, generate_flashcards_from_api, save_flashcards_as_csv, save_flashcards_as_json

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'


@auth.route("/")
def index():
    return render_template("dashboard.html")

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        #email = request.form['email']
        password = request.form['password']
        hashed_pw = generate_password_hash(password)

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists.")
            return redirect(url_for('auth.login'))

        new_user = User(username=username, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful. Please log in.")
        return redirect(url_for('auth.login'))

    return render_template('register.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Logged in successfully.")
            return redirect(url_for('auth.dashboard'))
        flash("Invalid credentials.")
    return render_template('login.html')


@auth.route('/dashboard')
@login_required
def dashboard():
    decks = Deck.query.filter_by(user_id=current_user.id).all()
    for deck in decks:
        deck.flashcards = deck.flashcards  # This ensures flashcards are available in the template
    return render_template("dashboard.html", decks=decks)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.")
    return redirect(url_for('auth.login'))


@auth.route('/flashcards')
@login_required
def flashcards():
    cards = Flashcard.query.filter_by(user_id=current_user.id).all()
    return render_template('flashcards.html', flashcards=cards)


@auth.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    
    try:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        # Extract text
        if file.filename.endswith(".pdf"):
            text_content = extract_text_from_pdf(file_path)
        elif file.filename.endswith((".ppt", ".pptx")):
            text_content = extract_text_from_pptx(file_path)
        else:
            return jsonify({"error": "Unsupported file type"}), 400

        # Generate flashcards
        flashcards = generate_flashcards_from_api(text_content)

        # Save
        csv_path = os.path.join(OUTPUT_FOLDER, "flashcards.csv")
        json_path = os.path.join(OUTPUT_FOLDER, "flashcards.json")
        save_flashcards_as_csv(flashcards, csv_path)
        save_flashcards_as_json(flashcards, json_path)

        return jsonify({
            "csvUrl": "/download/csv",
            "jsonUrl": "/download/json",
            "flashcards": flashcards
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@auth.route("/upload_json", methods=["POST"])
def upload_json_file():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files["file"]
    if file.filename == "" or not file.filename.endswith(".json"):
        return jsonify({"error": "Please upload a valid JSON file"}), 400

    try:
        data = json.load(file)
        if not isinstance(data, list):
            return jsonify({"error": "Invalid JSON format"}), 400

        # Create a new deck for this user
        new_deck = Deck(name=filename, user_id=current_user.id)
        db.session.add(new_deck)
        db.session.flush()  # get deck.id before committing

        # Add flashcards to this deck
        for item in data:
            question = item.get("question", "")
            answer = item.get("answer", "")
            flashcard = Flashcard(question=question, answer=answer, deck=new_deck)
            db.session.add(flashcard)

        db.session.commit()
        return jsonify({"message": "Deck uploaded successfully!"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@auth.route("/download/<filetype>", methods=["GET"])
def download_file(filetype):
    from flask import send_file  # imported only where used
    if filetype == "csv":
        return send_file(os.path.join(OUTPUT_FOLDER, "flashcards.csv"), as_attachment=True)
    elif filetype == "json":
        return send_file(os.path.join(OUTPUT_FOLDER, "flashcards.json"), as_attachment=True)
    else:
        return jsonify({"error": "Invalid file type"}), 400


@auth.route('/upload_deck', methods=['POST'])
@login_required
def upload_deck():
    # Check if the form data exists
    deck_name = request.form.get('deck_name')
    file = request.files.get('file')

    # If no deck name or file provided, show an error
    if not deck_name or not file:
        flash('Please provide both deck name and file.', 'danger')
        return redirect(url_for('dashboard'))

    # Process the uploaded file (JSON)
    try:
        deck_data = json.load(file)
        print(deck_data)  # Debug: Check what data you are receiving
    except Exception as e:
        flash(f'Error reading JSON file: {e}', 'danger')
        return redirect(url_for('dashboard'))

    # Create a new deck instance
    deck = Deck(name=deck_name, user_id=current_user.id)
    db.session.add(deck)
    db.session.commit()  # Commit to get the deck's id

    # Loop through the flashcards from the JSON file and save them to the DB
    for card_data in deck_data:
        flashcard = Flashcard(
            question=card_data['question'],
            answer=card_data['answer'],
            deck_id=deck.id
        )
        db.session.add(flashcard)

    db.session.commit()  # Commit the flashcards to the DB

    flash('Deck uploaded and saved successfully!', 'success')
    return redirect(url_for('dashboard'))
