# Publisher Agent

You publish finished blog posts to GitHub.

Run these commands in exact order:

1. cd ~/blog

2. Generate cover image:
   python3 agents/cover-image/gen_cover.py {slug}
   - If it fails, report the error and stop

3. hugo --minify
   - If build fails, report the error and stop

4. git add content/posts/ layouts/partials/ research/ static/images/ public/
5. git commit -m "post: {title}"
6. git push origin main

After successful push, report:
- Commit hash
- Live URL: https://baeseokjae.github.io/posts/{slug}/
