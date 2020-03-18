import time
import threading
import os
import random
import keyboard
import sys

config = {
    "divider": 50,
    "speed": 1,  # Timestamp
    "size-x": 20,
    "size-y": 48
}

state = {
    "state": "running", # Control if it is running
    "time": 0,
    "score": 0,
    "delta_speed": 1,
    "food": [], # A list of 2-element tuple to store the position of the next foods
    "snake": [], # A list of all transition nodes of a snake. The head is at the end of the list!
    "last-direction": (0, 0), # Store the last direction
    "direction": (0, 1), # A 2-element tuple for the snake's direction,
    "graphic": None, # A size-x * size-y tuple of entries
}

up = (-1, 0)
down = (1, 0)
left = (0, -1)
right = (0, 1)

graphic_mapping = {
    None: " ",
    "f": "*",
    "s": "■"
}

def push_left(state = state):
    if neg(state["last-direction"]) != left:
        state["direction"] = left

def push_right(state = state):
    if neg(state["last-direction"]) != right:
        state["direction"] = right
    
def push_up(state = state):
    if neg(state["last-direction"]) != up:
        state["direction"] = up
    
def push_down(state = state):
    if neg(state["last-direction"]) != down:
        state["direction"] = down

def divider(n = 50):
    return "■" * n + "\n"

def add(li, tu): # Used to add a list by a tuple
    # print(li, tu)
    for i in range(min(len(li), len(tu))):
        li[i] += tu[i]

def check_boundary(pos, config = config, ): # Check if the position reaches the boundary
    if pos[0] >= 0 and pos[0] < config["size-x"] and pos[1] >= 0 and pos[1] < config["size-y"]:
        return False
    else:
        return True

def check_eat_self(pos, graphic):
    if graphic[pos[0]][pos[1]] == "s":
        return True
    else:
        return False
    
def neg(tu): # Get the negtive direction
    li = list(tu)
    for i in range(len(li)):
        li[i] = -li[i]
    return tuple(li)

def get_direction(a, b):
    delta_x, delta_y = b[0] - a[0], b[1] - a[1]
    if delta_x <= -1:
        return up
    elif delta_x >= 1:
        return down
    elif delta_y <= -1:
        return left
    elif delta_y >= 1:
        return right
    else:
        print(a, b)
        assert (False)

def get_length(snake): # Get the length of a snake
    return len(snake)

def init_state(state = state, config = config):
    
    init_position = [random.randint(2, config["size-x"] - 2), random.randint(2, config["size-y"] - 2)] # Generate the initial position
    
    state["snake"] = [init_position]
    graphic = update_graphic(state, config)
    new_food(graphic, state, config)

def new_food(graphic, state, config):
    # Randomly generate a new food
    
    if len(state["snake"]) + len(state["food"]) >= config["size-x"] * config["size-y"]: # No place!
        return
    else:
        remaining_pos = [
            (i, j) for i in range(config["size-x"]) for j in range(config["size-y"]) if graphic[i][j] is None
        ]
        new_pos = random.choice(remaining_pos)
        state["food"].append(new_pos)
        graphic[new_pos[0]][new_pos[1]] = "f"
        return 
    
def update_graphic(state, config):
    new_graphic = [
                [None for j in range(config["size-y"])]
                for i in range(config["size-x"])
            ]
    
    s = state["snake"][0]
    new_graphic[s[0]][s[1]] = "s"
    
    for index in range(1, len(state["snake"])):
        prev, current = state["snake"][index - 1], state["snake"][index]
        direction = get_direction(prev, current)
        if direction[0] != 0:
            j = prev[1]
            # print(prev, current, direction)
            for i in range(prev[0], current[0] + direction[0], direction[0]):
                new_graphic[i][j] = "s"
        else:
            i = prev[0]
            # print(prev, current, direction)
            
            for j in range(prev[1], current[1] + direction[1], direction[1]):
                new_graphic[i][j] = "s"
    
    for i, j in state["food"]:
        new_graphic[i][j] = "f"
        
    return new_graphic

def draw_graphic(graphic, config):
    string = ""
    for i in range(config["size-x"]):
        string += "|"
        for j in range(config["size-y"]):
            string += graphic_mapping[graphic[i][j]] 
        string += "|\n"
    return string

