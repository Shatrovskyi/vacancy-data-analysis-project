from dataclasses import dataclass


@dataclass
class Vacancy:
    title: str
    company_name: str
    job_description: str
    location: str
    salary: str
    published: str
