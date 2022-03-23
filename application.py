import os

from flask import Flask, session, flash, redirect, render_template, request, session, url_for, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from dotenv import load_dotenv

app = Flask(__name__)

# Check for environment variable
##if not os.getenv("DATABASE_URL"):
  #  raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return render_template("inicio.html")

@app.route("/register")
def register():
  return render_template("register.html")

@app.route()