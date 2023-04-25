import streamlit as st

from typing import List
from sqlalchemy import create_engine, select, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, Session, relationship


class Base(DeclarativeBase):
    pass


class Restaurant(Base):
    __tablename__ = "restaurant"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    image_url: Mapped[str] = mapped_column(nullable=True)
    reviews: Mapped[List["Review"]] = relationship(
        back_populates="restaurant", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"Restaurant(id={self.id}, name={self.name}, number of reviews={len(self.reviews)}"


class Review(Base):
    __tablename__ = "review"
    id: Mapped[int] = mapped_column(primary_key=True)
    stars: Mapped[int]
    body: Mapped[str]

    restaurant_id: Mapped[int] = mapped_column(ForeignKey("restaurant.id"))
    restaurant: Mapped["Restaurant"] = relationship(back_populates="reviews")

    def __repr__(self) -> str:
        return f"Review(id={self.id}, stars={self.stars}, body={self.body}"


engine = create_engine("postgresql+psycopg2://user:password@localhost/db", echo=True)
#engine = create_engine("sqlite://", echo=True)
Base.metadata.create_all(engine)

if st.button(label="Drop tables", key=48302):
    with Session(engine) as session:
        session.query(Review).delete()
        session.commit()


def populate_with_sample_data():
    with Session(engine) as session:
        bocca_di_lupo = Restaurant(name="Bocca Di Lupo", image_url="https://cdn.squaremeal.co.uk/restaurants/2314/images/bocca-di-lupo-menu_30012020112543.jpg")
        mcdonalds = Restaurant(name="McDonald's", image_url="https://media-cdn.tripadvisor.com/media/photo-s/12/4d/a7/46/en-la-esquina-de-eltham.jpg")
        wong_kei = Restaurant(name="Wong Kei", image_url="https://chinatown.co.uk/wp-content/uploads/2016/08/wongkeiBeijing-Dumpling_Qumin-Genevieve-Stevenson-1-10d2aj-1.jpg")

        session.add_all([
            Review(
                restaurant=bocca_di_lupo,
                stars=4,
                body="Really good, would recommend."
            ),
            Review(
                restaurant=mcdonalds,
                stars=5,
                body="Great food, impressive atmosphere to boot."
            ),
            Review(
                restaurant=mcdonalds,
                stars=3,
                body="Awful, smelt like sick. Good nuggets."
            ),
            Review(
                restaurant=wong_kei,
                stars=2,
                body="Asked for rice, got noodles."
            )
        ])
        session.commit()



st.header("Add restaurant")
restaurant_name = st.text_input(label="Restaurant name")
image_url = st.text_input(label="Image URL")

if st.button(label="Submit restaurant"):
    with Session(engine) as session:
        session.add(Restaurant(
            name=restaurant_name,
            image_url=image_url,
        )),
        session.commit()
if st.button(label="Add sample data"):
    populate_with_sample_data()
st.divider()

st.subheader("Leave a review")
with Session(engine) as session:
    stmt = select(Restaurant)

    restaurants = [restaurant.name for restaurant in session.scalars(stmt)]
    restaurant_name = st.selectbox(label="Restaurant", options=restaurants)
    restaurant = session.query(Restaurant).filter(Restaurant.name == restaurant_name).first()
    stars = st.number_input(label="Stars (/5)", min_value=1, max_value=5, step=1)
    body = st.text_area(label="Review")
    if st.button(label="Submit review"):
        session.add(Review(restaurant=restaurant, stars=stars, body=body))
        session.commit()
        pass

    st.divider()

    stmt = select(Restaurant)

    for restaurant in session.scalars(stmt):
        st.header(restaurant.name)
        if restaurant.image_url:
            st.image(restaurant.image_url)
        if restaurant.reviews:
            st.subheader(f"Average rating: {sum([review.stars for review in restaurant.reviews])/len(restaurant.reviews):.1f}")
            st.subheader("Reviews")
            for review in restaurant.reviews:
                import random
                st.markdown(f"user{random.randint(100,  1000)}: **{review.stars}/5** '{review.body}'")
        else:
            st.markdown("*Be the first to leave a review!*")

        st.divider()
