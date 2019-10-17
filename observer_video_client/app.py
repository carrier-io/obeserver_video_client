#   Copyright 2019 getcarrier.io
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from flask import Flask, send_from_directory
from os import environ, kill, path, remove
from signal import SIGINT
from subprocess import Popen, PIPE
from multiprocessing import Process, Queue, active_children

xvfb_screen_to_record = environ.get("DISPLAY", ":99.0")
screen_resolution = environ.get("RESOLUTION", "1360x1020")
screen_depth = environ.get("DEPTH", "24")
codec = environ.get("CODEC", "x11grab")
ffmpef_path = environ.get("FFMPEG", "/usr/bin/ffmpeg")


def start_recording():
    cmd = [ffmpef_path,  "-r", "10", "-f", codec, "-s", screen_resolution, "-i",
           xvfb_screen_to_record, "-bufsize", "1k", "-y", "/tmp/output.mp4"]
    Popen(cmd, stderr=PIPE, stdout=PIPE).communicate()


def create_app():
    app = Flask(__name__)
    q = Queue()
    @app.teardown_appcontext
    def teardown_db(event):
        pass

    @app.route("/record/start", methods=["GET"])
    def record_screen():
        if len(active_children()):
            return "Stop previous recording first"
        if path.exists('/tmp/output.mp4'):
            remove('/tmp/output.mp4')
        proc = Process(target=start_recording, args=())
        proc.start()
        return "Ok"

    @app.route("/record/stop", methods=["GET"])
    def record_stop():
        try:
            proc = active_children()[0]
            kill(proc.pid + 1, SIGINT)
            proc.join()
        except:
            pass
        return send_from_directory('/tmp', filename="output.mp4", as_attachment=True)

    return app


def main():
    _app = create_app()
    host = "0.0.0.0"
    port = environ.get("LISTENER_PORT", 9999)
    _app.run(host=host, port=port, debug=True)


if __name__ == "__main__":
    main()
