---
title: 'macOS Data Protection Keychain for Electron Apps: Securing AI Agent Credentials'
date: 2026-09-20T01:01:09+00:00
description: Secure AI agent API keys in Electron apps with the macOS Data Protection Keychain, code-signing access groups, kSecUseDataProtectionKeychain, and Touch ID.
draft: false
cover:
  image: /images/macos-data-protection-keychain-electron-2026.png
  alt: 'macOS Data Protection Keychain for Electron Apps: Securing AI Agent Credentials'
  relative: false
tags:
- macOS
- Electron
- Keychain
- Security
- AI Agents
- API Keys
- Code Signing
schema: "schema-macos-data-protection-keychain-electron-2026"
---

Electron's `safeStorage` is not strong enough to protect the API keys your AI agent app stores. To secure OpenAI, Anthropic, or JWT credentials against other processes and malicious code, use the macOS Data Protection Keychain directly with `kSecUseDataProtectionKeychain: true`, restrict access to a code-signing access group, and gate decryption behind Touch ID or a password. This guide walks through the threat model, the code-signing setup, and a working implementation that keeps a dozen backgrounded agents from reading each other's secrets.

## Why AI Agent Credentials Need More Than safeStorage

When you build an Electron app that stores OpenAI or Anthropic API keys, `safeStorage.encryptString()` looks like the obvious choice. It is built into Electron, requires no native modules, and on macOS the key lives in the Keychain. That last fact is misleading. Electron's `safeStorage` is roughly a 100-line C++ wrapper over Chromium's OSCrypt, and it inherits every limitation of that layer — most importantly, the legacy file-based Keychain that any local process can query through the `security` CLI if it can read your app's binary path.

The danger is concrete for AI agents. A developer workstation today runs a dozen agent processes, language-server extensions, and npm packages all under the same user account. Legacy Keychain items are scoped to the signing identity, but historically any process invoking `/usr/bin/security` that knows the access group could pull the stored data without a prompt. Chen Guangliang's security analysis of Electron credential storage spells out the sharpest version of the problem: child processes, injected libraries, and malicious npm packages are treated as the app itself, so a compromised dependency can call the same decryption API and succeed with no user interaction.

The core question every credential-store design must answer is not "is it encrypted?" but **"encrypted against whom?"** Windows DPAPI protects against *other users*; the legacy macOS Keychain and the Linux secret store protect against *other applications*; hardware-backed stores such as the Data Protection Keychain protect against the OS reading your secrets directly. For AI agents running untrusted code, per-user stores are effectively readable by that code. Only a store that separates access at the application level — the Data Protection Keychain — gives you the isolation you actually need.

## The macOS Keychain Threat Model: Legacy File-Based vs. Data Protection Keychain

macOS has shipped two Keychain implementations, and the difference matters more than most Electron tutorials admit.

**Legacy file-based Keychain.** This is the store that Chromium's OSCrypt and therefore Electron's `safeStorage` target by default on macOS. Items live in a keychain file protected by a single master password, and the encryption key is stored in the Keychain Access database. Because the master key is shared per-user, any process running as the same user — including another agent, an injected library, or a tool that calls `security` — can, under the right conditions, obtain the data without a decryption prompt. The ACL is coarse and tied to a binary signer identity rather than a hardened per-app boundary.

**Data Protection Keychain (DPK).** Introduced in macOS 10.15, this is the modern store that keys on the device's hardware security. It supports three capabilities the legacy store does not:

- **Code-signing access groups** via the `keychain-access-groups` entitlement — only explicitly entitled apps in the same access group can read an item.
- **iCloud Keychain sync**, so credentials follow the user across devices.
- **Biometric access control** through `SecAccessControl` — Touch ID or device-owner password gating before a key is released.

The `security` CLI cannot open DPK items that are restricted by an access group, which closes the "any process can query via CLI" hole. When a rogue same-user process tries to read an item, the system surfaces the standard Keychain access prompt (or requires the configured biometric), and only that specific signed binary path is authorized — not every binary under your account.

This per-app isolation is exactly what makes the Data Protection Keychain superior to safeStorage for AI-agent credential vaults. Your agent's API key should be unreadable by the other agent running five feet away on the same machine, and only DPK gives you that boundary by default.

## What Electron's safeStorage Actually Protects (and Doesn't)

To make an informed choice you have to know precisely where safeStorage falls short.

