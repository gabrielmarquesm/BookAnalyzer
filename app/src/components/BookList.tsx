import AskQuestion from "../components/askQuestion";
import styles from "../styles/User.module.css";
import { handleDelete } from "../utils/bookUtils";

interface BookListProps {
  books: { id: string; owner_id: string; title: string; file_path: string }[];
  fetchBooks: () => void;
}

const BookList = ({ books, fetchBooks }: BookListProps) => {
  if (!books.length) return <p>No books available</p>;

  return (
    <ul className={styles.bookList}>
      {books.map((book) => (
        <li key={book.id} className={styles.bookItem}>
          <a
            href={`file:../../${book.owner_id}/${book.file_path}`}
            target="_blank"
            rel="noopener noreferrer"
            className={styles.bookTitle}
          >
            {book.title}
          </a>
          <div className={styles.bookActions}>
            <button
              onClick={() => handleDelete(book.id, fetchBooks)}
              className={styles.button}
            >
              Delete
            </button>
            <div className={styles.askQuestionWrapper}>
              <AskQuestion bookId={book.id} />
            </div>
          </div>
        </li>
      ))}
    </ul>
  );
};

export default BookList;
