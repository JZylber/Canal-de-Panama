from typing import TypedDict

class CanalState(TypedDict):
    locks: list[str]
    locks_water_level: list[str]
    queue_upstream: list[str]
    queue_downstream: list[str]
    gates: list[bool]
    direction: str
    control: list[(int,str)]
    open : bool

def initial_canal_state() -> CanalState:
    return {
        "locks": ["","",""],
        "locks_water_level": ["low","low","low"],
        "queue_upstream": [],
        "queue_downstream": [],
        "gates": [False,False,False,False],
        "direction": "upstream",
        "control": [],
        "open": True
        }

#Removes the boat from the lock
def remove_boat_from_lock(canal_state: CanalState, lock: int) -> str:
    boat = canal_state["locks"][lock]
    canal_state["locks"][lock] = ""
    return boat

#Moves the boat from the start to the end
def move_boat(canal_state: CanalState, start: str, end: str) -> None:
    boat = ""
    if start == "qu":
        boat = canal_state["queue_upstream"].pop(0)
    elif start == "qd":
        boat = canal_state["queue_downstream"].pop(0)
    else:
        boat = remove_boat_from_lock(canal_state,int(start))
    if end != "u" and end != "d":
        close_lock(canal_state,int(end))
        canal_state["locks"][int(end)] = boat
    else:
        close_lock(canal_state,int(start))

#Closes the lock gates
def close_lock(canal_state: CanalState, lock: int) -> None:
    canal_state["gates"][lock] = False
    canal_state["gates"][lock + 1] = False

#Opens the lock gate in the provided direction
def open_lock(canal_state: CanalState, lock: int, direction: str) -> None:
    if direction == "upstream":
        canal_state["gates"][lock + 1] = True
    else:
        canal_state["gates"][lock] = True

#Checks if both lock gates are closed
def lock_is_closed(canal_state: CanalState, lock: int) -> bool:
    return not canal_state["gates"][lock] and not canal_state["gates"][lock + 1]

def lock_is_empty(canal_state: CanalState, lock: int) -> bool:
    return canal_state["locks"][lock] == ""

def canal_is_empty(canal_state: CanalState) -> bool:
    return all(map(lambda lock: lock == "", canal_state["locks"])) and not any(canal_state["gates"])

#Returns the next lock in the provided direction
def get_next_lock(lock: int, direction: str) -> str | int:
    if direction == "upstream":
        if lock == 2:
            return "u"
        else:
            return lock + 1
    else:
        if lock == 0:
            return "d"
        else:
            return lock - 1
    
def execute_command(canal_state: CanalState, command: str) -> None:
    command_parts = command.split(" ")
    type, arg1, arg2 = command_parts
    if type == "move":
        move_boat(canal_state,arg1,arg2)
    elif type == "level":
        canal_state["locks_water_level"][int(arg1)] = arg2
    elif type == "queue":
        if arg1 == "qu":
            canal_state["queue_upstream"].append(arg2)
        else:
            canal_state["queue_downstream"].append(arg2)
    elif type == "direction":
        if not(canal_is_empty(canal_state)):
            canal_state["open"] = False
            canal_state["control"].append((1,f"direction {arg1} {arg2}"))
        else:
            canal_state["direction"] = arg2
            if arg1 == "open":
                canal_state["open"] = True

def execute_control(canal_state: CanalState) -> None:
    ready_commands = filter(lambda command: command[0] == 0, canal_state["control"])
    for command in ready_commands:
        execute_command(canal_state,command[1])
    canal_state["control"] = list(filter(lambda command: command[0] > 0, canal_state["control"]))
    return canal_state

