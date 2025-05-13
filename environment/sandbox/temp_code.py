def candidate(triangle):
    # Create a copy of the input triangle to avoid modifying it directly
    dp = [row[:] for row in triangle]
    
    # Start from the second last row and move towards the first row
    for i in range(len(triangle) - 2, -1, -1):
        # For each cell in the current row, update its value to be the minimum of its neighbors plus itself
        for j in range(len(dp[i])):
            dp[i][j] += min(dp[i+1][j], dp[i+1][j+1])
            
    # The minimum total path sum is stored in the first cell of the first row
    return dp[0][0]

assert candidate([[ 2 ], [3, 9 ], [1, 6, 7 ]]) == 6
assert candidate([[ 2 ], [3, 7 ], [8, 5, 6 ]]) == 10 
assert candidate([[ 3 ], [6, 4 ], [5, 2, 7 ]]) == 9
