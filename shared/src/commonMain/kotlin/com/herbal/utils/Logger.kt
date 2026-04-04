package com.herbal.utils

// Re-export from whitelabel-platform
import co.touchlab.kermit.Logger as KermitLogger
import co.touchlab.kermit.Severity

object Logger {
    private val logger = KermitLogger.withTag("MuseumApp")

    fun d(message: String) {
        logger.d { message }
    }

    fun i(message: String) {
        logger.i { message }
    }

    fun w(message: String) {
        logger.w { message }
    }

    fun e(message: String, throwable: Throwable? = null) {
        if (throwable != null) {
            logger.e(throwable) { message }
        } else {
            logger.e { message }
        }
    }

    fun v(message: String) {
        logger.v { message }
    }
}

// Convenience function for logging - converts LogLevel and delegates to platform
fun LOG(message: String, level: LogLevel = LogLevel.DEBUG) {
    val platformLevel = when (level) {
        LogLevel.VERBOSE -> com.whitelabel.platform.utils.LogLevel.VERBOSE
        LogLevel.DEBUG -> com.whitelabel.platform.utils.LogLevel.DEBUG
        LogLevel.INFO -> com.whitelabel.platform.utils.LogLevel.INFO
        LogLevel.WARN -> com.whitelabel.platform.utils.LogLevel.WARN
        LogLevel.ERROR -> com.whitelabel.platform.utils.LogLevel.ERROR
    }
    com.whitelabel.platform.utils.LOG(message, platformLevel, "MuseumApp")
}

fun LOG(message: String, throwable: Throwable) {
    com.whitelabel.platform.utils.LOG(message, throwable, "MuseumApp")
}

enum class LogLevel {
    VERBOSE,
    DEBUG,
    INFO,
    WARN,
    ERROR
}

// Performance monitoring - delegates to platform
inline fun <T> measureTimeAndLog(tag: String, block: () -> T): T {
    return com.whitelabel.platform.utils.measureTimeAndLog(tag, block)
}

// Thread checker - delegates to platform
fun checkMainThread() {
    com.whitelabel.platform.utils.checkMainThread()
}
