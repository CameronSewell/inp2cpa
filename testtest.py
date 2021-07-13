def add(a,b):
  return a+b

def test_add():
  assert add(2,3) == 5
  assert add('space', 'ship') == 'spaceship'
  
# pyautogui tests
import pyautogui

screenWidth,screenHeight = pyautogui.size()
currentMouseX, currentMouseY = pyautogui.position()
pyautogui.moveto(screenWidth/2, screenHeight/2)
