from familytree.people.models import Person

def describe_relative(person, relative):
    person_ancestors = person.ancestors()
    relative_ancestors = relative.ancestors()
    # First check for direct ancestors (i.e. parents, grandparents, great-grandparents, etc.)
    if relative in person_ancestors:
        distance = person_ancestors[relative]
        if distance == 1: return 'Mother' if relative.gender == 'F' else 'Father'
        else:             return ('Great-' * (distance - 2)) + ('Grandmother' if relative.gender == 'F' else 'Grandfather')
    elif person in relative_ancestors:
        distance = relative_ancestors[person]
        if distance == 1: return 'Daughter' if relative.gender == 'F' else 'Son'
        else:             return ('Great-' * (distance - 2)) + ('Granddaughter' if relative.gender == 'F' else 'Grandson')

    # Then check for shared ancestors.
    (ancestor, distance1, distance2) = closest_common_ancestor(person_ancestors, relative_ancestors)
    if ancestor: 
        if distance1 == 1 and distance2 == 1:   return 'Sister' if relative.gender == 'F' else 'Brother'
        elif distance1 == 1:                    return ('Great-' * distance2 - 2) + ('Niece' if relative.gender == 'F' else 'Nephew')
        elif distance2 == 1:                    return ('Great-' * distance1 - 2) + ('Aunt' if relative.gender == 'F' else 'Uncle')
        else:                                   return 'Cousin' # TO DO: Be more specific.
    return None


def closest_common_ancestor(person_ancestors, relative_ancestors):
    '''Returns the closest common ancestor of two people, or None if they are not blood relations.'''
    common_ancestor = None
    person_distance = 0
    relative_distance = 0
    for ancestor, distance in person_ancestors.items():
        if ancestor in relative_ancestors:
            distance2 = relative_ancestors[ancestor]
            if common_ancestor == None or distance < person_distance or distance2 < relative_distance:
                (common_ancestor, person_distance, relative_distance) = (ancestor, distance, distance2)
    return (common_ancestor, person_distance, relative_distance)
