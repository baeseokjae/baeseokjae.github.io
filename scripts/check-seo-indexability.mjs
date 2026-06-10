import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";

const siteBase = "https://baeseokjae.github.io";
const publicDir = new URL("../public/", import.meta.url).pathname;

const readPublic = (relativePath) => {
	const filePath = join(publicDir, relativePath);
	if (!existsSync(filePath)) {
		throw new Error(`Missing file: public/${relativePath}`);
	}
	return readFileSync(filePath, "utf8");
};

const extractTags = (xml, tagName) =>
	[...xml.matchAll(new RegExp(`<${tagName}>([^<]+)</${tagName}>`, "g"))].map(
		(match) => match[1].trim(),
	);

const htmlPathForUrl = (url) => {
	const parsed = new URL(url);
	if (parsed.origin !== siteBase) {
		return null;
	}
	if (parsed.pathname === "/") {
		return "index.html";
	}
	return `${parsed.pathname.replace(/^\/|\/$/g, "")}/index.html`;
};

const getAttribute = (tag, attributeName) => {
	const match = tag.match(
		new RegExp(`\\s${attributeName}=("[^"]*"|'[^']*'|[^\\s>]+)`, "i"),
	);
	if (!match) {
		return undefined;
	}
	return match[1].replace(/^["']|["']$/g, "");
};

const assertXmlBasics = (xml, label, expectedRoot) => {
	if (!xml.startsWith('<?xml version="1.0"')) {
		throw new Error(`${label}: XML declaration must be the first bytes`);
	}
	if (!xml.includes('xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"')) {
		throw new Error(`${label}: missing sitemap namespace`);
	}
	if (!xml.includes(`<${expectedRoot}`)) {
		throw new Error(`${label}: expected root <${expectedRoot}>`);
	}
};

const failures = [];
const fail = (message) => failures.push(message);

const indexXml = readPublic("sitemap.xml");
assertXmlBasics(indexXml, "sitemap.xml", "sitemapindex");

const childSitemaps = extractTags(indexXml, "loc");
if (childSitemaps.length === 0) {
	fail("sitemap.xml: sitemap index has no child sitemaps");
}

const allUrls = [];
for (const childUrl of childSitemaps) {
	if (!childUrl.startsWith(`${siteBase}/`)) {
		fail(`sitemap.xml: child sitemap is outside site: ${childUrl}`);
		continue;
	}

	const relativePath = new URL(childUrl).pathname.replace(/^\//, "");
	let childXml;
	try {
		childXml = readPublic(relativePath);
	} catch (error) {
		fail(error.message);
		continue;
	}

	assertXmlBasics(childXml, relativePath, "urlset");
	const urls = extractTags(childXml, "loc");
	if (urls.length === 0) {
		fail(`${relativePath}: has no URLs`);
	}
	allUrls.push(...urls.map((url) => [url, relativePath]));
}

const seen = new Set();
for (const [url, sitemapPath] of allUrls) {
	if (seen.has(url)) {
		fail(`${sitemapPath}: duplicate URL: ${url}`);
		continue;
	}
	seen.add(url);

	let parsed;
	try {
		parsed = new URL(url);
	} catch {
		fail(`${sitemapPath}: invalid URL: ${url}`);
		continue;
	}

	if (parsed.origin !== siteBase) {
		fail(`${sitemapPath}: URL outside site: ${url}`);
		continue;
	}

	const relativeHtmlPath = htmlPathForUrl(url);
	let html;
	try {
		html = readPublic(relativeHtmlPath);
	} catch (error) {
		fail(`${sitemapPath}: ${error.message} for ${url}`);
		continue;
	}

	const robotsTags = [
		...html.matchAll(/<meta\s+[^>]*name=["']?robots["']?[^>]*>/gi),
	].map((match) => match[0]);
	if (robotsTags.length !== 1) {
		fail(`${url}: expected exactly one robots meta tag, found ${robotsTags.length}`);
	}
	if (robotsTags.some((tag) => /noindex/i.test(tag))) {
		fail(`${url}: sitemap URL has noindex robots meta`);
	}

	const canonicalMatch = html.match(/<link\s+[^>]*rel=["']?canonical["']?[^>]*>/i);
	if (!canonicalMatch) {
		fail(`${url}: missing canonical link`);
		continue;
	}
	const canonical = getAttribute(canonicalMatch[0], "href");
	if (canonical !== url) {
		fail(`${url}: canonical mismatch: ${canonical ?? "(missing href)"}`);
	}
}

console.log(
	JSON.stringify(
		{
			childSitemaps: childSitemaps.length,
			urls: allUrls.length,
			failures: failures.length,
		},
		null,
		2,
	),
);

if (failures.length > 0) {
	console.error(failures.map((failure) => `- ${failure}`).join("\n"));
	process.exit(1);
}
