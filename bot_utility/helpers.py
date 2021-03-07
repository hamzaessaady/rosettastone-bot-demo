"""This Modal contains helpful functions, that simplified the app's code
"""

import os.path
import time

from configparser import ConfigParser
from cryptography.fernet import Fernet
from selenium.webdriver import ChromeOptions


# browser_options()
def browser_options(profile_path=None):
  """Add options to the browser
  """
  options = ChromeOptions()
  options.add_argument('--ignore-certificate-errors')
  options.add_argument("--lang=fr")
  if profile_path!= None: options.add_argument(f'--user-data-dir={profile_path}')
  options.add_argument("--disable-extensions")
  return options


# wait_before_after()
def wait_before_after(method):
  """A decorator to wait after and before executing a method

  Arguments:
    method {function} -- Method that performe an IG task

  Returns:
    function -- The new decorated method
  """
  WAIT_TIME = 2

  def wrapper(*args, **kwargs):
    time.sleep(WAIT_TIME)
    return method(*args, **kwargs)
    time.sleep(WAIT_TIME)

  return wrapper


# init_config()
def init_config():
  """Create and/or read the config.ini file

  Returns:
    ConfigParser -- configurations in config.ini
  """
  CONFIG_PATH = './config/config.ini'
  config = ConfigParser()
  newConfig = ConfigParser()

  # create config.ini if not exists
  if not os.path.isfile(CONFIG_PATH):

    config['RS_AUTH'] = {
      'IS_ENCR': '',
      'EMAIL': 'Your-Email@email.com',
      'PASSWORD': 'Your-Password',
    }
    config['ENV'] = {
      'DRIVER_PATH': './driver/chromedriver.exe',
      'PROFILE_PATH': 'C:\\Users\\hp\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 1'
    }

    with open(CONFIG_PATH, 'w') as f:
      config.write(f)

  # asserting configuration file has the correct extension
  path = CONFIG_PATH.split('.')
  assert path[len(path)-1] == 'ini'

  # Read config.ini
  config.read(CONFIG_PATH)
  newConfig.read(CONFIG_PATH)

  # After creating config.ini [First execution]
  if config['RS_AUTH']['IS_ENCR'] == '':
    newConfig.set('RS_AUTH', 'IS_ENCR', '0')
    with open(CONFIG_PATH, 'w') as f:
      newConfig.write(f)
  # Encrypting if not encrypted [Second execution]
  elif config['RS_AUTH']['IS_ENCR'] == '0':
    plainPassword = newConfig['RS_AUTH']['PASSWORD']
    newConfig.set('RS_AUTH', 'PASSWORD', encrypt_password(plainPassword))
    newConfig.set('RS_AUTH', 'IS_ENCR', '1')
    with open(CONFIG_PATH, 'w') as f:
      newConfig.write(f)
  # Decrypting if encrypted [Other executions]
  else:
    encryptedPassword = config['RS_AUTH']['PASSWORD']
    config['RS_AUTH']['PASSWORD'] = decrypt_password(encryptedPassword)

  return config


# encrypt_password()
def encrypt_password(password):
  """Encrypting a given password by performing a symmetric encryption

  Arguments:
    password {string} -- The given password

  Returns:
    string -- The encrypted password
  """
  # Generating the key
  key = Fernet.generate_key()
  file = open('./config/key.key', 'wb')
  file.write(key)
  file.close()

  # encrypting
  f = Fernet(key)
  encryptedPassword = f.encrypt(password.encode())

  return encryptedPassword.decode("utf-8")


# decrypt_password()
def decrypt_password(password):
  """Decrypting a given password by performing a symmetric encryption

  Arguments:
    password {string} -- The given password

  Returns:
    string -- The decrypted password
  """
  # Reading key
  file = open('./config/key.key', 'rb')
  key = file.read()
  file.close()

  # decrypt
  f = Fernet(key)
  decryptedPassword = f.decrypt(password.encode())

  return decryptedPassword.decode("utf-8")
