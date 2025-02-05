# bob/captive_portal.py

import subprocess
import threading
from flask import Flask, redirect
from bob.config import SURVEY_URL
from bob.logger import logger

app = Flask(__name__)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def redirect_all(path):
    """
    Catch all HTTP requests and redirect them to the survey URL.
    """
    logger.info("Redirecting request for /%s to survey at %s", path, SURVEY_URL)
    return redirect(SURVEY_URL, code=302)

def start_flask_server(port=8080):
    """
    Start the Flask server on the given port.
    """
    logger.info("Starting Flask server on port %s", port)
    app.run(host='0.0.0.0', port=port, debug=False)

def setup_iptables(redirect_port=8080):
    """
    Set an iptables rule to redirect all HTTP (port 80) traffic to the specified redirect port.
    """
    try:
        subprocess.check_call([
            'sudo', 'iptables', '-t', 'nat', '-A', 'PREROUTING',
            '-p', 'tcp', '--dport', '80', '-j', 'REDIRECT', '--to-port', str(redirect_port)
        ])
        logger.info("iptables rule added: Redirecting port 80 to port %s", redirect_port)
    except subprocess.CalledProcessError as e:
        logger.error("Error setting up iptables: %s", e)

def clear_iptables(redirect_port=8080):
    """
    Remove the iptables rule that redirects HTTP traffic.
    """
    try:
        subprocess.check_call([
            'sudo', 'iptables', '-t', 'nat', '-D', 'PREROUTING',
            '-p', 'tcp', '--dport', '80', '-j', 'REDIRECT', '--to-port', str(redirect_port)
        ])
        logger.info("iptables rule removed: Port 80 redirection cleared.")
    except subprocess.CalledProcessError as e:
        logger.error("Error clearing iptables: %s", e)

def start_captive_portal():
    """
    Configure iptables and start the Flask captive portal server in a separate thread.
    """
    setup_iptables(redirect_port=8080)
    flask_thread = threading.Thread(target=start_flask_server, args=(8080,), daemon=True)
    flask_thread.start()
    logger.info("Captive portal started. All HTTP traffic is being redirected to the survey.")

def stop_captive_portal():
    """
    Remove the iptables redirection rule (stopping the captive portal).
    """
    clear_iptables(redirect_port=8080)
    logger.info("Captive portal stopped.")

if __name__ == '__main__':
    start_captive_portal()
    input("Captive portal is active. Press Enter to stop...")
    stop_captive_portal()
