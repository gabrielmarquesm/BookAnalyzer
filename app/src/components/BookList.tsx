import React from "react";

type Book = {
  id: string;
  title: string;
};

type BookListProps = {
  books: Book[];
};

const BookList: React.FC<BookListProps> = ({ books }) => {
  if (!books.length) return <p>No books available</p>;

  return (
    <ul>
      {books.map((book) => (
        <li key={book.id}>{book.title}</li>
      ))}
    </ul>
  );
};

export default BookList;
