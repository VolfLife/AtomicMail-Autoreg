# AtomicMail Autoreg

#### A script that automatically opens an browser window and creates a mailbox in the [AtomicMail.io](https://atomicmail.io/) service

## Features

- Supports Edge/Chrome/Brave/Firefox browsers

- Automatic form filling

- Credentials auto-saving

## Usage

1. Install [Python 3.6+](https://www.python.org/downloads/windows/) and pip

2. Install required packages:

```
pip install selenium webdriver_manager
```

3. Check the compatibility of the driver version with your browser and place it in the script directory:

	For **Microsoft Edge**:
	Check version `edge://settings/help` and download [Edge WebDriver](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/) matching your Edge version

	For **Chrome**/**Brave**:
	Check version `chrome://settings/helpDownload` and download [СhromeDriver](https://developer.chrome.com/docs/chromedriver/downloads) matching your Chrome/Brave version
	
	For **Firefox**:
	Check version and download [GeckoDriver](https://github.com/mozilla/geckodriver/releases) matching your Firefox version

4. Run the script by double clicking or in the terminal/command prompt:

```
python AutoregEdge.py
```

5. Manually solve the CAPTCHA when prompted. Script will automatically continue after solving.

6. Credentials will be saved in `autoreg_XXXX.txt` file in the script directory.
