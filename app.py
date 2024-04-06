import os
from flask import Flask, render_template, request
import requests
from urllib.parse import urlparse, quote

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    username = request.form['username']
    directory = request.form.get('directory', username)

    os.makedirs(directory, exist_ok=True)

    encoded_username = quote(username)

    url = f"http://web.archive.org/web/timemap/?url=https://twitter.com/{encoded_username}&matchType=prefix&collapse=urlkey&output=json&fl=original,mimetype,timestamp"

    response = requests.get(url, stream=True)
    web_archive_lines = response.iter_lines()

    with open(os.path.join(directory, f"{username}.txt"), 'w') as text_file:
        with open(os.path.join(directory, f"{username}.webarchive"), 'wb') as web_file:
            for line in web_archive_lines:
                line = line.decode('utf-8')
                parts = line.split('"')
                if len(parts) > 1:
                    web_archive_url = parts[1]
                    web_file.write(f"https://web.archive.org/web/0/{web_archive_url}\n".encode('utf-8'))
                    timeline_record = urlparse(web_archive_url).path.split('/')[-1]
                    text_file.write(timeline_record + '\n')

    result = {
        'directory': directory,
        'username': username
    }

    return render_template('result.html', result=result)


if __name__ == '__main__':
    app.run(debug=True)