def update_state(state = state, config = config):
    if state["state"] == "running":
        state["time"] += 1
        config["speed"] *= state["delta_speed"]
        state["delta_speed"] = 1
        
        new_graphic = update_graphic(state, config)
        
        last_direction, direction, state["last-direction"] = state["last-direction"], state["direction"], state["direction"]
        
        # print("New Direction:", direction)
        
        if get_length(state["snake"]) == 1:
            current_pos = state["snake"][0][:]
            add(state["snake"][0], direction)
            
            if check_boundary(state["snake"][0]):
                state["state"] = "boundary"
                return
            
            new_graphic[state["snake"][0][0]][state["snake"][0][1]] = "s"
            
            if tuple(state["snake"][-1]) in state["food"]:
                # Add a tail node
                state["snake"] = [current_pos, state["snake"][0]]
                state["food"].remove(tuple(state["snake"][-1]))
                state["score"] += 1
                
                # Add new food
                new_food(new_graphic, state, config)
            else:
                new_graphic[current_pos[0]][current_pos[1]] = None
        
        else: # The snake has at least length 2

            if last_direction == direction: # Direction no change
                # We move the head forward and move the tail forward. All intermediate points remain the same.

                add(state["snake"][-1], direction)
                if check_boundary(state["snake"][-1]):
                    state["state"] = "boundary"
                    return
                # Check if it eats a food. If it eats a food, then the tail should not get forward
                head_pos = tuple(state["snake"][-1])
                
            else:
                # We add a new transition point to the head of the snake
                head_pos = state["snake"][-1][:]
                add(head_pos, direction)

                state["snake"].append(head_pos)
                if check_boundary(state["snake"][-1]):
                    state["state"] = "boundary"
                    return
                head_pos = tuple(head_pos)
            
            
            # Eat food or not.
            if head_pos in state["food"]:
                # Do not move the tail => Length + 1
                state["score"] += 1
                
                # Eat the food
                state["food"].remove(head_pos)
                
                # Add new food
                new_food(new_graphic, state, config)
                
            else:
                # Forward the tail
                tail_direction = get_direction(state["snake"][0], state["snake"][1])
                # print("tail:", state["snake"][0], state["snake"][1], tail_direction )
                new_graphic[state["snake"][0][0]][state["snake"][0][1]] = None # Remove the tail in graphic
                
                add(state["snake"][0], tail_direction)
                if check_eat_self(state["snake"][-1], new_graphic):
                    state["state"] = "eat_self"
                    return
                
                if state["snake"][0] == state["snake"][1]: # We need to remove the tail
                    state["snake"] = state["snake"][1:]
            
            new_graphic[head_pos[0]][head_pos[1]] = "s"
                
        del state["graphic"]
        state["graphic"] = new_graphic

def draw(state = state, config = config):
    string = ""
    string += divider(config["divider"])
    
    string += "Gluttonous Snake - Python | Author: Guochao Xie \n"
    
    string += divider(config["divider"])
    
    string += "{} | Time: {} | Score: {} | Speed: {}\n".format(state["state"], state["time"], state["score"], config["speed"])
    
    string += divider(config["divider"])
    
    # print(state)
    string += draw_graphic(state["graphic"], config)
    string += divider(config["divider"])
    # os.system("cls")
    sys.stdout.write(string)
    # sys.stdout.flush()
        
def run(state = state, config = config):
    init_state(state, config)
    pausing = False
    while True:
        try:
            if state["state"] == "running":
                pausing = False
                
                # Update States
                update_state()
                
                # Draw
                draw()
                
                # input()
                time.sleep(1 / config["speed"])
            elif state["state"] == "pause":
                if not pausing:
                    draw()
                pausing = True
                
                time.sleep(1 / config["speed"])
                
                continue
            else:
                print("Main thread end")
                return
        except KeyboardInterrupt:
            print("keyboard")
            state["state"] = "end"

            # return
def pause_resume(state = state, config = config):
    if state["state"] == "running":
        state["state"] = "pause"
    elif state["state"] == "pause":
        state["state"] = "running"

        
def end_handler():
    print("Trigger Termination")
    state["state"] = "end"
    
def add_speed():
    state["delta_speed"] = 2
    
def reduce_speed():
    state["delta_speed"] = 0.5

help_message = """
Space / Enter   : Pause / Resume
[               : Double Speed
]               : Half Speed
H               : Help
Q               : Quit
"""

def help_game():
    if state["state"] == "running":
        state["state"] = "pause"
    time.sleep(1 / config["speed"] + 0.1)
    print(help_message)
    
def quit_game():
    state["state"] = "end"
    
if __name__ == "__main__":
    input("Ready?")
    main_thread = threading.Thread(target = run)
    main_thread.start()

    keyboard.add_hotkey("up", push_up)
    keyboard.add_hotkey("down", push_down)
    keyboard.add_hotkey("left", push_left)
    keyboard.add_hotkey("right", push_right)
    keyboard.add_hotkey("space", pause_resume)
    keyboard.add_hotkey("enter", pause_resume)
    keyboard.add_hotkey("[", reduce_speed)
    keyboard.add_hotkey("]", add_speed)
    keyboard.add_hotkey("h", help_game) # Help
    keyboard.add_hotkey("q", quit_game) # Quit
    keyboard.add_hotkey("ctrl+c", quit_game)
    
    try:
        while state["state"] == "running":
            pass
    except KeyboardInterrupt:
        end_handler()


    main_thread.join()
    
    print("Game Over!")
    print("Your result: {}".format(state["state"]))
    print("Your score: {}".format(state["score"]))
    