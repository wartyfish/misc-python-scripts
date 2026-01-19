"""
Secret Santa / Gift Exchange Draw

This script generates a valid, one-to-one gift assignment for a list of
participants. Each participant gives to exactly one other participant
and receives exactly one gift, with no self-assignments.

Approach:
- Randomly partition participants into groups of specified minimum size 
- Within each group, generate a derangement via a circular shift
- Merge group-level assignments into a single global draw

Guarantees:
- No participant is assigned to themselves
- Every participant both gives and receives exactly once
- No retries or brute-force reshuffling are required
- The draw always succeeds given >= 3 participants

Notes:
- Randomness affects both group composition and assignments
- Grouping is used to avoid derangement edge cases and simplify logic
- Output is deterministic once randomness is fixed (e.g. via seeding)
"""

import random

##################
# core functions #
##################

# randomises list and from that builds groups sequentially
# amount and size of groups random, but must exceed minimum threshold (2 by default)
# returns a list of groups
def define_groups(my_list: list, min_group_size: int=2) -> list:
    random.shuffle(my_list)
    groups = []
    groups_index = 0
    item_count = 0
    groups.append([my_list[0]])
    
    for item in my_list:
        if item != my_list[0]:
            item_count += 1
            
            # make sure group size exceeds threshold size
            if len(groups[groups_index]) <= min_group_size or len(my_list) - item_count <= min_group_size - 1:
                groups[groups_index].append(item)

            # if allowed, each successive item has 50% change of joining group
            else:
                if random.randrange(2) == 0:
                    groups[groups_index].append(item)
                else:
                    groups_index += 1
                    groups.append([item])
    
    return groups

# creates a derangement of a list by offsetting by a randomised value
# pairs values from original list to offset one
def derange_group(my_list: list) -> dict:
    derangement_factor = random.randrange(1, len(my_list))
    participants_deranged = []
    for i in range(len(my_list)):
        j = (i + derangement_factor) % len(my_list)
        participants_deranged.append(my_list[j])

    return dict(zip(my_list, participants_deranged))


#####################
# Testing functions #
#####################

# used for modelling distribution of group sizes for given number of participants
def group_size_frequencies(list, iterations) -> dict:
    number_of_groups_count = {}
    [number_of_groups_count.setdefault(n, 0) for n in range(len(list) // 2 + 1)]

    for i in range(iterations):
        number_of_groups_count[len(define_groups(list))] += 1

    return number_of_groups_count

# displays the distribution modelled above
def print_distribution(my_list, iterations) -> None:
    distribution = group_size_frequencies(my_list, iterations)
    print(distribution)
    for n in distribution:
        print(f"Group size {n:2}: {"x"*int(round((int(distribution[n])/100)))}")

# checks the draw was valid by validating that every gifter is paired with a receiver
# and that no one is gifting for themself
def check_valid_draw(draw: dict) -> bool:
    gifters = list(draw.keys())
    receivers = list(draw.values())

    if not len(set(gifters)) == len(set(receivers)):
        return False
    
    if not all(participant in receivers for participant in gifters):
        return False

    return True

################
# main program #
################
def pull_from_hat(participants: list, min_group_size: int=3) -> dict:
    groups = define_groups(participants, min_group_size)
    draw = {}

    def merge_two_dicts(x, y):
        z = x.copy()
        z.update(y)
        return z

    for group in groups:
        print(group)
        group_paired = derange_group(group)
        
        draw = merge_two_dicts(draw, group_paired)

    return dict(sorted(draw.items()))

################

def main():
    participants = ["Alice", "Bob", "Charlie", "David", "Emma", "Frank", "Gabriel", "Hannah", "Imogen", "Jamie", "Kate",
                    "Liam", "Max", "Nick", "Olivia", "Peter", "Quentin", "Racheal", "Simon", "Tina", "Uma", "Velma", "Wilson",
                    "Xanvier", "Yorik", "Zack"]

    disallowed = {}
    disallowed["Alice"] = ["Bob", "David"]
    disallowed["Bob"]   = ["Alice", "David"]
    disallowed["David"] = ["Alice", "Bob"]

    group_size = 10
    participants = participants[:group_size]


    draws = pull_from_hat(participants)
    for participant in draws:
        print(f"{participant:8} is gifting {draws[participant]}")

    valid = True
    for i in range(10):
        if not check_valid_draw(draws):
            valid = False

    if valid:
        print("Grouping is valid")


if __name__ == "__main__":
    main()