export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html>
      <head>
        <script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXX"></script>
        <script dangerouslySetInnerHTML={{ __html: "fbq('init', '123');" }} />
      </head>
      <body>{children}</body>
    </html>
  );
}
