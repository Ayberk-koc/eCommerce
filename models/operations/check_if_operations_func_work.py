from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.models import Base
from product_operations import get_products_info
from cart_operations import add_to_cart, get_cart_info, remove_from_cart



# Setup test database
TEST_DATABASE_URL = "mysql://root:pin11221122@localhost/paypal_flasktut_test" #teste mit test database
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(engine)
db = TestingSessionLocal()





#print(get_products_info(db))

# add_to_cart(db, 1, 1, 4)
remove_from_cart(db, 1, 1)
print(get_cart_info(db, 1))




