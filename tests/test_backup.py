import subprocess
import pytest
import socket
from backup import backup, ConfigListDataClass, ConfigDataClass

BAD_CONFIG_FILE = """
offsite_1::
  description: 'Remote Backup Job 1'
"""

GOOD_CONFIG_FILE = """
offsite_1:
  description: 'Remote Backup Job 1'
  remote:
    host: '10.1.1.1'
    user: 'admin'
    paths:
      - '/share/Datafile'
      - '/share/Backupfiles'
  local:
    path: '/Volumes/offsite1'
  rsync:
    options: '--progress --recursive --archive --delete --verbose --stats --human-readable --copy-links'


offsite_2:
  description: 'Remote Backup Job 2'
  remote:
    host: '10.1.1.2'
    user: 'admin'
    paths:
      - '/share/Datafile'
      - '/share/Backupfiles'
  local:
    path: '/Volumes/offsite2'
  rsync:
    options: '--progress --recursive --archive --delete --verbose --stats --human-readable --copy-links'
"""

CONFIG_DATA_OBJECT = ConfigListDataClass(
    jobs=[
        ConfigDataClass(
            job_name='offsite_1',
            description='Remote Backup Job 1',
            remote_host='10.1.1.1',
            remote_user='admin',
            remote_paths=['/share/Datafile', '/share/Backupfiles'],
            local_path='/Volumes/offsite1',
            rsync_options='--progress --recursive --archive --delete --verbose --stats --human-readable --copy-links'),
        ConfigDataClass(
            job_name='offsite_2',
            description='Remote Backup Job 2',
            remote_host='10.1.1.2',
            remote_user='admin',
            remote_paths=['/share/Datafile', '/share/Backupfiles'],
            local_path='/Volumes/offsite2',
            rsync_options='--progress --recursive --archive --delete --verbose --stats --human-readable --copy-links')
    ]
)


def test_check_remote_socket_success(monkeypatch) -> None:
    monkeypatch.setattr(socket.socket, 'connect_ex', lambda ip, sct: 0)
    result = backup.checkRemoteSocket('192.168.1.200', 22)
    assert result


def test_check_remote_socket_exception(monkeypatch) -> None:
    with pytest.raises(backup.RemoteSocketNotFoundException):
        monkeypatch.setattr(socket.socket, 'connect_ex', lambda ip, sct: 1)
        backup.checkRemoteSocket('192.168.1.200', 22)


@pytest.fixture
def mock_config_good_file(mocker):
    yaml_config_data = mocker.mock_open(read_data=GOOD_CONFIG_FILE)
    mocker.patch("builtins.open", yaml_config_data)


@pytest.fixture
def mock_config_bad_file(mocker):
    yaml_config_data = mocker.mock_open(read_data=BAD_CONFIG_FILE)
    mocker.patch("builtins.open", yaml_config_data)


def test_read_config(mock_config_good_file) -> None:
    result = backup.readConfig(config_file_path='mock_file.yaml')
    assert repr(result) == repr(CONFIG_DATA_OBJECT)


def test_read_config_key_error(mock_config_bad_file) -> None:
    with pytest.raises(KeyError):
        backup.readConfig(config_file_path='mock_file.yaml')


def test_path_exists_check() -> None:
    assert backup.pathExistsCheck('./')


def test_path_exists_check_fail() -> None:
    with pytest.raises(backup.PathNotFoundException):
        backup.pathExistsCheck('/dkjashdgfkajshdfaskjhgasdkfjhs')


def test_rsync_check(monkeypatch) -> None:
    def subprocess_response(*args, **kwargs):
        return subprocess.CompletedProcess(
            args=['rsync', '--version'],
            returncode=0,
            stdout='rsync  version 2.6.9  protocol version 29\nCopyright \n',
            stderr='')

    monkeypatch.setattr(subprocess, 'run', subprocess_response)
    assert backup.rsyncCheck('2.6.9')
    with pytest.raises(backup.RsyncNotFoundException):
        backup.rsyncCheck('2.7.9')


def test_compile_rsync_command() -> None:
    configDataClass = ConfigDataClass(
        job_name="job1",
        description="This is job1",
        remote_host="192.168.10.10",
        remote_user="backup",
        remote_paths=['/backup1', '/backup2'],
        local_path="/backup3",
        rsync_options="--progress --recursive",
    )
    result = backup.compileRsyncCommand(
        config=configDataClass,
        dry_run=True
    )
    assert result == "rsync --progress --recursive --dry-run " \
                     "backup@192.168.10.10:'/backup1 /backup2' /backup3"


def test_validate_remote_path() -> None:
    with pytest.raises(backup.PathValidationException):
        backup.validateRemotePath('test/')


def test_validate_local_path() -> None:
    with pytest.raises(backup.PathValidationException):
        backup.validateLocalPath('test/')


def test_rsync(monkeypatch) -> None:
    def subprocess_response(*args, **kwargs):
        return subprocess.CompletedProcess(
            args=["rsync --progress --recursive --dry-run " \
                  "backup@192.168.10.10:' / backup1 / backup2' /backup3"],
            returncode=0,
            stdout='',
            stderr='')

    command = "rsync --progress --recursive --dry-run " \
              "backup@192.168.10.10:'/backup1 /backup2' /backup3"

    monkeypatch.setattr(subprocess, 'run', subprocess_response)
    result = backup.rsync(command)
    assert result == 0


def test_find_job_config() -> None:
    config = backup.ConfigListDataClass(
        [
            ConfigDataClass(
                job_name="job1",
                description="This is job1",
                remote_host="192.168.10.10",
                remote_user="backup",
                remote_paths=['/backup1', '/backup2'],
                local_path="/backup3",
                rsync_options="--progress --recursive",
            ),
            ConfigDataClass(
                job_name="job2",
                description="This is job2",
                remote_host="192.168.10.20",
                remote_user="backup",
                remote_paths=['/backup1', '/backup2'],
                local_path="/backup3",
                rsync_options="--progress --recursive",
            ),
        ]
    )

    result = backup.findJobConfig('job1', config)

    assert result == ConfigDataClass(job_name='job1',
                                     description='This is job1',
                                     remote_host='192.168.10.10',
                                     remote_user='backup',
                                     remote_paths=['/backup1', '/backup2'],
                                     local_path='/backup3',
                                     rsync_options='--progress --recursive')

    with pytest.raises(backup.ConfigJobNotFoundException):
        backup.findJobConfig('job3', config)
