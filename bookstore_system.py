import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

class Bookstore:

    def __init__(self):
        self.inventory = pd.read_csv("inventory.csv")
        self.sales = pd.read_csv("sales.csv")

        self.sales["Date"] = pd.to_datetime(self.sales["Date"], errors="coerce")
        self.inventory["Author"] = self.inventory["Author"].fillna("Unknown")
        self.inventory["Genre"] = self.inventory["Genre"].fillna("Unknown")
        self.inventory["Title"] = self.inventory["Title"].fillna("Unknown")
        self.inventory["Price"] = self.inventory["Price"].fillna(self.inventory["Price"].mean())
        self.inventory["Quantity"] = self.inventory["Quantity"].fillna(0)
        self.sales["Title"] = self.sales["Title"].fillna("Unknown")
        self.sales["Quantity Sold"] = self.sales["Quantity Sold"].fillna(0)
        self.sales["Total Revenue"] = self.sales["Total Revenue"].fillna(0)
        print("Data loaded and cleaned successfully.")

    def add_book(self, title, author, genre, price, quantity):

        if price <= 0:
            print("Price must be positive.")
            return

        new_book = pd.DataFrame({
            "Title": [title],
            "Author": [author],
            "Genre": [genre],
            "Price": [price],
            "Quantity": [quantity]
        })

        self.inventory = pd.concat([self.inventory, new_book], ignore_index=True)
        print("Book added successfully.")

    def update_inventory(self, title, quantity):
        if quantity < 0:
            print("Quantity cannot be negative.")
            return
        mask = self.inventory["Title"].str.lower() == title.lower()
        if mask.any():
            self.inventory.loc[mask, "Quantity"] = quantity
            print("Inventory updated successfully.")

        else:
            print("Book not found.")

    def record_sale(self, title, quantity):

        if quantity <= 0:
            print("Sale quantity must be positive.")
            return

        mask = self.inventory["Title"].str.lower() == title.lower()

        if not mask.any():
            print("Book not found.")
            return

        index = self.inventory.index[mask][0]

        available_stock = self.inventory.loc[index, "Quantity"]
        price = self.inventory.loc[index, "Price"]

        if quantity > available_stock:
            print("Not enough stock available.")
            return
        self.inventory.loc[index, "Quantity"] -= quantity
        revenue = quantity * price
        new_sale = pd.DataFrame({
            "Date": [pd.Timestamp.today()],
            "Title": [self.inventory.loc[index, "Title"]],
            "Quantity Sold": [quantity],
            "Total Revenue": [revenue]
        })
        self.sales = pd.concat([self.sales, new_sale],ignore_index=True)

        print("Sale recorded successfully.")
        print("Revenue:", revenue)

    def generate_report(self):

        print("\n========== Bookstore Report ==========")
        revenues = self.sales["Total Revenue"].to_numpy()
        total_revenue = np.sum(revenues)
        average_revenue = np.mean(revenues)
        prices = self.inventory["Price"].to_numpy()
        average_price = np.mean(prices)
        quantities = self.sales["Quantity Sold"].to_numpy()
        total_books_sold = np.sum(quantities)
        print("Total Revenue:", round(total_revenue, 2))
        print("Average Revenue:", round(average_revenue, 2))
        print("Average Book Price:", round(average_price, 2))
        print("Total Books Sold:", int(total_books_sold))

        quality1 = (self.sales.groupby("Title")["Quantity Sold"].sum().sort_values(ascending=False))

        print("\nBest Selling Books:")
        print(quality1.head(3))

        merged = pd.merge(self.sales,self.inventory[["Title", "Author", "Genre", "Price"]],on="Title",how="left")

        genre_revenue = (merged.groupby("Genre")["Total Revenue"].sum().sort_values(ascending=False))
        print("\nRevenue by Genre:")
        print(genre_revenue)

        author_revenue = ( merged .groupby("Author")["Total Revenue"] .sum() .sort_values(ascending=False))
        print("\nRevenue by Author:")
        print(author_revenue.head(10))

        monthly_sales = ( self.sales.groupby(self.sales["Date"].dt.to_period("M")) ["Total Revenue"].sum())

        if len(monthly_sales) > 1:
            growth = np.diff(monthly_sales) / monthly_sales[:-1] * 100
            print("\nSales Growth Rates:")
            print(growth)

        else:
            print("\nNot enough months to calculate growth.")

   
    def visualization(self):
        merged = pd.merge(
            self.sales,
            self.inventory[["Title", "Author", "Genre", "Price"]],
            on="Title",
            how="left",
        )

        plt.figure(figsize=(14, 10))

        plt.subplot(2, 2, 1)
        author_sales = (
            merged.groupby("Author")["Quantity Sold"]
            .sum()
            .sort_values(ascending=False)
            .head(5)
        )
        sns.barplot( x=author_sales.values, y=author_sales.index, hue=author_sales.index, legend=False, )
        plt.title("Total Sales by Author")
        plt.xlabel("Quantity Sold")
        plt.ylabel("Author")

        plt.subplot(2, 2, 2)
        monthly_sales = self.sales.groupby(
            self.sales["Date"].dt.to_period("M")
        )["Total Revenue"].sum()
        monthly_sales.index = monthly_sales.index.astype(str)
        plt.plot(monthly_sales.index, monthly_sales.values, marker="o", color="b")
        plt.title("Monthly Sales Trend")
        plt.xlabel("Month")
        plt.ylabel("Revenue")
        plt.xticks(rotation=45)

        plt.subplot(2, 2, 3)
        genre_revenue = merged.groupby("Genre")["Total Revenue"].sum()
        plt.pie(
            genre_revenue.values,
            labels=genre_revenue.index,
            autopct="%1.1f%%",
            startangle=140,
        )
        plt.title("Revenue Share by Genre")

        plt.subplot(2, 2, 4)
        correlation_data = merged[["Price", "Quantity Sold", "Total Revenue"]]
        correlation = correlation_data.corr()
        sns.heatmap(correlation, annot=True, cmap="coolwarm", fmt=".2f")
        plt.title("Correlation Heatmap")

        plt.tight_layout()
        plt.show()
        print("Generated Graphs.")

