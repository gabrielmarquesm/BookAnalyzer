import { useEffect } from 'react';
import { useRouter } from 'next/router';
import axios from 'axios';

const useAuth = () => {
  const router = useRouter();

  useEffect(() => {
    const checkAuth = async () => {
      try {
        await axios.get('/api/auth/check');
      } catch {
        router.push('/login');
      }
    };

    checkAuth();
  }, [router]);
};

export default useAuth;
