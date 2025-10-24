def array_equals(arr1, arr2):
    if len(arr1) != len(arr2):
        return False

    for i in range(len(arr1)):
        if arr1[i] != arr2[i]:
            return False

    return True


def print_array(arr):
    for row in arr:
        print(row)


def index_of(arr, predicate, default=-1):
    return next((i for i, e in enumerate(arr) if predicate(e)), default)