**What it does protect.** On macOS, safeStorage encrypts a string using AES-128-CBC with a key it stores in the Keychain (under `<AppName> Safe Storage`). The key entry is protected by the system ACL, the Keychain prompts for authorization, and the encrypted database remains unusable even if the disk is stolen — unless the account has no login password set. For casual, single-app secrets, safeStorage is meaningfully better than storing plaintext on disk.

**What it does not protect.**

- **Hardcoded IV and no authenticated encryption.** Chromium's OSCrypt encrypts with AES-128-CBC and a hardcoded initialization vector of 16 space characters — not a random IV per encryption. Identical plaintext produces identical ciphertext, enabling ciphertext comparison, and CBC without authentication leaves the data exposed to bit-flipping and padding-oracle attacks if an attacker can drive chosen plaintext into your store.
- **Linux falls back to plaintext-equivalent storage by default.** On Linux without libsecret or KWallet, Electron silently drops to `basic_text`: PBKDF2 with a single iteration, the hardcoded `saltysalt` salt, and a source password embedded in the binary. Worse, this is the *default* fallback and ships with no warning. Your "secure" API keys are effectively recoverable by anyone who can read the app's files.
- **No sandbox for extensions or code.** Electron does not sandbox extensions or plugins. Any runnable Node package, extension, or injected library runs with the same full privileges as the app and can call the decryption API itself. The VS Code case is instructive: any installed extension can read the entire secrets DB at `~/.config/Code/User/globalStorage/state.vscdb` and decrypt every secret, because the extension shares the app's single Keychain ACL.
- **Master keys live in process memory.** Recent malware such as VoidStealer (disclosed by Kaspersky in March 2026) steals the master key by attaching a debugger and setting a hardware breakpoint where the app calls its decryption API. No admin, no injection, and no EDR alert — the key simply spends a moment in the heap and gets siphoned out.

Note also that `safeStorage.isEncryptionAvailable()` returning `true` only means a secret store exists; it says nothing about how strong or how isolated that store is. Calling it is not a security guarantee.

## Setting Up a Signed Electron App: Code Signing and Keychain Sharing Entitlements

The Data Protection Keychain API rejects unsigned apps, so code signing is not optional — it is the foundation. Here is the minimal path to a signed, entitled macOS Electron app.

**1. Obtain a Developer ID Application certificate.** You need an Apple Developer account and a `Developer ID Application` (or `Mac App Distribution`) certificate. Electron Forge and electron-builder can pull certificates from the keychain via environment variables, but for local development you can sign ad hoc, as long as you understand that ad-hoc-signed apps must still declare the keychain access group.

**2. Add the Keychain Sharing entitlement.** Create an entitlements file (`build/entitlements.mac.plist`) that names your access group. Access groups are reverse-DNS identifiers; the convention is `<bundle-identifier>.<suffix>`, and groups outside your provisioning team must be prefixed with your Team ID:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>keychain-access-groups</key>
  <array>
    <string>$(AppIdentifierPrefix)com.yourteam.agentapp.credentials</string>
  </array>
</dict>
</plist>
```

**3. Point electron-builder at the entitlements.** In `package.json`:

```json
"build": {
  "mac": {
    "entitlements": "build/entitlements.mac.plist",
    "entitlementsInherit": "build/entitlements.mac.plist",
    "hardenedRuntime": true,
    "gatekeeperAssess": false
  }
}
```

**4. Sign and verify.** After building, confirm the signature and the access group are embedded:

```bash
codesign -d --entitlements - path/to/YourApp.app
```

If the entitlements dump shows `keychain-access-groups`, you are ready to use the Data Protection Keychain.

## Using the keychain-store Library: Accounts, mutableAccounts, and Touch ID

With signing in place, the cleanest way to reach `kSecUseDataProtectionKeychain` from Electron is the `keychain-store` npm package (companion to a Swift `KeychainStore` library for native macOS). It was built specifically because safeStorage's legacy keychain can be queried by other agents via the `security` CLI — dangerous when several AI agents run in the background. It targets the Data Protection Keychain, restricts items to code-signing access groups, and exposes the SecItem API without legacy file-based baggage.

A minimal add-and-read flow:

```js
import { KeychainStore } from "keychain-store";

const store = new KeychainStore({
  // bundle id is the default service; you can override
  service: "com.yourteam.agentapp",
});

