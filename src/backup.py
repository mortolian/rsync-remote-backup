"""
Rsync Backup Tool
----------------------------------------------------------------------
This is a very simple tool which facilitates the automated backup of
a linux or unix source path to a local path using rsync.
----------------------------------------------------------------------
LICENSE : GNU GPLv3
"""
import argparse
import os
import socket
import subprocess
import time
import yaml
from termcolor import colored, cprint
from dataclasses import dataclass

RSYNC_VERSION = '2.6.9'
DEFAULT_CONFIG = 'config.yaml'


@dataclass
class ConfigSyncPathsDataClass:
    name: str
    remote_path: str
    local_path: str


@dataclass
class ConfigDataClass:
    job_name: str
    description: str
    remote_host: str
    remote_user: str
    sync_paths: list[ConfigSyncPathsDataClass]
    rsync_options: str


@dataclass
class ConfigListDataClass:
    jobs: list[ConfigDataClass]


class RsyncNotFoundException(Exception):
    pass


class RemoveSocketNotFoundException(Exception):
    pass


class PathNotFoundException(Exception):
    pass


class ConfigJobNotFoundException(Exception):
    pass


def readConfig(config_file_path: str) -> ConfigListDataClass:
    """
    check if there is a config argument set and use that file else
    use the default config file.
    """
    with open(config_file_path, 'r') as config_file_content:
        try:
            configs = yaml.safe_load(config_file_content.read())
            return ConfigListDataClass(
                jobs=[ConfigDataClass(
                    job_name=c,
                    description=configs[c]['description'],
                    remote_host=configs[c]['remote']['host'],
                    remote_user=configs[c]['remote']['user'],
                    sync_paths=[ConfigSyncPathsDataClass(
                        name=p,
                        remote_path=configs[c]['sync']['paths'][p][
                            'remote_path'],
                        local_path=configs[c]['sync']['paths'][p][
                            'local_path'],
                    ) for p in configs[c]['sync']['paths']],
                    rsync_options=configs[c]['rsync']['options'],
                ) for c in configs]
            )
        except yaml.YAMLError as e:
            raise e
        except KeyError as e:
            raise KeyError(f'The configuration file seems to have '
                           f'an error: {e}')


def checkRemoteSocket(host: str, port: int = 22) -> bool:
    """
    Do a test to see that the host is available and that the
    required SSH port is available to connect to.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((host, port))
    if result != 0:
        raise RemoveSocketNotFoundException(
            f'Remote host {host} did not answer on '
            f'port {port}.')

    return True


def pathCheck(path) -> bool:
    """
    Checks whether a path exists and is a folder path (dir).
    """
    if os.path.exists(path) and os.path.isdir(path):
        return True

    raise PathNotFoundException(f'The path \'{path}\' could not be found.')


def rsyncCheck(version: str) -> bool:
    """
    This will check if rsync exists and if it matches the
    specified version. This can be useful to check what
    command arrangement will work.
    """
    response = subprocess.run(
        ['rsync', '--version'],
        capture_output=True,
        text=True
    )

    if response.stdout.find(version) == -1 or response.returncode != 0:
        raise RsyncNotFoundException(f'RSYNC is missing or not the '
                                     f'correct version. RSYNC {RSYNC_VERSION} '
                                     f'needed.')

    return True


def compileRsyncCommand(config: ConfigDataClass) -> str:
    """ This creates the rsync command and validates all the information. """
    return ''


def rsync():
    """
    This will run the final RSYNC.
    """
    ...


def findJobConfig(
        job: str,
        config: ConfigListDataClass
) -> ConfigDataClass:
    """
    This will find the first job in the config that relates to the
    specified job.
    """
    for c in config.jobs:
        if c.job_name == job:
            return c

    raise ConfigJobNotFoundException('The job config was not found.')


def parserSetup() -> argparse.Namespace:
    """ Set up the argument parser for the application. """
    parser = argparse.ArgumentParser('Backup Remote Files.')
    parser.add_argument('-j', '--job',
                        help='Specifies what config job to run.',
                        type=str)
    parser.add_argument('-s', '--show-available-jobs',
                        help='Shows a list of jobs available in the config.',
                        default=False,
                        action='store_true')
    parser.add_argument('-c', '--config',
                        help='Specify a config file if you do not want '
                             'to use the default config file (config.yaml).',
                        default=DEFAULT_CONFIG, type=str)
    parser.add_argument('-d', '--dry-run',
                        help='Will run the rsync without making any '
                             'changes to the source or destination.',
                        default=False,
                        action='store_true')

    return parser.parse_args()


def main():
    args = parserSetup()

    try:
        # Read the config file if available.
        config_path = args.config if args.config else DEFAULT_CONFIG
        config = readConfig(config_path)

        # If the user requested to see the available jobs, show a list.
        if not args.job and args.show_available_jobs:
            available_jobs = [a.job_name for a in config.jobs]
            cprint(f'These jobs are available in your config file: '
                   f'{available_jobs}', 'blue')
            exit(60)

        if args.job:
            # Check that the job exists in the config.
            job_config = findJobConfig(args.job, config)

            # Check to see if the correct RSYNC is available.
            rsyncCheck(RSYNC_VERSION)

            # Build RSYNC command from job config if it exists
            rsync_command = compileRsyncCommand(job_config)

            # Do RSYNC backup
            start_time = time.time()

            cprint(f'The job {args.job} took {(time.time() - start_time):.2f} '
                   f'seconds to complete.', 'yellow')

    except Exception as e:
        cprint(str(e), 'red')


if __name__ == '__main__':
    main()
