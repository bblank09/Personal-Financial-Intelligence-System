import os

# Google Cloud Run require dynamic PORT
if __name__ == "__main__":
    from app import create_app
    app = create_app()
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)
