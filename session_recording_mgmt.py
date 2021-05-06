#!/opt/anaconda3/bin/python
import time
from config import *
import datetime as dt
from typing import List, Dict
import os
from pathlib import Path
from misc import *
from subprocess import Popen, PIPE, DEVNULL
import signal


# ref: https://stackoverflow.com/a/31464349/11659389
class GracefulKiller:
  def __init__(self):
    signal.signal(signal.SIGINT, self.exit_gracefully)
    signal.signal(signal.SIGTERM, self.exit_gracefully)
    self.kill_now = False

  def exit_gracefully(self,signum, frame):
    self.kill_now = True


# subprocess management
class RecordingSession:
    def __init__(self, user:str, display:int):
        self.user = user
        self.display = display
        self.cmd_ffmpeg = f"ffmpeg -framerate 24 -f x11grab -i :{display} -c:v libx264 -crf 18 file_full_path"
        self._p: Popen = None


    def start(self):
        _file_dir = f"{RECORDING_DIR}{self.user}/"
        _file_name = get_file_name(self.user)
        _file_path = _file_dir + _file_name
        if not os.path.exists(_file_dir):
            os.mkdir(_file_dir)
        _cmd = self.cmd_ffmpeg.replace("file_full_path", _file_path)
        self._p = Popen(_cmd.split(), \
            # shell=True,\
            # text=True,\
            stdin=None,\
            stdout=DEVNULL,\
            stderr=DEVNULL\
            )

    def stop(self):
        self._p.terminate()
        self._p.wait()

    def is_monitoring(self) -> bool:
        _is_monitoring = self._p.poll() is None
        # if not _is_monitoring:
        #     print(self.user, "is not being monitored!!!")
            # For debugging only
            # with open(os.path.dirname(__file__)+os.sep+"log.txt", "a+") as f:
            #     _std = self._p.stdout.readlines()
            #     _err = self._p.stderr.readlines()
            #     if _std or _err:
            #         f.write(f"--------------------------{self.user}---------------------")
            #         f.write("\n===========================std=====================")
            #         f.write(_std)
            #         f.write("\n===========================err=====================")
            #         f.write(_err)
            #         f.write("\n")

        return _is_monitoring


class SessionRecordingManager:
    def __init__(self):
        self.users: List[str] = [] # all users that should be monitored
        self.users_active: List[str] = [] # users with active citrix session
        self.sessions: Dict[str, RecordingSession] = {}
        self.killer:GracefulKiller = GracefulKiller()


    def run(self):
        '''
        THis method will block current thread, which will work on:
        1. Check the state of each child process. Remove items which have invalid child process;
        2. Check the state of ctxqsession, start new and remove invalid recording items;
        3. Rotational saving:
            1) save recordings on a regular basis;
            2) remove recordings on an regular basis;
        '''
        _start_file_check = time.time()
        _is_new_recording_period = True
        _start_recording_period = int(time.time()/RECORDING_SESSION_DURATION_HOUR/3600)*RECORDING_SESSION_DURATION_HOUR*3600
        while True:
            # File check
            if time.time() - _start_file_check > INTERVAL_OF_FILE_CHECK_SEC:
                _start_file_check = time.time()
                check_file_delete(RECORDING_DIR)

            # periodically stop and start recording again
            # doing this is for cutting the video into pieces
            if _is_new_recording_period:
                _is_new_recording_period = False
                for _u, _session in self.sessions.items():
                    _session.stop()
                    _session.start()
            
            # load active users
            self.users_active = get_users_with_active_citrix_session()
            if "administrator" in self.users_active:
                self.users_active.remove("administrator")

            # check session status
            _u_to_delete = set()
            for _u, _session in self.sessions.items():
                # remove inactive recording sessions
                if not _session.is_monitoring():
                    _u_to_delete.add(_u)
                # remove recording sessions of inactive users
                if _u not in self.users_active:
                    _session.stop()
                    _u_to_delete.add(_u)
            for _u in _u_to_delete:
                del self.sessions[_u]

            # load active recording sessions
            # self.users_active = ["peter"] # This is for testing ONLY
            displays:Dict[str, int] = get_display(self.users_active)
            for _u in self.users_active:
                if _u not in self.sessions:
                    # start to monitor _u
                    _session = RecordingSession(_u, displays[_u])
                    _session.start()
                    self.sessions[_u] = _session

            time.sleep(INTERVAL_OF_MANAGER_MAIN_LOOP_SEC)

            # check killer
            if self.killer.kill_now:
                for _u, _session in self.sessions.items():
                    _session.stop()
                break

            # For debugging only
            # with open(os.path.dirname(__file__)+os.sep+"log.txt", "a+") as f:
            #     f.write(str(dt.datetime.now())+"\n")
            
            # process timing-related things
            # update whether it is new recording period
            if time.time() - _start_recording_period >= RECORDING_SESSION_DURATION_HOUR*3600:
                _start_recording_period = int(time.time()/RECORDING_SESSION_DURATION_HOUR/3600)*RECORDING_SESSION_DURATION_HOUR*3600
                _is_new_recording_period = True


if __name__ == "__main__":
    srm: SessionRecordingManager = SessionRecordingManager()
    srm.run()
    