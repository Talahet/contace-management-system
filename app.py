from flask import Flask, flash, redirect, request, jsonify, render_template, url_for, send_file
from flask_pymongo import PyMongo
import vobject
import bcrypt
from bson.objectid import ObjectId  # Import ObjectId for conversion
import io  # To handle file input/output for VCF import/export
import re


# MongoDB connection URL
mongodb_url = 'mongodb+srv://harshtala2662:OY66V5EmIdfR1z0s@cluster0.yqqux.mongodb.net/clustor0?retryWrites=true&w=majority&appName=Cluster0'
app = Flask(__name__)
app.config['MONGO_URI'] = mongodb_url
app.secret_key = '12345678900987654321'
mongo = PyMongo(app)


# Add the validate_email function here
def validate_email(email):
    # Simple email validation using regex
    email_regex = r"[^@]+@[^@]+\.[^@]+"
    return re.match(email_regex, email) is not None


# Home route
@app.route('/')
def index():
    return render_template('index.html')

# User signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if user already exists
        if mongo.db.users.find_one({'username': username}):
            return 'User already exists', 409

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Create a new user
        mongo.db.users.insert_one({
            'username': username,
            'password': hashed_password
        })

        return 'User created successfully', 201

    return render_template('signup.html')

# User login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = mongo.db.users.find_one({'username': username})

        # Verify password
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            flash('Login successful! You can now manage contacts.')
            return redirect(url_for('manage_contacts'))

        flash('Invalid credentials. Please try again.')
        return redirect(url_for('login'))

    return render_template('login.html')# Manage contacts route
@app.route('/manage_contacts', methods=['GET', 'POST'])
def manage_contacts():
    if request.method == 'POST':
        contact_data = {
            'name': request.form['name'],
            'email': request.form.get('email'),
            'phone': request.form.get('phone'),
            'tags': request.form.get('tags').split(',')  # Get tags and split by comma
        }
        # Validate email format
        if contact_data['email'] and not validate_email(contact_data['email']):
            flash('Invalid email format.', 'danger')
            return redirect(url_for('manage_contacts'))

        mongo.db.contacts.insert_one(contact_data)
        flash('Contact added successfully!', 'success')
        return redirect(url_for('manage_contacts'))

    # Handle search query
    search_query = request.args.get('search', '')
    if search_query:
        contacts = mongo.db.contacts.find({
            '$or': [
                {'name': {'$regex': search_query, '$options': 'i'}},
                {'email': {'$regex': search_query, '$options': 'i'}},
                {'tags': {'$regex': search_query, '$options': 'i'}}  # Search by tags
            ]
        })
    else:
        contacts = mongo.db.contacts.find()

    contact_list = [
        {
            'id': str(contact['_id']),
            'name': contact['name'],
            'email': contact.get('email', ''),
            'phone': contact.get('phone', ''),
            'tags': ', '.join(contact.get('tags', []))  # Join tags for display
        } for contact in contacts
    ]

    return render_template('manage_contacts.html', contacts=contact_list, search=search_query)




# Delete contact route
@app.route('/delete_contact/<contact_id>', methods=['POST'])
def delete_contact(contact_id):
    mongo.db.contacts.delete_one({'_id': ObjectId(contact_id)})
    flash('Contact deleted successfully!')
    return redirect(url_for('manage_contacts'))

# Import contacts from VCF
@app.route('/import', methods=['POST'])
def import_contacts():
    vcf_file = request.files['file']
    
    try:
        vcf_data = vobject.readOne(vcf_file.read().decode('utf-8'))
    except Exception as e:
        return f"Error reading VCF file: {e}", 400

    if hasattr(vcf_data, 'fn') and hasattr(vcf_data, 'email'):
        contact_data = {
            'name': vcf_data.fn.value,
            'email': vcf_data.email.value if vcf_data.email else None,
            'phone': vcf_data.tel.value if vcf_data.tel else None
        }
        mongo.db.contacts.insert_one(contact_data)
    else:
        return "Invalid VCF format: 'fn' or 'email' not found", 400

    return 'Contacts imported', 201

# Export contacts to VCF
@app.route('/export')
def export_contacts():
    contacts = mongo.db.contacts.find()
    vcf_stream = io.StringIO()  # Use StringIO to handle in-memory file

    for contact in contacts:
        vcf = vobject.vCard()
        vcf.add('fn').value = contact['name']
        if contact.get('email'):
            vcf.add('email').value = contact['email']
        if contact.get('phone'):
            vcf.add('tel').value = contact['phone']
        vcf_stream.write(vcf.serialize())

    vcf_stream.seek(0)  # Move the cursor back to the start of the stream
    return send_file(io.BytesIO(vcf_stream.read().encode('utf-8')), mimetype='text/vcard', as_attachment=True, download_name='contacts.vcf')


if __name__ == '__main__':
    app.run(debug=True)
