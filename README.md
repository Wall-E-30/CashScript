# CashScript 💰

> **Master Your Finances.** The smartest way to track income, visualize expenses, and take full control of your financial future.

![Project Banner](website/static/images/homepage.png) 

## 📖 About The Project

**CashScript** is a full-stack personal finance management application built with **Flask** and **PostgreSQL**. It allows users to track their daily transactions, categorize spending, and visualize their financial health through interactive charts.

Whether you are saving for a goal or just trying to figure out where your salary went, CashScript provides the insights you need in a simple, secure, and responsive interface.

### ✨ Key Features
* **🔐 Secure Authentication:** User registration, login, and secure password reset (powered by Brevo SMTP).
* **📊 Interactive Dashboard:** Dynamic charts (Bar, Line, Doughnut) using **Chart.js** to visualize spending habits.
* **📱 Fully Responsive:** Optimized for both desktop and mobile devices.
* **💸 Transaction Management:** Add, edit, and delete income/expense records with ease.
* **🏷️ Custom Categories:** Users can create personalized categories (e.g., "Food", "Rent", "Freelance").
* **☁️ Cloud Database:** Powered by **Neon (PostgreSQL)** for reliable, persistent data storage.
* **🔍 Advanced Filtering:** Filter transaction history by date ranges (Last 7 Days, Last Month, etc.).

---

## 🛠️ Tech Stack

* **Backend:** Python, Flask, SQLAlchemy
* **Database:** PostgreSQL (Hosted on Neon.tech)
* **Frontend:** HTML5, Bootstrap 5, JavaScript, Chart.js
* **Email Service:** Brevo (formerly Sendinblue) SMTP
* **Deployment:** Render

---

## 🚀 Getting Started

Follow these instructions to set up the project locally on your machine.

### Prerequisites
* Python 3.x installed
* A [Neon.tech](https://neon.tech) account (for the database)
* A [Brevo](https://brevo.com) account (for email features)

### Installation

1.  **Clone the repository**
    ```bash
    git clone [https://github.com/Wall-E-30/CashScript](https://github.com/Wall-E-30/CashScript)
    cd CashScript
    ```

2.  **Create and activate a virtual environment**
    ```bash
    # Windows
    python -m venv venv
    venv\Scripts\activate

    # Mac/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up Environment Variables**
    Create a `.env` file in the root directory and add the following configuration:
    ```env
    SECRET_KEY=your_secret_key_here
    SQLALCHEMY_DATABASE_URI=postgres://user:password@ep-url.region.neon.tech/dbname?sslmode=require
    
    # Email Configuration (Brevo)
    MAIL_SERVER=smtp-relay.brevo.com
    MAIL_PORT=2525
    MAIL_USE_TLS=True
    MAIL_USERNAME=your_brevo_login_email
    MAIL_PASSWORD=your_brevo_smtp_key
    MAIL_DEFAULT_SENDER=your_real_gmail@gmail.com
    ```

5.  **Initialize the Database**
    Run the application once to create the tables automatically (based on `db.create_all()` in the code):
    ```bash
    python run.py
    ```

6.  **Run the App**
    ```bash
    python run.py
    ```
    Visit `http://127.0.0.1:5000` in your browser.

---

## 📸 Screenshots

| Dashboard | Add Transaction |
|:---:|:---:|
| ![Dashboard](website/static/images/dashboard.png) | ![Add Transaction](website/static/images/add_transaction.png) |

---

## 🤝 Contributing

Contributions are welcome! If you have suggestions for improvements or new features:
1.  Fork the Project.
2.  Create your Feature Branch (`git checkout -b feature/NewFeature`).
3.  Commit your Changes (`git commit -m 'Add some NewFeature'`).
4.  Push to the Branch (`git push origin feature/NewFeature`).
5.  Open a Pull Request.

---

## 👤 Author

**Tilak**
* GitHub: [Wall-E-30](https://github.com/Wall-E-30)
* LinkedIn: [Tilak Gaur](https://www.linkedin.com/in/tilak-gaur-bb6204361/)

---

## ⭐️ Show your support

Give a ⭐️ if this project helped you!
