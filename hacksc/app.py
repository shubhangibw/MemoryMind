# from flask import Flask, render_template

# app = Flask(__name__)

# @app.route('/')
# def home():
#     return render_template('index.html')

# if __name__ == '__main__':
#     app.run(debug=True)


from flask import Flask, request, render_template, send_from_directory
import openai
import requests
import pyttsx3
from pydub import AudioSegment
import os

app = Flask(__name__)

# Set OpenAI API Key
openai.api_key = 'your-openai-api-key'

# Directory to save generated files
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Helper Functions
def generate_lyrics(text_input):
    prompt = f"Turn the following paragraph into song lyrics, with verses and a chorus. The theme is reflective and melancholic.\n\n{text_input}"
    response = openai.Completion.create(
        model="gpt-4",
        prompt=prompt,
        max_tokens=300,
        n=1,
        temperature=0.7
    )
    return response.choices[0].text.strip()

def generate_music(genre='Pop', mood='Reflective'):
    aiva_api_url = 'https://api.aiva.ai/v1/music/generate'
    headers = {'Authorization': 'Bearer YOUR_AIVA_API_KEY', 'Content-Type': 'application/json'}
    data = {
        'style': genre,
        'mood': mood,
        'length': 180
    }
    response = requests.post(aiva_api_url, headers=headers, json=data)
    if response.status_code == 200:
        music_data = response.json()
        return music_data.get('music_url')
    else:
        raise Exception("Error generating music:", response.text)

def synthesize_vocals(lyrics):
    engine = pyttsx3.init()
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'song_vocals.mp3')
    engine.save_to_file(lyrics, output_path)
    engine.runAndWait()
    return output_path

def combine_music_and_vocals(music_url, vocals_path):
    music = AudioSegment.from_file(music_url)
    vocals = AudioSegment.from_file(vocals_path)
    vocals = vocals - 10  # Adjust vocal volume if necessary
    combined = music.overlay(vocals, position=0)
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'final_song.mp3')
    combined.export(output_path, format="mp3")
    return output_path

# Flask Routes
@app.route('/')
def index():
    return render_template('test.html') 
#  chnage to index file LATER

@app.route('/create_song', methods=['POST'])
def create_song():
    text_input = request.form['text_input']
    
    # Generate lyrics
    lyrics = generate_lyrics(text_input)
    
    # Generate music
    music_url = generate_music(genre='Pop', mood='Reflective')
    
    # Synthesize vocals
    vocals_path = synthesize_vocals(lyrics)
    
    # Combine music and vocals
    final_song_path = combine_music_and_vocals(music_url, vocals_path)
    
    return send_from_directory(directory=UPLOAD_FOLDER, filename='final_song.mp3', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
