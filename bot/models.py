from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey, Text
from sqlalchemy.types import TIMESTAMP

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    collections = relationship("Collection", back_populates="user", cascade="all, delete-orphan")
    added_words = relationship("AddedWord", back_populates="user", cascade="all, delete-orphan")

class Collection(Base):
    __tablename__ = "collections"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    user = relationship("User", back_populates="collections")
    added_words = relationship("AddedWord", back_populates="collection", cascade="all, delete-orphan")

class Word(Base):
    __tablename__ = "words"

    id = Column(Integer, primary_key=True)
    english_word = Column(String, nullable=False, unique=True)
    translations = relationship("Translation", back_populates="word", cascade="all, delete-orphan")
    added_words = relationship("AddedWord", back_populates="word", cascade="all, delete-orphan")

class Translation(Base):
    __tablename__ = "translations"

    id = Column(Integer, primary_key=True)
    word_id = Column(Integer, ForeignKey("words.id", ondelete="CASCADE"))
    translation = Column(String, nullable=False)
    example_en = Column(Text)
    example_ru = Column(Text)
    word = relationship("Word", back_populates="translations")
    added_words = relationship("AddedWord", back_populates="translation", cascade="all, delete-orphan")

class AddedWord(Base):
    __tablename__ = "added_words"

    id = Column(Integer, primary_key=True)
    word_id = Column(Integer, ForeignKey("words.id", ondelete="CASCADE"))
    translation_id = Column(Integer, ForeignKey("translations.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    collection_id = Column(Integer, ForeignKey("collections.id", ondelete="CASCADE"))
    next_repeat = Column(type_=TIMESTAMP(timezone=True), nullable=True)

    user = relationship("User", back_populates="added_words")
    word = relationship("Word", back_populates="added_words")
    translation = relationship("Translation", back_populates="added_words")
    collection = relationship("Collection", back_populates="added_words")
