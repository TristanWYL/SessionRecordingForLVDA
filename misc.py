#!/opt/anaconda3/bin/python
import datetime
from config import *
from typing import List, Optional, Dict
import os
from pathlib import Path
from subprocess import Popen, PIPE, CalledProcessError
import re
import logging


logger = logging.getLogger("srlogger")
logger.setLevel(level=LOG_LEVEL)
_handler = logging.FileHandler(LOG_FILEPATH, encoding='UTF-8')
_handler.setLevel(LOG_LEVEL)
_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
_handler.setFormatter(_formatter)
logger.addHandler(_handler)


def get_file_name(user:str) -> str:
    timestamp = datetime.datetime.now().strftime("%Y_%m_%d__%H_%M_%S")
    return user + "_" + timestamp + ".mp4"


def get_dt_from_filename(filename:str) -> datetime.datetime:
    return datetime.datetime.strptime(filename[-24:-4], "%Y_%m_%d__%H_%M_%S")


def should_delete(filename:str) -> bool:
    file_start_date: datetime.datetime = get_dt_from_filename(filename)
    return datetime.datetime.now() - file_start_date >= datetime.timedelta(hours=RECORDING_SESSION_DURATION_HOUR+PRESERVE_DAY*24)


def get_monitored_users() -> List[str]:
    users = []
    with open(str(Path(os.path.dirname(__file__)).parent)+os.sep+"config"+os.sep+"monitored_user_list.txt", "r") as f:
        _users = f.read().split("\n")
    for u in _users:
        if u == "":
            continue
        users.append(u)
    return users


def get_users_with_active_citrix_session() -> List[str]:
    cmd = "/opt/Citrix/VDA/bin/ctxqsession 2> /dev/null"
    users_active = []
    p = Popen(cmd, \
        shell=True,\
        text=True,\
        stdin=PIPE,\
        stdout=PIPE,\
        stderr=PIPE)
    if p.wait() == 0:
        # returncode is normal
        # this subprocess is terminated normally
        ret = p.stdout.readlines()
        # remove the first line
        ret = ret[1:]
        # analyze the data
        for line in ret:
            items = line.split()
            if items[2] == "active":
                users_active.append(items[1])
        return users_active
    raise CalledProcessError(p.returncode, cmd)


def get_displays_by_who(users: Optional[List[str]] = None) -> Dict[str, int]:
    cmd = "who 2> /dev/null"
    name_start_at = len(DOMAIN) + 1
    user_display_pair = {}
    p = Popen(cmd, \
        shell=True,\
        text=True,\
        stdin=PIPE,\
        stdout=PIPE,\
        stderr=PIPE)
    if p.wait() == 0:
        # returncode is normal
        # this subprocess is terminated normally
        ret = p.stdout.readlines()
        # analyze the data
        for line in ret:
            if line.startswith(DOMAIN):
                items = line.split()
                _user = items[0][name_start_at:]
                _display = items[1][1:]
                if users:
                    if _user in users:
                        user_display_pair[_user] = int(_display)
                else:
                    user_display_pair[_user] = int(_display)            
        return user_display_pair
    raise CalledProcessError(p.returncode, cmd)
    

def get_ctxlogin_info() -> Dict[str, str]:
    '''
    run cmd "pstree -Aup | grep 'ctxlogin('" to get gnome sessions from which we can 
    find the PID of gnome processes
    Return: pair: user vs str of PID
    '''
    cmd = "pstree -Aup | grep 'ctxlogin(' 2> /dev/null"
    user_gnome_pid_pair = {}
    p = Popen(cmd, \
        shell=True,\
        text=True,\
        stdin=PIPE,\
        stdout=PIPE,\
        stderr=PIPE)
    if p.wait() == 0:
        # returncode is normal
        # this subprocess is terminated normally
        ret = p.stdout.readlines()
        # analyze the data
        for line in ret:
            p = re.compile("ctxlogin\((\d+),([\w\.]+)\)")
            m = p.search(line)
            _pid, _u = m.groups()
            user_gnome_pid_pair[_u] = _pid
        return user_gnome_pid_pair
    raise CalledProcessError(p.returncode, cmd)


def get_display_by_pid(pid: str) -> int:
    _filepath = f"/proc/{pid}/environ"
    _pattern = "DISPLAY=:(\d+)"
    p = re.compile(_pattern)
    try:
        with open(_filepath, "r") as f:
            _file_content = f.read()
            m = p.search(_file_content)
            if len(m.groups()) == 1:
                return int(m.group(1))
            else:
                logger.warning("Failed to find the DISPLAY environment variable of process %s", pid)
                return -1
    except:
        logger.exception("Try to read the environment variables of process %s", pid)
        return -1


def get_displays_by_gnome_proc(users: Optional[List[str]]) -> Dict[str, int]:
    # get the user_gnome_pid pair first
    user_gnome_pid_pair = get_ctxlogin_info()
    user_display_pair = {}
    if users:
        for _u in users:
            if _u in user_gnome_pid_pair:
                user_display_pair[_u] = get_display_by_pid(user_gnome_pid_pair[_u])
            else:
                logger.warning("User %s does not have a running ctxlogin process", _u)
                user_display_pair[_u] = -1
    else:
        for _u, _pid in user_gnome_pid_pair.items():
            user_display_pair[_u] = get_display_by_pid(_pid)
    return user_display_pair


def check_file_delete(dir: str):
    for _dir, _, files in os.walk(dir):
        for _file in files:
            file_path = _dir + os.sep + _file
            if file_path.endswith("mp4"):
                if should_delete(file_path):
                    os.remove(file_path)

if __name__ == "__main__":
    users = get_display_by_pid("10839")
    user = 1
    print(1)
    