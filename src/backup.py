#!/usr/bin/python

""" Rsync Backup Tool

This is a very simple tool which facilitates the automated backup of
a linux or unix source path to a local path using rsync.

--dry-run       Will run the rsync without making any changes to the source or destination.
--config=[]     If you require to set a specific or different config files for the program.
                The default config filename is: config.yml
-h --help       This will display the program help.

USAGE : rsync_backup.py -h --help --config=[] --dry-run
LICENSE : GNU GPLv3
"""

import os
import subprocess
import time
import re
import sys
import getopt
import socket
import yaml


def path_check(path):
    """
    Checks whether a path exists and is a folder path (dir).
    :param path:
    :return bool:
    """
    if os.path.exists(path) and os.path.isdir(path):
        return True

    return False


def ping_host(host):
    """
    This method pings the host to check if it receives a response and if the host is up.

    We send 5 packets ('-c 5') and wait 3 milliseconds ('-W 3') for a response. The function returns
    the return code from the ping utility.

    0 - Success
    1 - No Reply
    2 - Other Errors

    :param host:
    :return numerical:
    """
    ret_code = subprocess.call(['ping', '-c', '5', '-W', '3', host], stdout=open(os.devnull, 'w'), stderr=open(os.devnull, 'w'))
    return ret_code


def host_socket_test(host, port):
    """
    Test a host by connecting to a socket on the host.
    :param host:
    :param port:
    :return bool:
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((host, port))
    if result == 0:
        return True

    return False


def generate_rsync_cmd(user, host, options, src_paths, dst_path, dry_run=False):
    """
    This will generate the rsync command which will make the backup.

    :param user:
    :param host:
    :param options:
    :param src_paths:
    :param dst_path:
    :param dry_run:
    :return mixed:
    """
    if len(src_paths) > 0 and isinstance(src_paths, list):
        path_list = "'" + ' '.join(src_paths) + "'"
    else:
        return False

    if not user:
        return False

    if not host:
        return False

    if not options:
        return False

    if dry_run:
        options = options + " --dry-run"

    if not dst_path:
        return False

    the_command = "rsync {attribs} {user}@{host}:{src_paths} {dst_drive_path}".format(
        attribs=options,
        user=user,
        host=host,
        src_paths=path_list,
        dst_drive_path=dst_path
    )

    return the_command


def rsync_check(version):
    """
    This will check if rsync exists and if it matches the version which was specified.
    This is important, because different versions of RSYNC work slightly differently.
    :param version:
    :return bool:
    """
    try:
        # check if rsync exists
        response_rsync = subprocess.run('rsync --version', shell=True, stdout=subprocess.PIPE,
                                        stderr=subprocess.DEVNULL)

        if response_rsync.returncode != 0 and response_rsync.returncode != 1:
            raise Exception("RSYNC not found on this OS.")

        response_version = subprocess.check_output('rsync --version', shell=True)
        version_re = re.findall(r"((version) (\d.\d.\d))", str(response_version))

        if version_re[0][2]:
            if str(version_re[0][2]) == str(version):
                return True
            else:
                raise Exception("Incorrect version detected: " + str(version_re))
        else:
            raise Exception("Could not determine version number")

    except Exception as rsync_exception:
        print("RSYNC ERROR: " + str(rsync_exception.args))
        return False

    return False


def print_help():
    """
    Helper method which will simply print the CMD help.
    It will exit by default because it assumes that the program cannot continue.
    :return:
    """
    print("./rsync_backup.py -h --help --config=[] --dry-run")
    exit(3)


if __name__ == "__main__":

    # Set the default Program config
    PROGRAM_CONFIG = "config.yml"
    RSYNC_DRY_RUN = False

    try:
        # Get program arguments
        opts, args = getopt.getopt(sys.argv[1:], "h", ["help", "config=", "dry-run"])
    except getopt.GetoptError as e:
        print("Something went wrong : " + str(e.args))
        print_help()
        exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print_help()
        elif opt in "--config":
            print("CONFIG: {})".format(arg))
            PROGRAM_CONFIG = arg
        elif opt in "--dry-run":
            print(">>> A DRY RUN")
            RSYNC_DRY_RUN = True

    # Load the PROGRAM YAML config
    try:
        config = yaml.safe_load(open(PROGRAM_CONFIG))
    except Exception as configExteption:
        print(configExteption.args)
        exit(4)

    # Set global configuration
    BACKUP_NAME = config["backup_name"]
    BACKUP_DESCRIPTION = config["backup_description"]
    REMOTE_HOST = config["remote"]["host"]
    REMOTE_USER = config["remote"]["user"]
    SRC_PATH_LIST = config["local"]["path_list"]
    DST_DRIVE_NAME = config["local"]["drive_name"]
    DST_DRIVE_PATH = config["local"]["drive_path"]
    DST_DRIVE_CHECK = config["local"]["drive_check"]
    RSYNC_OPTIONS = config["rsync"]["options"]
    RSYNC_VERSION = config["rsync"]["version"]
    RSYNC_CHECK = config["rsync"]["check"]

    # Print the program start stuff
    start_time = time.time()
    print(">>> START : {name} : {description}".format(name=BACKUP_NAME, description=BACKUP_DESCRIPTION))

    # Check that RSYNC Requirement is met for this OS.
    if RSYNC_CHECK:
        rsync_check(RSYNC_VERSION)

    # Check that the remote host is UP
    if ping_host(REMOTE_HOST) != 0:
        print("Remote host cannot be found on the network.")
        exit(4)
    if not host_socket_test(REMOTE_HOST, 22):
        print("Remote host SSH port not available.")
        exit(4)

    # Check that the destination path exists
    if DST_DRIVE_CHECK:
        if not path_check(DST_DRIVE_PATH):
            print(">>> Destination path does not exist. This could mean that the drive is not mounted correctly or at "
                  "the destination specified in the config.")
            exit(4)

    # If everything has been checked, the RSYNC command can be generated and run.
    rsync_cmd = generate_rsync_cmd(
        REMOTE_USER,
        REMOTE_HOST,
        RSYNC_OPTIONS,
        SRC_PATH_LIST,
        DST_DRIVE_PATH,
        RSYNC_DRY_RUN
    )

    rsync_response = subprocess.run(rsync_cmd, shell=True, stderr=subprocess.DEVNULL)

    if rsync_response.returncode not in (0,1,23):
        print("RSYNC could not be completed successfully.")

    end_time = time.time() - start_time
    print(">>> COMPLETE - {time:.2f} (Seconds)".format(time=end_time))

