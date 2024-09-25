




result = 0
for i in range(1, 4 + 1):
  result += 4 * i + sum(j for j in range(1, 4 + 1))

print(result)