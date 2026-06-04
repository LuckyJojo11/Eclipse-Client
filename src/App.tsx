import { Download, Github, Home, ListChecks, CircleHelp } from "lucide-react";
import { useEffect, useState } from "react";
import "./styles.css";

const navButtons = [
  { label: "Home", href: "#", Icon: Home },
  { label: "Features", href: "#features", Icon: ListChecks },
  { label: "Download", href: "#download", Icon: Download },
  { label: "GitHub", href: "https://github.com/LuckyJojo11/Eclipse-Client", Icon: Github },
  { label: "About", href: "#about", Icon: CircleHelp }
];

type ReleaseInfo = {
  version: string;
  downloadUrl: string;
  fileName: string;
};

function App() {
  const [release, setRelease] = useState<ReleaseInfo | null>(null);
  const [releaseError, setReleaseError] = useState("");

  useEffect(() => {
    async function loadLatestRelease() {
      try {
        const response = await fetch("https://api.github.com/repos/LuckyJojo11/Eclipse-Client/releases/latest");
        if (!response.ok) {
          throw new Error("Could not load latest release.");
        }

        const data = await response.json();
        const asset = data.assets?.find((item: { name: string }) => item.name.endsWith(".exe"));

        setRelease({
          version: data.tag_name ?? "Latest",
          downloadUrl: asset?.browser_download_url ?? data.html_url,
          fileName: asset?.name ?? "Open release page"
        });
      } catch {
        setReleaseError("Latest release could not be loaded.");
      }
    }

    loadLatestRelease();
  }, []);

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
              <h3>{release ? release.version : "Latest Release"}</h3>
              <p>
                {release
                  ? `Download ${release.fileName}`
                  : releaseError || "Checking GitHub for the newest version..."}
              </p>
            </div>
            <a
              className="primary-button"
              href={release?.downloadUrl ?? "https://github.com/LuckyJojo11/Eclipse-Client/releases"}
            >
              {release ? "Download Latest" : "Open Downloads"}
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
