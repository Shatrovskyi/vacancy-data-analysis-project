from dataclasses import dataclass


@dataclass
class DirtyVacancy:
    title: str
    company_name: str
    job_description: list | None
    additional_info: list | None
    salary: str


@dataclass
class CleanVacancy:
    title: str
    company_name: str
    job_description: str | None
    english_level: str
    salary: str