book1 = Bookstore()

print("\n📚 WELCOME TO BOOKSTORE MANAGEMENT SYSTEM   ")
while True:

    print("\n========== Bookstore System ==========")
    print("1. Add Book")
    print("2. Update Inventory")
    print("3. Record Sale")
    print("4. Generate Report")
    print("5. Show Visualizations")
    print("6. Show Inventory")
    print("7. Show Sales")
    print("8. Exit")
    try:
        choice1 = int(input("Enter your choice: "))

        match choice1:
            case 1:
                title = input("Enter book title: ")
                author = input("Enter author: ")
                genre = input("Enter genre: ")
                try:
                    price = float(input("Enter price: "))
                    quantity = int(input("Enter quantity: "))
                    book1.add_book(title, author, genre,price,quantity)

                except ValueError:
                    print("Please enter valid numeric values.")
            case 2:
                title = input("Enter book title: ")
                try:
                    quantity = int(input("Enter new quantity: "))
                    book1.update_inventory(title,quantity)
                except ValueError:
                    print("Quantity must be a number.")
            case 3:
                title = input("Enter book title: ")
                try:
                    quantity = int(input("Enter quantity sold: "))
                    book1.record_sale( title, quantity)
                except ValueError:
                    print("Quantity must be a number.")
            case 4:
                book1.generate_report()
            case 5:
                book1.visualization()
            case 6:
                print(book1.inventory)
            case 7:
                print(book1.sales)
            case 8:
                print("Thank you for using Bookstore System.")
                break
            case _:
                print("Invalid choice1!")
    except ValueError:
        print("Invalid choice1! Enter only number.")