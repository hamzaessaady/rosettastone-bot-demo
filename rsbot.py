import tkinter as tk
import threading
import traceback
from PIL import ImageTk, Image

from bot_utility.rosettastone_bot import RosettaStoneBot

class Application(tk.Frame):
  """Main Application/GUI class
  """

  WIDTH = 400
  HEIGHT = 500
    

  def __init__(self, master):
    """The constructor of the main window
    """
    super().__init__(master)

    # Attributes
    self.master = master
    self.rs_bot = None

    # master config
    master.title('Home')
    master.geometry(f'{self.WIDTH}x{self.HEIGHT}')

    #Threads
    self.load_bot_thread = threading.Thread(target=self.load_bot)

    # Create widgets/grid
    self.create_widgets()


  def create_widgets(self):
    """Creates the different wingets in the home window
    """
    # background
    bg = ImageTk.PhotoImage(Image.open('./assets/images/skin.png'))
    label_bg = tk.Label(self.master, image=bg)
    label_bg.image = bg
    label_bg.place(relwidth=1, relheight=1)

    # Buttons
    self.login_btn = tk.Button(
      self.master, 
      text='Log in',
      font=('Poppins',11),
      relief=tk.SOLID,
      bg='#299AE2', fg="white", bd=0.5,
      command=self.load_bot_thread.start)
    self.login_btn.place(relx=0.3, rely=0.24, relwidth=0.4, relheight=0.06)

    self.vocabulary_btn = tk.Button(
      self.master, 
      text='Vocabulary',
      font=('Poppins',15),
      relief=tk.RAISED, bd=2,
      bg='#299AE2', fg="white", highlightbackground='#299AE2',
      state=tk.DISABLED,
      command=self.vocabulary)
    self.vocabulary_btn.place(relx=0.25, rely=0.5, relwidth=0.5, relheight=0.07)

    self.multiple_choice_btn = tk.Button(
      self.master, 
      text='Multiple choice',
      font=('Poppins',15),
      relief=tk.RAISED, bd=2,
      bg='#299AE2', fg="white", highlightbackground='#299AE2',
      state=tk.DISABLED,
      command=self.multiple_choice)
    self.multiple_choice_btn.place(relx=0.25, rely=0.58, relwidth=0.5, relheight=0.07)

    
    

    # Entry
    frame_input = tk.Frame(self.master, bg='#ECC400')
    frame_input.place(relx=0.1, rely=0.35, relwidth=0.8, relheight=0.05)

    self.course_label = tk.Label(frame_input, text='Course', font=('Poppins',10), bg='#ECC400')
    self.course_label.place(relx=0, relwidth=0.2)

    self.course_val = tk.IntVar(value=0)
    self.course_entry = tk.Entry(frame_input, textvariable=self.course_val, font=('Poppins',10), bg='#ffffff')
    self.course_entry.place(relx=0.2, relwidth=0.1)

    self.lesson_label = tk.Label(frame_input, text='Lesson', font=('Poppins',10), bg='#ECC400')
    self.lesson_label.place(relx=0.3, relwidth=0.2)
    
    self.lesson_val = tk.IntVar(value=0)
    self.lesson_entry = tk.Entry(frame_input, textvariable=self.lesson_val, font=('Poppins',10), bg='#ffffff')
    self.lesson_entry.place(relx=0.5, relwidth=0.1)

    self.iterations_label = tk.Label(frame_input, text='#iter', font=('Poppins',10), bg='#ECC400')
    self.iterations_label.place(relx=0.6, relwidth=0.2)
    
    self.iterations_val = tk.IntVar(value=50)
    self.iterations_entry = tk.Entry(frame_input, textvariable=self.iterations_val, font=('Poppins',10), bg='#ffffff')
    self.iterations_entry.place(relx=0.8, relwidth=0.1)

    # self.scan_users_btn = tk.Button(
    #   self.master,
    #   text='Scan Users',
    #    font=('Boldmatte Personal Use Only',18),
    #   relief=tk.RAISED,
    #   bg='white', fg="black", bd=2,
    #   state=tk.DISABLED,
    #   command=self.scan_users_window)
    # self.scan_users_btn.place(relx=0.15, rely=0.65, relwidth=0.7, relheight=0.1)

    # global filter_icon
    # filter_icon = ImageTk.PhotoImage(Image.open('./filter.png'))
    # self.filter_btn = tk.Button(
    #   self.master, 
    #   text='  Filter',
    #   font=('Montserrat SemiBold',11),
    #   relief=tk.SOLID,
    #   bg='#121113', fg="white", bd=0.5,
    #   image=filter_icon, compound=tk.LEFT,
    #   command=self.filter_window)
    # self.filter_btn.place(relx=0.67, rely=0.9, relwidth=0.3, relheight=0.06)


  def load_bot(self):
    """Initialize the rsBot
           (This is where the rsBot singleton is first created)
    """
    # Print some text
    self.login_btn['state'] = tk.DISABLED
    self.login_btn.config(text='wait ...', disabledforeground='white')

    # Instanciating the RosettaStoneBot class
    self.userName = RosettaStoneBot.config['RS_AUTH']['EMAIL']
    password = RosettaStoneBot.config['RS_AUTH']['PASSWORD']
    self.rs_bot = RosettaStoneBot(self.userName, password)

    # Loging
    try:
      self.rs_bot.login()
    except:
      traceback.print_exc()
      self.rs_bot.notify_error()


    # printing some text
    self.login_btn.config(
      text='Logged in',
      bg='#ffffff', fg="#231F1F", disabledforeground='#231F1F')
    self.vocabulary_btn['state'] = tk.ACTIVE
    self.multiple_choice_btn['state'] = tk.ACTIVE


  def vocabulary(self):
    try:
      self.rs_bot.goto_lesson(self.course_val.get(),self.lesson_val.get())
      self.rs_bot.train_vocabulary(self.iterations_val.get())
      self.rs_bot.notify_end_operation()
    except:
      traceback.print_exc()
      self.rs_bot.notify_error()


  def multiple_choice(self):
    try:
      self.rs_bot.goto_lesson(self.course_val.get(),self.lesson_val.get())
      self.rs_bot.train_multiple_choice()
      self.rs_bot.notify_end_operation()
    except:
      traceback.print_exc()
      self.rs_bot.notify_error()


  def __del__(self):
    """Destructor
    """
    if self.rs_bot != None : self.rs_bot.driver.close()


if __name__ == '__main__':

  root = tk.Tk()
  app = Application(master=root)
  app.mainloop()
