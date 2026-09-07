bearzo.club — Bearzo1_YT website
================================

Single self-contained page for the YouTuber Bearzo1_YT.
Deploys to: bearzo.club

FILES
  index.html    The site (HTML + CSS + JS in one file).
  credits.html   Credits / attribution page, linked from the footer.
  changelog.html Dated log of every change, linked from the footer next to credits.
                 Newest entry goes at the TOP of <ul class="log">; give it
                 class="entry now" and move the "now" class off the old one.
                 Tags: add / rem / chg / fix.
  images/        All artwork (Nova Skin renders, favicon, the two bear cutouts).
                 UPLOAD THIS FOLDER TOO - without it the site shows no images.

TO DEPLOY
  Upload index.html, credits.html, changelog.html AND the images/ folder.
  Any static host works — Netlify (drag the folder in), Cloudflare Pages,
  GitHub Pages, Vercel, or plain shared hosting.

CSS IS NOW COMPILED & INLINED (no Tailwind CDN) — colors/layout load
  reliably on GitHub Pages / any static host.

NEEDS INTERNET AT VIEW TIME (loaded externally, not bundled):
  - Google Fonts (Space Grotesk / JetBrains Mono / Press Start 2P / Inter)
  - Channel avatar + video thumbnails (YouTube CDN)
  Game logos (Minecraft, FNaF, Garry's Mod, Fortnite) are embedded, so they
  always show. If the avatar/thumbnails ever fail to load, they fall back to
  the crowned-bear mark instead of a broken-image icon.

CONTENT
  - Real most-popular videos (top 6, tap to play inline)
  - Games, Duh Bear Squad Minecraft server (DuhBearzoSquad.ddns.net:4609, bedrock port 4609) + rules
  - Community rules (10) + Minecraft server rules (8)
  - Socials: YouTube @bearzo1_yt, Discord discord.gg/fMZnRZEeT8,
    TikTok @bearzo1_yt, Twitch twitch.tv/bearzo1_yt

WEEKLY AUTO-UPDATE (optional)
  update_videos.py re-scrapes the channel and rewrites the top-6 videos AND the
  hero stat tiles (videos count, top-video views) in every copy. Run it anytime:
      python3 update_videos.py            (add --dry-run to preview)
  To run it automatically every Sunday, install the LaunchAgent:
      cp com.thankdapro.bearzo-update.plist ~/Library/LaunchAgents/
      launchctl load -w ~/Library/LaunchAgents/com.thankdapro.bearzo-update.plist
  It refreshes the LOCAL files only — re-upload index.html afterward to publish.

PRODUCTION PASS (2026-07-31) — what "exceptional" added on top of the base site
  - Social unfurl: Open Graph + Twitter Card + canonical + theme-color, so the
    Discord-pinned link shows the crowned-bear image, title & blurb.
  - Accessibility: <main> landmark + skip link, keyboard-operable server-IP box
    (Enter/Space) with an aria-live announcement, visible grass focus ring,
    AA-contrast text, full prefers-reduced-motion coverage, and a no-JS fallback
    so content still shows if scripts are blocked.
  - Honest copy: the IP box only says "COPIED" when the clipboard write actually
    succeeds; otherwise it selects the text and says "SELECT + COPY".
  - Mobile: hamburger menu with section links + a Join Discord shortcut.
  - Thumbnails now show in full colour on touch devices (were stuck grayscale).
  - Signature moment: copying the server IP triggers a Minecraft "block-break"
    voxel burst + pixel-font toast.
  - Motion trimmed for focus (removed cursor glow, tilt limited to the hero card,
    shimmer limited to the hero headline); canvas pauses when the tab is hidden.

Theme: black + Minecraft grass-green, Space Grotesk / pixel fonts.

EASTER EGG (2026-09-06)
  A faint bear photo hides in the top-right of the "games on the menu." section
  (8% opacity, 246px, brightens to 18% on hover). Click him: a goofy running
  sound plays, he vanishes, and a cut-out bear runs across the bottom of the
  screen in 2s. Then it's gone until you refresh. Hidden entirely in
  accessibility mode / prefers-reduced-motion.
  THE SOUND IS INLINED as a base64 data URI inside index.html (#bearSfx, 37KB)
  on purpose - there is no separate audio file to upload or forget.
  The rollercoaster shot is a full-bleed band between the server and community
  sections - full width, nothing on top of it, no scroll pinning.
