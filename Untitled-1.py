class ListNode:
     def __init__(self, val=0, next=None):
         self.val = val
         self.next = next

 
class Solution:
    def hasCycle(self, head):
        fast,slow=head,head
        while fast and fast.next:
            slow=slow.next
            fast=fast.next.next
            if slow==fast:
                print("t") 
                return
        print("f")
# Create nodes
node1 = ListNode(1)
node2 = ListNode(2)
node3 = ListNode(3)

# Link them: 1 -> 2 -> 3 -> back to 2 (cycle)
node1.next = node2
node2.next = node3   # cycle here

# Test
sol = Solution()
sol.hasCycle(node1)

