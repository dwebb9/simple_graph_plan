from GP.Custom_GraphPlan import solution
import numpy as np

class Problem():
    def __init__(self, init, actions, goal):
        self.init = init
        self.actions = actions
        self.goal = goal
        self.graph = [init]
        self.mutex_states = []
        return

    def expand_graph(self, action_list):
        next_level = self.graph[-1].copy()
        # print("Graph",self.graph)
        # print("Action List", action_list[0])
        # for i, effect in enumerate(list(np.squeeze(action_list))):
        for i, effect in enumerate(action_list[0]):
            if effect not in next_level:
                next_level.append(effect)
        self.graph.append(next_level)
        # print("Next level", next_level)
        return

    def check_goal(self):
        for i, g in enumerate(self.goal):
            if g not in self.graph[-1]:
                return False
        return True

    # def get_mutex_states(self, action_list):
    #     cur_states = self.graph[-1]
    #     mutex = []
    #     for s in cur_states:
    #         temp = [s]
    #         for c in cur_states:
    #             if s[0] == '~' and s[1:] == c:
    #                 temp.append(c)
    #             elif '~'+s == c:
    #                 temp.append(c)
    #             else:
    #                 pass
            
    #     return

    def find_solution(self, action_list):
        flipped_actions = action_list.copy()
        flipped_actions.reverse()
        a1 = flipped_actions[0]
        a2 = flipped_actions[1:]
        solution_set = []
        # creates list of possible solutions
        for i, action in enumerate(a1):
            # print("action: ",action)
            # print("i", i)
            possible_solution =[[action]]
            for j, acts in enumerate(a2):
                cur_actions = possible_solution[-1]
                prev_actions = []
                for ca in cur_actions:
                    # Find preconditions
                    precond = []
                    for u, pre in self.actions.actions:
                        if u == ca:
                            precond = pre
                    for k, act in enumerate(acts):
                        if act in precond and act not in prev_actions:
                            prev_actions.append(act)
                            # print(prev_actions)
                possible_solution.append(prev_actions)
            solution_set.append(possible_solution)
        
        # Check possible solutions
        approved_solutions = []
        # temp_set = solution_set[:]
        for i, solution in enumerate(solution_set):
            state = self.init.copy()
            # print("Solution:",solution[::-1])
            temp = solution[::-1]
            for j, actions in enumerate(solution[::-1]):
                actions = actions[:]
                for k, action in enumerate(actions):
                    if action[0] == '~':
                        try:
                            state[state.index(action[1:])] = action
                        except ValueError:
                            temp[j].remove(action)
                    else:
                        try:
                            state[state.index('~'+action)] = action
                        except ValueError:
                            temp[j].remove(action)
                if state == self.goal:
                    print("FOUND SOLUTION")
                    approved_solutions.append(temp[:j+1])
                    break
        # print("Approved:",approved_solutions)
        
        # remove redundant elements
        prev = []
        for action in approved_solutions:
            # print("got in")
            # print(action)
            not_first = False
            for act in action:
                # print("ACT: ",act)
                if not_first:
                    for i in act:
                        # TODO: CHANGE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                        # print("i: ", i)
                        if i[0] == '~':
                            if i[1:] in prev:
                                act.remove(i)
                                prev.remove(i[1:])
                                # print("act: ", act)
                                # print("prev: ", prev)

                                
                        #     try:
                        #         state[state.index(action[1:])] = action
                        #     except ValueError:
                        #         temp[j].remove(action)
                #         else:
                #             try:
                #                 state[state.index('~'+action)] = action
                #             except ValueError:
                #                 temp[j].remove(action)
                prev = act
                not_first = True
                
        
        if len(approved_solutions):
            return True, approved_solutions
        else:
            return False, 0

    def print_graph(self):
        print("===== Graph =====")
        for i, g in enumerate(self.graph):
            print('Level',i,':',g)

    def graph_plan(self):
        self.actions.get_mutex_actions()
        action_list = []
        solution_found = False
        while not solution_found:
            action_list.append(self.actions.get_possible_actions(self.graph[-1]))
            # print('possible actions', action_list[-1])
            self.expand_graph([action_list[-1]])
            # self.mutex_states.append(self.get_mutex_states(action_list[-1]))
            if self.check_goal():
                solution_found, solution = self.find_solution(action_list)
                # if len(self.graph) > 5:
                #     break
        self.print_graph()
        return solution

