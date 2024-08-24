import React, { useState, useEffect } from "react";
import { useRouter } from "next/router";
import styles from "../styles/User.module.css";
import AskQuestion from "../components/askQuestion";

const UserPage = () => {
  const [books, setBooks] = useState<any[]>([]);
  const [search, setSearch] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const router = useRouter();

  useEffect(() => {
    fetchBooks();
  }, []);

  const fetchBooks = async () => {
    const token = localStorage.getItem("token");
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/books/books`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      if (!response.ok) throw new Error("Failed to fetch books");
      const data = await response.json();
      setBooks(data);
    } catch (error) {
      console.error("Failed to fetch books", error);
    }
  };

  const handleDelete = async (bookId: string) => {
    const token = localStorage.getItem("token");
    try {
      await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/books/books/${bookId}`,
        {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      fetchBooks();
    } catch (error) {
      console.error("Failed to delete book", error);
    }
  };

  const handleSearch = async () => {
    try {
      const token = localStorage.getItem("token");
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/books/books?title=${search}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      if (!response.ok) throw new Error("Failed to search books");
      const data = await response.json();
      setBooks(data);
    } catch (error) {
      console.error("Failed to search books", error);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    const formData = new FormData();
    const fileUrl = URL.createObjectURL(file);

    formData.append("files", file);
    const token = localStorage.getItem("token");

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/books/book`,
        {
          method: "POST",
          body: formData,
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      if (!response.ok) throw new Error("Failed to upload book");
      fetchBooks();
    } catch (error) {
      console.error("Failed to upload book", error);
    }
  };

  return (
    <div className={styles.container}>
      <h1 className={styles.heading}>Welcome to Your Books</h1>

      <input
        type="text"
        placeholder="Search by title"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className={styles.input}
      />
      <button onClick={handleSearch} className={styles.button}>
        Search
      </button>

      <input
        type="file"
        onChange={(e) => setFile(e.target.files ? e.target.files[0] : null)}
        className={styles.input}
      />
      <button onClick={handleUpload} className={styles.button}>
        Upload Book
      </button>

      <ul className={styles.bookList}>
        {books.map((book) => (
          <li key={book.id} className={styles.bookItem}>
            <a
              href={`file:../../${book.owner_id}}/${book.file_path}`}
              target="_blank"
              rel="noopener noreferrer"
              className={styles.bookTitle}
            >
              {book.title}
            </a>
            <div className={styles.bookActions}>
              <button
                onClick={() => handleDelete(book.id)}
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
    </div>
  );
};

export default UserPage;