// store an OpenAI key, restricted to your access group
await store.setAccount("openai-api-key", {
  account: "openai",
  data: "sk-...",                 // the secret
  accessGroup: "com.yourteam.agentapp.credentials",
  dataProtection: true,           // kSecUseDataProtectionKeychain
});

// read it back
const { data } = await store.getAccount("openai-api-key");
```

The library keeps two named item sets:

- **`accounts`** — immutable account entries created once and never updated, useful for fixed metadata like an agent role's public identifiers.
- **`mutableAccounts`** — writable entries where secrets like rotating API keys and JWTs live. Rotating a key is a single store update rather than a delete-and-recreate.

Two practical advantages follow. First, package access is restricted to the exact item names you declare, so a compromised dependency cannot enumerate the whole vault. Second, because access is tied to your signing access group, another agent process — even with the same user — cannot read your items without a Keychain authorization.

## Adding Biometric Protection: User-Presence vs. Biometrics-Only

The Data Protection Keychain adds a security tier no other Electron credential store reaches: you can require Touch ID or the device password before the key is released. `SecAccessControl` offers two flags with different behavior:

- **User-presence** (`kSecAccessControlUserPresence`): passes if the user authenticates with *either* Touch ID or the device password. Best default for most agents — a fallback exists but no secret is ever handed out without a human gesture.
- **Biometry any** / **biometry current set** (`kSecAccessControlBiometryAny` or `...BiometryCurrentSet`): requires Touch ID specifically, with no password fallback. Use `BiometryAny` for a permissive biometric policy or `BiometryCurrentSet` if you want enrollments added later to be excluded.

In `keychain-store`, pass an access-control option on write:

```js
const { data } = await store.getAccount("openai-api-key", {
  accessControl: "userPresence", // or "biometryAny" | "biometryCurrentSet"
});
```

Reads then trigger the system prompt for authorization before returning the key. That prompt is a deliberate feature: it converts a silent background read by rogue code into an on-screen event the user will notice and approve or reject. For a long-lived backgrounded AI agent, gate the initial unlock (for example, at startup) with user-presence, then hold the decrypted key in memory for the session — but recognize the trade-off: the key will briefly live in memory, which is why you should never log or dump it.

For most agent use cases, **user-presence is the recommended default**: it offers a usable unlock path and still blocks unattended reads. Reserve biometry-only for vaults that must never be readable with a stolen password alone.

## Cross-Platform Fallback: safeStorage on Linux and Windows

The Data Protection Keychain is macOS-only, and an Electron app is typically cross-platform. The recommended pattern is to use `keychain-store` where it is strong (macOS) and fall back to `safeStorage` on Linux and Windows, preserving Electron's cross-platform promise while taking the strongest option on every OS where it exists:

```js
const platform = process.platform;
const isMac = platform === "darwin";

const vault = isMac
  ? keychainStoreVault          // Data Protection Keychain + Touch ID
  : safeStorageVault;           // safeStorage (DPAPI / libsecret)
