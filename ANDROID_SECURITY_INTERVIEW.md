# Android Security for Interviews

Conceptual explanations of banking-grade security patterns—what they are, why they matter, and when to use them.

---

## 1. Certificate Pinning

### What is it?

Certificate pinning is a technique where you hardcode (pin) the exact SSL/TLS certificate or public key you expect from your server into your app. Instead of trusting *any* certificate signed by a valid Certificate Authority (CA), your app only accepts *specific* certificates.

### The Problem It Solves

**Normal HTTPS flow:**
- Your app trusts any certificate signed by a valid CA
- CAs are supposed to be trustworthy, but they're not perfect
- If a CA is compromised (or issues a cert to an attacker by mistake), an attacker can MITM your traffic
- Example: In 2011, Dutch CA DigiNotar was hacked and issued fake certs for Google, Facebook, etc.

**With pinning:**
- Even if an attacker has a valid certificate from a compromised CA, it won't match the pinned cert in your app
- Your app rejects it and fails the connection (safe failure)

### When You'd Use It

- Banking apps, payment apps, any app handling sensitive data
- Apps where the cost of MITM is extremely high
- Not needed for weather apps or public data

### Interview Angle

"Certificate pinning prevents Man-in-the-Middle attacks even if a Certificate Authority is compromised. Normal HTTPS trusts any valid CA, but pinning trusts only specific certificates. This is critical for banking apps where intercepted traffic could mean stolen money or credentials."

### Implementation Strategy

Two approaches:
1. **Network Security Configuration (XML)** — declarative, Android handles it
2. **OkHttp CertificatePinner** — programmatic, more control

Always pin 2+ certificates (backup strategy). When rotating certs, keep the old one pinned for 30+ days so cached APKs still work.

---

## 2. Token Management (JWT/OAuth)

### What is it?

Tokens (JWTs, OAuth access tokens) are credentials that prove you're authenticated. They're issued by the server after login and sent with every subsequent request to say "I'm user X, and I logged in."

### The Problem It Solves

**Without tokens:**
- You'd send username/password with every request
- Password lives on device in plaintext (bad)
- Password traverses network frequently (bad)
- One compromised request exposes the password forever (bad)

**With tokens:**
- Password only sent once (during login)
- Token sent with requests (much safer)
- Token expires after N minutes (limited lifetime)
- Token can be revoked by the server
- New tokens can be issued without user re-entering password

### Key Concepts

**Access Token:** Short-lived (15 min - 1 hour). Proves you're authenticated right now.

**Refresh Token:** Long-lived (days/weeks). Used to get a new access token when the old one expires. Never sent to API endpoints, only to the auth server.

**Why two tokens?**
- If access token is stolen, attacker has limited time (15 min)
- If refresh token is stolen but hidden in secure storage, still hard to use
- Separation of concerns: access token is "hot" (sent everywhere), refresh token is "cold" (stays in storage)

### When You'd Use It

Every modern API. Banking apps especially.

### Interview Angle

"Tokens replace sending passwords with every request. Access tokens are short-lived and sent with each API call. Refresh tokens are long-lived and stored securely, used only to get new access tokens. This means even if an access token is stolen, the attacker has limited time to use it."

### Implementation Strategy

1. **Store tokens securely** — EncryptedSharedPreferences or DataStore (encrypted by default)
2. **Attach to requests** — Interceptor adds `Authorization: Bearer $token` header
3. **Handle 401 responses** — If server says "token expired", use refresh token to get a new one
4. **Refresh automatically** — Do this in an interceptor so the user never knows
5. **Clear on logout** — Delete token from storage

Key gotcha: If multiple requests arrive while token is expired, only ONE should refresh (use `synchronized` block). Others wait for the refresh, then retry with new token.

---

## 3. Request Signing (HMAC/RSA)

### What is it?

Request signing means creating a cryptographic signature of your request and sending it with the request. The server re-computes the signature and verifies it matches. If it matches, the request wasn't tampered with.

### The Problem It Solves

