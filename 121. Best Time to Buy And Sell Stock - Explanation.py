prices = [10,9,8,7,6,5]
x=0
lists=[]
for x in range(len(prices)-1):
        for i in range(x + 1, len(prices)):  
                lists.append( prices[x] - prices[i])
print(lists)

y=min(lists)
if y>0:
        print(0)
else:
        print(y)