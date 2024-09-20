export const fetchBooks = async (setBooks: any) => {
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

    if (response.status === 404) {
      setBooks([]);
      return;
    }

    if (!response.ok) throw new Error("Failed to fetch books");
    const data = await response.json();
    setBooks(data);
  } catch (error) {
    console.error("Failed to fetch books", error);
  }
};

export const handleDelete = async (bookId: string, fetchBooks: () => void) => {
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

export const handleSearch = async (search: string, setBooks: any) => {
  const token = localStorage.getItem("token");
  try {
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_BASE_URL}/books/books?title=${search}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
    if (response.status === 404) {
      console.log("No books found");
      setBooks([]);
      return;
    }

    if (!response.ok) throw new Error("Failed to search books");
    const data = await response.json();
    setBooks(data);
  } catch (error) {
    console.error("Failed to search books", error);
  }
};
