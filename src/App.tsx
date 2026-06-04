import { Download, Github, Home, ListChecks, CircleHelp } from "lucide-react";
import "./styles.css";

const navButtons = [
  { label: "Home", href: "#", Icon: Home },
  { label: "Features", href: "#features", Icon: ListChecks },
  { label: "Download", href: "#download", Icon: Download },
  { label: "GitHub", href: "https://github.com/LuckyJojo11/Eclipse-Client", Icon: Github },
  { label: "About", href: "#about", Icon: CircleHelp }
];

function App() {
  return (
    <>
      <header className="topbar">
        <a className="topbar-logo" href="#">
          Eclipse Client
        </a>

        <nav className="topbar-nav">
          {navButtons.map((button) => (
            <a href={button.href} key={button.label}>
              <button.Icon size={16} />
              {button.label}
            </a>
          ))}
        </nav>
      </header>

      <main className="page">
        <section className="hero">
          <p className="eyebrow">Minecraft Launcher</p>
          <h1>Eclipse Client</h1>
          <p className="hero-text">
            A custom Minecraft launcher focused on simple instance management, modded
            Minecraft support and a clean launcher experience.
          </p>

          <div className="actions">
            <a className="primary-button" href="https://github.com/LuckyJojo11/Eclipse-Client/releases">
              Download
            </a>
            <a className="secondary-button" href="https://github.com/LuckyJojo11/Eclipse-Client">
              View on GitHub
            </a>
          </div>
        </section>

        <section className="section" id="features">
          <h2>Features</h2>
          <div className="feature-grid">
            <article>
              <h3>Instances</h3>
              <p>Create separate profiles for different Minecraft versions and mod loaders.</p>
            </article>
            <article>
              <h3>Modding</h3>
              <p>Designed for Vanilla, Fabric, Forge and NeoForge instances.</p>
            </article>
            <article>
              <h3>Downloads</h3>
              <p>Future releases will be available directly from the GitHub Releases page.</p>
            </article>
          </div>
        </section>

        <section className="section download-section" id="download">
          <h2>Download</h2>
          <p>
            The newest public builds are published on GitHub Releases. Choose the latest
            release and download the file for Windows.
          </p>

          <div className="download-card">
            <div>
              <h3>Latest Release</h3>
              <p>Download Eclipse Client from the official GitHub release page.</p>
            </div>
            <a className="primary-button" href="https://github.com/LuckyJojo11/Eclipse-Client/releases">
              Open Downloads
            </a>
          </div>
        </section>

        <section className="section info-box" id="install">
          <h2>How to install</h2>
          <ol>
            <li>Open the GitHub Releases page.</li>
            <li>Download the newest Eclipse Client release.</li>
            <li>Extract or run the downloaded file.</li>
            <li>Follow the setup instructions shown by the launcher.</li>
          </ol>
        </section>

        <section className="section" id="about">
          <h2>About</h2>
          <p>
            Eclipse Client is a fan-made launcher project by LuckyJojo11. The goal is to
            make Minecraft instance management easier and provide a clean place for downloads,
            modding information and setup instructions.
          </p>
          <p>
            The project is currently being rebuilt, so this website will grow together with
            the new launcher.
          </p>
        </section>

        <section className="section warning">
          <h2>Important note</h2>
          <p>
            Eclipse Client is a fan-made project. It is not an official Minecraft product
            and is not affiliated with Mojang or Microsoft.
          </p>
        </section>
      </main>
    </>
  );
}

export default App;
