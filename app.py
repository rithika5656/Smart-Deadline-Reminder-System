import os
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mail import Mail, Message
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from models import db, User, Deadline

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///deadlines.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Mail Configuration
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

# Initialize extensions
db.init_app(app)
mail = Mail(app)

# Create database tables
with app.app_context():
    db.create_all()


def send_reminder_email(user_email, user_name, deadline):
    """Send a reminder email for an upcoming deadline"""
    try:
        msg = Message(
            subject=f"⏰ Reminder: {deadline.title} - Due Soon!",
            sender=app.config['MAIL_USERNAME'],
            recipients=[user_email]
        )
        
        msg.html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; text-align: center;">
                <h1 style="color: white; margin: 0;">📚 Deadline Reminder</h1>
            </div>
            <div style="padding: 30px; background: #f8f9fa;">
                <p>Hi <strong>{user_name}</strong>,</p>
                <p>This is a friendly reminder about your upcoming deadline:</p>
                <div style="background: white; padding: 20px; border-radius: 10px; border-left: 4px solid #667eea;">
                    <h2 style="margin: 0 0 10px 0; color: #333;">{deadline.title}</h2>
                    <p style="color: #666; margin: 5px 0;"><strong>Type:</strong> {deadline.deadline_type.title()}</p>
                    <p style="color: #666; margin: 5px 0;"><strong>Due:</strong> {deadline.due_date.strftime('%B %d, %Y at %I:%M %p')}</p>
                    <p style="color: #666; margin: 5px 0;"><strong>Description:</strong> {deadline.description or 'No description'}</p>
                </div>
                <p style="margin-top: 20px;">Good luck! 🍀</p>
                <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                <p style="color: #999; font-size: 12px;">This email was sent by Smart Deadline Reminder System.</p>
            </div>
        </body>
        </html>
        """
        
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False


def check_and_send_reminders():
    """Check for upcoming deadlines and send reminders"""
    with app.app_context():
        now = datetime.utcnow()
        
        # Get all deadlines that haven't been reminded yet
        deadlines = Deadline.query.filter_by(reminder_sent=False).all()
        
        for deadline in deadlines:
            reminder_time = deadline.due_date - timedelta(hours=deadline.reminder_hours)
            
            # If it's time to send the reminder
            if now >= reminder_time and now < deadline.due_date:
                user = User.query.get(deadline.user_id)
                if user:
                    success = send_reminder_email(user.email, user.name, deadline)
                    if success:
                        deadline.reminder_sent = True
                        db.session.commit()
                        print(f"Reminder sent for: {deadline.title}")


# Setup scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(func=check_and_send_reminders, trigger="interval", minutes=5)
scheduler.start()


@app.route('/')
def index():
    """Display dashboard with all deadlines"""
    user = User.query.first()
    if user:
        deadlines = Deadline.query.filter_by(user_id=user.id).order_by(Deadline.due_date).all()
    else:
        deadlines = []
    return render_template('index.html', deadlines=deadlines)


@app.route('/add', methods=['GET', 'POST'])
def add_deadline():
    """Add a new deadline"""
    user = User.query.first()
    
    if request.method == 'POST':
        if not user:
            flash('Please set up your profile in Settings first!', 'error')
            return redirect(url_for('settings'))
        
        title = request.form.get('title')
        description = request.form.get('description')
        due_date_str = request.form.get('due_date')
        deadline_type = request.form.get('deadline_type')
        reminder_hours = int(request.form.get('reminder_hours', 24))
        
        try:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            flash('Invalid date format!', 'error')
            return redirect(url_for('add_deadline'))
        
        new_deadline = Deadline(
            title=title,
            description=description,
            due_date=due_date,
            deadline_type=deadline_type,
            reminder_hours=reminder_hours,
            user_id=user.id
        )
        
        db.session.add(new_deadline)
        db.session.commit()
        
        flash(f'Deadline "{title}" added successfully!', 'success')
        return redirect(url_for('index'))
    
    return render_template('add_deadline.html')


@app.route('/delete/<int:id>', methods=['POST'])
def delete_deadline(id):
    """Delete a deadline"""
    deadline = Deadline.query.get_or_404(id)
    title = deadline.title
    db.session.delete(deadline)
    db.session.commit()
    flash(f'Deadline "{title}" deleted!', 'success')
    return redirect(url_for('index'))


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    """User settings page"""
    user = User.query.first()
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        
        if user:
            user.name = name
            user.email = email
        else:
            user = User(name=name, email=email)
            db.session.add(user)
        
        db.session.commit()
        flash('Settings saved successfully!', 'success')
        return redirect(url_for('settings'))
    
    return render_template('settings.html', user=user)


@app.route('/test-email', methods=['POST'])
def test_email():
    """Send a test email"""
    user = User.query.first()
    
    if not user:
        flash('Please set up your profile first!', 'error')
        return redirect(url_for('settings'))
    
    try:
        msg = Message(
            subject="🧪 Test Email - Smart Deadline Reminder",
            sender=app.config['MAIL_USERNAME'],
            recipients=[user.email]
        )
        msg.html = """
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h1>✅ Test Successful!</h1>
            <p>Your email configuration is working correctly.</p>
            <p>You will now receive reminders for your upcoming deadlines.</p>
        </body>
        </html>
        """
        mail.send(msg)
        flash('Test email sent successfully! Check your inbox.', 'success')
    except Exception as e:
        flash(f'Failed to send email: {str(e)}', 'error')
    
    return redirect(url_for('settings'))


if __name__ == '__main__':
    app.run(debug=True)
