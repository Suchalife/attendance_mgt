import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Industrial Intelligence — Employee AMS",
  description: "Face-recognition powered attendance management for industrial workforce operations.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap"
          rel="stylesheet"
        />
        <link
          href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=swap"
          rel="stylesheet"
        />
      </head>
      <body style={{ fontFamily: "'Inter', sans-serif", background: "#f6fafd", margin: 0 }}>
        {children}
      </body>
    </html>
  );
}
