from app import create_app
import os

if __name__ == "__main__":
    # Define a porta na qual o Flask irá escutar
    port = int(os.environ.get('PORT', 5433))
    app = create_app()
    app.run(host='0.0.0.0', port=port)