```

Know the ceiling of each fallback:

- **Windows** uses DPAPI, which is per-user and not per-app. Any process running as the same user can decrypt without a prompt; there is no isolation between two agents under one account.
- **Linux** uses libsecret/KWallet, which is also per-user. And if no secret store is present, safeStorage silently drops to `basic_text` — the plaintext-equivalent default described earlier. Always call `safeStorage.isEncryptionAvailable()` and refuse to run if it reports only `basic_text`.

The cross-platform reality is that only macOS gives you real per-application isolation out of the box. On Linux and Windows, treat safeStorage as obfuscation rather than a true vault, and consider hardware-backed or cloud-KMS-backed options for anything you cannot afford to leak.

## Common Pitfalls: The security CLI, Hardcoded IV, basic_text, and Unsandboxed Extensions

Bake these four failure modes into your threat model now, because each one has shipped in production apps.

1. **The `security` CLI can drain a legacy keychain.** If you use safeStorage on macOS, the underlying keychain item may be readable by any process that can invoke `/usr/bin/security` with the right path and access group. Always use the Data Protection Keychain (`kSecUseDataProtectionKeychain: true`) with a code-signing access group so the CLI is refused.
2. **The hardcoded IV defeats ciphertext indistinguishability.** Same secret twice → same ciphertext, because OSCrypt reuses a fixed 16-space IV in AES-128-CBC. Anyone who can write to your store and observe the output can test guesses or flip bytes. There is no per-record authentication.
3. **Linux `basic_text` is a silent plaintext fallback.** When libsecret/KWallet is missing, safeStorage returns `basic_text` by default: PBKDF2 with one iteration, the `saltysalt` salt, and a hardcoded password. Verify the actual backend with `safeStorage.getSelectedStorageBackend()` before trusting the result; if it is not a real secret store, refuse to persist secrets.
4. **Electron does not sandbox extensions or plugins.** Any runnable code you load shares your process privileges and your Keychain ACL, so it can decrypt without a prompt. Vet dependencies as you would code that reaches into your production database, keep the trusted runtime as small as possible, and never bundle credentials inside the renderer or an extension host.

## Comparing Options: safeStorage vs. keytar vs. keychain-store vs. electron-store

| Option | Platform isolation | Biometric / Touch ID | Native build | Notes |
|--------|-------------------|----------------------|--------------|-------|
| `safeStorage` (built-in) | macOS: legacy file-based (per-signer, weak); Windows/Linux: per-user | No | None (Chromium built in) | Hardcoded IV; silent `basic_text` fallback on Linux |
| `keytar` | Legacy Keychain / per-user | No | Native module builds per platform | Reliable but unmaintained ergonomics, build pain |
| `keychain-store` (npm, macOS) | **Data Protection Keychain, per-app access group** | **Yes (UserPresence / Biometry)** | Optional Swift lib | Strongest option; macOS-only, falls back to safeStorage elsewhere |
| `electron-store` with custom encryption | Per-app *file* only | No | None | The `encryptionKey` option is obfuscation, not real security — do not use for API keys |

The row to internalize: `electron-store`'s `encryptionKey` (e.g., `'this_only_obfuscates'`) is not encryption you should rely on — it is reversible obfuscation with a key in the source. `keytar` works but adds native-module build friction and does not reach the Data Protection Keychain. `keychain-store` is the only drop-in that gives you per-app isolation plus biometric gating on macOS.

## Step-by-Step Summary Checklist

Follow this order to ship a securely vaulted AI-agent credential store in an Electron app:

1. **Sign the app** with a Developer ID Application certificate; confirm with `codesign -d --entitlements -`.
2. **Add the `keychain-access-groups` entitlement** naming your access group in `build/entitlements.mac.plist`, with hardened runtime enabled.
3. **Depend on `keychain-store`** and set `dataProtection: true` plus your `accessGroup` on every item.
4. **Store secrets in `mutableAccounts`**; keep public metadata in immutable `accounts`.
5. **Gate reads with `userPresence`** for the general unlock; use biometry-only only for vaults that must never be readable with a password alone.
6. **On Linux and Windows, fall back to `safeStorage`**, but check `getSelectedStorageBackend()` and refuse to persist if it reports `basic_text`.
7. **Vet every dependency and extension** as if it could call your decryption API, because in Electron it can.
8. **Never log the key or the decrypted secret**, and keep in-memory copies short-lived.

## FAQ

**Is Electron's `safeStorage` secure enough to store API keys?**
Not for AI-agent credentials on macOS. It relies on the legacy file-based Keychain and Chromium's OSCrypt, which uses a hardcoded IV, and on Linux it silently falls back to plaintext-equivalent `basic_text` storage. Use the Data Protection Keychain with a code-signing access group instead.

**What is `kSecUseDataProtectionKeychain`?**
It is a SecItem flag that directs the Keychain API to the modern Data Protection Keychain instead of the legacy file-based store. It enables code-signing access groups, iCloud Keychain sync, and biometric access control that the legacy store does not support.

**Can the `security` CLI read secrets stored by the Data Protection Keychain?**
No, when items are scoped to a code-signing access group, the `security` CLI cannot open them the way it can query legacy file-based keychain items. This is the key isolation gap safeStorage leaves open.

**What does Touch ID add to keychain storage?**
`SecAccessControl` with user-presence requires the user to authenticate with Touch ID or the device password before a key is released, turning silent background reads into an on-screen approval. It blocks unattended decryption by malicious code and is the recommended default for agents.

**Is the Data Protection Keychain available on Linux or Windows?**
No, it is macOS-only. On Linux and Windows you fall back to `safeStorage`, which is per-user (Windows DPAPI and libsecret/KWallet) and offers no per-application isolation, and on Linux it may silently drop to plaintext-equivalent `basic_text` if no secret store is installed.
