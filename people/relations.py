def describe_relative(person, relative, person_ancestor_distances={}, relative_ancestor_distances={}):
    if person.id != relative.id:
        # First check for direct ancestors (i.e. parents, grandparents, great-grandparents, etc.)
        if relative in person_ancestor_distances:
            distance = person_ancestor_distances[relative]
            if distance == 1:
                return 'Mother' if relative.gender == 'F' else 'Father'
            else:
                base = 'Grandmother' if relative.gender == 'F' else 'Grandfather'
                return _describe_offset(base, distance)
        elif person in relative_ancestor_distances:
            distance = relative_ancestor_distances[person]
            if distance == 1:
                return 'Daughter' if relative.gender == 'F' else 'Son'
            else:
                base = 'Granddaughter' if relative.gender == 'F' else 'Grandson'
                return _describe_offset(base, distance)

        # Then check for shared ancestors.
        (ancestor, distance1, distance2) = closest_common_ancestor(person_ancestor_distances,
                                                                   relative_ancestor_distances)
        if ancestor:
            if distance1 == 1 and distance2 == 1:
                return 'Sister' if relative.gender == 'F' else 'Brother'
            elif distance1 == 1:
                base = 'Niece' if relative.gender == 'F' else 'Nephew'
                return _describe_offset(base, distance2)
            elif distance2 == 1:
                base = 'Aunt' if relative.gender == 'F' else 'Uncle'
                return _describe_offset(base, distance1)
            else:
                pos = min((distance1, distance2)) - 1
                removes = abs(distance1 - distance2)
                if removes > 0:
                    return ' {0} Cousin {1} Removed'.format(position(pos), number_of_times(removes))
                else:
                    return ' {0} Cousin'.format(position(pos))
    return None

def _describe_offset(base, distance):
    if distance <= 2:
        return base
    else:
        return ('Great-' if distance == 3 else 'Great(x{0})-'.format(distance - 2)) + base


def closest_common_ancestor(person_ancestors, relative_ancestors):
    '''Returns the closest common ancestor of two people, or None if they are
    not blood relations.'''
    common_ancestor = None
    person_distance = 0
    relative_distance = 0
    for ancestor, distance in person_ancestors.items():
        if ancestor in relative_ancestors:
            distance2 = relative_ancestors[ancestor]
            if common_ancestor == None or distance < person_distance or distance2 < relative_distance:
                (common_ancestor, person_distance, relative_distance) = (ancestor, distance, distance2)
    return (common_ancestor, person_distance, relative_distance)


def position(position):
    remainder = position % 10
    if remainder == 1 and position != 11:
        return str(position) + 'st'
    elif remainder == 2 and position != 12:
        return str(position) + 'nd'
    elif remainder == 3 and position != 13:
        return str(position) + 'rd'
    return str(position) + 'th'

def number_of_times(number):
    if number == 1:
        return 'Once'
    elif number == 2:
        return 'Twice'
    elif number == 3:
        return 'Thrice'
    else:
        return str(number) + ' Times'

