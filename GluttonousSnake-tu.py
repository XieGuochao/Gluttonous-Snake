import keyboard
import random
import threading
import time
import sys
import curses
from curses import wrapper

# Static
config = {
    "divider": 22, # The width of divider
    "size-x": 10, # The height of window
    "size-y": 20 # The width of window
}

# Dynamic
state = {
    "state": "running", # "running", "pause", "boundary", "eat_self"
    "time": 0,
    "score": 0,
    "speed": 1, # Speed is the frequency to move.
    "food": [], # A list of 2-element tuple to store the position of the next foods
    "snake": [], # A list of all transition nodes of a snake. The head is at the end of the list!
    "last-direction": (0, 0), # Store the last direction
    "direction": (0, 1), # A 2-element tuple for the snake's direction,
    "blocks": None, # A size-x * size-y tuple of entries
}

# Constants

up = (-1, 0)
down = (1, 0)
left = (0, -1)
right = (0, 1)

help_message = """
Space / Enter   : Pause / Resume
[               : Slower
]               : Faster
H               : Help
Q               : Quit
"""

graphic_mapping = {
    None: " ",
    "f": "*",
    "s": "■"
}


def push_left():
    # print("Trigger push_left")
    if check_update_direction(state["snake"], left):
        state["direction"] = left

def push_right():
    # print("Trigger push_right")
    if check_update_direction(state["snake"], right):
        state["direction"] = right

def push_up():
    # print("Trigger push_up")
    if check_update_direction(state["snake"], up):
        state["direction"] = up

    
def push_down():
    # print("Trigger push_down")
    if check_update_direction(state["snake"], down):
        state["direction"] = down


def faster():
    # print("Trigger Faster")
    state["speed"] *= 2
    
def slower():
    # print("Trigger Slower")
    state["speed"] /= 2
    
def help_function():
    # print("Trigger help")
    # print(help_message)

    
    state["state"] = "pause"
    
def quit_function():
    # print("Trigger quit")
    state["state"] = "quit"
    
def pause_resume():
    # print("Trigger Pause Resume")
    if state["state"] == "pause":
        state["state"] = "running"
    elif state["state"] == "running":
        state["state"] = "pause"
        

def update_state():
    """
    Check if state["state"] is running, if not, we can return immediately.
    Update state["time"]
    Get the states of all blocks before the move.
    Use the state["direction"] and state["last-direction"] to update the state["food"], state["snake"], and state["blocks"].
    """   
    
    global state
    
    if state["state"] != "running":
        return
    
    state["time"] += 1
    
    # Clear state["blocks"]
    clear_blocks(state["blocks"])
    
    # Update blocks using snake and food
    update_blocks(state["blocks"], state["snake"], state["food"])
    
    # Get the current head and the new head's position
    head = state["snake"][-1]
    new_pos = add_2D(head, state["direction"])
    
    # Check if it hits the boundary
    if not check_boundary(new_pos, config["size-x"], config["size-y"]):
        state["state"] = "boundary"
        return
    
    # Check if it eats itself
    if not check_eat_self(new_pos, state["snake"]):
        state["state"] = "eatself"
        return
    
    # Now the new position is valid, append it to the snake and update blocks
    state["snake"].append(new_pos)
    state["blocks"][new_pos[0]][new_pos[1]] = "s"
    
    
    # if snake eats / does not eat food
    if new_pos in state["food"]:
        # Remove it from the food
        state["food"].remove(new_pos)
        state["score"] += 1
        
        # Generate new food
        new_food = generate_new_foods(state["blocks"])
        if new_food is None: # You win!
            state["state"] = "win"
        else:
            state["food"].append(new_food)
            state["blocks"][new_food[0]][new_food[1]] = "f"
    else:
        x, y = state["snake"][0]
        state["snake"] = state["snake"][1:]
        state["blocks"][x][y] = None
        
    return

