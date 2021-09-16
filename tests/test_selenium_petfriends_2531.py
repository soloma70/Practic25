import pytest
from settings import valid_name, valid_email, valid_pass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

@pytest.fixture(autouse=True)
def autoriz():
   '''Фикстура загружает веб-драйвер Хром, меняет размер окна, устанавливает явные и неявные ожидания,
   страницу авторизации Pet Friends, логинится на сайте, после выполнея основного кода закрывает браузер'''

   pytest.driver = webdriver.Chrome('C:/1/chromedriver.exe')
   pytest.driver.set_window_size(1280, 720)
   pytest.driver.implicitly_wait(10)

   # Переходим на страницу авторизации
   pytest.driver.get('http://petfriends1.herokuapp.com/login')

   # Вводим email
   WebDriverWait(pytest.driver, 10).until(EC.presence_of_element_located((By.ID, 'email')))
   pytest.driver.find_element_by_id('email').send_keys(valid_email)
   # Вводим пароль
   WebDriverWait(pytest.driver, 10).until(EC.presence_of_element_located((By.ID, 'pass')))
   pytest.driver.find_element_by_id('pass').send_keys(valid_pass)
   # Нажимаем на кнопку входа в аккаунт
   pytest.driver.find_element_by_css_selector('button[type="submit"]').click()

   yield

   pytest.driver.quit()


def test_login_pass():
   '''Тест проверяет загрузку страницы "Все питомцы"'''

   # Проверка, что мы на главной странице
   assert pytest.driver.find_element_by_tag_name('h1').text == "PetFriends"

def test_show_all_pets():
   '''Тест проверяет наличие фото у питомца;
      наличие имени, возраста и породы'''

   # Получение массива данных из таблицы всех питомцев
   images_all_pets = pytest.driver.find_elements_by_css_selector('.card-deck.card-img-top')
   names_all_pets = pytest.driver.find_elements_by_css_selector('.card-deck.card-title')
   descriptions_all_pets = pytest.driver.find_elements_by_css_selector('.card-deck.card-text')

   # Внутри соответствующего масива есть имя питомца, возраст и вид
   for i in range(len(names_all_pets)):
      # Проверяем наличие атрибута src у картинки
      assert images_all_pets[i].get_attribute('src') != ''
      # Проверям элемент, который должен содержать его имя, имеет не пустой текст
      assert names_all_pets[i].text != ''
      # Проверяем, что в элементе выводится и возраст, и вид питомца
      assert descriptions_all_pets[i].text != ''
      assert ', ' in descriptions_all_pets[i]
      parts = descriptions_all_pets[i].text.split(", ")
      assert len(parts[0]) > 0
      assert len(parts[1]) > 0

def test_show_my_pets():
   '''Тест проверяет загрузку страницы "Мои питомцы";
   наличие имени, возраста и породы;
   в статистике пользователя и в таблице одинаковае количество питомцев;
   хотя бы у половины питомцев есть фото;
   в таблице нет повторяющихся питомцев и повторяющихся имен питомцев'''

   #click page my pets
   #если ширина окна < 800
   #pytest.driver.find_element_by_class_name("navbar-toggler-icon").click()
   pytest.driver.find_element_by_xpath("//a[@href='/my_pets']").click()

   # Проверяем, что мы оказались на странице пользователя My Pets
   assert pytest.driver.find_element_by_tag_name('h2').text == valid_name

   # Получение массива данных из таблицы моих питомцев
   images_my_pets = pytest.driver.find_elements_by_css_selector('div#all_my_pets table tbody tr th img')
   names_my_pets = pytest.driver.find_elements_by_css_selector('div#all_my_pets table tbody tr td:nth-of-type(1)')
   types_my_pets = pytest.driver.find_elements_by_css_selector('div#all_my_pets table tbody tr td:nth-of-type(2)')
   ages_my_pets = pytest.driver.find_elements_by_css_selector('div#all_my_pets table tbody tr td:nth-of-type(3)')

   # Получение количества питомцев из статистики пользователя
   count_my_pets = pytest.driver.find_element_by_css_selector('html body div div div').text.split('\n')
   count_my_pets_count = int((count_my_pets[1].split(' '))[1])

   count_my_pets_name = 0
   count_my_pets_img = 0
   names_my_pets_mas = []
   types_my_pets_mas = []
   ages_my_pets_mas = []
   list_my_pets = []
   unique_list_my_pets = []

   for j in range(len(names_my_pets)):
      count_my_pets_name += 1

      if images_my_pets[j].get_attribute('src') != '':
         count_my_pets_img += 1

      names_my_pets_mas += names_my_pets[j].text.split(", ")
      types_my_pets_mas += types_my_pets[j].text.split(", ")
      ages_my_pets_mas += ages_my_pets[j].text.split(", ")
      list_my_pets.append([names_my_pets[j].text, types_my_pets[j].text, ages_my_pets[j].text])

      if list_my_pets[j] not in unique_list_my_pets:
         unique_list_my_pets.append(list_my_pets[j])

      # У всех питомцев есть имя, возраст и порода
      assert names_my_pets[j].text != ''
      assert types_my_pets[j].text != ''
      assert ages_my_pets[j].text != ''

   # Присутствуют все питомцы
   assert count_my_pets_count == count_my_pets_name, 'ERROR: В статистике пользователя и в таблице разное количество питомцев'

   # Хотя бы у половины питомцев есть фото
   assert count_my_pets_count/2 <= count_my_pets_img, 'ERROR: Фото есть менее, чем у половины питомцев'

   # У всех питомцев разные имена
   assert len(names_my_pets_mas) == len(set(names_my_pets_mas)), 'ERROR: Есть повторяющиеся имена'

   # В списке нет повторяющихся питомцев
   assert len(list_my_pets) == len(unique_list_my_pets), 'ERROR: Есть повторяющиеся питомцы'

def test_exit():
   '''Тест проверяет работу кнопки "Выйти'''

   pytest.driver.find_element_by_xpath("//button[@class='btn btn-outline-secondary']").click()
   assert pytest.driver.find_element_by_xpath("//button[@class='btn btn-success']").text == 'Зарегистрироваться', 'ERROR: ошибка Log Out'

