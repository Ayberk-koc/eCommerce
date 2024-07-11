import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models import Base
from models.operations.product_operations import get_products_info





# Setup test database
TEST_DATABASE_URL = "mysql://root:pin11221122@localhost/paypal_flasktut"
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

def test_get_products_info(db_session: Session):
    dict = get_products_info(db_session)
    return dict





# def test_create_product(db_session):
#     product = create_product(db_session, "Test Product", "This is a test", 9.99)
#     assert product.name == "Test Product"
#     assert product.price == 9.99
#
# def test_get_product(db_session):
#     product = create_product(db_session, "Test Product", "This is a test", 9.99)
#     retrieved_product = get_product(db_session, product.id)
#     assert retrieved_product is not None
#     assert retrieved_product.name == "Test Product"
#
# def test_get_all_products(db_session):
#     create_product(db_session, "Product 1", "Description 1", 9.99)
#     create_product(db_session, "Product 2", "Description 2", 19.99)
#     products = get_all_products(db_session)
#     assert len(products) == 2
#     assert products[0].name in ["Product 1", "Product 2"]
#     assert products[1].name in ["Product 1", "Product 2"]


















