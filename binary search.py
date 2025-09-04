nums = [-1,0,2,4,6,8]
target=33
high=((len(nums)))-1
low=0
while low<= high:
    mid=low+(high-low)//2
    if target==nums[mid]:
        print("index",mid)
        break
    elif target<nums[mid]:
        high=mid-1
    else:
        low=mid+1
else:
    print("-1")





