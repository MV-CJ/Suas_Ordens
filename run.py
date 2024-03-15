from app import create_app
import os

if __name__ == "__main__":
    # Define a porta na qual o Flask irá escutar
    port = int(os.environ.get('PORT', 5000))
    # Cria o aplicativo Flask
    app = create_app()
    # Inicia o aplicativo Flask
    app.run(host='0.0.0.0', port=port)
