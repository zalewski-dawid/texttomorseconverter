from flask import Flask, render_template,jsonify, request, redirect, url_for
import os
from flask_bootstrap import Bootstrap5
from flask_mail import Mail,Message
from form import TextForm
from dotenv import load_dotenv
from TextToMorseConverter import TextToMorseConverter
import random
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column
from sqlalchemy import String,Integer,Date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime, timedelta,timezone
from flask_apscheduler import APScheduler



load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
bootstrap = Bootstrap5(app)
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

#Scheduled the deletion task to run every day
@scheduler.task('interval',id='delete_expired_users',days=1)
def scheduled_delete_expired_users():
    delete_expired_users()


# Initialize Flask-Limiter
limiter = Limiter(
    get_remote_address,  # Get the client's IP address
    app=app,
    default_limits=["200 per day", "50 per hour"]  # Global rate limits
)

app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')



mail=Mail(app)


#DATABASE

class Base(DeclarativeBase):
    pass

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DB_URI')
db=SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users_info'
    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    user_id:Mapped[str]=mapped_column(String(26),nullable=False)
    user_token:Mapped[str]=mapped_column(String(255),nullable=False)
    created_at: Mapped[datetime] = mapped_column(Date, default=datetime.date)



with app.app_context():
    db.create_all()


@app.route("/",methods=["GET","POST"])
def index():
    form=TextForm()

    if form.validate_on_submit():
        text_to_morse_conv=TextToMorseConverter()

        data={
            'original_text': form.text.data,
            'morse_code': text_to_morse_conv.text_to_morse(form.text.data)
        }
        return jsonify(data)

    return render_template('index.html',form=form)

@app.route('/api/generate_data')
#@limiter.limit("5 per minute, 50 per day")
def handling_api():
    user_id=str(request.args.get("user_id"))
    user_token=str(request.args.get("user_token"))
    user_input=str(request.args.get("user_input"))
    if not user_id:
        return jsonify({'ERROR':'user_id param is required'})

        if not user_token:
            return jsonify({'ERROR':'user_token param is required'})

            if not user_input:
                return jsonify({'ERROR':'user_input param is required'})

    else:
        if db.session.query(User).filter_by(user_id=user_id).first():
            result=db.session.query(User).filter_by(user_id=user_id).first()

            if check_password_hash(result.user_token, user_token):
                text_to_morse_conv=TextToMorseConverter()

                data = {
                    'original_text': user_input,
                    'morse_code': text_to_morse_conv.text_to_morse(user_input)
                }
                return jsonify(data)
            else:
                return jsonify({'ERROR':'token_id is not found or expired'})
        else:
            return jsonify({'ERROR':'user_id is not found or expired'})


def generate_random_string():
    letters_and_digits = [chr(i) for i in range(65, 91)] + [chr(i) for i in range(97, 123)] + [chr(i) for i in
                                                                                               range(48, 58)]
    random.shuffle(letters_and_digits)

    random_string=''
    for x in range(26):
        random_string += random.choice(letters_and_digits)


    random_string_list = list(random_string)

    random.shuffle(random_string_list)


    return ''.join(random_string_list)




@app.route('/api/generate_credentials')
#@limiter.limit("2 per day")
def generate_credentials():

    email=request.args.get('email')

    if not email:

        return jsonify({'error': 'email parameter not provided'})
    else:
        user_id = generate_random_string()
        user_token = generate_random_string()

        #Checking in the database if there is no such user_id
        if db.session.query(User).filter_by(user_id=user_id).first():
            user_id=generate_random_string()
            if db.session.query(User).filter_by(user_id=user_id).first():
                user_token=generate_random_string()



        # sending email message
        email_to_send = email
        msg = Message(
            subject=f"YOUR MORSE CONVERTER API CREDENTIALS",
            body=f"KEEP IT SAFE!\nuser_id: {user_id}\nuser_token: {user_token}\n",
            recipients=[email_to_send]
        )

        try:
            mail.send(msg)

            # adding user credentials to the database
            hash_and_salted_user_token = generate_password_hash(user_token, method='pbkdf2:sha256', salt_length=8)

            new_user = User(user_id=user_id, user_token=hash_and_salted_user_token,created_at=datetime.now(timezone.utc).date())
            db.session.add(new_user)
            db.session.commit()

            return jsonify({"status": "success"})

        except Exception as e:
            return jsonify({"status": f"failed {e}"})


@app.route('/api/doc')
def api_doc():
    return render_template('api.html')

@app.route('/about')
def about():
    return render_template('about.html')

def delete_expired_users():

    with app.app_context():
        one_month_ago = datetime.now(timezone.utc).date() - timedelta(days=30)
        # Find all users who were created more than one month ago
        if db.session.query(User).filter(User.created_at < one_month_ago).all():
            expired_users = db.session.query(User).filter(User.created_at < one_month_ago).all()

            # Delete each expired user
            for user in expired_users:
                db.session.delete(user)

            db.session.commit()




if __name__ == "__main__":
    app.run(debug=True)