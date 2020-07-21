import rubik

actions = [rubik.F, rubik.Fi, rubik.L, rubik.Li, rubik.U, rubik.Ui]

def two_way_trans(forward_state, backward_state, depth):
    if depth > 15:
        return None, None
    if depth % 2 == 0:
        for iterator in forward_state.keys():
            if backward_state.get(iterator) != None:
                return forward_state[iterator], backward_state[iterator]
            for action in actions:
                new_state = rubik.perm_apply(action, iterator)
                if forward_state.get(new_state) is None:
                    forward_state[new_state] = forward_state[iterator] + [action]
        return two_way_trans(forward_state, backward_state, depth + 1)
    else:
        for iterator in backward_state.keys():
            if forward_state.get(iterator) != None:
                return forward_state[iterator], backward_state[iterator]
            for action in actions:
                new_state = rubik.perm_apply(action, iterator)
                if backward_state.get(new_state) is None:
                    backward_state[new_state] = backward_state[iterator] + [action]
        return two_way_trans(forward_state, backward_state, depth + 1)
    # else:
    #     backward_state_new = backward_state[:]
    #     for iterator in backward_state:
    #         state, action_q = iterator[0][:], iterator[1][:]
    #         for iterator1 in forward_state:
    #             if state == iterator1[0][:]:
    #                 return iterator1[1], action_q
    #         for action in actions:
    #             new_state = rubik.perm_apply(action, state)
    #             backward_state_new.append([new_state, action_q+[action]])
    #     backward_state = backward_state_new[:]
    #     return two_way_trans(forward_state, backward_state, depth + 1)

def shortest_path(start, end):
    """
    Using 2-way BFS, finds the shortest path from start_position to
    end_position. Returns a list of moves. 

    You can use the rubik.quarter_twists move set.
    Each move can be applied using rubik.perm_apply
    """
    # raise NotImplementedError
    forward_dict = {start:[]}
    backward_dict = {end:[]}
    forward_path, backward_path = two_way_trans(forward_dict, backward_dict, 0)
    if forward_path is None and backward_path is None:
        return None
    margin_path = []
    for iterator in forward_path:
        if iterator != []:
            margin_path.append(iterator)
    for i in range(len(backward_path)-1, -1, -1):
        if backward_path[i] != []:
            margin_path.append(rubik.perm_inverse(backward_path[i]))
    return margin_path