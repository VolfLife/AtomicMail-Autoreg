import os
import glob
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
import time

def find_account_files():
    """Находит все файлы autoreg_*.txt в текущей директории"""
    return glob.glob('autoreg_*.txt')

def parse_account_file(file_path):
    """Извлекает логин и пароль из файла"""
    with open(file_path, 'r') as file:
        content = file.read()
        # Ищем строку с логином (без @atomicmail.io)
        login_line = next(line for line in content.split('\n') if line.startswith('login:'))
        login = login_line.split(':')[1].strip().replace('@atomicmail.io', '')
        # Ищем строку с паролем
        password_line = next(line for line in content.split('\n') if line.startswith('password:'))
        password = password_line.split(':')[1].strip()
        return login, password

def login_account(driver, email, password):
    try:
        driver.get("https://atomicmail.io/app/auth/sign-in")
        
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
                
        # Проверка на ошибку "Incorrect password or username"
        try:
            error_message = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'p._errorMessage_so3dh_74')))
            if error_message.text == "Incorrect password or username":
                print(f"Ошибка авторизации: неверный логин или пароль для {email} / Authorization error: incorrect login or password for {email}")
                return False
        except:
            pass  # Элемент с ошибкой не найден — значит, авторизация успешна
        
        print(f"\nАвторизация успешна для {email}@atomicmail.io / Authorization successful for {email}@atomicmail.io")
        return True
        
    except Exception as e:
        print(f"Ошибка при авторизации / Error during authorization: {str(e)}")
        return False
        
def delete_account(driver, password):
    try:
        print("\nНачинаем процесс удаления аккаунта... / Let's start the account deletion process...")
        
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
        print(f"Ошибка при удалении аккаунта / Error deleting account: {str(e)}")
        return False

def main():
    # Настройки для Edge
    edge_options = Options()
    edge_options.add_argument("--start-maximized")
    edge_options.add_experimental_option("detach", True)  # Чтобы браузер не закрывался

    # Находим все файлы с аккаунтами
    account_files = find_account_files()
    
    if not account_files:
        print("Не найдено файлов с аккаунтами для удаления / No account files found to delete")
        input("\nНажмите Enter чтобы закрыть программу... / Press Enter to close the program...")
        return

    try:
        for file_path in account_files:
        
            try:
        
                # Извлекаем данные из файла
                email, password = parse_account_file(file_path)
                print(f"\nОбрабатываем аккаунт / Processing the account: {email}")

                # Инициализация драйвера
                driver = webdriver.Edge(
                    service=Service("msedgedriver.exe"),
                    options=edge_options
                )

                # Логинимся
                if not login_account(driver, email, password):
                    print(f"Не удалось войти в аккаунт {email} / Failed to log into your account {email}")
                    os.remove(file_path)
                    print(f"Файл {file_path} удален / File {file_path} has been deleted")
                    driver.quit()
                    continue

                # Удаляем аккаунт
                if delete_account(driver, password):
                    print(f"Аккаунт {email} успешно удален / Account {email} successfully deleted")
                    # Удаляем файл после успешного удаления
                    os.remove(file_path)
                    print(f"Файл {file_path} удален / File {file_path} has been deleted")
                else:
                    print(f"Не удалось удалить аккаунт {email} / Failed to delete account {email}")
                    os.remove(file_path)
                    print(f"Файл {file_path} удален / File {file_path} has been deleted")

                # Закрываем браузер
                driver.quit()
                time.sleep(2)  # Пауза между обработкой аккаунтов

            except Exception as e:
                print(f"Ошибка при обработке файла {file_path} / Error processing file {file_path}: {str(e)}")
                if 'driver' in locals():
                    driver.quit()

        # Когда файлы закончились
        input("\nНажмите Enter чтобы закрыть программу... / Press Enter to close the program...")
        
    except KeyboardInterrupt:
        print("\nПрограмма прервана пользователем / Program interrupted by user")
        if driver is not None:
            driver.quit()        

if __name__ == "__main__":
    main()