# app.py
from flask import Flask, render_template, request, send_from_directory
from cryptography.fernet import Fernet
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
ENCRYPTED_FOLDER = 'encrypted'
DECRYPTED_FOLDER = 'decrypted'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(ENCRYPTED_FOLDER, exist_ok=True)
os.makedirs(DECRYPTED_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ENCRYPTED_FOLDER'] = ENCRYPTED_FOLDER
app.config['DECRYPTED_FOLDER'] = DECRYPTED_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/encrypt', methods=['POST'])
def encrypt_file():
    file = request.files['file']
    key_input = request.form['enc_key'].encode()

    key = Fernet.generate_key()  # Optional: derive from password using KDF
    fernet = Fernet(key)

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    with open(filepath, 'rb') as f:
        data = f.read()

    encrypted = fernet.encrypt(data)
    encrypted_filename = f"enc_{file.filename}.enc"
    encrypted_path = os.path.join(app.config['ENCRYPTED_FOLDER'], encrypted_filename)

    with open(encrypted_path, 'wb') as f:
        f.write(encrypted)

    return render_template("index.html", encrypted_file=encrypted_filename, show_key=key.decode())

@app.route('/decrypt', methods=['POST'])
def decrypt_file():
    file = request.files['file']
    key_input = request.form['dec_key'].encode()

    try:
        fernet = Fernet(key_input)
    except:
        return "❌ Invalid decryption key format!"

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    with open(filepath, 'rb') as f:
        encrypted_data = f.read()

    try:
        decrypted_data = fernet.decrypt(encrypted_data)
    except:
        return "❌ Decryption failed! Invalid key or corrupted file."

    output_filename = file.filename.replace('.enc', '')
    output_path = os.path.join(app.config['DECRYPTED_FOLDER'], output_filename)

    with open(output_path, 'wb') as f:
        f.write(decrypted_data)

    return render_template("index.html", decrypted_file=output_filename)

@app.route('/download/<folder>/<filename>')
def download_file(folder, filename):
    folder_path = app.config.get(f'{folder.upper()}_FOLDER')
    return send_from_directory(folder_path, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
