# Android Security for Banking Applications

A practical guide to securing banking apps on Android—certificate pinning, token management, secure storage, and MITM prevention.

---

## 1. Certificate Pinning

**Why:** A compromised CA can issue valid certificates for your domain. Pinning hardcodes the exact certificate/key you expect, making MITM impossible even with a valid certificate.

### Network Security Configuration (Declarative)

Simplest approach. Create `res/xml/network_security_config.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <domain-config cleartextTrafficPermitted="false">
        <domain includeSubdomains="true">api.yourbank.com</domain>
        
        <!-- Pin public key (SPKi format) -->
        <pin-set expiration="2026-12-31">
            <!-- Production certificate pin -->
            <pin digest="SHA-256">AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=</pin>
            <!-- Backup pin (for cert rotation) -->
            <pin digest="SHA-256">BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB=</pin>
        </pin-set>
    </domain-config>
</network-security-config>
```

Reference in `AndroidManifest.xml`:

```xml
<application
    android:networkSecurityConfig="@xml/network_security_config"
    ...>
</application>
```

**How to get the pin:**
```bash
# Extract public key from certificate
openssl x509 -in certificate.crt -pubkey -noout | openssl pkey -pubin -outform DER | openssl dgst -sha256 -binary | openssl enc -base64
```

### OkHttp Certificate Pinner (Programmatic)

For more control:

```kotlin
val certificatePinner = CertificatePinner.Builder()
    .add("api.yourbank.com", "sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=")
    .add("api.yourbank.com", "sha256/BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB=")
    .build()

val okHttpClient = OkHttpClient.Builder()
    .certificatePinner(certificatePinner)
    .connectTimeout(30, TimeUnit.SECONDS)
    .readTimeout(30, TimeUnit.SECONDS)
    .writeTimeout(30, TimeUnit.SECONDS)
    .build()

val retrofit = Retrofit.Builder()
    .baseUrl("https://api.yourbank.com/")
    .client(okHttpClient)
    .addConverterFactory(GsonConverterFactory.create())
    .build()
```

**Backup pin strategy:** Always pin 2+ public keys. When you rotate certificates, keep the old pin active for 30+ days so users with cached APKs don't break.

---

## 2. Token Management (JWT/OAuth)

### Secure Storage with EncryptedSharedPreferences

Use `androidx.security:security-crypto`:

```kotlin
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey

fun getEncryptedPreferences(context: Context): SharedPreferences {
    val masterKey = MasterKey.Builder(context)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
        .build()

    return EncryptedSharedPreferences.create(
        context,
        "bank_secure_prefs",
        masterKey,
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
    )
}

// Store token
fun storeAccessToken(context: Context, token: String) {
    getEncryptedPreferences(context).edit().putString("access_token", token).apply()
}

// Retrieve token
fun getAccessToken(context: Context): String? {
    return getEncryptedPreferences(context).getString("access_token", null)
}
```

The `MasterKey` is automatically managed by Android Keystore—you never see the key.

### DataStore (Modern Alternative)

For Kotlin-first apps, use DataStore with coroutines:

```kotlin
private val accessTokenKey = stringPreferencesKey("access_token")
private val refreshTokenKey = stringPreferencesKey("refresh_token")

suspend fun storeTokens(context: Context, accessToken: String, refreshToken: String) {
    context.dataStore.edit { preferences ->
        preferences[accessTokenKey] = accessToken
        preferences[refreshTokenKey] = refreshToken
    }
}

suspend fun getAccessToken(context: Context): String? {
    return context.dataStore.data.map { it[accessTokenKey] }.first()
}
```

DataStore is encrypted by default and handles thread safety.

### Token Refresh with Interceptor

Automatically refresh tokens before they expire:

