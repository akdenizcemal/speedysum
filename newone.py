s = "{([])}"
hashs={")":"(","]":"[","}":"{"}
stack=[]
valid = True
for b in s:
    if b in hashs:
        if stack and stack[-1]==hashs[b]:
            stack.pop()
        else:
            valid=False
            break
    else:
        stack.append(b)
if valid and not stack:
    print("True")
else:
    print("False")
