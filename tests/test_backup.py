import pytest
import socket
import yaml
from src import backup
from src.data_classes import ConfigDataClass, ConfigListDataClass

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
    assert result == CONFIG_DATA_OBJECT


def test_read_config_key_error(mock_config_bad_file) -> None:
    with pytest.raises(KeyError):
        backup.readConfig(config_file_path='mock_file.yaml')
