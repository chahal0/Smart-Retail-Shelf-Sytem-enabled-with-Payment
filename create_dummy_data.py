import pandas as pd
import random

# Extended list of items (100+ items)
items = [
    'Milk', 'Bread', 'Eggs', 'Butter', 'Cheese', 'Yogurt', 'Apple', 'Banana', 'Orange', 'Grapes',
    'Strawberry', 'Blueberry', 'Raspberry', 'Watermelon', 'Pineapple', 'Mango', 'Peach', 'Pear',
    'Cherry', 'Lemon', 'Lime', 'Avocado', 'Tomato', 'Potato', 'Onion', 'Carrot', 'Cucumber',
    'Lettuce', 'Spinach', 'Broccoli', 'Cauliflower', 'Peppers', 'Mushrooms', 'Zucchini', 'Eggplant',
    'Garlic', 'Ginger', 'Chicken', 'Beef', 'Pork', 'Fish', 'Shrimp', 'Tofu', 'Beans', 'Lentils',
    'Rice', 'Pasta', 'Noodles', 'Flour', 'Sugar', 'Salt', 'Pepper', 'Oil', 'Vinegar', 'Soy Sauce',
    'Ketchup', 'Mustard', 'Mayo', 'Salsa', 'Chips', 'Pretzels', 'Popcorn', 'Chocolate', 'Cookies',
    'Cake', 'Pie', 'Ice Cream', 'Soda', 'Water', 'Juice', 'Coffee', 'Tea', 'Beer', 'Wine',
    'Whiskey', 'Vodka', 'Rum', 'Gin', 'Tequila', 'Soap', 'Shampoo', 'Conditioner', 'Toothpaste',
    'Toothbrush', 'Deodorant', 'Lotion', 'Sunscreen', 'Razor', 'Shaving Cream', 'Toilet Paper',
    'Paper Towels', 'Napkins', 'Trash Bags', 'Foil', 'Plastic Wrap', 'Detergent', 'Bleach',
    'Cleaner', 'Sponge', 'Broom', 'Mop', 'Bucket'
]

# Generate mbd.csv (Market Basket Analysis) - 500 transactions
transactions = []
for _ in range(500):
    k = random.randint(3, 10) # 3 to 10 items per basket
    t = random.sample(items, k)
    transactions.append(t)

df_mbd = pd.DataFrame(transactions)
df_mbd.to_csv('mbd.csv', header=False, index=False)

# Generate Book2.csv (Seasonal Analysis)
seasons = ['Winter', 'Spring', 'Summer', 'Autumn']
data = []
for season in seasons:
    # Randomly select trending items for each season
    seasonal_items = random.sample(items, 30) 
    for item in seasonal_items:
        qty = random.randint(50, 500)
        data.append({'Product': item, 'Quantity': qty, 'Season': season})

df_book2 = pd.DataFrame(data)
df_book2.to_csv('Book2.csv', index=False)

print("Diverse dummy CSVs created with 100 items.")
