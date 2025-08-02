import os
import glob
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

def find_account_files():
    """Находит все файлы autoreg_*.txt в текущей директории"""
    return glob.glob('autoreg_*.txt')

def parse_account_file(file_path):
    """Извлекает логин и пароль из файла"""
    with open(file_path, 'r') as file:
        content = file.read()
        login_line = next(line for line in content.split('\n') if line.startswith('login:'))
        login = login_line.split(':')[1].strip().replace('@atomicmail.io', '')
        password_line = next(line for line in content.split('\n') if line.startswith('password:'))
        password = password_line.split(':')[1].strip()
        return login, password

def get_accounts_list(account_files):
    """Возвращает список email-адресов из файлов аккаунтов"""
    accounts = []
    for file_path in account_files:
        try:
            login, _ = parse_account_file(file_path)
            accounts.append(f"{login}@atomicmail.io")
        except Exception as e:
            print(f"Ошибка при чтении файла {file_path}: {str(e)}")
            accounts.append(f"Ошибка в файле: {file_path}")
    return accounts

def login_account(driver, email, password):
    try:
        driver.get("https://atomicmail.io/app/auth/sign-in")
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        ).send_keys(email)
        driver.find_element(By.XPATH, '//button[contains(., "Submit")]').click()
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "password"))
        ).send_keys(password)
        driver.find_element(By.XPATH, '//button[contains(., "Sign In")]').click()
                
        try:
            error_message = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'p._errorMessage_so3dh_74')))
            if error_message.text == "Incorrect password or username":
                print(f"Ошибка авторизации: неверный логин или пароль для {email}")
                return False
        except:
            pass
        
        print(f"\nАвторизация успешна для {email}@atomicmail.io")
        return True
        
    except Exception as e:
        print(f"Ошибка при авторизации: {str(e)}")
        return False

def logout_account(driver):
    try:
        print("\nВыход из аккаунта...")
        
        # 1. Нажимаем на аватар
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'div._avatar_1r8j4_1'))
        ).click()
        
        # 2. Нажимаем на Logout в выпадающем меню
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//li[@class="_option_qpn4s_60"]//span[contains(text(), "Logout")]'))
        ).click()
        
        print("Успешно вышли из аккаунта")
        return True
        
    except Exception as e:
        print(f"Ошибка при выходе из аккаунта: {str(e)}")
        return False

def delete_account(driver, password):
    try:
        print("\nНачинаем процесс удаления аккаунта...")
        
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'div._avatar_1r8j4_1'))
        ).click()
        
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//li[@class="_option_qpn4s_60"]//span[contains(text(), "Settings")]'))
        ).click()
        
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button._backgroundWhite_100ok_68._borderRed_100ok_116'))
        ).click()
        
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button._backgroundRed_100ok_80'))
        ).click()
        
        password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="password"]'))
        )
        password_field.send_keys(password)
        
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Verify")]'))
        ).click()
        
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Delete my account")]'))
        ).click()
        
        return True
        
    except Exception as e:
        print(f"Ошибка при удалении аккаунта: {str(e)}")
        return False

def select_account(account_files):
    accounts = get_accounts_list(account_files)
    print("\nДоступные аккаунты:")
    for i, email in enumerate(accounts, 1):
        print(f"{i}. {email}")
    
    while True:
        try:
            choice = int(input("\nВыберите аккаунт (номер): "))
            if 1 <= choice <= len(account_files):
                return account_files[choice-1]
            else:
                print("Неверный номер, попробуйте еще раз")
        except ValueError:
            print("Введите число")

def account_action_menu(driver, password, file_path):
    while True:
        print("\nВыберите действие:")
        print("1. Удалить аккаунт")
        print("2. Выйти из аккаунта")
        
        try:
            choice = int(input("Ваш выбор (1-2): "))
            if choice == 1:
                if delete_account(driver, password):
                    os.remove(file_path)
                    print(f"Аккаунт удален, файл {file_path} удален")
                    return True  # Аккаунт удален, нужно выбрать новый
                else:
                    continue
            elif choice == 2:
                if logout_account(driver):
                    return False  # Аккаунт не удален, можно выбрать новый
                else:
                    continue
            else:
                print("Неверный выбор, попробуйте еще раз")
        except ValueError:
            print("Введите число от 1 до 2")

def main():
    # Настройка для Brave
    brave_path = "C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"  # Проверь путь к Brave!

    chrome_options = Options()
    chrome_options.binary_location = brave_path  # Указываем путь к Brave
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_experimental_option("detach", True)

    account_files = find_account_files()
    
    if not account_files:
        print("Не найдено файлов с аккаунтами")
        return

    driver = None
    
    try:
        while True:
            file_path = select_account(account_files)
            email, password = parse_account_file(file_path)
            print(f"\nОбрабатываем аккаунт: {email}@atomicmail.io")

            if driver is None:
                service = Service(executable_path="chromedriver.exe")
                driver = webdriver.Chrome(
                    service=service,
                    options=chrome_options
                )

            if login_account(driver, email, password):
                account_deleted = account_action_menu(driver, password, file_path)
                if account_deleted:
                    account_files = find_account_files()  # Обновляем список файлов
                    if not account_files:
                        print("Больше нет аккаунтов для обработки")
                        break
            else:
                print(f"Не удалось войти в аккаунт {email}@atomicmail.io")
                os.remove(file_path)
                print(f"Файл {file_path} удален")
                account_files = find_account_files()  # Обновляем список файлов
                if not account_files:
                    print("Больше нет аккаунтов для обработки")
                    break

    finally:
        if driver is not None:
            driver.quit()

if __name__ == "__main__":
    main()