"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("dev@careeros.local");

  const onContinue = () => {
    localStorage.setItem("careeros_dev_email", email);
    router.push("/dashboard");
  };

  return (
    <div className="mx-auto flex min-h-screen max-w-lg items-center px-4">
      <div className="card w-full p-8">
        <h1 className="text-2xl font-semibold">CareerOS Login</h1>
        <p className="mt-2 text-sm text-black/70">Dev-mode auth header for local backend.</p>
        <label className="mt-6 block text-sm font-medium">Email</label>
        <input
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="mt-2 w-full rounded-lg border border-black/15 px-3 py-2"
        />
        <button onClick={onContinue} className="mt-4 w-full rounded-lg bg-ember px-4 py-2 font-medium text-white">
          Continue
        </button>
      </div>
    </div>
  );
}
