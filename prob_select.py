# Cmput 496 sample code
# Sampling from a discrete probability distribution
# Written by Martin Mueller

import random

# probabilities should add up to 1
def verify_weights(distribution):
    epsilon = 0.000000001 # allow small numerical error
    sum1 = 0.0
    for item in distribution:
        sum1 += item[1]
    assert abs(sum1 - 1.0) < epsilon
    print(sum1)

# This method is slow but simple
def random_select(distribution):
    r = random.random();
    sum = 0.0
    for item in distribution:
        sum += item[1]
        if sum > r:
            return item
    return distribution[-1] # some numerical error, return last element

drinks = [("Coffee", 0.3), ("Tea", 0.2), ("OJ", 0.4), ("Milk", 0.07), ("Milkshake", 0.03)]
verify_weights(drinks)

for _ in range(100):
    item = random_select(drinks)
    print(item[0])
