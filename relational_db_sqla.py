"""
Assignment: Relational Database Management with SQLAlchemy
Author: Kyris
Description:
    Practice creating and managing a relational database using Python
    and SQLAlchemy. Defines tables, sets up relationships, and performs
    basic CRUD operations using SQLite as the database backend.
"""

# ---------- Part 1: Setup ----------
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean, select, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

engine = create_engine('sqlite:///shop.db')
Base = declarative_base()
Session = sessionmaker(bind=engine)  # pylint: disable=invalid-name
session = Session()


# ---------- Part 2: Define Tables ----------
class User(Base):
    """
    Represents a customer in the shop database.

    Attributes:
        id (int): Primary key, auto-incremented.
        name (str): The user's full name.
        email (str): The user's email address. Must be unique.
        orders (list[Order]): All orders placed by this user.
            Cascade delete ensures orders are removed if the user is deleted.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    email = Column(String(200), unique=True)

    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")


class Product(Base):
    """
    Represents a product available for purchase in the shop.

    Attributes:
        id (int): Primary key, auto-incremented.
        name (str): The product's name.
        price (int): The product's price in dollars.
        orders (list[Order]): All orders that include this product.
    """

    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    price = Column(Integer)

    orders = relationship("Order", back_populates="product")


class Order(Base):
    """
    Represents a purchase order linking a User to a Product.

    Attributes:
        id (int): Primary key, auto-incremented.
        user_id (int): Foreign key referencing the User who placed the order.
        product_id (int): Foreign key referencing the Product being ordered.
        quantity (int): Number of units ordered.
        status (bool): Shipping status. False = not shipped, True = shipped.
        user (User): The User object associated with this order.
        product (Product): The Product object associated with this order.
    """

    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer)
    status = Column(Boolean, default=False)

    user = relationship("User", back_populates="orders")
    product = relationship("Product", back_populates="orders")


# ---------- Part 3: Create Tables ----------
Base.metadata.create_all(engine)


# ---------- Part 4: Insert Data ----------
def insert_sample_data():
    """
    Inserts sample users, products, and orders into the database.

    Only runs if the database is empty, preventing duplicate rows
    on subsequent script executions.

    Users:
        - Kathy, Andrea, Brendan, LuLu each receive at least one order.
        - Marcus is intentionally left without any orders so he can be
          used to demonstrate a clean user deletion in Part 5.

    Products:
        Five products are created across a range of price points.

    Orders:
        Five orders are distributed across four users, with a mix of
        shipped (status=True) and unshipped (status=False) orders for
        use in the Bonus queries.
    """
    existing_users = session.execute(select(User)).scalars().first()

    if not existing_users:
        # 5 users — Marcus has no orders and will be deleted in Part 5
        user1 = User(name="Kathy",   email="kathy@example.com")
        user2 = User(name="Andrea",  email="andrea@example.com")
        user3 = User(name="Brendan", email="brendan@example.com")
        user4 = User(name="LuLu",    email="lulu@example.com")
        user5 = User(name="Marcus",  email="marcus@example.com")

        # 5 products
        product1 = Product(name="Laptop",     price=1200)
        product2 = Product(name="Headphones", price=150)
        product3 = Product(name="Mouse",      price=40)
        product4 = Product(name="Keyboard",   price=80)
        product5 = Product(name="Webcam",     price=100)

        session.add_all([user1, user2, user3, user4, user5,
                         product1, product2, product3, product4, product5])
        session.commit()

        # 5 orders spread across 4 users (Marcus has none)
        order1 = Order(user_id=user1.id, product_id=product1.id, quantity=1, status=True)
        order2 = Order(user_id=user1.id, product_id=product3.id, quantity=2, status=False)
        order3 = Order(user_id=user2.id, product_id=product2.id, quantity=1, status=False)
        order4 = Order(user_id=user3.id, product_id=product4.id, quantity=3, status=True)
        order5 = Order(user_id=user4.id, product_id=product5.id, quantity=2, status=False)

        session.add_all([order1, order2, order3, order4, order5])
        session.commit()

        print("Sample data inserted.\n")
    else:
        print("Data already exists — skipping insert.\n")


def query_all_users():
    """Retrieves and prints all users in the database."""
    print("--- All Users ---")
    users = session.execute(select(User)).scalars().all()
    for u in users:
        print(f"  id={u.id} | name={u.name} | email={u.email}")


def query_all_products():
    """Retrieves and prints all products with their name and price."""
    print("\n--- All Products ---")
    products = session.execute(select(Product)).scalars().all()
    for p in products:
        print(f"  {p.name}: ${p.price}")


def query_all_orders():
    """
    Retrieves and prints all orders, showing the user's name,
    product name, quantity, and shipping status.
    """
    print("\n--- All Orders ---")
    orders = session.execute(select(Order)).scalars().all()
    for o in orders:
        shipped = "shipped" if o.status else "not shipped"
        print(f"  {o.user.name} ordered {o.quantity}x {o.product.name} [{shipped}]")


def update_product_price(product_name, new_price):
    """
    Updates the price of a product by name.

    Args:
        product_name (str): The name of the product to update.
        new_price (int): The new price to set in dollars.
    """
    print(f"\n--- Updating {product_name} price ---")
    product = (session.execute(select(Product)
               .where(Product.name == product_name))
               .scalars().first())
    if product:
        print(f"  Old price: ${product.price}")
        product.price = new_price
        session.commit()
        print(f"  New price: ${product.price}")
    else:
        print(f"  No product named '{product_name}' found.")


def delete_user_by_name(name):
    """
    Deletes a user from the database by name.

    If the user has existing orders and cascade delete is configured,
    those orders will be removed automatically. For best results,
    use this on a user with no orders to demonstrate a clean deletion.

    Args:
        name (str): The name of the user to delete.
    """
    print(f"\n--- Deleting user: {name} ---")
    user = session.execute(select(User).where(User.name == name)).scalars().first()
    if user:
        order_count = len(user.orders)
        print(f"  Deleting: {user.name} (id={user.id}) — had {order_count} order(s)")
        session.delete(user)
        session.commit()
        print("  Deleted successfully.")
    else:
        print(f"  No user named '{name}' found.")


def query_unshipped_orders():
    """
    Bonus: Retrieves and prints all orders that have not yet been shipped
    (status=False).
    """
    print("\n--- Unshipped Orders ---")
    unshipped = session.execute(select(Order).where(Order.status == False)).scalars().all()  # pylint: disable=singleton-comparison
    if unshipped:
        for o in unshipped:
            print(f"  Order {o.id}: {o.quantity}x {o.product.name} for {o.user.name}")
    else:
        print("  No unshipped orders.")


def query_order_count_per_user():
    """
    Bonus: Counts and prints the total number of orders placed by each user,
    using a SQL GROUP BY aggregation.
    """
    print("\n--- Order Count per User ---")
    results = session.execute(
        select(User.name, func.count(Order.id))  # pylint: disable=not-callable
        .join(Order, Order.user_id == User.id)
        .group_by(User.name)
    ).all()
    for name, count in results:
        print(f"  {name}: {count} order(s)")


# ---------- Run all steps ----------
if __name__ == "__main__":
    insert_sample_data()
    query_all_users()
    query_all_products()
    query_all_orders()
    update_product_price("Laptop", 1100)
    delete_user_by_name("Marcus")
    query_unshipped_orders()
    query_order_count_per_user()
