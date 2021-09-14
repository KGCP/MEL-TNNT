# Yield successive n-sized chunks from l
def divide_chunks(l,n):
    # looping till length l
    for i in range(0, len(l), n): 
        yield l[i:i + n]
  
def partionlist(l,n):
    return list(divide_chunks(l,n))

def partiondict(dictionary,n):
    l = [{k:v} for k,v in dictionary.items()]
    partionedlist = partionlist(l,n)
    empty_list = []
    for ele in partionedlist:
        d = {}
        for item in ele:
            d = dict(d,**item)
        empty_list.append(d)
    return empty_list
