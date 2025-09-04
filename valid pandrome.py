s =  "tab a cat"
k=s.replace(" ","")
l1=[]
l2=()
u=(len(k)//2)
print(u)
for i in range(u):
    l1.append((k[i]))
print(l1)
j=s[::-1]
print(j)
o=j.replace(" ","")
print(o)
print(k)
p=o.capitalize()
y=k.capitalize()
if p==y:
    print("treu")
else:
    print("gfalse")