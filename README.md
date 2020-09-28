# Rsync Backup Tool

This is a very simple tool which facilitates the automated backup of
a linux or unix source path to a local path using rsync.

## Requirements

You will require Python 3.7 to run this application. It has not been tested
with any other versions.

#### Python
* 3.7.x

#### Python YAML
```bash
pip install pyyaml
```

#### OS
* Mac OSX
* Ubuntu
* Debian
* FreeBSD

#### RSYNC
* Rsync 2.6.9

## Setup Remote Key

You can automate the login process by setting up remote key authentication.

```bash
ssh-keygen
ssh-copy-id {remote_user}@{remote_host}
```

# Usage

The application is fairly straight forward. To start you have to setup the
configuration file for the remote host you want to backup. The default filename is ```config.yml```. If you only
need one config file, use the detault naming and leave out the ```--config={config}```;

You can specify a config through cmd line using ```--config={config}```

```bash
$ ./rsync_backup.py --config=2tbconfig.yml
```

When you have setup the config for the backup process you can run the program. If you want to run a test
first to see if your config is error free, you can specify ```--dry-run```. This will not make any changes
on disk.

```bash
$ ./rsync_backup.py --dry-run
```

You can the program options displayed in CLI by using: ```-h``` or ```--help```.

```bash
$ ./rsync_backup.py --help
```

#### RSYNC Check

If the RSYNC check is causing unexpected problems or if you want to force the program to run, you can
change the config option ```check``` to ```False``` 

```yaml
rsync:
   check: False
```

#### Basic RSYNC Options
* --ignore-existing 
* --archive 
* --progress 
* --recursive 
* --delete 
* --stats 
* --human-readable 
* --copy-links 
* --ignore-errors

#### License
GNU GPLv3

# Requirements
#### REQUIREMENTS

* The program should be able to backup files from a remote network location like a NAS to a local attached drive.
* The program should use RSYNC to do the backup.
* The program should only have to require one password entry for each remote backup LOCATION.
* The program should be configurable using a config file.
* Configuration should not be stored to GIT.
* The program should write a log of the backup to file.

#### RSYNC EXAMPLE
```bash
rsync --progress --recursive --archive --delete --verbose --stats --human-readable --copy-links jack@192.168.1.22:'/share/test2 /share/test1' /Users/gideon/Desktop/rsync/dst_drive
```

#### INFORMATION
* https://download.samba.org/pub/rsync/rsync.html
* https://unix.stackexchange.com/questions/368210/how-to-rsync-multiple-source-folders
