class Solution(object):
    def rotate(self, nums, k):
        """
        :type nums: List[int]
        :type k: int
        :rtype: None Do not return anything, modify nums in-place instead.
        """

        # for i in range(k):
        #     buff = nums[-1]
        #     nums[1:] = nums[:-1]
        #     nums[0] = buff
        nums = nums[-k % len(nums):] + nums[:len(nums) - k % len(nums)] if k % len(nums) else nums
        print(nums)


Solution().rotate([1, 2, 3, 4, 5, 6, 7], 3)