```kotlin
class AuthInterceptor(
    private val context: Context,
    private val authService: AuthService
) : Interceptor {
    
    override fun intercept(chain: Interceptor.Chain): Response {
        var request = chain.request()
        
        // Add access token to request
        val token = runBlocking { getAccessToken(context) }
        request = request.newBuilder()
            .addHeader("Authorization", "Bearer $token")
            .build()
        
        var response = chain.proceed(request)
        
        // If 401 (unauthorized), try to refresh
        if (response.code == 401) {
            synchronized(this) {
                // Check again inside synchronized block (token might have been refreshed by another request)
                val newToken = runBlocking { getAccessToken(context) }
                
                if (newToken != token) {
                    // Another thread refreshed it, retry with new token
                    request = request.newBuilder()
                        .header("Authorization", "Bearer $newToken")
                        .build()
                    return chain.proceed(request)
                }
                
                // Refresh the token
                val refreshToken = runBlocking { getRefreshToken(context) }
                val refreshResponse = authService.refreshToken(refreshToken).execute()
                
                if (refreshResponse.isSuccessful) {
                    val newAccessToken = refreshResponse.body()?.accessToken ?: return response
                    runBlocking { storeAccessToken(context, newAccessToken) }
                    
                    // Retry original request with new token
                    request = request.newBuilder()
                        .header("Authorization", "Bearer $newAccessToken")
                        .build()
                    response.close()
                    return chain.proceed(request)
                } else {
                    // Refresh failed—logout user
                    logout(context)
                    return response
                }
            }
        }
        
        return response
    }
}

// Add to OkHttpClient
val okHttpClient = OkHttpClient.Builder()
    .addInterceptor(AuthInterceptor(context, authService))
    .build()
```

### Token Invalidation on Logout

```kotlin
fun logout(context: Context) {
    val prefs = getEncryptedPreferences(context)
    prefs.edit().clear().apply()
    
    // Also clear in-memory state
    clearAuthState()
}
```

---

## 3. Request Signing (HMAC/RSA)

Guarantee request integrity—server verifies that requests came from your app and weren't tampered with.

### HMAC-SHA256 Signing (Shared Secret)

```kotlin
import javax.crypto.Mac
import javax.crypto.spec.SecretKeySpec
import android.util.Base64

fun signRequest(
    method: String,
    path: String,
    timestamp: String,
    body: String,
    secret: String
): String {
    val message = "$method\n$path\n$timestamp\n$body"
    
    val mac = Mac.getInstance("HmacSHA256")
    val secretKeySpec = SecretKeySpec(secret.toByteArray(), "HmacSHA256")
    mac.init(secretKeySpec)
    
    val signature = mac.doFinal(message.toByteArray())
    return Base64.encodeToString(signature, Base64.NO_WRAP)
}

// Use in interceptor
.addInterceptor { chain ->
    val originalRequest = chain.request()
    val timestamp = System.currentTimeMillis().toString()
    val body = // read request body if present
    
    val signature = signRequest(
        originalRequest.method,
        originalRequest.url.pathSegments.joinToString("/"),
        timestamp,
        body,
        SHARED_SECRET
    )
    
    val signedRequest = originalRequest.newBuilder()
        .addHeader("X-Signature", signature)
        .addHeader("X-Timestamp", timestamp)
        .build()
    
    chain.proceed(signedRequest)
}
```

Server re-computes the signature and compares. If it doesn't match, the request was tampered with.

### RSA Signing (Public Key)

For higher security, use RSA stored in Keystore:

```kotlin
import android.security.keystore.KeyProperties
import android.security.keystore.KeyGenParameterSpec
import javax.crypto.Cipher
import java.security.KeyStore

fun generateRSAKeyPair(alias: String) {
    val keyStore = KeyStore.getInstance("AndroidKeyStore")
    keyStore.load(null)
    
    if (!keyStore.containsAlias(alias)) {
        val keyGenerator = KeyPairGenerator.getInstance(
            KeyProperties.KEY_ALGORITHM_RSA,
            "AndroidKeyStore"
        )
        
        val spec = KeyGenParameterSpec.Builder(
            alias,
            KeyProperties.PURPOSE_SIGN or KeyProperties.PURPOSE_VERIFY
        )
            .setDigests(KeyProperties.DIGEST_SHA256)
            .setSignaturePaddings(KeyProperties.SIGNATURE_PADDING_RSA_PKCS1)
            .setUserAuthenticationRequired(false)  // Set true if biometric auth needed
            .build()
        
        keyGenerator.initialize(spec)
        keyGenerator.generateKeyPair()
    }
}

fun signWithRSA(message: String, keyAlias: String): String {
    val keyStore = KeyStore.getInstance("AndroidKeyStore")
    keyStore.load(null)
    
    val privateKey = keyStore.getKey(keyAlias, null) as PrivateKey
    val signature = Signature.getInstance("SHA256withRSA")
    signature.initSign(privateKey)
    signature.update(message.toByteArray())
    
    return Base64.encodeToString(signature.sign(), Base64.NO_WRAP)
}
```

