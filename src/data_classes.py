from dataclasses import dataclass


@dataclass
class ConfigDataClass:
    job_name: str
    description: str
    remote_host: str
    remote_user: str
    remote_paths: list
    local_path: str
    rsync_options: str


@dataclass
class ConfigListDataClass:
    jobs: list[ConfigDataClass]
