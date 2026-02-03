from website import create_app

app = create_app()

if __name__ == "__main__":
    # with app.app_context():
    #     from website.models import User, Category, Transaction
    #     db.create_all()

    app.run(debug=True)