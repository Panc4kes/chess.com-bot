import chess
import chess.engine
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from pywinauto import application
from pywinauto import Desktop
import time
import os
import sys
import glob

running_script_directory = os.path.dirname(os.path.realpath(__file__))
os.chdir(running_script_directory)

for file in glob.glob("stockfish*"):
    print("Found Stockfish binary version",file.strip(".exe"))
    stockfish_name = file

try:
    engine = chess.engine.SimpleEngine.popen_uci(stockfish_name)
except:
    print("No Stockfish binary found")
    input("Press any key to exit.")
    sys.exit()

board = chess.Board()
limit = chess.engine.Limit(time=0.2)
driver = webdriver.Chrome("chromedriver.exe")
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--no-sandbox')

with open("board.txt") as f:
    array = [i.split() for i in f]

#url = input("Enter a url\n> ")
url = "https://www.chess.com/play/computer"
driver.get(url)
input("Press any key to continue...")

def open_chrome():
    '''
    THIS FUNCTION ASSURES THAT CHROME IS OPEN SO check_fen() CAN WORK PROPERLY
    '''
    app = application.Application().connect(title_re =".*Chess.*")
    app_dialog = app.top_window()

    if not app_dialog.has_focus():
        app_dialog.set_focus()

    

def check_fen():
    open_chrome()
    download = driver.find_element_by_class_name("download")
    download.click()
    time.sleep(2)

    form = driver.find_elements_by_class_name("form-input-input")[1]
    close = driver.find_element_by_css_selector(".icon-font-chess.x.icon-font-secondary")
    close.click()
    return form.get_attribute("value")

def find_loc(piece):
    for i, row in enumerate(array):
        for j, col in enumerate(row):
            if col == piece:
                return [j+1, 8-i]

while not board.is_game_over():
    board = chess.Board(check_fen())
    piece_size = driver.find_element_by_css_selector(".layout-board.board").size["height"]/8
    
    result = engine.play(board, limit)
    origin = find_loc(str(result.move)[:2])
    target = find_loc(str(result.move)[-2:])
    offset = [a - b for a, b in zip(target, origin)]
    # print(origin, target)
    offset[0] *= piece_size
    offset[1] *= -piece_size
    
    origin_push = iter(driver.find_elements_by_class_name(f"square-{origin[0]}{origin[1]}"))
    while True:
        try:
            action_chains = ActionChains(driver)
            action_chains.drag_and_drop_by_offset(next(origin_push), offset[0], offset[1]).click().perform()
            break
        except:
            pass
    # Make GUI Responses to the promotion from the engine pick
    if len(str(result.move)) > 4:
        promotion_button = driver.find_element_by_class_name("promotion-piece.w" + str(result.move)[-1].lower())
        promotion_button.click()
        time.sleep(2)
    board.push(result.move)

    time.sleep(3)
    print(board, "\n")