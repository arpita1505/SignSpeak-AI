"""Main Header component."""
import './Header.css'

export function Header() {
  return (
    <header className="header">
      <div className="header-content">
        <h1 className="header-title">SignSpeak AI</h1>
        <p className="header-subtitle">
          Real-Time Indian Sign Language to Text and Speech Translator
        </p>
      </div>
    </header>
  )
}
