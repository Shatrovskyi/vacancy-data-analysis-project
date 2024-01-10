import csv
import re
from urllib.parse import urljoin
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    ElementClickInterceptedException,
)
from bs4 import BeautifulSoup
from selenium.webdriver.remote.webelement import WebElement

from vacancy import Vacancy
from dataclasses import astuple, fields


BASE_URL = "https://djinni.co/"

PYTHON_VACANCY_URL = urljoin(BASE_URL, "jobs/?primary_keyword=Ruby")

options = Options()
# options.add_argument("--headless")
driver = Chrome(options=options)
driver.get(PYTHON_VACANCY_URL)


def pagination(driver: WebDriver) -> bool:
    try:
        next_page_button = driver.find_element(
            By.CSS_SELECTOR, ".page-item:last-child a"
        )
        next_page_button.click()
        return True
    except ElementClickInterceptedException:
        return False


def cleaned_job_description(data_original_text):
    soup = BeautifulSoup(data_original_text, "html.parser")
    plain_text = soup.get_text(separator=" ")
    cleaned_text = re.sub(r"\s+", " ", plain_text).strip()

    return cleaned_text


def parse_single_vacancy(vacancy_soup: WebElement) -> Vacancy:
    title = vacancy_soup.find_element(By.CLASS_NAME, "job-list-item__link").text.strip()
    company_name = vacancy_soup.find_element(By.CSS_SELECTOR, "a.mr-2").text.strip()
    job_description_text = vacancy_soup.find_element(
        By.CSS_SELECTOR, ".job-list-item__description > " "span"
    ).get_attribute("data-original-text")
    job_description = cleaned_job_description(job_description_text)
    location = vacancy_soup.find_element(By.CLASS_NAME, "location-text").text.strip()
    published = vacancy_soup.find_element(
        By.CSS_SELECTOR, "span.mr-2.nobr"
    ).get_attribute("data-original-title")

    try:
        salary = driver.find_element(
            By.CSS_SELECTOR, "span.public-salary-item"
        ).text.strip()
    except:
        salary = None

    return Vacancy(
        title=title,
        company_name=company_name,
        job_description=job_description,
        location=location,
        salary=salary,
        published=published,
    )


def get_all_vacancies_from_page(driver) -> [Vacancy]:
    vacancies = driver.find_elements(By.CLASS_NAME, "job-list-item")
    return [parse_single_vacancy(vacancy) for vacancy in vacancies]


def write_products_to_csv(cleaned_vacancies: list[Vacancy], csv_path: str) -> None:
    vacancy_fields = [field.name for field in fields(Vacancy)]

    with open(csv_path, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(vacancy_fields)
        writer.writerows([astuple(vacancy) for vacancy in cleaned_vacancies])


def get_all_vacancies() -> None:
    all_vacancies = []

    try:
        while True:
            vacancies = get_all_vacancies_from_page(driver)
            all_vacancies.extend(vacancies)

            if not pagination(driver):
                print("Done")
                break
    except Exception as e:
        print(f"Error: {e}")

    write_products_to_csv(all_vacancies, csv_path="../data/python_vacancies.csv")


if __name__ == "__main__":
    get_all_vacancies()
