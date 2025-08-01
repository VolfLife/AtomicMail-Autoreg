from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import random
import msvcrt
import string
import time
import winreg
import os

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


def find_chrome_path():
    try:
        # Проверка реестра
        reg_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe"
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
            path = winreg.QueryValue(key, None)
            if os.path.exists(path):
                return path
    except:
        pass

    # Проверка стандартных путей
    common_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe")
    ]
    
    for path in common_paths:
        if os.path.exists(path):
            return path

    return None
    
def main():
    chrome_options = Options()

    chrome_path = find_chrome_path()

    if chrome_path:
        chrome_options.binary_location = chrome_path
        print(f"Используется Chrome по пути / Chrome is used along the way: {chrome_path}")
    else:
        print("Chrome не найден в стандартных расположениях / Chrome was not found in standard locations")
        chrome_path = input("Введите полный путь к chrome.exe / Enter the full path to chrome.exe: ")
        if os.path.exists(chrome_path):
            chrome_options.binary_location = chrome_path
        else:
            raise FileNotFoundError("Указанный путь к Chrome не существует / The indicated path to Chrome does not exist")

    chrome_options.add_argument("--start-maximized")
    chrome_options.add_experimental_option("detach", True)


    while True:

        # Инициализация драйвера (правильный способ для Selenium 4+)
        service = Service(executable_path="chromedriver.exe")
        driver = webdriver.Chrome(
            service=service,
            options=chrome_options
        )

        success, email, password = register_account(driver)
    
        if success:
            timeout = 15  # Время ожидания в секундах
            print(f"\nСоздать еще один аккаунт? / Create another account? (y/n) [Автоматический выбор 'y' через {timeout} сек.]: ", end='', flush=True)
            
            start_time = time.time()
            choice = None
            
            while (time.time() - start_time) < timeout:
                remaining = int(timeout - (time.time() - start_time))
                print(f"\rОсталось: {remaining} сек. / Time left: {remaining} sec.", end='', flush=True)
                
                if msvcrt.kbhit():  # Если была нажата клавиша
                    char = msvcrt.getch().decode('utf-8').lower()
                    if char == 'y':
                        choice = char
                        break
                    else:
                        choice = "close"
                        break
                time.sleep(0.1)  # Небольшая задержка, чтобы не нагружать CPU
            
            if choice is None:
                print("\n\nВремя вышло, продолжаем... / Time's up, continuing...")
                choice = 'y'
            else:
                print("\n")  # Переход на новую строку после ввода
            
            if choice == 'y':
                driver.quit()
                continue
            else:
                delete_choice = input("Удалить созданный аккаунт? / Delete the created account? (y/n): ").lower()
                if delete_choice == 'y':
                    if delete_account(driver, password):
                        print("Аккаунт был успешно удален / The account was successfully deleted")
                    else:
                        print("Не удалось удалить аккаунт / Failed to remove the account")                
                choice = input("\nСоздать еще один аккаунт? / Create another account? (y/n): ").lower()
                if choice == 'y':
                    driver.quit()
                    continue
                else:
                    input("\nНажмите Enter чтобы закрыть браузер... / Click Enter to close the browser ...")
                    driver.quit()
                    break
        else:
            input("\nНажмите Enter чтобы закрыть браузер... / Click Enter to close the browser ...")
            driver.quit()
            break


def register_account(driver):
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
                print(f"Ошибка при нажатии кнопки / A mistake click: {str(e)}")
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
        random_id = ''.join(random.choices(string.ascii_letters + string.digits, k=9))
        filename = f"autoreg_{email}.txt"
        with open(filename, "w") as file:
            file.write(f"login: {email}@atomicmail.io\npassword: {password}\n{email}@atomicmail.io:{password}")
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

        return True, email, password

    except Exception as e:
        print(f"Ошибка: {str(e)}")
        # Даже при ошибке оставляем браузер открытым
        input("Нажмите Enter чтобы закрыть браузер... / Click Enter to close the browser...")
        driver.quit()

def delete_account(driver, password):
    try:
        print("\nНачинаем процесс удаления аккаунта... / We begin the process of removing the account...")
        
        # 1. Нажимаем на аватар
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'div._avatar_1r8j4_1'))
        ).click()
        
        # 2. Нажимаем на Settings в выпадающем меню
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//li[@class="_option_qpn4s_60"]//span[contains(text(), "Settings")]'))
        ).click()
        
        # 3. Нажимаем кнопку Delete (красная)
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button._backgroundWhite_100ok_68._borderRed_100ok_116'))
        ).click()
        
        # 4. Нажимаем вторую кнопку Delete (красная с белым текстом)
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button._backgroundRed_100ok_80'))
        ).click()
        
        # 5. Вводим пароль
        password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="password"]'))
        )
        password_field.send_keys(password)
        
        # 6. Нажимаем Verify
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Verify")]'))
        ).click()
        
        # 7. Нажимаем окончательную кнопку Delete my account
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Delete my account")]'))
        ).click()
        
        return True
        
    except Exception as e:
        print(f"Ошибка при удалении аккаунта / An error when deleting an account: {str(e)}")
        return False
        
        
if __name__ == "__main__":
    main()        
