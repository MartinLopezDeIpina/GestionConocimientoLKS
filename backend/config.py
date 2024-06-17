import os


class Config:
    STATIC_FOLDER = 'static'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clavesecreta'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'postgresql://postgres:123@localhost/postgres'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    LLM_MODEL = 'gpt-3.5-turbo'
    REPO_BASE_FOLDER = os.path.join("static", "data")
