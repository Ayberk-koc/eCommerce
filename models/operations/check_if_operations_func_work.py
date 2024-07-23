from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.models import Base
from product_operations import get_products_info
from cart_operations import add_to_cart, get_cart_info, remove_from_cart, calc_price_list



# Setup test database
TEST_DATABASE_URL = "mysql://root:pin11221122@localhost/paypal_flasktut" # _test  das an den link machen für test db,
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(engine)
db = TestingSessionLocal()






#print(get_products_info(db))

#add_to_cart(db, "hallo", 6, 3)
# remove_from_cart(db, "hallo", 2)
# remove_from_cart(db, 1, 2)
print(get_cart_info(db, "hallo"))

#print(calc_price_list(get_cart_info(db, "hallo")))


