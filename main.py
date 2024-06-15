import api
import gui
import models

if __name__ == "__main__":
    print("Enter username:")
    api.current_user = input()
    gui.gui_loop()