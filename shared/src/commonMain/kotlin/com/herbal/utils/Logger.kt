package com.herbal.utils

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

