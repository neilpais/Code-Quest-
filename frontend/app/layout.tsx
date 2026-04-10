import "./globals.css"
import { Press_Start_2P } from "next/font/google"

const pixelFont = Press_Start_2P({
  subsets: ["latin"],
  weight: "400"
})

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body suppressHydrationWarning>
        <div className={pixelFont.className}>
          {children}
        </div>
      </body>
    </html>
  )
}
