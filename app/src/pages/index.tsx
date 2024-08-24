import React from "react";
import { useRouter } from "next/router";

const HomePage = () => {
  const router = useRouter();

  React.useEffect(() => {

    router.push("/login");
  }, [router]);

  return null;
};

export default HomePage;