def move_through_locks(canal_state: CanalState) -> None:
    direction = canal_state["direction"]
    if direction == "upstream":
        #Moves through locks from upstream to downstream
        for lock in range(len(canal_state["locks"]) - 1,-1,-1):
            # Actions can only be performed if a boat is present in the lock and the lock is closed
            if not lock_is_empty(canal_state,lock) and lock_is_closed(canal_state,lock):
                lock_level = canal_state["locks_water_level"][lock]
                #If the lock water level is low and the direction is upstream, the water level of the lock should be raised
                if lock_level == "low":
                    canal_state["control"].append((10,f"level {lock} high"))
                    canal_state["locks_water_level"][lock] = "filling"
                #If the lock water level is high and the direction is upstream, the boat could be moved to the next lock
                elif lock_level == "high":
                    next_lock = get_next_lock(lock,canal_state["direction"])
                    #If the next lock is the upstream end of the canal, the boat can go out
                    if next_lock == "u":
                        #Open the lock upstream gate
                        open_lock(canal_state,lock,direction)
                        #Start moving the boat out of the lock
                        canal_state["control"].append((2,f"move {lock} u"))
                    else:
                        next_lock_level = canal_state["locks_water_level"][next_lock]
                        next_lock_boat = canal_state["locks"][next_lock]
                        #If the upstream lock is high, no boats are present and it is closed, water level should be lowered
                        if next_lock_level == "high" and next_lock_boat == "" and lock_is_closed(canal_state,next_lock):
                            canal_state["control"].append((10,f"level {next_lock} low"))
                            canal_state["locks_water_level"][next_lock] = "draining"
                        #If the upstream lock is low, no boats are present and it is closed, the boat can be moved to the next lock
                        elif next_lock_level == "low" and next_lock_boat == "" and lock_is_closed(canal_state,next_lock):
                            #Open the lock upstream gate
                            open_lock(canal_state,lock,direction)
                            #Start moving the boat to the next lock
                            canal_state["control"].append((2,f"move {lock} {next_lock}"))
    else:
        #Moves through locks from downstream to upstream
        for lock in range(len(canal_state["locks"])):
            # Actions can only be performed if a boat is present in the lock and the lock is closed
            if not lock_is_empty(canal_state,lock) and lock_is_closed(canal_state,lock):
                lock_level = canal_state["locks_water_level"][lock]
                #If the lock water level is high and the direction is downstream, the water level of the lock should be lowered
                if lock_level == "high":
                    canal_state["control"].append((10,f"level {lock} low"))
                    canal_state["locks_water_level"][lock] = "draining"
                #If the lock water level is low and the direction is downstream, the boat could be moved to the next lock
                elif lock_level == "low":
                    next_lock = get_next_lock(lock,canal_state["direction"])
                    #If the next lock is the downstream end of the canal, the boat can go out
                    if next_lock == "d":
                        #Open the lock downstream gate
                        open_lock(canal_state,lock,direction)
                        #Start moving the boat out of the lock
                        canal_state["control"].append((2,f"move {lock} d"))
                    else:
                        next_lock_level = canal_state["locks_water_level"][next_lock]
                        next_lock_boat = canal_state["locks"][next_lock]
                        #If the downstream lock is low, no boats are present and it is closed, water level should be raised
                        if next_lock_level == "low" and next_lock_boat == "" and lock_is_closed(canal_state,next_lock):
                            canal_state["control"].append((10,f"level {next_lock} high"))
                            canal_state["locks_water_level"][next_lock] = "filling"
                        #If the downstream lock is high, no boats are present and it is closed, the boat can be moved to the next lock
                        elif next_lock_level == "high" and next_lock_boat == "" and lock_is_closed(canal_state,next_lock):
                            #Open the lock downstream gate
                            open_lock(canal_state,lock,direction)
                            #Start moving the boat to the next lock
                            canal_state["control"].append((2,f"move {lock} {next_lock}"))
    return canal_state

def move_boats_from_queue(canal_state: CanalState) -> None:
    #If the direction is upstream, boats should be moved from the upstream queue to the first lock
    if canal_state["direction"] == "upstream":
        #If the first lock is empty and closed, a boat from the downstream queue could be moved from the queue to the lock
        if lock_is_empty(canal_state,0) and lock_is_closed(canal_state,0) and len(canal_state["queue_downstream"]) > 0:
            #If the lock water level is high, it should be lowered before moving the boat
            if canal_state["locks_water_level"][0] == "high":
                canal_state["control"].append((10,f"level 0 low"))
                canal_state["locks_water_level"][0] = "draining"
            elif canal_state["locks_water_level"][0] == "low":
                #Open the lock downstream gate
                open_lock(canal_state,0,"downstream")
                #Start moving the boat to the first lock
                canal_state["control"].append((2,f"move qd 0"))
    else:
        #If the last lock is empty and closed, a boat from the upstream queue could be moved from the queue to the lock
        if lock_is_empty(canal_state,2) and lock_is_closed(canal_state,2) and len(canal_state["queue_upstream"]) > 0:
            #If the lock water level is low, it should be raised before moving the boat
            if canal_state["locks_water_level"][2] == "low":
                canal_state["control"].append((10,f"level 2 high"))
                canal_state["locks_water_level"][2] = "filling"
            elif canal_state["locks_water_level"][2] == "high":
                #Open the lock upstream gate
                open_lock(canal_state,2,"upstream")
                #Start moving the boat to the last lock
                canal_state["control"].append((2,f"move qu 2"))
    return canal_state

def minute(canal_state: CanalState) -> None:
    #Decreases the time of the commands in the control list by 1
    canal_state["control"] = list(map(lambda command: (command[0] - 1,command[1]), canal_state["control"]))
    #Executes the commands that are ready
    execute_control(canal_state)
    #Moves the boats through the locks
    move_through_locks(canal_state)
    #Attempt to move boats from the queue to the locks if the canal is open
    if canal_state["open"]:
        move_boats_from_queue(canal_state)
                