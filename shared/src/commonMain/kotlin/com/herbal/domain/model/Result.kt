@file:Suppress("unused")
package com.herbal.domain.model

import com.whitelabel.core.domain.model.onSuccess as coreOnSuccess
import com.whitelabel.core.domain.model.onError as coreOnError
import com.whitelabel.core.domain.model.getOrNull as coreGetOrNull
import com.whitelabel.core.domain.model.getOrThrow as coreGetOrThrow

// Typealias to core Result — all existing code keeps working
typealias Result<T> = com.whitelabel.core.domain.model.Result<T>

// Re-export extension functions so existing imports keep working
inline fun <T> Result<T>.onSuccess(action: (T) -> Unit): Result<T> = coreOnSuccess(action)
inline fun <T> Result<T>.onError(action: (Throwable) -> Unit): Result<T> = coreOnError(action)
fun <T> Result<T>.getOrNull(): T? = coreGetOrNull()
fun <T> Result<T>.getOrThrow(): T = coreGetOrThrow()
