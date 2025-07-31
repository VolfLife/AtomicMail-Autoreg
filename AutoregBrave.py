from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import random
import string
import time

# Генерация случайных данных
def random_name(length=6):
    return ''.join(random.choice(string.ascii_letters) for _ in range(length)).capitalize()

def random_password(length=12):
    """Генерирует сложный пароль с минимум 1 цифрой и 1 спецсимволом"""
    chars = string.ascii_letters
    digits = string.digits
    symbols = "!@#$%^&*_+-="
    
    # Гарантируем хотя бы 1 цифру и 1 символ
    password = [
        random.choice(digits),
        random.choice(symbols),
        *[random.choice(chars + digits + symbols) for _ in range(length-2)]
    ]
    
    random.shuffle(password)
    return ''.join(password)


# Настройка для Brave
brave_path = "C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"  # Проверь путь к Brave!

chrome_options = Options()
chrome_options.binary_location = brave_path  # Указываем путь к Brave
chrome_options.add_argument("--start-maximized")
chrome_options.add_experimental_option("detach", True)

# Инициализация драйвера (правильный способ для Selenium 4+)
service = Service(executable_path="chromedriver.exe")
driver = webdriver.Chrome(
    service=service,
    options=chrome_options
)


try:

    driver.get("https://atomicmail.io/app/auth/sign-up")
    # 1. Заполнение имени и фамилии
    first_name = driver.find_element(By.CSS_SELECTOR, 'input[name="firstName"]')
    last_name = driver.find_element(By.CSS_SELECTOR, 'input[name="lastName"]')
    first_name.send_keys(random_name())
    last_name.send_keys(random_name())

    # 2. Нажатие кнопки Submit
    submit_btn = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
    submit_btn.click()

    # 3. Заполнение почты
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="username"]'))
    )
    username = driver.find_element(By.CSS_SELECTOR, 'input[name="username"]')
    email = f"{random_name().lower()}.{random_name().lower()}"
    username.send_keys(email)

    # 4. Нажатие кнопки Submit
    submit_btn = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
    submit_btn.click()

    # 5. Заполнение пароля
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="password"]'))
    )
    password = random_password()
    driver.find_element(By.CSS_SELECTOR, 'input[name="password"]').send_keys(password)
    driver.find_element(By.CSS_SELECTOR, 'input[name="confirmPassword"]').send_keys(password)

    # 6. Нажатие кнопки Download & Proceed
    submit_btn = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
    submit_btn.click()


    # Улучшенное нажатие кнопки Download & Proceed
    def click_download_proceed():
        try:
            # Ищем кнопку по комбинации атрибутов
            button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, 
                    '//button[@type="submit" and contains(., "Download & Proceed")]'))
            )
            # Прокручиваем к кнопке и кликаем
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
            time.sleep(1)  # Небольшая пауза для стабилизации
            button.click()
            return True
        except Exception as e:
            print(f"Ошибка при нажатии кнопки: {str(e)}")
            return False

    # Пытаемся нажать кнопку несколько раз
    for attempt in range(3):
        if click_download_proceed():
            break
        time.sleep(2)

    # Ожидание капчи (максимум 60 секунд)
    print("Ожидаем капчу / Waiting for captcha...")
    start_time = time.time()
    while time.time() - start_time < 60:
        try:
            # Проверяем, появилась ли кнопка "Sign in now!"
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, 
                    '//button[contains(., "Sign in now!")]'))
            )
            print("Капча пройдена / Captcha passed!")
            break
        except:
            time.sleep(1)
            continue
    else:
        print("Не удалось дождаться прохождения капчи за 60 секунд \nFailed to wait for the captcha to be solved in 60 seconds")

    # 8. Нажатие кнопки Sign in now
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'button._submit_w8uxz_61'))
    ).click()

    # 9. Сохранение данных в файл
    filename = f"autoreg_{random.randint(1000, 9999)}.txt"
    with open(filename, "w") as file:
        file.write(f"login: {email}@atomicmail.io\npassword: {password}\n{email}:{password}")
    print(f"Данные сохранены в {filename}")

    # Авторизация в новом окне
    #driver.execute_script("window.open('');")
    #driver.switch_to.window(driver.window_handles[1])
    #driver.get("https://atomicmail.io/app/auth/sign-in")
    
    # Заполнение логина
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "username"))
    ).send_keys(email)
    driver.find_element(By.XPATH, '//button[contains(., "Submit")]').click()
    
    # Заполнение пароля
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "password"))
    ).send_keys(password)
    driver.find_element(By.XPATH, '//button[contains(., "Sign In")]').click()
    
    print("\n \nАвторизация успешна! Браузер остается открытым. / \nAuthorization successful! Browser remains open.")
    print(f"|======================== \nLogin: {email}@atomicmail.io \n| \nPassword: {password} \n| \n{email}@atomicmail.io:{password} \n|========================")


    input("\n \nНажмите Enter чтобы закрыть браузер... \nPress Enter to close the browser...")
    driver.quit()

except Exception as e:
    print(f"Ошибка: {str(e)}")
    # Даже при ошибке оставляем браузер открытым
    input("Нажмите Enter чтобы закрыть браузер...")
    driver.quit()

