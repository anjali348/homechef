import Link from "next/link";
import "./globals.css";

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <nav className="border-b border-[#EAE0D0] bg-white/60 px-6 py-4">
          <div className="mx-auto flex max-w-2xl gap-6">
            <Link href="/" className="font-serif text-[#3F6B3F] hover:text-[#2F512F]">Pantry</Link>
            <Link href="/chat" className="font-serif text-[#3F6B3F] hover:text-[#2F512F]">Ask</Link>
            <Link href="/add" className="font-serif text-[#3F6B3F] hover:text-[#2F512F]">Add recipe</Link>
          </div>
        </nav>
        {children}
      </body>
    </html>
  );
}