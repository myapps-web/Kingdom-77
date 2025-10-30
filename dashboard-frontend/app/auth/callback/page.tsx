/**
 * Auth Callback - Handle Discord OAuth2 Callback
 */

'use client';

import { useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Loading from '@/components/Loading';

export default function AuthCallback() {
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    const handleCallback = async () => {
      const code = searchParams.get('code');
      const error = searchParams.get('error');

      if (error) {
        console.error('OAuth error:', error);
        router.push('/?error=auth_failed');
        return;
      }

      if (!code) {
        router.push('/');
        return;
      }

      try {
        // Exchange code for token
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/login`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ code }),
        });

        if (!response.ok) {
          throw new Error('Failed to login');
        }

        const data = await response.json();
        
        // Store token and user info
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('user', JSON.stringify(data.user));

        // Redirect to dashboard
        router.push('/dashboard');
      } catch (error) {
        console.error('Login failed:', error);
        router.push('/?error=login_failed');
      }
    };

    handleCallback();
  }, [router, searchParams]);

  return <Loading />;
}
