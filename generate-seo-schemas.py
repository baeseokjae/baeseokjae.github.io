#!/usr/bin/env python3
import os
import re
import json
from datetime import datetime
from pathlib import Path
import yaml


blog_dir = Path("/home/ubuntu/blog")
posts_dir = blog_dir / "content" / "posts"
partials_dir = blog_dir / "layouts" / "partials"

def extract_faq_items(content):
    """Extract FAQ items from markdown content"""
    faq_pattern = r'## FAQ.*?(?=## [A-Z]|\Z)'
    faq_match = re.search(faq_pattern, content, re.DOTALL | re.IGNORECASE)
    if not faq_match:
        return []

    faq_section = faq_match.group(0)

    # Pattern for Q&A pairs: ### Question as heading, followed by answer text
    qa_pattern = r'###\s+([^\n]+)\n\n([^\n]*(?:\n(?!###)[^\n]*)*)'
    matches = re.findall(qa_pattern, faq_section)

    faq_items = []
    for question, answer in matches:
        question = question.strip()
        answer = answer.strip()
        if question and answer:
            faq_items.append({"question": question, "answer": answer})

    return faq_items

def shorten_description(desc, max_len=155):
    """Shorten description to fit meta description limit"""
    if len(desc) <= max_len:
        return desc
    # Try to cut at a word boundary
    trimmed = desc[:max_len]
    last_space = trimmed.rfind(' ')
    if last_space > max_len - 20:
        trimmed = trimmed[:last_space]
    return trimmed.rstrip('.,;:')

def generate_schema(slug, title, description, date_published, faq_items, image_path):
    """Generate Article and FAQ schema JSON-LD"""
    article_schema = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title,
        "description": shorten_description(description),
        "datePublished": datetime.fromisoformat(str(date_published).replace('+00:00', '')).isoformat() + 'Z',
        "author": {
            "@type": "Organization",
            "name": "Blog"
        },
        "image": image_path
    }

    faq_schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": item["question"],
                "@Answer": {
                    "@type": "Answer",
                    "text": item["answer"]
                }
            }
            for item in faq_items
        ]
    }

    # Fix the typo
    for item in faq_schema["mainEntity"]:
        item["acceptedAnswer"] = item.pop("@Answer")

    return article_schema, faq_schema

def main():
    processed = 0
    skipped = 0
    for post_file in sorted(posts_dir.glob("*.md")):
        slug = post_file.stem
        schema_file = partials_dir / f"schema-{slug}.html"

        # Read post
        with open(post_file) as f:
            content = f.read()
            # Split content and metadata
            metadata_start = content.find('---')
            metadata_end = content.find('---', metadata_start + 3)
            
            metadata = yaml.safe_load(content[metadata_start + 3:metadata_end])
            post_content = content[metadata_end + 3:].strip()

        title = metadata.get("title", "")
        description = metadata.get("description", "")
        date = metadata.get("date", "")
        cover = metadata.get("cover", {})
        image = cover.get("image", f"/images/{slug}.png") if isinstance(cover, dict) else f"/images/{slug}.png"

        # Extract FAQ items
        faq_items = extract_faq_items(post_content)

        # Generate Article schema
        article_schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": title,
            "description": shorten_description(description),
            "datePublished": datetime.fromisoformat(str(date).replace('+00:00', '')).isoformat() + 'Z',
            "author": {
                "@type": "Organization",
                "name": "Blog"
            },
            "image": image
        }

        # Create HTML file
        html_content = f"""<script type="application/ld+json">
{json.dumps(article_schema, indent=2)}
</script>"""

        # Add FAQ schema if FAQ items found
        if faq_items:
            faq_schema = {
                "@context": "https://schema.org",
                "@type": "FAQPage",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": item["question"],
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": item["answer"]
                        }
                    }
                    for item in faq_items
                ]
            }
            html_content += f"""
<script type="application/ld+json">
{json.dumps(faq_schema, indent=2)}
</script>"""

        # Write file
        with open(schema_file, 'w') as f:
            f.write(html_content)

        if faq_items:
            print(f"✓ {slug}: {len(faq_items)} FAQ items")
        else:
            print(f"✓ {slug}: Article schema only")
        processed += 1

    print(f"\n✓ Generated schemas for {processed} posts")

if __name__ == "__main__":
    main()
