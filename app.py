from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st


class Bookstore:
	def __init__(self):
		data_dir = Path(__file__).resolve().parent
		inventory_path = data_dir / "inventory.csv"
		sales_path = data_dir / "sales.csv"

		inventory_columns = ["Title", "Author", "Genre", "Price", "Quantity"]
		sales_columns = ["Date", "Title", "Quantity Sold", "Total Revenue"]

		self.inventory = (
			pd.read_csv(inventory_path)
			if inventory_path.exists()
			else pd.DataFrame(columns=inventory_columns)
		)
		self.sales = (
			pd.read_csv(sales_path)
			if sales_path.exists()
			else pd.DataFrame(columns=sales_columns)
		)

		for column in inventory_columns:
			if column not in self.inventory:
				self.inventory[column] = np.nan
		for column in sales_columns:
			if column not in self.sales:
				self.sales[column] = np.nan

		self.sales["Date"] = pd.to_datetime(self.sales["Date"], errors="coerce")
		self.inventory["Author"] = self.inventory["Author"].fillna("Unknown")
		self.inventory["Genre"] = self.inventory["Genre"].fillna("Unknown")
		self.inventory["Title"] = self.inventory["Title"].fillna("Unknown")
		self.inventory["Price"] = pd.to_numeric(self.inventory["Price"], errors="coerce")
		self.inventory["Price"] = self.inventory["Price"].fillna(
			self.inventory["Price"].mean()
		).fillna(0)
		self.inventory["Quantity"] = pd.to_numeric(
			self.inventory["Quantity"], errors="coerce"
		).fillna(0)
		self.sales["Title"] = self.sales["Title"].fillna("Unknown")
		self.sales["Quantity Sold"] = pd.to_numeric(
			self.sales["Quantity Sold"], errors="coerce"
		).fillna(0)
		self.sales["Total Revenue"] = pd.to_numeric(
			self.sales["Total Revenue"], errors="coerce"
		).fillna(0)
		print("Data loaded and cleaned successfully.")

	def add_book(self, title, author, genre, price, quantity):
		if price <= 0:
			print("Price must be positive.")
			return
		if quantity < 0:
			print("Quantity cannot be negative.")
			return

		new_book = pd.DataFrame(
			{
				"Title": [title],
				"Author": [author],
				"Genre": [genre],
				"Price": [price],
				"Quantity": [quantity],
			}
		)
		self.inventory = pd.concat([self.inventory, new_book], ignore_index=True)
		print("Book added successfully.")

	def update_inventory(self, title, quantity):
		if quantity < 0:
			print("Quantity cannot be negative.")
			return
		mask = self.inventory["Title"].astype(str).str.lower() == title.lower()
		if mask.any():
			self.inventory.loc[mask, "Quantity"] = quantity
			print("Inventory updated successfully.")
		else:
			print("Book not found.")

	def record_sale(self, title, quantity):
		if quantity <= 0:
			print("Sale quantity must be positive.")
			return

		mask = self.inventory["Title"].astype(str).str.lower() == title.lower()
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
		new_sale = pd.DataFrame(
			{
				"Date": [pd.Timestamp.today()],
				"Title": [self.inventory.loc[index, "Title"]],
				"Quantity Sold": [quantity],
				"Total Revenue": [revenue],
			}
		)
		self.sales = pd.concat([self.sales, new_sale], ignore_index=True)
		print("Sale recorded successfully.")
		print("Revenue:", revenue)

	def generate_report(self):
		print("\n========== Bookstore Report ==========")
		total_revenue = np.sum(self.sales["Total Revenue"].to_numpy())
		average_revenue = np.mean(self.sales["Total Revenue"].to_numpy())
		average_price = np.mean(self.inventory["Price"].to_numpy())
		total_books_sold = np.sum(self.sales["Quantity Sold"].to_numpy())

		print("Total Revenue:", round(total_revenue, 2))
		print("Average Revenue:", round(average_revenue, 2))
		print("Average Book Price:", round(average_price, 2))
		print("Total Books Sold:", int(total_books_sold))

		best_sellers = self.sales.groupby("Title")["Quantity Sold"].sum()
		print("\nBest Selling Books:")
		print(best_sellers.sort_values(ascending=False).head(3))

		merged = pd.merge(
			self.sales,
			self.inventory[["Title", "Author", "Genre", "Price"]],
			on="Title",
			how="left",
		)
		print("\nRevenue by Genre:")
		print(merged.groupby("Genre")["Total Revenue"].sum().sort_values(ascending=False))
		print("\nRevenue by Author:")
		print(
			merged.groupby("Author")["Total Revenue"]
			.sum()
			.sort_values(ascending=False)
			.head(10)
		)

		monthly_sales = self.sales.groupby(
			self.sales["Date"].dt.to_period("M")
		)["Total Revenue"].sum()
		if len(monthly_sales) > 1:
			growth = np.diff(monthly_sales) / monthly_sales.iloc[:-1].to_numpy() * 100
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
		sns.barplot(x=author_sales.values, y=author_sales.index, hue=author_sales.index, legend=False)
		plt.title("Total Sales by Author")
		plt.xlabel("Quantity Sold")
		plt.ylabel("Author")

		plt.subplot(2, 2, 2)
		monthly_sales = self.sales.groupby(
			self.sales["Date"].dt.to_period("M")
		)["Total Revenue"].sum()
		plt.plot(monthly_sales.index.astype(str), monthly_sales.values, marker="o")
		plt.title("Monthly Sales Trend")
		plt.xlabel("Month")
		plt.ylabel("Revenue")
		plt.xticks(rotation=45)

		plt.subplot(2, 2, 3)
		genre_revenue = merged.groupby("Genre")["Total Revenue"].sum()
		if genre_revenue.sum() > 0:
			plt.pie(genre_revenue.values, labels=genre_revenue.index, autopct="%1.1f%%")
		else:
			plt.text(0.5, 0.5, "No revenue data", ha="center", va="center")
		plt.title("Revenue Share by Genre")

		plt.subplot(2, 2, 4)
		correlation = merged[["Price", "Quantity Sold", "Total Revenue"]].corr()
		sns.heatmap(correlation, annot=True, cmap="coolwarm", fmt=".2f")
		plt.title("Correlation Heatmap")
		plt.tight_layout()
		plt.show()
		print("Generated graphs.")


