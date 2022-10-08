# Rsync Backup Automation

This is a small abstraction on the RSYNC command found on Unix or Linux
to automate some repetitive things you have to do when creating complex backups
between two Unix or Linux systems with encryption.

This method of backup is often referred to as a one way sync backup.

There may be other tools out there that can do this better, but I needed
something more basic and specific to my needs. It was also fun to create.

**This script is ideally suited for the following situations:**
- Backup of a remote NAS to local storage. Like off site backups.
- Automation of sync backup from a remote system with Rsync and SSH access 
to local storage.

## Requirements

- Python 3.10.x
- Rsync version 2.6.9 protocol version 29

## Getting Started

### Clone the repo to where you are going to use it

Note: Versioned releases will be available soon:

```commandline
git clone git@github.com:mortolian/rsync-remote-backup.git
```
or
```commandline
git clone https://github.com/mortolian/rsync-remote-backup.git
```

### Get setup

There is a Makefile included in the root of the project with everything you 
need to get started. It is recommended that you run the script in the VENV,
but you can also run it outside a VENV if you install all the requirements
globally.

Setup VENV

```commandline
make venv-setup
. ./venv/bin/activate
make build
make setup
```

Setup with global dependencies

```commandline
python3 -m build
pip3 install -e .
```

### Set up your first config file from the example config provided

You have to set up what you need to be synced. This happens in the
`config.yaml` file. This is the default config if you don't specify
a custom one. You can have many config files for different automations.

The config begins with a job name `offsite_1`, which you specify when you run
the `backup.py` script using the `-j` attribute.

From there you provide a description of the job to remember what it's for etc.

The `remote` section of the YAML file provides all the details the script needs
for the remote host. The paths will be compiled into one command to run the
RSYNC command only once. Notice that these are full path names and does not
have a tailing slash.

The `local` section only has a path to set at this time. This is where all
your synced files will end up. Notice that this is a full path and no tailing
slash.

The `rsync` section allows you to set some custom RSYNC attributes if you 
would like to have some control over how it is run.

You can read the RSYNC documentation for more information on the various attributes.
https://download.samba.org/pub/rsync/rsync.1#OPTION_SUMMARY

```yaml
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
```

### Running the script

From the root of the project folder run the following to get the help
printout of how to use the script.

```commandline
python ./src/backup.py --help
```
```commandline
usage: Backup Remote Files. [-h] [-j JOB] [-s] [-c CONFIG] [-d]

options:
  -h, --help            show this help message and exit
  -j JOB, --job JOB     Specifies what config job to run.
  -s, --show-available-jobs
                        Shows a list of jobs available in the config.
  -c CONFIG, --config CONFIG
                        Specify a config file if you do not want to use the default config file (config.yaml).
  -d, --dry-run         Will run the rsync without making any changes to the source or destination.
```

### Run A Job

When you are setup you can run the job with the following command.

```commandline
python ./src/backup.py -j offsite_1
```
or, if not inside VENV
```commandline
python3 ./src/backup.py -j offsite_1
```

You can also simulate the job with a "dry run", to make sure everything
works the way you intended. Add `--dry-run` to the command for this option.

### The password

The password will only be asked once, because the sources that will be
synced are compiled into one command.

You can also set up an SSH key authentication between the remote machine
and where you are going to run the RSYNC automation script. This will 
remove the password prompt, and you can then also schedule the command with
no intervention required.

There are many tutorials available on the internet to get this setup and 
here is some basic commands to get you started.

```bash
ssh-keygen
ssh-copy-id {remote_user}@{remote_host}
```

## Reference Websites For This Project

- https://setuptools.pypa.io/en/latest/userguide/dependency_management.html
- https://github.com/jazzband/pip-tools
- https://alexo.dev/blog/avoiding-pip-freeze-2/
- https://towardsdatascience.com/stop-using-pip-freeze-for-your-python-projects-9c37181730f9
- https://docs.python.org/3/distutils/configfile.html
- https://download.samba.org/pub/rsync/rsync.html
- https://unix.stackexchange.com/questions/368210/how-to-rsync-multiple-source-folders

## Future Updates And Additions

- The program should write a log of the backup to file.