---

## 4. Secure Storage with Android Keystore

Keystore protects keys with hardware-backed encryption (if available).

```kotlin
fun storeEncryptionKey(alias: String) {
    val keyStore = KeyStore.getInstance("AndroidKeyStore")
    keyStore.load(null)
    
    if (!keyStore.containsAlias(alias)) {
        val keyGenerator = KeyGenerator.getInstance(
            KeyProperties.KEY_ALGORITHM_AES,
            "AndroidKeyStore"
        )
        
        val spec = KeyGenParameterSpec.Builder(
            alias,
            KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT
        )
            .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
            .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
            .setUserAuthenticationRequired(true)  // Require fingerprint
            .setUserAuthenticationValidityDurationSeconds(300)  // Valid for 5 min
            .build()
        
        keyGenerator.init(spec)
        keyGenerator.generateKey()
    }
}

fun encryptData(plaintext: String, keyAlias: String): Pair<String, String> {
    val keyStore = KeyStore.getInstance("AndroidKeyStore")
    keyStore.load(null)
    
    val secretKey = keyStore.getKey(keyAlias, null) as SecretKey
    val cipher = Cipher.getInstance("AES/GCM/NoPadding")
    cipher.init(Cipher.ENCRYPT_MODE, secretKey)
    
    val iv = cipher.iv
    val ciphertext = cipher.doFinal(plaintext.toByteArray())
    
    return Pair(
        Base64.encodeToString(ciphertext, Base64.NO_WRAP),
        Base64.encodeToString(iv, Base64.NO_WRAP)
    )
}

fun decryptData(ciphertext: String, iv: String, keyAlias: String): String {
    val keyStore = KeyStore.getInstance("AndroidKeyStore")
    keyStore.load(null)
    
    val secretKey = keyStore.getKey(keyAlias, null) as SecretKey
    val cipher = Cipher.getInstance("AES/GCM/NoPadding")
    
    val decodedIv = Base64.decode(iv, Base64.NO_WRAP)
    val spec = GCMParameterSpec(128, decodedIv)
    cipher.init(Cipher.DECRYPT_MODE, secretKey, spec)
    
    val plaintext = cipher.doFinal(Base64.decode(ciphertext, Base64.NO_WRAP))
    return String(plaintext)
}
```

**Hardware-backed:** On devices with TEE (Trusted Execution Environment), the key never leaves the secure enclave—attackers can't extract it even with root.

---

## 5. MITM Prevention Checklist

- ✅ Certificate pinning (Network Security Config or OkHttp)
- ✅ Enforce HTTPS only (`cleartextTrafficPermitted="false"`)
- ✅ Validate certificate chains (trust manager)
- ✅ Use strong TLS versions (TLS 1.2+)
- ✅ Disable insecure cipher suites
- ✅ Implement token refresh (don't reuse old tokens forever)
- ✅ Sign sensitive requests (HMAC/RSA)
- ✅ Encrypt token storage (Keystore)

---

## 6. Sensitive Data Handling

### What NOT to Log
```kotlin
// ❌ BAD
Log.d("Auth", "Token: $accessToken")
Log.d("Card", "CC: $cardNumber")

// ✅ GOOD
Log.d("Auth", "Token fetched (${token.length} chars)")
Log.d("Card", "Card masked: ****-****-****-${cardNumber.takeLast(4)}")
```

### Clear Data When Done
```kotlin
// Clear sensitive from memory after use
val password = readPassword()
try {
    // use password
} finally {
    password.fill('\u0000')  // Clear the array
}
```

### Disable Backups
Prevent system from backing up sensitive data to cloud:

```xml
<!-- AndroidManifest.xml -->
<application
    android:allowBackup="false"
    android:usesCleartextTraffic="false"
    ...>
</application>
```

---

## Summary

| Task | Solution |
|------|----------|
| Pin certificates | Network Security Config or OkHttp CertificatePinner |
| Store tokens | EncryptedSharedPreferences or DataStore |
| Refresh tokens | AuthInterceptor with 401 handling |
| Guarantee integrity | HMAC-SHA256 or RSA signing |
| Protect keys | Android Keystore (hardware-backed if available) |
| Prevent MITM | Certificate pinning + enforce HTTPS |

For banking apps: **combine all of these.** Each layer adds defense.
