import os


class Config:
    STATIC_FOLDER = 'static'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clavesecreta'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'postgresql://postgres:123@localhost/postgres'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')
    LANGSMITH_API_KEY = os.getenv('LANGSMITH_API_KEY')

    LANGCHAIN_TRACING_V2 = os.getenv('LANGCHAIN_TRACING_V2')

    LLM_MODEL = 'gpt-3.5-turbo'
    REPO_BASE_FOLDER = os.path.join("static", "data")

    AUTH0_DOMAIN = 'dev-martinlkspracticasoauth.eu.auth0.com'
    API_IDENTIFIER = 'https://secure-python-flask-api'
    ALGORITHMS = ["RS256"]

