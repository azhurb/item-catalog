from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base, Category, CategoryItem, User

engine = create_engine('sqlite:///catalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

User1 = User(
    name="Oleksii Zhurbytskyi", email="zhurbitsky@gmail.com",
    picture="https://lh3.googleusercontent.com/-pRA8Hgrls18/"
    "AAAAAAAAAAI/AAAAAAAAH8w/6-AqEE8pjfc/photo.jpg")
session.add(User1)
session.commit()

category1 = Category(user_id=1, name="Snowboarding")
session.add(category1)
session.commit()

categoryItem1 = CategoryItem(
    user_id=1,
    name="Snowboard",
    description="Snowboards are boards that are usually the width of one's "
    "foot longways, with the ability to glide on snow. Snowboards are "
    "differentiated from monoskis by the stance of the user.",
    category=category1)
session.add(categoryItem1)
session.commit()

categoryItem2 = CategoryItem(
    user_id=1,
    name="Goggles",
    description="Bindings are separate components from the snowboard deck "
    "and are very important parts of the total snowboard interface. ",
    category=category1)
session.add(categoryItem2)
session.commit()

categoryItem3 = CategoryItem(
    user_id=1,
    name="Bindings",
    description="Ski goggles and snowboard goggles can help protect your "
    "eyes from these on-mountain hazards, making your outing a lot more "
    "enjoyable.",
    category=category1)
session.add(categoryItem3)
session.commit()

category2 = Category(user_id=1, name="Soccer")
session.add(category2)
session.commit()

categoryItem1 = CategoryItem(
    user_id=1,
    name="Jersey",
    description="A jersey as used in sport is a shirt worn by a member of a "
    "team, typically depicting the athlete's name and team number as well as "
    "the logotype of the team or corporate sponsor.",
    category=category2)
session.add(categoryItem1)
session.commit()

categoryItem2 = CategoryItem(
    user_id=1,
    name="Shin guard",
    description="A shin guard or shin pad is a piece of equipment worn on "
    "the front of a player's shin to protect them from injury.",
    category=category2)
session.add(categoryItem2)
session.commit()

categoryItem3 = CategoryItem(
    user_id=1,
    name="Football boot",
    description="Football boots, called cleats or soccer shoes in North "
    "America, are an item of footwear worn when playing football.",
    category=category2)
session.add(categoryItem3)
session.commit()

category3 = Category(user_id=1, name="Hockey")
session.add(category3)
session.commit()

categoryItem1 = CategoryItem(
    user_id=1,
    name="Stick",
    description="A hockey stick is a piece of equipment used by the players "
    "in most forms of hockey to move the ball or puck.",
    category=category3)
session.add(categoryItem1)
session.commit()

categoryItem2 = CategoryItem(
    user_id=1,
    name="Helmet",
    description="A helmet with strap, and optionally a face cage or visor, "
    "is required of all ice hockey players.",
    category=category3)
session.add(categoryItem2)
session.commit()

categoryItem3 = CategoryItem(
    user_id=1,
    name="Shoulder pads",
    description="Hockey shoulder pads are typically composed of a passed "
    "vest with front and back panels, with velcro straps for closure, and "
    "soft or hard-shelled shoulder caps with optional attached upper "
    "arm pads.",
    category=category3)
session.add(categoryItem3)
session.commit()

print "added category items!"
