from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date, timedelta
# from flask_moment import Moment
from models import db, User, Transaction, Category
from sqlalchemy.exc import IntegrityError
from collections import defaultdict
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer

app = Flask(__name__)   #create app instance
# moment = Moment(app)    #Bind Flask-Moment to the app
app.config['SECRET_KEY'] = 'mysecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'tilakjaipalgaur31@gmail.com'
app.config['MAIL_PASSWORD'] = 'avgg wpas cevz odsm'

db.init_app(app)
mail = Mail(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

s = URLSafeTimedSerializer(app.config['SECRET_KEY'])

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/register', methods = ['GET', 'POST'])
def register():

    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        try:
            username = request.form['username']
            password = generate_password_hash(request.form['password'])
            email = request.form['email']

            user_exists = User.query.filter((User.username == username) | (User.email == email)).first()
            if user_exists:
                flash('Username or Email already exists!', 'error')
                return redirect(url_for('register'))
            
            hashed_pw = generate_password_hash(password)
            new_user = User(username = username, password_hash = password, email = email)
            db.session.add(new_user)
            db.session.commit()

            flash('You are registered successfully!!', 'success')
            return redirect(url_for('login'))
            
        except IntegrityError:
            db.session.rollback() # Undo the change
            flash('Username already taken.', 'error')
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'error')
            
    return render_template('register.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form['email']
        
        # Find user by email now
        user = User.query.filter_by(email=email).first()

        if user:
            # Generate token using the email
            token = s.dumps(email, salt='email-confirm')
            
            msg = Message('Password Reset Request', sender='noreply@demo.com', recipients=[email])
            link = url_for('reset_password', token=token, _external=True)
            msg.body = f'Click here to reset your password: {link}'
            
            try:
                mail.send(msg)
                flash('Email sent!', 'success')
            except Exception as e:
                flash(f'Error sending email: {str(e)}', 'error')
        else:
            flash('Email sent!', 'success') # Security: don't reveal if email exists
            
        return redirect(url_for('login'))
        
    return render_template('forgot_password.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    try:
        # Decode token to get email back
        email = s.loads(token, salt='email-confirm', max_age=3600)
    except:
        flash('The reset link is invalid or has expired.', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        password = request.form['password']
        hashed_pw = generate_password_hash(password)
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        # Update the password
        user.password_hash = hashed_pw 
        db.session.commit()
        
        flash('Your password has been updated! You can now login.', 'success')
        return redirect(url_for('login'))

    return render_template('reset_password.html')

@app.route('/login', methods = ['GET' , 'POST'])
def login():
    
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        user = User.query.filter_by(username = request.form['username']).first()

        if user and check_password_hash(user.password_hash, request.form['password']):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials','error')
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    # transactions = Transaction.query.filter_by(user_id = current_user.id).order_by(Transaction.date.asc()).all()
    all_transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.date.asc()).all()
    total_income = sum(t.amount for t in all_transactions if t.type == 'Income')
    total_expense = sum(t.amount for t in all_transactions if t.type == 'Expense')
    balance = total_income - total_expense
    
    expense_cat_totals = {}
    income_cat_totals = {}

    #Chart data
    for t in all_transactions:
        cat_name = t.category.name if t.category else 'Uncategorized'
        
        if t.type == 'Expense':
            expense_cat_totals[cat_name] = expense_cat_totals.get(cat_name, 0) + t.amount
        elif t.type == 'Income':
            income_cat_totals[cat_name] = income_cat_totals.get(cat_name, 0) + t.amount

    daily_data = defaultdict(lambda: {'income': 0, 'expense': 0})   #imported
    
    for t in all_transactions:
        date_str = t.date.strftime('%Y-%m-%d')
        if t.type == 'Income':
            daily_data[date_str]['income'] += t.amount
        else:
            daily_data[date_str]['expense'] += t.amount

    dates_list = sorted(daily_data.keys())
    income_list = [daily_data[d]['income'] for d in dates_list]
    expense_list = [daily_data[d]['expense'] for d in dates_list]
    # suggestions = []
    # if category_totals:
    #     max_categories = max(category_totals, key = category_totals.get)
    #     max_amt = category_totals[max_categories]

    #     if max_amt > 2000:
    #         suggestions.append(f"You spent ₹{max_amt} on {max_categories}. Consider reducing")
    #     else:
    #         suggestions.append("You are spending wisely.")
    page = request.args.get('page', 1, type=int)
    per_page = 7 # Adjust this number to change rows per page
    
    pagination = Transaction.query.filter_by(user_id=current_user.id)\
        .order_by(Transaction.date.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
        
    transactions_for_table = pagination.items
    has_categories = Category.query.filter_by(user_id=current_user.id).first() is not None
    return render_template(
        'dashboard.html', 
        username = current_user.username,
        total_income = total_income,
        total_expense = total_expense,
        balance = balance,
        transactions = transactions_for_table,
        pagination = pagination,
        
        exp_cat_labels = list(expense_cat_totals.keys()),
        exp_cat_values = list(expense_cat_totals.values()),
        
        inc_cat_labels = list(income_cat_totals.keys()),
        inc_cat_values = list(income_cat_totals.values()),

        
        date_labels = dates_list,
        date_income = income_list,
        date_expense = expense_list,
        has_categories = has_categories
        #suggestions = suggestions
    )

@app.route('/add', methods = ['GET', 'POST'])
@login_required
def add_transaction():
    categories = Category.query.all()
    today_str = date.today().strftime('%Y-%m-%d')
    if not categories:
        flash('You must create a category (like "Food" or "Salary") first!', 'info')
        return redirect(url_for('add_category'))
    if request.method == 'POST':
        try:
            title = request.form['title']
            amount = float(request.form['amount'])
            date_obj = datetime.strptime(request.form['date'], '%Y-%m-%d')

            if date_obj.date() > date.today() + timedelta(days=1):
                flash('You cannot select a future date!', 'error')
                return render_template('add_transaction.html', categories=categories, today=today_str)

            category_id = request.form.get('category_id')
            payment_mode = request.form['payment_mode']
            tran_type = request.form['type']

            selected_category = Category.query.filter_by(user_id=current_user.id).all()
            if selected_category and selected_category.type != tran_type:
                flash(f"Error: You cannot select an '{selected_category.type}' category for an '{tran_type}' transaction!", 'error')
                return render_template('add_transaction.html', categories=categories, today=today_str)

            new_tran = Transaction(
                title=title,
                amount=amount,
                date=date_obj,
                payment_mode=payment_mode,
                type=tran_type,
                user_id=current_user.id,
                category_id=category_id
            )

            db.session.add(new_tran)
            db.session.commit()
            flash('Transaction added!!', 'success')
            return redirect(url_for('dashboard'))
            
        except ValueError:
            flash('Invalid input! Please check amount or date.', 'error')
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding transaction: {str(e)}', 'error')
    
    return render_template('add_transaction.html', categories = categories)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_transaction(id):

    transaction = Transaction.query.get_or_404(id)
    categories = Category.query.all()
    today_str = date.today().strftime('%Y-%m-%d')
    
    if transaction.user_id != current_user.id:
        flash('Unauthorized Access!!!', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        try:
            title = request.form['title']
            amount = float(request.form['amount'])
            payment_mode = request.form['payment_mode']
            trans_type = request.form['type']
            category_id = request.form['category_id']
            
            new_date = datetime.strptime(request.form['date'], '%Y-%m-%d')

            if new_date.date() > date.today():
                flash('You cannot select a future date!', 'error')
                return redirect(request.url)
            
            selected_category = Category.query.filter_by(user_id=current_user.id).all()
            if selected_category and selected_category.type != trans_type:
                flash(f"Mismatch: Category '{selected_category.name}' is for {selected_category.type}, but you selected {trans_type}.", 'error')
                return redirect(request.url)
            
            transaction.title = title
            transaction.amount = amount
            transaction.date = new_date
            transaction.payment_mode = payment_mode
            transaction.type = trans_type
            transaction.category_id = category_id
            
            db.session.commit()
            flash('Transaction updated successfully!', 'success')
            return redirect(url_for('dashboard'))

        except ValueError:
            flash('Invalid input! Please check the amount.', 'error')
            return redirect(request.url)
            
        except Exception as e:
            db.session.rollback() 
            flash(f'Error updating transaction: {str(e)}', 'error')
            return redirect(request.url)
    
    return render_template('edit_transaction.html', transaction=transaction, categories=categories, today=today_str)

@app.route('/delete/<int:id>')
@login_required
def delete_transaction(id):
    transaction = Transaction.query.get_or_404(id)
    
    if transaction.user_id != current_user.id:
        flash('Unauthorised Access!!!','error')
        return redirect(url_for('dashboard'))
    
    try:
        db.session.delete(transaction)
        db.session.commit()
        flash('Transaction deleted successfully!!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting transaction.', 'error')

    return redirect (url_for('dashboard'))

# Categories CRUD
@app.route('/categories')
@login_required
def list_categories():
    categories = Category.query.filter_by(user_id=current_user.id).all()
    return render_template('categories.html', categories = categories)

@app.route('/categories/add', methods = ['GET','POST'])
@login_required
def add_category():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        cat_type = request.form['type']

        if Category.query.filter_by(name = name).first():
            flash('Category already exists!!','error')
        else:
            new_cat = Category(name=name, description=description, type=cat_type, user_id = current_user.id)
            db.session.add(new_cat)
            db.session.commit()
            flash('Category added!', 'success')
            return redirect(url_for('list_categories'))
    return render_template('add_category.html')

@app.route('/categories/edit/<int:id>', methods = ['GET', 'POST'])
@login_required
def edit_category(id):
    category = Category.query.get_or_404(id)
    if request.method == 'POST':
        category.name = request.form['name']
        category.description = request.form['description']
        category.type = request.form['type']
        db.session.commit()
        flash('Category was updated successfully!!','success')
        return redirect(url_for('list_categories'))
    return render_template('edit_category.html',category = category)

@app.route('/categories/delete/<int:id>')
@login_required
def delete_category(id):
    category = Category.query.get_or_404(id)

    associated_transactions = Transaction.query.filter_by(category_id=id).first()
    
    if associated_transactions:
        flash(f"Cannot delete '{category.name}' because it is assigned to existing transactions.", "error")
        return redirect(url_for('list_categories'))
    
    db.session.delete(category)
    db.session.commit()
    flash('Category was deleted successfully!!','success')
    return redirect(url_for('list_categories'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)


