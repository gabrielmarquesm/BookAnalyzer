import React, { useState, useEffect } from "react";
import { useRouter } from "next/router";
import styles from "../styles/User.module.css";
import BookList from "../components/BookList";
import {
  fetchBooks as fetchBooksUtil,
  handleDelete,
  handleSearch,
} from "../utils/bookUtils";

const UserPage = () => {
  const [books, setBooks] = useState<any[]>([]);
  const [search, setSearch] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const router = useRouter();

  const fetchBooks = async () => {
    await fetchBooksUtil(setBooks);
  };

  useEffect(() => {
    fetchBooks();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("token");
    router.push("/login");
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  };

  const handleFileUpload = async () => {
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
      {/* Page Title */}
      <h1 className={styles.pageTitle}>Your Book List</h1>

      {/* Logout Button */}
      <button onClick={handleLogout} className={styles.logoutButton}>
        Logout
      </button>

      {/* Search Input */}
      <input
        type="text"
        placeholder="Search by title"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className={styles.searchInput}
      />
      <button
        onClick={() => handleSearch(search, setBooks)}
        className={styles.searchButton}
      >
        Search
      </button>

      {/* File Input and Upload Button */}
      <div className={styles.uploadWrapper}>
        <input
          type="file"
          onChange={handleFileChange}
          className={styles.fileInput}
        />
        <button
          onClick={handleFileUpload}
          className={styles.uploadButton}
          disabled={!file}
        >
          Upload Book
        </button>
      </div>

      {/* Book List */}
      <BookList books={books} fetchBooks={fetchBooks} />
    </div>
  );
};

export default UserPage;