def main():
	bookstore = Bookstore()
	print("\nWELCOME TO BOOKSTORE MANAGEMENT SYSTEM")

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
			choice = int(input("Enter your choice: "))
		except ValueError:
			print("Invalid choice. Enter only a number.")
			continue

		if choice == 1:
			title = input("Enter book title: ")
			author = input("Enter author: ")
			genre = input("Enter genre: ")
			try:
				price = float(input("Enter price: "))
				quantity = int(input("Enter quantity: "))
				bookstore.add_book(title, author, genre, price, quantity)
			except ValueError:
				print("Please enter valid numeric values.")
		elif choice == 2:
			title = input("Enter book title: ")
			try:
				quantity = int(input("Enter new quantity: "))
				bookstore.update_inventory(title, quantity)
			except ValueError:
				print("Quantity must be a number.")
		elif choice == 3:
			title = input("Enter book title: ")
			try:
				quantity = int(input("Enter quantity sold: "))
				bookstore.record_sale(title, quantity)
			except ValueError:
				print("Quantity must be a number.")
		elif choice == 4:
			bookstore.generate_report()
		elif choice == 5:
			bookstore.visualization()
		elif choice == 6:
			print(bookstore.inventory)
		elif choice == 7:
			print(bookstore.sales)
		elif choice == 8:
			print("Thank you for using Bookstore System.")
			break
		else:
			print("Invalid choice.")


@st.cache_resource
def get_bookstore():
	return Bookstore()


def save_data(bookstore):
	data_dir = Path(__file__).resolve().parent
	bookstore.inventory.to_csv(data_dir / "inventory.csv", index=False)
	bookstore.sales.to_csv(data_dir / "sales.csv", index=False)
	get_bookstore.clear()


def run_streamlit():
	st.set_page_config(page_title="Bookstore Dashboard", page_icon="Book", layout="wide")
	bookstore = get_bookstore()

	st.title("Bookstore Management Dashboard")
	st.caption("Inventory, sales and revenue analytics")

	with st.sidebar:
		page = st.radio("Open", ["Dashboard", "Inventory", "Sales", "Manage Books", "Reports"])

	if page == "Dashboard":
		first, second, third, fourth = st.columns(4)
		first.metric("Total Revenue", f"INR {bookstore.sales['Total Revenue'].sum():,.2f}")
		second.metric("Books Sold", int(bookstore.sales["Quantity Sold"].sum()))
		third.metric("Current Stock", int(bookstore.inventory["Quantity"].sum()))
		fourth.metric("Book Titles", len(bookstore.inventory))
		st.dataframe(bookstore.inventory, use_container_width=True, hide_index=True)

	elif page == "Inventory":
		st.header("Current Inventory")
		st.dataframe(bookstore.inventory, use_container_width=True, hide_index=True)

	elif page == "Sales":
		st.header("Sales Records")
		st.dataframe(bookstore.sales, use_container_width=True, hide_index=True)

	elif page == "Manage Books":
		st.header("Manage Books")
		with st.form("add_book_form"):
			title = st.text_input("Title")
			author = st.text_input("Author")
			genre = st.text_input("Genre")
			price = st.number_input("Price", min_value=0.01, step=1.0)
			quantity = st.number_input("Quantity", min_value=0, step=1)
			if st.form_submit_button("Add Book"):
				if not title.strip() or not author.strip() or not genre.strip():
					st.error("Title, author and genre are required.")
				else:
					bookstore.add_book(title.strip(), author.strip(), genre.strip(), price, int(quantity))
					save_data(bookstore)
					st.success("Book added successfully.")
					st.rerun()

		titles = bookstore.inventory["Title"].astype(str).tolist()
		if titles:
			selected_title = st.selectbox("Book to update or sell", titles)
			new_quantity = st.number_input("New quantity", min_value=0, step=1)
			if st.button("Update Stock"):
				bookstore.update_inventory(selected_title, int(new_quantity))
				save_data(bookstore)
				st.success("Inventory updated successfully.")
				st.rerun()

			sale_quantity = st.number_input("Quantity sold", min_value=1, step=1)
			if st.button("Record Sale"):
				stock = bookstore.inventory.loc[bookstore.inventory["Title"] == selected_title, "Quantity"].iloc[0]
				if sale_quantity > stock:
					st.error("Not enough stock available.")
				else:
					bookstore.record_sale(selected_title, int(sale_quantity))
					save_data(bookstore)
					st.success("Sale recorded successfully.")
					st.rerun()

	elif page == "Reports":
		st.header("Reports and Visualizations")
		merged = bookstore.sales.merge(bookstore.inventory[["Title", "Author", "Genre", "Price"]], on="Title", how="left")
		st.subheader("Best-selling books")
		st.bar_chart(bookstore.sales.groupby("Title")["Quantity Sold"].sum().sort_values(ascending=False).head(10))
		st.subheader("Revenue by genre")
		st.bar_chart(merged.groupby("Genre")["Total Revenue"].sum().sort_values(ascending=False))


if __name__ == "__main__":
	run_streamlit()
