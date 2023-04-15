from flask import Flask, render_template, request, send_file, url_for, redirect, jsonify, json
from pytube import YouTube
from pydub import AudioSegment
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'temp')

@app.route('/')
def home():
    file_list = os.listdir(app.config['UPLOAD_FOLDER'])
    
    # Get response query parameter if present
    response_str = request.args.get('response')
    if response_str:
        response = json.loads(response_str)
    else:
        response = None
    
    return render_template('home.html', files=file_list, response=response)


@app.route('/convert', methods=['POST', 'GET'])
def convert():
    url = request.form['url']
    format = request.form['format']

    try:
        yt = YouTube(url)
        if format == 'mp3':
            # download video and extract audio
            stream = yt.streams.filter(only_audio=True).first()
            stream.download(output_path=app.config['UPLOAD_FOLDER'], filename=f'{yt.title}.mp4')
            audio_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{yt.title}.mp4')
            audio = AudioSegment.from_file(audio_path, format='mp4')
            audio.export(os.path.join(app.config['UPLOAD_FOLDER'], f'{yt.title}.mp3'), format='mp3')
            os.remove(audio_path)
            filename = f'{yt.title}.mp3'
        elif format == 'mp4':
            # download video
            stream = yt.streams.filter(file_extension='mp4').first()
            stream.download(output_path=app.config['UPLOAD_FOLDER'], filename=f'{yt.title}.mp4')
            filename = f'{yt.title}.mp4'
        else:
            return 'Invalid format'
        return render_template('download.html', filename=filename)
    except:
        return 'Failed to convert video'

@app.route('/download/<filename>', methods=['POST', 'GET'])
def download(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return send_file(file_path, as_attachment=True)

@app.route('/delete/<filename>')
def delete(filename):
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        os.remove(file_path)
        message = f'{filename} has been deleted. You will be redirected to the home page in a moment.'
        return jsonify({'status': 'success', 'message': message, 'redirect': url_for('home')}), 200
    except:
        message = f'Failed to delete {filename}.'
        return jsonify({'status': 'error', 'message': message}), 500



if __name__ == '__main__':
    app.run(debug=True)

