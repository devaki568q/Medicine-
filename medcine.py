from flask import Flask, render_template, request, jsonify
import pymongo
import gridfs
from bson.objectid import ObjectId
import os
from flask_mail import Mail, Message

app = Flask(__name__)

# MongoDB connection setup
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["mydatabase"]
fs = gridfs.GridFS(db)
image_details_collection = db["image_details"]

# Flask-Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'cuted3208@gmail.com'
app.config['MAIL_PASSWORD'] = 'nxuj ulvz pjyv rzje'
app.config['MAIL_DEFAULT_SENDER'] = 'devakimurugesan601@gmail.com'
mail = Mail(app)

def convert_objectid_to_str(obj):
    """Recursively convert ObjectId fields to string in the given object."""
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, dict):
        return {k: convert_objectid_to_str(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_objectid_to_str(i) for i in obj]
    else:
        return obj

@app.route('/')
def index():
    return render_template('medimage.html')

@app.route('/retrieve_image', methods=['POST'])
def retrieve_image_and_details():
    try:
        # Get the medicine name and email from the form
        medicine_name = request.form.get("medicine_name")
        recipient_email = request.form.get("email")
        output_folder_path = 'static/images'  # Folder for storing the image temporarily

        # Retrieve the image details by medicine name
        image_details = image_details_collection.find_one({"Medicine Name": medicine_name})

        if image_details:
            image_id = image_details["_id"]

            # Retrieve the image from GridFS
            image = fs.get(ObjectId(image_id))
            image_save_path = f"{output_folder_path}/image_{image_id}.jpg"

            # Save the image temporarily
            os.makedirs(output_folder_path, exist_ok=True)
            with open(image_save_path, 'wb') as file:
                file.write(image.read())

            # Convert ObjectId fields to string
            image_details_str = convert_objectid_to_str(image_details)

            # Render the image and its details in HTML
            rendered_html = render_template('med.html', image_path=image_save_path, image_details=image_details_str)

            # Send an email with the image and details
            if recipient_email:
                send_email(recipient_email, "Medicine Details", image_details_str, image_save_path)

            return rendered_html

        else:
            return f"No details found for medicine: {medicine_name}"

    except gridfs.errors.NoFile:
        return f"Image not found in GridFS for the specified medicine."
    except Exception as e:
        return f"An error occurred: {e}"

def send_email(to, subject, body, image_path):
    """Send an email with the provided body and attached image."""
    try:
        msg = Message(subject, recipients=[to])
        msg.body = f"Here are the details of the requested medicine:\n\n{body}"

        with open(image_path, 'rb') as image_file:
            msg.attach("medicine_image.jpg", "image/jpeg", image_file.read())

        mail.send(msg)
        print(f"Email sent to {to}")
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == '__main__':
    app.run(debug=True)