def draw():
    """Draw on screen using state["blocks"] """
    # print("Gluttonous Snake: ")
    # print("Author: Guochao Xie")
    # print("Time: {} | Score: {} | Speed: {}".format(state["time"], state["score"], state["speed"]))
    # print("-" * config["divider"])
    
    # for i in range(len(state["blocks"])):
    #     print("|", end="")
    #     for j in range(len(state["blocks"][i])):
    #         print(graphic_mapping[state["blocks"][i][j]], end="")
    #     print("|")
    
    # print("-"* config["divider"])
    # return
        
    screen.clear()
    screen.addstr("Gluttonous Snake:\n")
    screen.addstr("Author: Guochao Xie\n")
    screen.addstr("Time: {} | Score: {} | Speed: {}\n".format(state["time"], state["score"], state["speed"]))
    screen.addstr("-" * config["divider"] + "\n")
    
    for i in range(len(state["blocks"])):
        screen.addstr("|")
        for j in range(len(state["blocks"][i])):
            screen.addstr(graphic_mapping[state["blocks"][i][j]])
        screen.addstr("|\n")
    screen.addstr("-"* config["divider"])
    screen.refresh()
    


def run():
    """The main thread for computation."""
    while True:
        if state["state"] == "running":
            update_state()
            
            draw()
            
            time.sleep(1 / state["speed"])
        elif state["state"] == "pause":
            
            draw()
            
            # print(help_message)
            
            screen.addstr(help_message)
            screen.refresh()
            time.sleep(1 / state["speed"])
        
        else:
            print("Game over: {}".format(state["state"]))
            print("Your score: {}".format(state["score"]))
            print("Main thread end")
            return
        

# Help functions

def add_2D(x, y):
    return (x[0] + y[0], x[1] + y[1])

def check_boundary(pos, x, y):
    """If True, it does not hit the boundary; if False, it hits the boundary."""
    if pos[0] >= 0 and pos[0] < x and pos[1] >= 0 and pos[1] < y:
        return True
    else:
        return False

def check_eat_self(pos, snake):
    """If True, it does not eat itself; if False, it eats itself."""
    if pos in snake:
        return False
    else:
        return True

def init_blocks(x, y):
    """Create a x*y 2D array with all None"""
    return [[None for _ in range(y)] for _ in range(x)]

def clear_blocks(blocks):
    """Reset the blocks as None"""
    for i in range(len(blocks)):
        for j in range(len(blocks[i])):
            blocks[i][j] = None

def update_blocks(blocks, snake, food):
    """
    For position in snake, set the block as 's'
    For position in food, set the block as 'f'
    """
    for x, y in snake:
        blocks[x][y] = 's'
        
    for x, y in food:
        blocks[x][y] = 'f'

def generate_new_foods(blocks):
    """If their is vacancy, randomly choose one; otherwise, return None"""
    
    # Get a list of vacant positions
    vacancy = [(i, j) for i in range(len(blocks)) for j in range(len(blocks[i])) if blocks[i][j] is None]
    
    # Empty
    if len(vacancy) == 0:
        return None
    else:
        return random.choice(vacancy)

def check_update_direction(snake, new_direction):
    """If we can update the direction, return True"""
    
    # Check the length
    if len(snake) == 1:
        return True
    
    # Compare the new pos with the previous direction
    if add_2D(snake[-1], new_direction) == snake[-2]:
        return False
    
    return True

def init():
    state["blocks"] = init_blocks(config["size-x"], config["size-y"])
    
    head = generate_new_foods(state["blocks"])
    print(head)
    state["snake"] = [head]
    update_blocks(state["blocks"], state["snake"], state["food"])
    
    food = generate_new_foods(state["blocks"])
    print(food)
    state["food"] = [food]
    update_blocks(state["blocks"], state["snake"], state["food"])
    

    
def main(main_screen = None):
    global screen
    screen = main_screen
    
    init()
    
    main_thread = threading.Thread(target = run)
    main_thread.start()
    
    main_thread.join()
    print("Game Over")
    # while True:
    #     pass
    
if __name__ == "__main__":
    keyboard.add_hotkey("up", push_up)
    keyboard.add_hotkey("down", push_down)
    keyboard.add_hotkey("left", push_left)
    keyboard.add_hotkey("right", push_right)
    keyboard.add_hotkey("space", pause_resume)
    keyboard.add_hotkey("enter", pause_resume)
    keyboard.add_hotkey("[", slower)
    keyboard.add_hotkey("]", faster)
    keyboard.add_hotkey("h", help_function)
    keyboard.add_hotkey("q", quit_function)
    
    # main()
    
    wrapper(main)
    
    sys.exit(0)