"""RosettaStoneBot class
"""

import random
import string
import time
from numpy import arange
from winsound import PlaySound, SND_FILENAME

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException

from .helpers import init_config, browser_options, wait_before_after
from .selectors import Selectors

class RosettaStoneBot:

  # Constants
  RS_URL = 'https://login.rosettastone.com/'

  # Class variables
  __instance = None
  config = init_config()

  @staticmethod
  def getInstance():
    """ Static access method. """
    if RosettaStoneBot.__instance == None:
      raise Exception("This class has no instance yet!")
    return RosettaStoneBot.__instance 


  # Constructor
  def __init__(self, email, password):
    """Creates an instance of RosettaStoneBot class.

    Arguments:
      email {string} -- The email given in config.ini
      password {string} -- The password given in config.ini
    """
    if RosettaStoneBot.__instance != None:
      raise Exception("This class is a singleton!")
    else:
      self.email = email
      self.password = password
      driver_path = self.config['ENV']['DRIVER_PATH']
      options = browser_options()
      self.driver = webdriver.Chrome(driver_path, chrome_options=options)
      # self.driver = webdriver.Chrome(driver_path)
      RosettaStoneBot.__instance = self
        

  # Login
  @wait_before_after
  def login(self):
    """Logs a user into RosettaStone via the web portal
    """
    self.driver.get(self.RS_URL)
    self.driver.execute_script('document.__proto__.hasFocus = function() {return true};')

    # log in
    self.find_elements('email')[0].send_keys(self.email)
    self.find_elements('password')[0].send_keys(self.password)
    self.find_elements('login_btn')[0].click()

  
  @wait_before_after
  def train_vocabulary(self, iterations):

    for i in range(iterations):
      # Go to Vocabulary activity
      self.find_elements('vocabulary_btn')[0].click()

      # Click forward
      while(True):
        try:
          WebDriverWait(self.driver,3).until(
            EC.presence_of_element_located(
              (By.XPATH, Selectors['next_activity_btn']['pointer'])))
          break
        except TimeoutException as err:
          time.sleep(2)
          self.find_elements('forward_btn')[0].click()
          
      
      # Go to next activity
      self.find_elements('next_activity_btn')[0].click()
  

  @wait_before_after
  def train_multiple_choice(self):

    answers = []
    failed_activities_indexes = set()
    multiple_choice_activities =  self.find_elements('multiple_choice_btn')

    # For each activity
    for index, multiple_choice_activity in enumerate(multiple_choice_activities):

      try:
        multiple_choice_activity.click()
      except ElementClickInterceptedException as err:
          pass

      WebDriverWait(self.driver,60).until(
        EC.presence_of_element_located(
          (By.XPATH, Selectors['step_content']['pointer'])))

      # Check speaking
      if len(self.find_elements('speech_btn')) != 0:
        answers.append([])
        continue

      is_steps_finished = False
      activity_answers = []

      # For each step
      while(not is_steps_finished):

        choice_elements = self.find_elements('choice_span')
        choices = [i for i in range(len(choice_elements))]
        correct_multi_choices = set()

        for i in range(3):

          # Check multi-answer
          if len(self.find_elements('radio_btn')) != 0:
            is_multi = False
            random_choice = random.choice(choices)
            choice_elm = choice_elements[random_choice]
            choice_elm.click()
            time.sleep(3)
          else:
            is_multi = True
            if len(correct_multi_choices) == 0:
              for choice in choice_elements:
                choice.click()
                time.sleep(3)
            else:
              for choice in choice_elements:
                if choice.text in correct_multi_choices:
                  choice.click()
                  time.sleep(3)
   
          self.find_elements('check_answer_btn')[0].click()

          try_again_elements = self.find_elements('try_again_btn')
          show_answer_elements = self.find_elements('show_answer_btn')
          next_activity_elements = self.find_elements('next_activity_btn')

          if len(try_again_elements) != 0:
            if (is_multi):
              correct_choices = self.find_elements('correct_choice_span')
              for correct_choice in correct_choices:
                correct_multi_choices.add(correct_choice.text)
              activity_answers.append(correct_multi_choices)
            else:
              choices.remove(random_choice)
            try_again_elements[0].click()
          elif len(show_answer_elements) != 0:
            show_answer_elements[0].click()
            activity_answers.append(self.find_elements('correct_choice_span')[0].text)
            failed_activities_indexes.add(index)
            next_activity_elements_2 = self.find_elements('next_activity_btn')
            if len(next_activity_elements_2) == 0:
              self.find_elements('submit_btn')[0].click()
            else:
              is_steps_finished = True
              next_activity_elements_2[0].click()
            break
          elif len(next_activity_elements) != 0:
            if(not is_multi):
              activity_answers.append(choice_elm.text)
            next_activity_elements[0].click()
            is_steps_finished = True
            break
          else:
            if(not is_multi):
              activity_answers.append(choice_elm.text)
            self.find_elements('submit_btn')[0].click()
            break
      
      answers.append(activity_answers)
    
    # Answering the failed questions
    for j in failed_activities_indexes:
      try:
        multiple_choice_activities[j].click()
      except ElementClickInterceptedException as err:
          pass

      WebDriverWait(self.driver,60).until(
        EC.presence_of_element_located(
          (By.XPATH, Selectors['step_content']['pointer'])))

      is_steps_finished = False
      step = 0

      # For each step
      while(not is_steps_finished):
        choice_elements = self.find_elements('choice_span')
        for choice_element in choice_elements:
          if choice_element.text in answers[j][step]:
            choice_element.click()
            time.sleep(3)
        self.find_elements('check_answer_btn')[0].click()
        next_activity_elements = self.find_elements('next_activity_btn')
        if len(next_activity_elements) == 0:
          self.find_elements('submit_btn')[0].click()
        else:
          is_steps_finished = True
          next_activity_elements[0].click()
        step += 1
  
  
  @wait_before_after
  def goto_lesson(self, course, lesson):
    """Go to lesson dashboard
    """
    # Explicit wait
    WebDriverWait(self.driver,120).until(
      EC.presence_of_element_located(
        (By.XPATH, Selectors['my_goals_span']['pointer'])))
    # Click Launchpad
    self.find_elements('launchpad')[0].click()
    # Explicit wait
    WebDriverWait(self.driver,120).until(
      EC.presence_of_element_located(
        (By.XPATH, Selectors['my_courses']['pointer'])))
    # Choose Course
    self.find_elements('course_launch_btn')[course].click()
    # Explicit wait
    WebDriverWait(self.driver,120).until(
      EC.presence_of_element_located(
        (By.XPATH, Selectors['my_courses_txt']['pointer'])))
    # Choose Lesson
    self.find_elements('lesson_launch_btn')[lesson].click()
    # Explicit wait
    WebDriverWait(self.driver,120).until(
      EC.presence_of_element_located(
        (By.XPATH, Selectors['activity_map_list']['pointer'])))


  def notify_end_operation(self):
    PlaySound('./assets/sounds/finish_beep', SND_FILENAME)


  def notify_error(self):
    PlaySound('./assets/sounds/error_beep', SND_FILENAME)

  # find_elements
  @wait_before_after
  def find_elements(self, field):
    """Find the element correspoding to a field inside the IG page

    Arguments:
      field {string} -- field name (correspond to the keys in Selectors)

    Returns:
      list -- The corresponding elements
    """
    elements = []
    if field in Selectors:
      pointer = Selectors[field]['pointer']
      if Selectors[field]['type'] == 'name':
        elements = self.driver.find_elements_by_name(pointer)
      elif Selectors[field]['type'] == 'xpath':
        elements = self.driver.find_elements_by_xpath(pointer)
      elif Selectors[field]['type'] == 'css':
        elements = self.driver.find_elements_by_css_selector(pointer)
        
    return elements