class ActionList():
    def __init__(self, names):
        self.actions = []
        self.mutex = []
        self.names = names
        return

    # Adds an action t
    def add_action(self, result, preconditions):
        """
        Adds an action to the list of all possible actions.\n
        Parameters:\n
        result (string) - the outcome of the actions, eg. 'A' or '~B'\n
        precondictions (list of strings) - the requirements for the action to be possible. In general this should
        include at least the opposite of whatever the result is. So if result = 'A', precond = ['~A']. Other 
        preconditions can be added to the list, eg. ['~A', 'B', '~C'], but this parameter must always be a list
        even if only one precondition exists.
        """
        self.actions.append([result, preconditions])
        return

    def print_actions(self):
        """
        Prints out the list of actions and their preconditions. 
        The format is [action, [preconditions]]
        """
        for action in self.actions:
            print(action)
        return

    def get_possible_actions(self, graph):
        """
        Identifies which actions are possible, given the current state of the graph.\n
        Parameters:\n
        graph (list) - The current state of the graph.
        """
        possible_actions = []
        for i, a in enumerate(self.actions):
            impossible = False
            for p in a[1]:
                if p not in graph:
                    impossible = True
                    break
            if not impossible:
                possible_actions.append(a[0])
        # print(possible_actions)
        return possible_actions

    def get_mutex_actions(self):
        """
        Identifies actions that are mutually exclusive
        """
        for a, p in self.actions:
            mutex = []
            for a2, p2 in self.actions:
                if a == a2:
                    continue
                else:
                    if a[0] == '~' and a[1:] == a2:
                        mutex.append(a2)
                    elif a2[0] == '~' and a2[1:] == a:
                        mutex.append(a2)
                    else:
                        if a in p2:
                            mutex.append(a2)
                        elif a[0] == '~' and a[1:] in p2:
                            mutex.append(a2)
                        elif '~'+a in p2:
                            mutex.append(a2)
            self.mutex.append([a, mutex])
        # print('Mutex Actions',self.mutex)
        return

def get_names(initial):
    names = []
    for i in initial:
        if i[0] == '~':
            names.append(i[1:])
        else:
            names.append(i)
    return names

# def get_initial_state(names):
#     # Initialize everything with 1's 
#     init = np.ones(len(names), dtype=int)
#     # Iterate through the names, checking for any that begin with '~'
#     # and setting that location in the init array to a 0
#     for i, name in enumerate(names):
#         if name[0] == '~':
#             init[i] = 0
#     # Return the init array
#     return init

def main(init, names, actions):
    # init = get_initial_state(names)
    goal = names
    # goal[2] = '~' + goal[2]
    problem = Problem(init, actions, goal)
    solution = problem.graph_plan()
    print("===== Solution =====")
    print(solution)
    return

if __name__ == "__main__":
    # Set the initial state of the system (use a list of names, with a '~' as the first character
    # if the component is off or malfunctining)
    # eg. initial = ['~A', 'B', 'C', '~D', 'E']
    # which means that there are 5 components, A, B, C, D, and E. Two of which are malfunctioning, A and D
    # initial = ['Camera', '~IMU', '~OpenCV', 'PPS']
    initial = ['Camera', '~IMU', '~OpenCV', 'PPS', 'SAM', 'Thruster1', 'Thruster2', 'Controller']
    names = get_names(initial)
    # Create action class
    actions = ActionList(names)
    actions.add_action('Camera', ['~Camera', '~PPS', '~SAM'])
    actions.add_action('IMU', ['~IMU', '~PPS', '~SAM'])
    actions.add_action('~OpenCV', ['OpenCV'])
    actions.add_action('OpenCV', ['~OpenCV', 'Camera', 'PPS'])
    actions.add_action('~PPS', ['PPS'])
    actions.add_action('~SAM', ['SAM'])
    actions.add_action('SAM', ['~SAM', 'Camera', 'IMU', 'OpenCV', 'Thruster1', 'Thruster2', 'Controller'])
    actions.add_action('PPS', ['~PPS', 'Camera', 'IMU'])
    actions.add_action('~Controller', ['Controller'])
    actions.add_action('Controller', ['~Controller', 'Thruster1', 'Thruster2'])
    actions.add_action('Thruster1', ['~Thruster1'])
    actions.add_action('Thruster2', ['~Thruster2'])




    # actions.add_action('Camera', ['Camera'])
    # actions.add_action('IMU', ['IMU'])
    # actions.add_action('OpenCV',['OpenCV'])
    # actions.add_action('PPS', ['PPS'])
    # actions.add_action('~Camera', ['~Camera'])
    # actions.add_action('~IMU', ['~IMU'])
    # actions.add_action('~OpenCV',['~OpenCV'])
    # actions.add_action('~PPS', ['~PPS'])

    main(initial, names, actions)