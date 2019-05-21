def test(list=None):
    if 'element' in list if list is not None else []:
        print('yes')
    else:
        print('no')

test(['some', 'element'])
test()