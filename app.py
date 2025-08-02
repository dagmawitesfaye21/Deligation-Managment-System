import os
import mimetypes
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.config['UPLOAD_FOLDER'] = 'files'
app.config['ALLOWED_EXTENSIONS'] = {
    'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 
    'txt', 'csv', 'xls', 'xlsx', 'ppt', 'pptx', 'odt', 
    'ods', 'odp', 'zip', 'rar'
}

# Supported languages
LANGUAGES = {
    'en': 'English',
    'am': 'Amharic'
}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def get_files_for_staff(branch_name, staff_id):
    base_path = os.path.join(app.config['UPLOAD_FOLDER'], branch_name, staff_id)
    
    # Print debug information
    print(f"Looking for files in: {base_path}")
    
    if not os.path.exists(base_path):
        print(f"Directory does not exist: {base_path}")
        return None
    
    files = {}
    found_files = False
    
    for filename in os.listdir(base_path):
        file_path = os.path.join(base_path, filename)
        if os.path.isfile(file_path):
            print(f"Found file: {filename}")
            
            # Flexible matching for delegation letter
            if 'deligation' in filename.lower() or 'delegation' in filename.lower():
                files['letter'] = {
                    'filename': filename,
                    'path': file_path,
                    'type': mimetypes.guess_type(filename)[0] or 'application/octet-stream',
                    'url': url_for('uploaded_file', filename=os.path.join(branch_name, staff_id, filename))
                }
                found_files = True
            # Flexible matching for ID front
            elif 'front' in filename.lower():
                files['id_front'] = {
                    'filename': filename,
                    'path': file_path,
                    'type': mimetypes.guess_type(filename)[0] or 'application/octet-stream',
                    'url': url_for('uploaded_file', filename=os.path.join(branch_name, staff_id, filename))
                }
                found_files = True
            # Flexible matching for ID back
            elif 'back' in filename.lower():
                files['id_back'] = {
                    'filename': filename,
                    'path': file_path,
                    'type': mimetypes.guess_type(filename)[0] or 'application/octet-stream',
                    'url': url_for('uploaded_file', filename=os.path.join(branch_name, staff_id, filename))
                }
                found_files = True
    
    print(f"Files found: {files}")
    return files if found_files else None

@app.route('/')
def home():
    lang = request.args.get('lang', 'en')
    return redirect(url_for('upload', lang=lang))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    lang = request.args.get('lang', 'en')
    
    if request.method == 'POST':
        branch_name = request.form.get('branch_name')
        staff_id = request.form.get('staff_id')
        
        if not branch_name or not staff_id:
            flash('Branch name and Staff ID are required', 'error')
            return redirect(url_for('upload', lang=lang))
        
        if 'delegation_letter' not in request.files or 'id_front' not in request.files or 'id_back' not in request.files:
            flash('Please upload all required files', 'error')
            return redirect(url_for('upload', lang=lang))
        
        letter_file = request.files['delegation_letter']
        id_front_file = request.files['id_front']
        id_back_file = request.files['id_back']
        
        if letter_file.filename == '' or id_front_file.filename == '' or id_back_file.filename == '':
            flash('Please select all required files', 'error')
            return redirect(url_for('upload', lang=lang))
        
        if not (allowed_file(letter_file.filename) and allowed_file(id_front_file.filename) and allowed_file(id_back_file.filename)):
            flash('Allowed file types are: ' + ', '.join(app.config['ALLOWED_EXTENSIONS']), 'error')
            return redirect(url_for('upload', lang=lang))
        
        try:
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], branch_name, staff_id)
            os.makedirs(upload_path, exist_ok=True)
            
            # Get file extensions
            letter_ext = letter_file.filename.rsplit('.', 1)[1].lower()
            id_front_ext = id_front_file.filename.rsplit('.', 1)[1].lower()
            id_back_ext = id_back_file.filename.rsplit('.', 1)[1].lower()
            
            # Create standardized filenames
            letter_filename = f"{branch_name}_{staff_id}_Delegation_Letter.{letter_ext}"
            id_front_filename = f"{branch_name}_{staff_id}_ID_Front.{id_front_ext}"
            id_back_filename = f"{branch_name}_{staff_id}_ID_Back.{id_back_ext}"
            
            # Save files
            letter_file.save(os.path.join(upload_path, secure_filename(letter_filename)))
            id_front_file.save(os.path.join(upload_path, secure_filename(id_front_filename)))
            id_back_file.save(os.path.join(upload_path, secure_filename(id_back_filename)))
            
            flash('Files uploaded successfully!', 'success')
        except Exception as e:
            flash(f'Error uploading files: {str(e)}', 'error')
            print(f"Error during file upload: {str(e)}")
        
        return redirect(url_for('upload', lang=lang))
    
    return render_template('upload.html', lang=lang)

@app.route('/manage', methods=['GET', 'POST'])
def manage():
    lang = request.args.get('lang', 'en')
    
    if request.method == 'POST':
        branch_name = request.form.get('branch_name')
        staff_id = request.form.get('staff_id')
        
        if not branch_name or not staff_id:
            flash('Branch name and Staff ID are required', 'error')
            return redirect(url_for('manage', lang=lang))
        
        files = get_files_for_staff(branch_name, staff_id)
        
        if not files:
            flash('No delegation found for this staff. Please register them first.', 'error')
            return redirect(url_for('upload', lang=lang))
        
        return render_template('manage.html', 
                            files=files, 
                            branch_name=branch_name, 
                            staff_id=staff_id,
                            lang=lang)
    
    return render_template('manage.html', lang=lang)

@app.route('/files/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/change_language/<lang>')
def change_language(lang):
    referrer = request.referrer or url_for('home')
    return redirect(f"{referrer.split('?')[0]}?lang={lang}")

@app.errorhandler(404)
def page_not_found(e):
    lang = request.args.get('lang', 'en')
    return render_template('404.html', lang=lang), 404

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)  # Add host and port parameters