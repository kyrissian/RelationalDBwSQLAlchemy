"""
Assignment: Relational Database Management with SQLAlchemy
Author: Kyris
Description:
    Practice creating and managing a relational database using Python
    and SQLAlchemy. Defines tables, sets up relationships, and performs
    basic CRUD operations using SQLite as the database backend.
"""

# ---------- Part 1: Setup ----------
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean, select, func, CheckConstraint
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, selectinload

engine = create_engine('sqlite:///shop.db')
Base = declarative_base()
Session = sessionmaker(bind=engine)  # pylint: disable=invalid-name


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
    name = Column(String(100), nullable=False)
    email = Column(String(200), unique=True, nullable=False)

    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"User(id={self.id}, name={self.name!r}, email={self.email!r})"


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
    __table_args__ = (
        CheckConstraint("price >= 0", name="ck_products_price_non_negative"),
    )

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    price = Column(Integer, nullable=False)

    orders = relationship("Order", back_populates="product")

    def __repr__(self):
        return f"Product(id={self.id}, name={self.name!r}, price={self.price})"


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
    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_orders_quantity_positive"),
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    status = Column(Boolean, default=False, nullable=False)

    user = relationship("User", back_populates="orders")
    product = relationship("Product", back_populates="orders")

    def __repr__(self):
        return (
            "Order("
            f"id={self.id}, user_id={self.user_id}, product_id={self.product_id}, "
            f"quantity={self.quantity}, status={self.status}"
            ")"
        )


# ---------- Part 3: Create Tables ----------
Base.metadata.create_all(engine)


# ---------- Part 4: Insert Data ----------
def insert_sample_data(session):
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
        users = {
            "Kathy": User(name="Kathy", email="kathy@example.com"),
            "Andrea": User(name="Andrea", email="andrea@example.com"),
            "Brendan": User(name="Brendan", email="brendan@example.com"),
            "LuLu": User(name="LuLu", email="lulu@example.com"),
            "Marcus": User(name="Marcus", email="marcus@example.com"),
        }

        # 5 products
        products = {
            "Laptop": Product(name="Laptop", price=1200),
            "Headphones": Product(name="Headphones", price=150),
            "Mouse": Product(name="Mouse", price=40),
            "Keyboard": Product(name="Keyboard", price=80),
            "Webcam": Product(name="Webcam", price=100),
        }

        for user in users.values():
            session.add(user)

        for product in products.values():
            session.add(product)

        # 5 orders spread across 4 users (Marcus has none)
        orders = [
            Order(user=users["Kathy"], product=products["Laptop"], quantity=1, status=True),
            Order(user=users["Kathy"], product=products["Mouse"], quantity=2, status=False),
            Order(user=users["Andrea"], product=products["Headphones"], quantity=1, status=False),
            Order(user=users["Brendan"], product=products["Keyboard"], quantity=3, status=True),
            Order(user=users["LuLu"], product=products["Webcam"], quantity=2, status=False),
        ]

        for order in orders:
            session.add(order)
        session.commit()

        print("Sample data inserted.\n")
    else:
        print("Data already exists — skipping insert.\n")


def query_all_users(session):
    """Retrieves and prints all users in the database."""
    print("--- All Users ---")
    users = session.execute(select(User)).scalars().all()
    for u in users:
        print(f"  id={u.id} | name={u.name} | email={u.email}")


def query_all_products(session):
    """Retrieves and prints all products with their name and price."""
    print("\n--- All Products ---")
    products = session.execute(select(Product)).scalars().all()
    for p in products:
        print(f"  {p.name}: ${p.price}")


def query_all_orders(session):
    """
    Retrieves and prints all orders, showing the user's name,
    product name, quantity, and shipping status.
    """
    print("\n--- All Orders ---")
    orders = session.execute(
        select(Order).options(selectinload(Order.user), selectinload(Order.product))
    ).scalars().all()
    for o in orders:
        shipped = "shipped" if o.status else "not shipped"
        print(f"  {o.user.name} ordered {o.quantity}x {o.product.name} [{shipped}]")


def update_product_price(session, product_name, new_price):
    """
    Updates the price of a product by name.

    Args:
        product_name (str): The name of the product to update.
        new_price (int): The new price to set in dollars.
    """
    print(f"\n--- Updating {product_name} price ---")
    if new_price < 0:
        print("  Price cannot be negative.")
        return

    product = (session.execute(select(Product)
               .where(Product.name == product_name))
               .scalars().first())
    if product:
        print(f"  Old price: ${product.price}")
        if product.price == new_price:
            print("  Price unchanged; no update needed.")
            return
        product.price = new_price
        session.commit()
        print(f"  New price: ${product.price}")
    else:
        print(f"  No product named '{product_name}' found.")


def delete_user_by_id(session, user_id):
    """
    Deletes a user from the database by their primary key ID.

    Because cascade="all, delete-orphan" is configured on User.orders,
    any orders belonging to the deleted user are automatically removed
    from the orders table as well — no manual cleanup required.
    This demonstrates referential integrity enforced at the ORM level.

    Args:
        user_id (int): The primary key ID of the user to delete.
    """
    print(f"\n--- Deleting user with id={user_id} ---")
    user = session.execute(select(User).where(User.id == user_id)).scalars().first()
    if user:
        order_count = len(user.orders)
        print(f"  Deleting: {user.name} (id={user.id}) — had {order_count} order(s)")
        session.delete(user)
        session.commit()
        print("  Deleted successfully.")
    else:
        print(f"  No user with id={user_id} found.")


def run_delete_user_by_id_demo(session, target_name="Marcus"):
    """
    Demonstrates the Part 5 delete-by-ID requirement using a known user.

    Args:
        target_name (str): Name used to look up a user ID for deletion.
    """
    target_user = session.execute(select(User).where(User.name == target_name)).scalars().first()
    if target_user:
        delete_user_by_id(session, target_user.id)
    else:
        print("\n--- Deleting user by ID ---")
        print(f"  '{target_name}' was already deleted in a prior run.")


def query_unshipped_orders(session):
    """
    Bonus: Retrieves and prints all orders that have not yet been shipped
    (status=False).
    """
    print("\n--- Unshipped Orders ---")
    unshipped = session.execute(
        select(Order)
        .where(Order.status.is_(False))
        .options(selectinload(Order.user), selectinload(Order.product))
    ).scalars().all()
    if unshipped:
        for o in unshipped:
            print(f"  Order {o.id}: {o.quantity}x {o.product.name} for {o.user.name}")
    else:
        print("  No unshipped orders.")


def query_order_count_per_user(session):
    """
    Bonus: Counts and prints the total number of orders placed by each user,
    using a SQL GROUP BY aggregation.
    """
    print("\n--- Order Count per User ---")
    results = session.execute(
        select(User.name, func.count(Order.id))  # pylint: disable=not-callable
        .outerjoin(Order, Order.user_id == User.id)
        .group_by(User.name)
    ).all()
    for name, count in results:
        print(f"  {name}: {count} order(s)")


# ---------- Run all steps ----------
if __name__ == "__main__":
    with Session() as db_session:
        insert_sample_data(db_session)
        query_all_users(db_session)
        query_all_products(db_session)
        query_all_orders(db_session)
        update_product_price(db_session, "Laptop", 1100)
        run_delete_user_by_id_demo(db_session)
        query_unshipped_orders(db_session)
        query_order_count_per_user(db_session)