**Without signing:**
- Attacker intercepts request and modifies it
- Changes amount in payment from $10 to $10,000
- Sends modified request to server
- Server processes the modified request (doesn't know it was changed)

**With signing:**
- Request is signed with a secret (only your app knows the secret)
- Attacker intercepts and modifies the request
- Signature no longer matches the modified content
- Server rejects the request as tampered

### Two Approaches

**HMAC-SHA256 (Shared Secret):**
- You and the server share a secret key
- You compute: `signature = HMAC_SHA256(secret, request_data)`
- Send signature in header
- Server computes the same thing, verifies it matches
- If attacker modifies request, signature won't match

**RSA (Public Key):**
- You have a private key (in Keystore, never leaves device)
- You compute: `signature = RSA_sign(private_key, request_data)`
- Send signature in header
- Server has your public key, verifies: `RSA_verify(public_key, signature, request_data)`
- Attacker can't forge a signature without your private key

### When You'd Use It

- Banking apps signing payment requests
- Sensitive data modifications
- Not needed for reads/queries

### Interview Angle

"Request signing prevents tampering with data in transit. Even if HTTPS is broken (unlikely but possible), signing ensures the server knows if the request was modified. HMAC requires a shared secret, RSA requires only the public key (stronger). RSA is better for banking because the private key never leaves the secure enclave."

### Implementation Strategy

Sign the request in an OkHttp interceptor. Include in the signature:
- HTTP method (GET, POST, etc.)
- Request path
- Timestamp (prevents replay attacks)
- Request body

Never sign authentication headers (they change), only the payload.

---

## 4. Android Keystore

### What is it?

Android Keystore is a secure container for cryptographic keys. Keys stored here are encrypted and, on modern devices, protected by a hardware Trusted Execution Environment (TEE). Even if your phone is rooted, attackers can't extract keys from Keystore.

### The Problem It Solves

**Without Keystore:**
- You store encryption keys in code or shared preferences
- Rooted phone + decompiled APK = attacker has the key
- Key is compromised forever
- Any data encrypted with that key is now decryptable by anyone

**With Keystore:**
- Key is stored in a hardware-protected enclave
- Even root access can't extract it
- Key stays inside the TEE, performs operations there
- Data encrypted with TEE keys can't be decrypted outside the TEE

### Hardware-Backed vs Software-Backed

**Hardware-backed (TEE):**
- Key lives in the phone's secure processor
- Attacker with root can't extract it
- Available on most modern Android phones

**Software-backed:**
- Key is encrypted in software
- More secure than nothing, less than hardware
- Fallback if device doesn't have TEE

### When You'd Use It

- Storing tokens (indirectly, via EncryptedSharedPreferences)
- Storing encryption keys for sensitive data
- Signing requests with private keys (payment apps)

### Interview Angle

"Android Keystore stores cryptographic keys in a hardware-protected enclave (TEE) that even root access can't break into. Keys never leave the enclave. This is why EncryptedSharedPreferences and DataStore are secure—they use Keystore under the hood. Banking apps rely on this to protect tokens and payment keys."

### Implementation Strategy

1. Generate a key in Keystore (only once, check if it exists first)
2. Use the key to encrypt/decrypt or sign/verify
3. Never export the key outside Keystore
4. Optional: Require biometric authentication before key can be used

```kotlin
// Generate key once
val spec = KeyGenParameterSpec.Builder(
    "token_key",
    KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT
)
    .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
    .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
    .setUserAuthenticationRequired(true)  // Require fingerprint
    .build()

KeyGenerator.getInstance("AES", "AndroidKeyStore").apply {
    init(spec)
    generateKey()
}

// Use the key (biometric prompt will appear if auth required)
val key = keyStore.getKey("token_key", null)
cipher.init(Cipher.ENCRYPT_MODE, key)
val encrypted = cipher.doFinal(plaintext.toByteArray())
```

---

## 5. Secure Storage: EncryptedSharedPreferences vs DataStore

### EncryptedSharedPreferences

**What:** Wrapper around SharedPreferences that encrypts keys and values using Keystore.

**Pros:**
- Simple to use (same API as SharedPreferences)
- Transparent encryption/decryption
- Works with existing SharedPreferences code

**Cons:**
- Synchronous (blocks UI if you're not careful)
- Shared preferences are technically insecure even encrypted (used for config, not secrets)

**When:** Storing non-sensitive settings that need encryption (app preferences, user IDs).

### DataStore

**What:** Modern replacement for SharedPreferences. Encrypted by default, async (coroutine-based), type-safe.

**Pros:**
- Fully async (no blocking)
- Type-safe (compile-time checking)
- Transactions (all writes succeed or all fail)
- Encrypted by default (via Keystore)

**Cons:**
- Slightly more boilerplate
- Requires coroutines

**When:** Modern apps, anything with tokens, any app written in Kotlin.

### Interview Angle

"SharedPreferences is insecure even when encrypted—it's really for config. EncryptedSharedPreferences adds encryption but is still synchronous. DataStore is the modern choice: it's async, type-safe, encrypted by default, and works well with Kotlin coroutines. For tokens, use DataStore."

### Implementation Comparison

**EncryptedSharedPreferences:**
```kotlin
val prefs = getEncryptedPreferences(context)
prefs.edit().putString("access_token", token).apply()  // Synchronous
```

**DataStore:**
```kotlin
context.dataStore.edit { prefs ->
    prefs[ACCESS_TOKEN_KEY] = token  // Async, suspending
}
```

---

## 6. MITM (Man-in-the-Middle) Prevention

### What is a MITM Attack?

Attacker positions themselves between your app and the server:
```
[Your App] <---> [Attacker] <---> [Server]
```

Attacker can:
- Read all traffic (steal tokens, credentials, data)
- Modify traffic (change amounts in transactions, inject malware)
- Replay old requests (charge you twice)

Happens on public WiFi, compromised networks, intercepting proxies.

### How to Prevent

**Layer 1: HTTPS**
- Encrypts traffic so attacker can't read it
- But: doesn't prevent MITM if cert is compromised

**Layer 2: Certificate Pinning**
- Ensures attacker can't forge a valid cert
- Prevents MITM even if CA is compromised

**Layer 3: Request Signing**
- Ensures attacker can't modify requests
- Even if they intercept it, signature won't match

**Layer 4: Token Refresh**
- Access token is short-lived (15 min)
- Even if token is stolen, attacker has limited time
- New token can't be obtained without refresh token (stored securely)

### Interview Angle

"MITM attacks are prevented by layers: HTTPS hides traffic, certificate pinning prevents fake certs, request signing prevents tampering, and token refresh limits the damage if a token is stolen. A good banking app implements all of these."

---

## 7. OAuth 2.0 / Token Refresh Flow

### The Flow

**Login:**
1. User enters credentials
2. App sends to server
3. Server validates, returns: `{ accessToken, refreshToken }`
4. App stores both securely (DataStore)

**Making Requests:**
1. App attaches `Authorization: Bearer $accessToken` to request
2. Server validates token, processes request
3. If token valid, request succeeds

**Token Expires:**
1. App makes request with expired token
2. Server returns 401 (Unauthorized)
3. App intercepts 401, uses `refreshToken` to get new `accessToken`
4. App retries original request with new token
5. Request succeeds
6. User never knows token expired

**Logout:**
1. App deletes both tokens from storage
2. Server invalidates tokens in its database
3. Any stolen token is now useless

### Why Two Tokens?

- **Access token:** Sent with every request. If stolen, attacker has limited time (15 min).
- **Refresh token:** Stored securely, used only for auth server. If stolen, harder to use (requires going to auth server, might be detected).

Attacker who steals access token can pretend to be you for 15 minutes. Attacker who steals refresh token can get new access tokens forever (unless server detects unusual refresh patterns).

### Interview Angle

"OAuth uses two tokens: short-lived access tokens for API calls, long-lived refresh tokens for getting new access tokens. If access token is stolen, you have 15 minutes. If refresh token is stolen, the server can detect suspicious refresh activity. The refresh logic should happen transparently in an interceptor—user never knows the token expired."

---

## 8. Sensitive Data Handling

### Never Log Sensitive Data

**Bad:**
```kotlin
Log.d("Auth", "Token: $accessToken")  // Token visible in logcat
Log.d("Payment", "Card: $cardNumber")  // Card visible in logcat
```

**Good:**
```kotlin
Log.d("Auth", "Token length: ${token.length}")  // Just metadata
Log.d("Payment", "Card last 4: ${card.takeLast(4)}")  // Masked
```

Why: On user's rooted device, attacker can read logcat. Logcat may be uploaded for crash reporting. Tokens/cards in logs = compromise.

### Clear Sensitive Data from Memory

**Bad:**
```kotlin
val password = readPassword()
authenticateUser(password)  // Password might stay in memory
```

**Good:**
```kotlin
val password = readPassword()
try {
    authenticateUser(password)
} finally {
    password.fill('\u0000')  // Overwrite with zeros
}
```

Why: If app crashes or is analyzed later, sensitive data in memory can be extracted.

### Disable Backups

```xml
<application android:allowBackup="false" ...>
</application>
```

Why: If backups are enabled, system backs up app data to Google Drive. If cloud account is hacked, attacker gets your tokens.

### Interview Angle

"Sensitive data shouldn't appear in logs (use metadata instead). Overwrite sensitive strings/arrays after use so they don't linger in memory. Disable cloud backups so tokens don't end up in compromised cloud accounts."

---

## 9. API Security Best Practices

### Rate Limiting

**What:** Limit how many requests per second a client can make.

**Why:** Prevents brute force attacks (trying every password), DoS attacks.

**Implementation:** Server enforces, not app. But app should handle 429 (Too Many Requests) gracefully.

### Replay Attack Prevention

**What:** Attacker intercepts a valid request and sends it again.

Example: `POST /transfer money=$1000` → attacker replays → user charged twice.

**Prevention:**
- Timestamp in request (`X-Timestamp` header)
- Server rejects requests older than 60 seconds
- Server keeps a set of recent timestamps, rejects duplicates

### Idempotency

**What:** Making the same request twice should have the same effect as once.

**Example:**
- Bad: `POST /transfer` — if network dies, user doesn't know if money was sent. Retry might send twice.
- Good: `POST /transfer?idempotencyKey=ABC123` — even if retried 10 times, money sent once

**Implementation:** Client sends unique key, server stores it. If same key arrives again, return cached response instead of processing.

### Interview Angle

"API security requires timestamp checks to prevent replay attacks, idempotency keys to ensure retries don't cause duplicates, and rate limiting to prevent brute force. The client should implement idempotency keys on critical requests like payments."

---

## Summary Table

| Concept | Problem | Solution |
|---------|---------|----------|
| **Certificate Pinning** | Compromised CA issues fake cert | Pin specific certs in app |
| **Token Management** | Passwords unsafe to send repeatedly | Use short-lived access tokens + long-lived refresh tokens |
| **Request Signing** | Attacker modifies request in transit | Sign request with HMAC/RSA, server verifies |
| **Android Keystore** | Keys extractable from rooted phone | Store keys in hardware TEE |
| **DataStore/Encrypted Prefs** | Plaintext tokens in storage | Encrypt tokens with Keystore |
| **Token Refresh Flow** | Stolen token useful forever | Access token expires, refresh token gets new one |
| **No Logging Secrets** | Secrets visible in logcat | Log metadata only, mask sensitive values |
| **Replay Prevention** | Attacker sends same request twice | Add timestamp, server rejects old requests |
| **Idempotency** | Retries cause duplicates | Client sends unique key, server deduplicates |

### Interview Approach

When asked about security:

1. **Identify the threat** — "What's the worst that could happen?"
2. **Explain the solution** — "Here's why this prevents that threat"
3. **Mention implementation** — "On Android, you'd use..."
4. **Show judgment** — "You'd combine multiple layers for banking apps, but not all apps need everything"

Example: "For a banking app, I'd use certificate pinning to prevent MITM, tokens with refresh for auth, request signing for payments, and Keystore to protect keys. For a weather app, just HTTPS is fine."
