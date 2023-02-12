# python -m pytest -v --driver Edge --driver-path edgedriver.exe tests/test_25.py
import time

import pytest
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options as browser_options

user = "qwer@qwer.ru"
password = "qwer1234"

def wait(driver, sec):
    return WebDriverWait(driver, sec)

@pytest.fixture(scope="session")
def setup():
    browser_options = webdriver.EdgeOptions()
    driver = webdriver.Edge(options=browser_options)
    driver.get("https://petfriends.skillfactory.ru/")
    wait(driver, 2)
    driver.maximize_window()
    driver.find_element(By.XPATH, "//button[contains(text(),'Зарегистрироваться')]").click()
    driver.find_element(By.LINK_TEXT, "У меня уже есть аккаунт").click()
    wait(driver, 2)
    driver.find_element(By.ID, "email").clear()
    driver.find_element(By.ID, "email").send_keys(user)
    driver.find_element(By.ID, "pass").clear()
    driver.find_element(By.ID, "pass").send_keys(password)
    driver.find_element(By.XPATH, "//button[contains(text(),'Войти')]").click()
    assert driver.find_element(By.TAG_NAME, 'h1').text == "PetFriends"

    wait(driver, 2).until(EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/my_pets')]")))
    driver.find_element(By.XPATH, "//a[contains(@href, '/my_pets')]").click()
    driver.implicitly_wait(3)

    assert driver.find_elements(By.XPATH, "//tbody/tr") != 0
    user_info = driver.find_elements(By.XPATH, "//div[contains(@class, 'left')]")
    my_pets_list = driver.find_elements(By.XPATH, "//tbody/tr")
    time.sleep(5)
    yield user_info, my_pets_list
    driver.quit()

class TestPF:
    def test_my_pets_actual_list(self, setup):
        # Проверим, что количество питомцев в списке соответствует информации в описании профиля.
        user_info, my_pets_list = setup
        user_info_list = user_info[0].text.split("\n")
        my_pets_sum = user_info_list[1]
        my_pets_sum = int(my_pets_sum[my_pets_sum.find(":") + 1:].replace(" ", ""))
        print(f'Питомцев в инфо: {my_pets_sum},\nв таблице: {len(my_pets_list)}')
        assert my_pets_sum == len(my_pets_list)

    def test_my_pets_with_foto_and_without(self, setup):
        # Проверим, что питомцев с фото больше, чем без фото.
        _, my_pets_list = setup
        count_with_foto = 0
        count_without_photo = 0
        for item in my_pets_list:
            if item.find_element(By.XPATH, "th//img").get_attribute('src') == "":
                count_without_photo += 1
            else:
                count_with_foto += 1
        print(f"Питомцев с фото = {count_with_foto},\n без фото = {count_without_photo}")

        assert count_with_foto > count_without_photo

    def test_all_pets_with_name_breed_age(self, setup):
        # Проверим, что у не всех питомцев имеются имена/порода/возраст.
        _, my_pets_list = setup
        pet_name_breed_age = False
        for i in range(len(my_pets_list)):
            if not pet_name_breed_age:
                break
            for j in range(len(my_pets_list)):
                if my_pets_list[i].find_element(By.XPATH, "td[{}]".format(j)).text == "":
                    pet_name_breed_age = False
                    break

        assert pet_name_breed_age == False
        print("Не у всех питомцев есть имя, порода и возраст")
        """в список питомцев пользователя намерено включены примеры с пустыми полями"""


    def test_all_names_different(self, setup):
        # Проверим, что у всех питомцев разные имена.
        _, my_pets_list = setup
        all_names_different = True
        list_names = []
        for i in range(len(my_pets_list)):
            name = my_pets_list[i].find_element(By.XPATH, "td[1]").text
            if name in list_names:
                all_names_different = False
                break
            list_names.append(name)
        print("У всех питомцев разные имена")
        print(list_names)
        assert all_names_different

   
