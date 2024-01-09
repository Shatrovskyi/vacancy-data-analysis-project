import csv
import re
from urllib.parse import urljoin
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
)
from bs4 import BeautifulSoup
from vacancy import DirtyVacancy, CleanVacancy
from dataclasses import astuple, fields


BASE_URL = "https://djinni.co/"

PYTHON_VACANCY_URL = urljoin(BASE_URL, "jobs/?primary_keyword=Python")

options = Options()
options.add_argument("--headless")
driver = Chrome(options=options)
driver.get(PYTHON_VACANCY_URL)


def get_vacancy_hrefs_by_page(driver: WebDriver) -> list:
    soup = BeautifulSoup(driver.page_source, "html.parser")
    elements = soup.select(".job-list-item__title a")

    return [urljoin(BASE_URL, element["href"]) for element in elements]


def pagination(driver: WebDriver) -> bool:
    try:
        next_page_button = driver.find_element(
            By.CSS_SELECTOR, ".page-item:last-child a"
        )
        next_page_button.click()
        return True
    except ElementClickInterceptedException:
        return False


def get_full_vacancy_hrefs() -> list:
    all_job_urls = []

    while True:
        job_urls = get_vacancy_hrefs_by_page(driver)
        all_job_urls.extend(job_urls)

        if not pagination(driver):
            print("Done")
            break

    return all_job_urls


def find_element(driver, by, selector):
    try:
        element = driver.find_element(by, selector)
        return element
    except NoSuchElementException:
        return None


def clean_dirty_vacancy(dirty_vacancy: DirtyVacancy) -> CleanVacancy:
    title = dirty_vacancy.title
    company_name = dirty_vacancy.company_name
    job_description = "".join(dirty_vacancy.job_description)

    #
    info_pattern = re.compile(r"Англійська: (\w+)", re.DOTALL)
    info_match = re.search(info_pattern, dirty_vacancy.additional_info)
    english_level = info_match.group(1) if info_match else None

    salary = dirty_vacancy.salary

    return CleanVacancy(title, company_name, job_description, english_level, salary)


def parse_whole_vacancy_info(vacancy_link: str) -> DirtyVacancy:
    driver.get(vacancy_link)

    title_element = find_element(driver, By.CSS_SELECTOR, ".detail--title-wrapper h1")
    title = title_element.text.strip() if title_element else None

    company_name_element = find_element(driver, By.CSS_SELECTOR, ".job-details--title")
    company_name = company_name_element.text.strip() if company_name_element else None

    job_description_elements = find_element(driver, By.CSS_SELECTOR, ".mb-4")
    job_description = (
        job_description_elements.text.strip() if job_description_elements else None
    )

    additional_info_elements = find_element(
        driver, By.CSS_SELECTOR, ".job-additional-info--body"
    )
    additional_info = (
        " ".join(
            [
                element.text.strip()
                for element in additional_info_elements.find_elements(By.XPATH, ".//li")
            ]
        )
        if additional_info_elements
        else None
    )

    salary_element = find_element(driver, By.CSS_SELECTOR, ".public-salary-item")
    salary = salary_element.text.strip() if salary_element else None

    return DirtyVacancy(
        title=title,
        company_name=company_name,
        job_description=job_description,
        additional_info=additional_info,
        salary=salary,
    )


def get_all_cleaned_vacancies():
    vacancy_links = get_full_vacancy_hrefs()
    cleaned_vacancies = []
    for vacancy_link in vacancy_links:
        vacancy_info = parse_whole_vacancy_info(vacancy_link)
        clean_dirty_vacancy_info = clean_dirty_vacancy(vacancy_info)
        cleaned_vacancies.append(clean_dirty_vacancy_info)

    return cleaned_vacancies


def write_products_to_csv(cleaned_vacancies: list[CleanVacancy], csv_path: str) -> None:
    vacancy_fields = [field.name for field in fields(CleanVacancy)]

    with open(csv_path, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(vacancy_fields)
        writer.writerows([astuple(vacancy) for vacancy in cleaned_vacancies])


def main():
    cleaned_vacancies = get_all_cleaned_vacancies()
    write_products_to_csv(cleaned_vacancies, csv_path="../data/python_vacancies.csv")
    print("Done")


if __name__ == "__main__":
    main()
